"""Train the Go → Cangjie Transformer — incremental & resumable.

Run as::

    python -m go2cj.neural.train                    # resume + train 1 epoch
    python -m go2cj.neural.train --epochs 3         # train 3 more epochs
    python -m go2cj.neural.train --restart          # start over from scratch

Checkpoint protocol (designed for short, repeated training sessions):

* ``model.pt``         — model weights + config + optimizer / scheduler
                         state + epoch counter.  Written **atomically**
                         after *every* epoch so a SIGKILL never loses
                         more than one epoch's progress.
* ``vocab.json``       — token vocab.  Built **once** on first run and
                         then frozen, so the same `model.pt` continues
                         to be loadable as the curated trainset grows
                         (new tokens go to ``<unk>``; OOV stays
                         < 1% in practice because we anonymize).
* ``model_meta.json``  — running metrics for human inspection.

The trainer assembles fresh training data on every invocation
(curated trainset + synthetic generator + anonymization), so adding
new pairs to ``go2cj/trainset/`` and re-running picks them up
immediately.  Validation accuracy is reported every epoch and the
checkpoint is always saved with the *latest* metrics.

Quality knobs that have been tuned for this small problem:

* Anonymized inputs — model only learns canonical templates.
* d_model=96, 2 enc / 2 dec layers, nhead=6 — small & fast on CPU
  (~0.7 M params); converges in a few epochs on ≤ 20 k pairs.
* OneCycleLR is recreated each run scaled by the *remaining* epochs.
* Curriculum: short anonymized chunks dominate early; long
  multi-statement chunks are weighted in via the curated trainset.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from .anonymize import anonymize_pair
from .corpus import generate_corpus
from .curated import augment_pairs, load_curated_pairs
from .model import Seq2SeqTransformer
from .vocab import Vocab, tokenize_text


PKG_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PKG_DIR / "model.pt"           # best-so-far (used by translator)
DEFAULT_LAST_PATH = PKG_DIR / "model_last.pt"        # latest (used to resume training)
DEFAULT_VOCAB_PATH = PKG_DIR / "vocab.json"
DEFAULT_META_PATH = PKG_DIR / "model_meta.json"


def _atomic_save(state, path: Path) -> None:
    """Atomic-replace ``torch.save`` so checkpoints are never half-written."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    torch.save(state, tmp)
    os.replace(tmp, path)


def _atomic_write_text(text: str, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def build_corpus(n_synth: int, curated_factor: int, seed: int,
                 anonymize: bool = True):
    """Assemble training pairs from curated + synthetic sources."""
    curated = load_curated_pairs()
    if anonymize:
        curated_expanded = augment_pairs(curated, factor=curated_factor,
                                         seed=seed)
    else:
        curated_expanded = list(curated)
    synth = generate_corpus(n_samples=n_synth, seed=seed) if n_synth > 0 else []
    if anonymize:
        synth = [anonymize_pair(g, c) for g, c in synth]
    all_pairs = curated_expanded + synth
    return all_pairs, len(curated), len(curated_expanded), len(synth)


class PairDataset(Dataset):
    def __init__(self, pairs, vocab: Vocab, max_len: int = 256):
        self.pairs = pairs
        self.vocab = vocab
        self.max_len = max_len

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx):
        go, cj = self.pairs[idx]
        src = self.vocab.encode(tokenize_text(go))[: self.max_len]
        tgt = self.vocab.encode(
            tokenize_text(cj), add_bos=True, add_eos=True
        )[: self.max_len]
        return (
            torch.tensor(src, dtype=torch.long),
            torch.tensor(tgt, dtype=torch.long),
        )


def collate(batch, pad_idx: int):
    srcs, tgts = zip(*batch)
    max_s = max(len(x) for x in srcs)
    max_t = max(len(x) for x in tgts)
    def pad(xs, m):
        out = torch.full((len(xs), m), pad_idx, dtype=torch.long)
        for i, x in enumerate(xs):
            out[i, : len(x)] = x
        return out
    return pad(srcs, max_s), pad(tgts, max_t)


