"""Fine-tune CodeT5p-220m on the curated Go↔Cangjie chunk corpus.

Usage::

    bash scripts/download_base.sh                # one-time: fetch base model
    python -m go2cj_v3.train                     # 1 epoch incremental
    python -m go2cj_v3.train --epochs 3          # multi-epoch
    python -m go2cj_v3.train --restart --epochs 3   # restart from base

Best-checkpoint protocol (mirrors go2cj v1/v2):

* ``go2cj_v3/finetuned/``       — best by ``val_seq_acc``; used for inference.
* ``go2cj_v3/finetuned_last/``  — latest end-of-epoch snapshot for resuming.
* ``go2cj_v3/train_meta.json``  — running epoch counter + best metrics.

A bad new epoch never overwrites the deployed ``finetuned/`` directory.

Hyperparameter differences vs go2cj-v2 (the 60 M codet5-small backbone):

* batch_size default 2 (vs 4) — 220 M params + 512 seq length on CPU
  hits ~6-8 GB peak; batch 2 leaves headroom for sandbox runners.
* lr default 3e-5 (vs 5e-5) — bigger models prefer slightly smaller LRs.
* warmup_steps default 100 — codet5p-220m is more sensitive to early
  large updates; a short linear warmup avoids the loss spiking on
  step 1.
* max_seq_len default 512 (vs 384) — codet5p was pre-trained at 512
  context, and several test cases have func main bodies that
  tokenise to >400 BPE tokens.
* augment_factor default 8 (vs 12) — the bigger model already
  generalises better, so we cut augmentation to keep epoch time
  bounded on CPU.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import torch
from torch.utils.data import DataLoader, Dataset

from .dataset import load_curated_corpus, load_curated_pairs
from .translator import (
    BASE_MODEL_DIR, FINETUNED_DIR, FINETUNED_LAST_DIR, TASK_PREFIX,
    _load_tokenizer,
)


_PKG = Path(__file__).resolve().parent
META_PATH = _PKG / "train_meta.json"


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
class PairDataset(Dataset):
    def __init__(self, pairs: List[Tuple[str, str]], tokenizer,
                 max_input_len: int, max_target_len: int):
        self.pairs = pairs
        self.tok = tokenizer
        self.max_in = max_input_len
        self.max_out = max_target_len

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, i):
        go, cj = self.pairs[i]
        src = TASK_PREFIX + go
        enc = self.tok(
            src, truncation=True, max_length=self.max_in,
            padding=False, return_tensors=None,
        )
        # Modern HF tokenizers no longer need ``as_target_tokenizer``; just
        # tokenise the target with the same vocab.
        tgt = self.tok(
            cj, truncation=True, max_length=self.max_out,
            padding=False, return_tensors=None,
        )
        return {
            "input_ids": enc["input_ids"],
            "attention_mask": enc["attention_mask"],
            "labels": tgt["input_ids"],
        }


def _collate(batch, pad_id: int, label_pad: int = -100):
    max_in = max(len(b["input_ids"]) for b in batch)
    max_out = max(len(b["labels"]) for b in batch)
    input_ids, attn, labels = [], [], []
    for b in batch:
        n = len(b["input_ids"])
        input_ids.append(b["input_ids"] + [pad_id] * (max_in - n))
        attn.append(b["attention_mask"] + [0] * (max_in - n))
        m = len(b["labels"])
        labels.append(b["labels"] + [label_pad] * (max_out - m))
    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attn, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }


# ---------------------------------------------------------------------------
# Meta IO
# ---------------------------------------------------------------------------
@dataclass
class Meta:
    epoch: int = 0
    best_epoch: int = -1
    best_val_seq_acc: float = -1.0
    best_val_tok_acc: float = -1.0
    best_val_loss: float = float("inf")

    @classmethod
    def load(cls) -> "Meta":
        if META_PATH.is_file():
            d = json.loads(META_PATH.read_text("utf-8"))
            return cls(**{k: d.get(k, getattr(cls(), k))
                          for k in cls().__dict__.keys()})
        return cls()

    def save(self):
        META_PATH.write_text(
            json.dumps(self.__dict__, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Eval (sequence + token accuracy on a fixed validation slice of curated pairs)
# ---------------------------------------------------------------------------
@torch.no_grad()
def evaluate(model, tokenizer, val_pairs, max_input_len: int,
             max_target_len: int, batch_size: int = 2):
    model.eval()
    tot_tok = ok_tok = 0
    ok_seq = 0
    for i in range(0, len(val_pairs), batch_size):
        batch = val_pairs[i:i + batch_size]
        src = [TASK_PREFIX + g for g, _ in batch]
        enc = tokenizer(src, return_tensors="pt", padding=True,
                        truncation=True, max_length=max_input_len)
        out = model.generate(
            input_ids=enc["input_ids"],
            attention_mask=enc["attention_mask"],
            max_new_tokens=max_target_len,
            num_beams=1, do_sample=False,
        )
        for j, (_, ref) in enumerate(batch):
            pred = tokenizer.decode(out[j], skip_special_tokens=True).strip()
            ref_s = ref.strip()
            if pred == ref_s:
                ok_seq += 1
            # token-level (simple whitespace split for a cheap proxy)
            p_tok = pred.split()
            r_tok = ref_s.split()
            for k in range(max(len(p_tok), len(r_tok))):
                tot_tok += 1
                if k < len(p_tok) and k < len(r_tok) and p_tok[k] == r_tok[k]:
                    ok_tok += 1
    return (ok_seq / max(1, len(val_pairs)),
            ok_tok / max(1, tot_tok))


# ---------------------------------------------------------------------------
# Main trainer
# ---------------------------------------------------------------------------
def _atomic_save_model(model, tokenizer, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(tmp)
    tokenizer.save_pretrained(tmp)
    # Atomic-ish replace.
    if dst.exists():
        shutil.rmtree(dst)
    tmp.rename(dst)


def _linear_warmup_lambda(warmup_steps: int):
    def fn(step: int) -> float:
        if warmup_steps <= 0:
            return 1.0
        if step < warmup_steps:
            return float(step + 1) / float(warmup_steps)
        return 1.0
    return fn


def main(argv=None):
    p = argparse.ArgumentParser(prog="go2cj_v3.train")
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=2)
    p.add_argument("--lr", type=float, default=3e-5)
    p.add_argument("--warmup-steps", type=int, default=100)
    p.add_argument("--max-input-len", type=int, default=512)
    p.add_argument("--max-target-len", type=int, default=512)
    p.add_argument("--augment-factor", type=int, default=8)
    p.add_argument("--val-frac", type=float, default=0.05)
    p.add_argument("--val-max", type=int, default=120,
                   help="Cap eval set size to keep epoch time bounded on CPU.")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--restart", action="store_true",
                   help="Discard finetuned/ + finetuned_last/ and start from base.")
    p.add_argument("--num-workers", type=int, default=0)
    p.add_argument("--limit-train-batches", type=int, default=0,
                   help="If > 0, cap training batches per epoch (CPU safety).")
    p.add_argument("--grad-accum", type=int, default=1,
                   help="Gradient accumulation steps (effective batch = "
                        "batch_size * grad_accum).")
    args = p.parse_args(argv)

    random.seed(args.seed)
    torch.manual_seed(args.seed)

    from transformers import T5ForConditionalGeneration

    # Decide which checkpoint to load.
    if args.restart:
        for d in (FINETUNED_DIR, FINETUNED_LAST_DIR):
            if d.exists():
                shutil.rmtree(d)
        if META_PATH.exists():
            META_PATH.unlink()
        load_from = BASE_MODEL_DIR
    elif FINETUNED_LAST_DIR.is_dir():
        load_from = FINETUNED_LAST_DIR
    elif FINETUNED_DIR.is_dir():
        load_from = FINETUNED_DIR
    else:
        load_from = BASE_MODEL_DIR

    if not (load_from / "config.json").is_file():
        sys.exit(f"[train] no model at {load_from}. "
                 "Run scripts/download_base.sh first.")

    print(f"[train] loading from {load_from}", flush=True)
    tokenizer = _load_tokenizer(load_from)
    model = T5ForConditionalGeneration.from_pretrained(str(load_from))
    model.train()

    pad_id = tokenizer.pad_token_id or 0

    # Build corpus.
    canon = load_curated_pairs()
    if not canon:
        sys.exit("[train] no curated pairs in trainset/.")
    rng = random.Random(args.seed)
    rng.shuffle(canon)
    n_val = max(1, min(args.val_max, int(len(canon) * args.val_frac)))
    val_pairs = canon[:n_val]
    train_canon = canon[n_val:]
    train_pairs = load_curated_corpus(args.augment_factor)
    # Filter augmented pairs to those whose canonical pair is in the
    # training half (so augmented validation pairs don't leak).
    val_set = {(g.strip(), c.strip()) for g, c in val_pairs}
    train_pairs = [(g, c) for g, c in train_pairs
                   if (g.strip(), c.strip()) not in val_set]
    rng.shuffle(train_pairs)

    print(f"[train] curated={len(canon)} val={len(val_pairs)} "
          f"train(aug)={len(train_pairs)} aug_factor={args.augment_factor}",
          flush=True)

    ds = PairDataset(train_pairs, tokenizer,
                     args.max_input_len, args.max_target_len)
    loader = DataLoader(
        ds, batch_size=args.batch_size, shuffle=True,
        num_workers=args.num_workers,
        collate_fn=lambda b: _collate(b, pad_id),
    )

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr,
                            weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, _linear_warmup_lambda(args.warmup_steps),
    )

    meta = Meta.load()

    for ep in range(args.epochs):
        meta.epoch += 1
        t0 = time.time()
        model.train()
        running = 0.0
        n_batches = 0
        opt.zero_grad()
        for step, batch in enumerate(loader):
            if args.limit_train_batches and step >= args.limit_train_batches:
                break
            out = model(**batch)
            loss = out.loss / max(1, args.grad_accum)
            loss.backward()
            if (step + 1) % max(1, args.grad_accum) == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                opt.zero_grad()
            running += float(out.loss.detach())
            n_batches += 1
            if step % 50 == 0:
                lr_now = opt.param_groups[0]["lr"]
                print(f"[train] epoch {meta.epoch} step {step}/"
                      f"{len(loader)} loss={float(out.loss.detach()):.4f} "
                      f"lr={lr_now:.2e}",
                      flush=True)
        avg_loss = running / max(1, n_batches)

        # Validation
        val_seq, val_tok = evaluate(
            model, tokenizer, val_pairs,
            args.max_input_len, args.max_target_len,
        )
        dt = time.time() - t0
        print(f"[train] epoch {meta.epoch} done in {dt:.1f}s "
              f"loss={avg_loss:.4f} val_seq={val_seq:.3f} "
              f"val_tok={val_tok:.3f}", flush=True)

        # Save "last" snapshot.
        _atomic_save_model(model, tokenizer, FINETUNED_LAST_DIR)

        # Save "best" if strictly better on val_seq.
        if val_seq > meta.best_val_seq_acc + 1e-9:
            meta.best_val_seq_acc = val_seq
            meta.best_val_tok_acc = val_tok
            meta.best_val_loss = avg_loss
            meta.best_epoch = meta.epoch
            _atomic_save_model(model, tokenizer, FINETUNED_DIR)
            print(f"[train] new best @ epoch {meta.epoch}: "
                  f"val_seq={val_seq:.3f}", flush=True)
        meta.save()

    print(f"[train] finished. best_epoch={meta.best_epoch} "
          f"best_val_seq_acc={meta.best_val_seq_acc:.3f}", flush=True)


if __name__ == "__main__":
    main()