def label_smoothed_nll(logits, target, pad_idx, smoothing=0.1):
    logp = nn.functional.log_softmax(logits, dim=-1)
    nll = -logp.gather(-1, target.unsqueeze(-1)).squeeze(-1)
    smooth = -logp.mean(dim=-1)
    loss = (1 - smoothing) * nll + smoothing * smooth
    mask = (target != pad_idx).float()
    return (loss * mask).sum() / mask.sum().clamp_min(1)


def _evaluate(model, val_loader, pad_idx):
    model.eval()
    v_correct = v_total = 0
    with torch.no_grad():
        for src, tgt in val_loader:
            tgt_in = tgt[:, :-1]
            tgt_out = tgt[:, 1:]
            logits = model(src, tgt_in)
            pred = logits.argmax(-1)
            mask = (tgt_out != pad_idx)
            v_correct += int(((pred == tgt_out) & mask).sum().item())
            v_total += int(mask.sum().item())
    return v_correct / max(1, v_total)


def _evaluate_seq(model, val_loader, vocab, bos_idx, eos_idx, max_len):
    model.eval()
    seq_correct = seq_total = 0
    with torch.no_grad():
        for src, tgt in val_loader:
            preds = model.greedy_decode(
                src, bos_idx=bos_idx, eos_idx=eos_idx, max_len=max_len,
            )
            for i in range(preds.size(0)):
                if vocab.decode(preds[i].tolist()) == \
                   vocab.decode(tgt[i].tolist()):
                    seq_correct += 1
                seq_total += 1
    return seq_correct, seq_total


def train(
    n_samples: int = 8000,
    curated_factor: int = 60,
    epochs: int = 1,
    batch_size: int = 96,
    lr: float = 5e-4,
    seed: int = 0xC0FFEE,
    d_model: int = 96,
    nhead: int = 6,
    n_layers: int = 2,
    max_len: int = 256,
    restart: bool = False,
    anonymize: bool = True,
    model_path: Path = DEFAULT_MODEL_PATH,
    vocab_path: Path = DEFAULT_VOCAB_PATH,
    meta_path: Path = DEFAULT_META_PATH,
    log_every: int = 100,
) -> None:
    torch.manual_seed(seed)
    random.seed(seed)
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    # Has a previous checkpoint? Determine resume mode.
    # Prefer model_last.pt for resume (latest optimizer state); fall back
    # to model.pt if model_last.pt is missing (older checkpoints).
    last_path = DEFAULT_LAST_PATH
    resume_from = last_path if last_path.exists() else model_path
    have_ckpt = resume_from.exists() and vocab_path.exists()
    resume = have_ckpt and not restart

    print(
        f"[train] {'RESUME' if resume else 'FRESH'} — "
        f"assembling corpus (synth={n_samples}, curated_factor={curated_factor}, "
        f"anonymize={anonymize}) ...",
        flush=True,
    )
    pairs, n_curated_raw, n_curated_aug, n_synth = build_corpus(
        n_samples, curated_factor, seed, anonymize=anonymize,
    )
    print(
        f"[train] curated={n_curated_raw} → augmented={n_curated_aug}; "
        f"synth={n_synth}; total={len(pairs)}",
        flush=True,
    )
    rng = random.Random(seed)
    rng.shuffle(pairs)
    split = int(len(pairs) * 0.97)
    train_pairs, val_pairs = pairs[:split], pairs[split:]

    # Vocab — frozen on first build so checkpoints stay compatible.
    if resume:
        vocab = Vocab.load(vocab_path)
        print(f"[train] loaded vocab ({len(vocab)} tokens) from {vocab_path}",
              flush=True)
    else:
        all_tokens = []
        for go, cj in pairs:
            all_tokens.append(tokenize_text(go))
            all_tokens.append(tokenize_text(cj))
        vocab = Vocab.build(all_tokens, min_freq=1)
        vocab.save(vocab_path)
        print(f"[train] built vocab ({len(vocab)} tokens) → {vocab_path}",
              flush=True)

    pad_idx = vocab.stoi["<pad>"]
    bos_idx = vocab.stoi["<bos>"]
    eos_idx = vocab.stoi["<eos>"]

    train_ds = PairDataset(train_pairs, vocab, max_len=max_len)
    val_ds = PairDataset(val_pairs, vocab, max_len=max_len)
    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        collate_fn=lambda b: collate(b, pad_idx),
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        collate_fn=lambda b: collate(b, pad_idx),
    )

    # Model — reuse config from checkpoint when resuming, otherwise build fresh.
    if resume:
        state = torch.load(resume_from, map_location="cpu", weights_only=False)
        cfg = state["config"]
        # Sanity: same vocab size?  If a contributor added new tokens to
        # the trainset, the new tokens map to <unk> for this checkpoint,
        # which is fine.  We never *grow* the vocab without --restart.
        model = Seq2SeqTransformer(**cfg)
        model.load_state_dict(state["model_state"])
        start_epoch = int(state.get("epoch", 0))
        prev_meta = state.get("meta", {})
        print(
            f"[train] resumed {resume_from.name} from epoch {start_epoch} "
            f"(prev val_tok_acc={prev_meta.get('val_tok_acc', 'n/a')})",
            flush=True,
        )
    else:
        cfg = dict(
            vocab_size=len(vocab),
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=n_layers,
            num_decoder_layers=n_layers,
            dim_feedforward=4 * d_model,
            dropout=0.1,
            pad_idx=pad_idx,
            max_len=max(max_len + 8, 64),
        )
        model = Seq2SeqTransformer(**cfg)
        start_epoch = 0

    n_params = sum(p.numel() for p in model.parameters())
    print(f"[train] model params = {n_params/1e6:.2f}M (d_model={cfg['d_model']}, "
          f"layers={cfg['num_encoder_layers']}, nhead={cfg['nhead']})",
          flush=True)

    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        optim, max_lr=lr,
        total_steps=epochs * max(1, len(train_loader)),
        pct_start=0.1,
    )
    # Restore optimizer state if resuming (so momentum etc. carries over).
    if resume:
        try:
            if "optim_state" in state:
                optim.load_state_dict(state["optim_state"])
        except Exception as e:
            print(f"[train] warning: could not restore optimizer state ({e})",
                  flush=True)

    # Read existing "best" metrics from meta_path so a partial training
    # session can never demote a good checkpoint.
    best_tok_acc = -1.0
    best_seq_acc = -1.0
    best_epoch = 0
    if meta_path.exists():
        try:
            prev = json.loads(meta_path.read_text())
            best_tok_acc = float(prev.get("best_val_tok_acc",
                                          prev.get("val_tok_acc", -1.0)))
            best_seq_acc = float(prev.get("best_val_seq_acc",
                                          prev.get("val_seq_acc", -1.0)))
            best_epoch = int(prev.get("best_epoch", prev.get("epoch", 0)))
        except Exception:
            pass

    v_acc = 0.0
    for local_ep in range(1, epochs + 1):
        global_ep = start_epoch + local_ep
        model.train()
        t0 = time.time()
        epoch_loss = 0.0
        n_batches = 0
        for step, (src, tgt) in enumerate(train_loader, 1):
            tgt_in = tgt[:, :-1]
            tgt_out = tgt[:, 1:]
            logits = model(src, tgt_in)
            loss = label_smoothed_nll(logits, tgt_out, pad_idx)
            optim.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optim.step()
            sched.step()
            epoch_loss += float(loss.item())
            n_batches += 1
            if step % log_every == 0:
                print(
                    f"[train] ep{global_ep} {step}/{len(train_loader)} "
                    f"loss {loss.item():.4f} lr {sched.get_last_lr()[0]:.2e}",
                    flush=True,
                )
        v_acc = _evaluate(model, val_loader, pad_idx)
        # Also compute seq accuracy each epoch (slower but lets us
        # promote/discard checkpoints accurately every epoch).
        seq_correct, seq_total = _evaluate_seq(
            model, val_loader, vocab, bos_idx, eos_idx, max_len,
        )
        seq_acc = seq_correct / max(1, seq_total)
        elapsed = time.time() - t0
        print(
            f"[train] ep{global_ep} done loss={epoch_loss/max(1,n_batches):.4f} "
            f"val_tok_acc={v_acc:.4f} val_seq_acc={seq_acc:.4f} "
            f"time={elapsed:.1f}s",
            flush=True,
        )

        # Promote to best if strictly better on the primary metric
        # (seq_acc), with tok_acc as the tie-breaker.  This is the
        # "always keep the best version, discard worse" guarantee.
        improved = (seq_acc > best_seq_acc) or (
            seq_acc == best_seq_acc and v_acc > best_tok_acc
        )
        if improved:
            best_tok_acc = v_acc
            best_seq_acc = seq_acc
            best_epoch = global_ep

        meta = {
            "epoch": global_ep,
            "best_epoch": best_epoch,
            "n_samples": n_samples,
            "curated_pairs_raw": n_curated_raw,
            "curated_pairs_augmented": n_curated_aug,
            "synth_pairs": n_synth,
            "total_pairs": len(pairs),
            "batch_size": batch_size,
            "lr": lr,
            "vocab_size": len(vocab),
            "params": int(n_params),
            "val_tok_acc": v_acc,
            "val_seq_acc": seq_acc,
            "best_val_tok_acc": best_tok_acc,
            "best_val_seq_acc": best_seq_acc,
            "anonymize": anonymize,
            "seed": seed,
        }
        ckpt = {
            "model_state": model.state_dict(),
            "optim_state": optim.state_dict(),
            "config": cfg,
            "epoch": global_ep,
            "anonymize": anonymize,
            "meta": meta,
        }
        # ALWAYS save "last" — resume continues optimizer state seamlessly.
        _atomic_save(ckpt, DEFAULT_LAST_PATH)
        # ONLY overwrite "best" model.pt when this epoch improved.  The
        # translator loads model.pt, so inference always uses the best.
        if improved or not model_path.exists():
            _atomic_save(ckpt, model_path)
            promoted = "PROMOTED"
        else:
            promoted = (
                f"kept best (ep{best_epoch} "
                f"seq_acc={best_seq_acc:.4f}, tok_acc={best_tok_acc:.4f})"
            )
        _atomic_write_text(json.dumps(meta, indent=2), meta_path)
        print(
            f"[train] checkpoint saved (ep{global_ep}, "
            f"{DEFAULT_LAST_PATH.stat().st_size/1e6:.2f}MB) — {promoted}",
            flush=True,
        )

    print(
        f"[train] best checkpoint = ep{best_epoch} "
        f"(val_seq_acc={best_seq_acc:.4f}, val_tok_acc={best_tok_acc:.4f})",
        flush=True,
    )


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Train / resume the Go→Cangjie Transformer.")
    p.add_argument("--samples", type=int, default=8000,
                   help="Synthetic samples per run (default: 8000).")
    p.add_argument("--curated-factor", type=int, default=60,
                   help="How many anonymized variants per curated pair.")
    p.add_argument("--epochs", type=int, default=1,
                   help="Epochs to add this run (resume-friendly).")
    p.add_argument("--batch-size", type=int, default=96)
    p.add_argument("--lr", type=float, default=5e-4)
    p.add_argument("--d-model", type=int, default=96)
    p.add_argument("--nhead", type=int, default=6)
    p.add_argument("--layers", type=int, default=2)
    p.add_argument("--seed", type=int, default=0xC0FFEE)
    p.add_argument("--restart", action="store_true",
                   help="Throw away existing model.pt / vocab.json.")
    p.add_argument("--no-anonymize", action="store_true",
                   help="Disable anonymization (debugging only).")
    args = p.parse_args(argv)
    train(
        n_samples=args.samples,
        curated_factor=args.curated_factor,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        d_model=args.d_model,
        nhead=args.nhead,
        n_layers=args.layers,
        seed=args.seed,
        restart=args.restart,
        anonymize=not args.no_anonymize,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
