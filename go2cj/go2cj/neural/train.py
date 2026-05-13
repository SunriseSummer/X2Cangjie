"""Train the Go → Cangjie Transformer.

Run as::

    python -m go2cj.neural.train --samples 20000 --epochs 12

Saves ``model.pt`` and ``vocab.json`` next to the package so that
:class:`go2cj.neural.translator.NeuralTranslator` can load them.
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

from .corpus import generate_corpus
from .model import Seq2SeqTransformer
from .vocab import Vocab, tokenize_text


PKG_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PKG_DIR / "model.pt"
DEFAULT_VOCAB_PATH = PKG_DIR / "vocab.json"
DEFAULT_META_PATH = PKG_DIR / "model_meta.json"


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
        return torch.tensor(src, dtype=torch.long), torch.tensor(
            tgt, dtype=torch.long
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


def label_smoothed_nll(
    logits: torch.Tensor, target: torch.Tensor, pad_idx: int, smoothing: float = 0.1
) -> torch.Tensor:
    """Label-smoothed cross-entropy that ignores pad positions."""
    V = logits.size(-1)
    logp = nn.functional.log_softmax(logits, dim=-1)
    nll = -logp.gather(-1, target.unsqueeze(-1)).squeeze(-1)
    smooth = -logp.mean(dim=-1)
    loss = (1 - smoothing) * nll + smoothing * smooth
    mask = (target != pad_idx).float()
    return (loss * mask).sum() / mask.sum().clamp_min(1)


def train(
    n_samples: int = 20000,
    epochs: int = 12,
    batch_size: int = 64,
    lr: float = 5e-4,
    seed: int = 0xC0FFEE,
    d_model: int = 128,
    nhead: int = 4,
    n_layers: int = 3,
    max_len: int = 256,
    model_path: Path = DEFAULT_MODEL_PATH,
    vocab_path: Path = DEFAULT_VOCAB_PATH,
    meta_path: Path = DEFAULT_META_PATH,
    log_every: int = 50,
) -> None:
    torch.manual_seed(seed)
    random.seed(seed)
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    print(f"[train] generating {n_samples} synthetic pairs ...", flush=True)
    pairs = generate_corpus(n_samples=n_samples, seed=seed)
    random.shuffle(pairs)
    split = int(len(pairs) * 0.97)
    train_pairs, val_pairs = pairs[:split], pairs[split:]

    print("[train] building vocab ...", flush=True)
    all_tokens = []
    for go, cj in pairs:
        all_tokens.append(tokenize_text(go))
        all_tokens.append(tokenize_text(cj))
    vocab = Vocab.build(all_tokens, min_freq=1)
    print(f"[train] vocab size = {len(vocab)}", flush=True)
    vocab.save(vocab_path)

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

    model = Seq2SeqTransformer(
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
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[train] model params = {n_params/1e6:.2f}M", flush=True)

    optim = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        optim, max_lr=lr, total_steps=epochs * max(1, len(train_loader)),
        pct_start=0.1,
    )

    for epoch in range(1, epochs + 1):
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
                    f"[train] epoch {epoch} step {step}/{len(train_loader)} "
                    f"loss {loss.item():.4f} lr {sched.get_last_lr()[0]:.2e}",
                    flush=True,
                )
        # Validation token accuracy.
        model.eval()
        v_correct = 0
        v_total = 0
        with torch.no_grad():
            for src, tgt in val_loader:
                tgt_in = tgt[:, :-1]
                tgt_out = tgt[:, 1:]
                logits = model(src, tgt_in)
                pred = logits.argmax(-1)
                mask = (tgt_out != pad_idx)
                v_correct += int(((pred == tgt_out) & mask).sum().item())
                v_total += int(mask.sum().item())
        v_acc = v_correct / max(1, v_total)
        print(
            f"[train] epoch {epoch} done loss={epoch_loss/max(1,n_batches):.4f} "
            f"val_tok_acc={v_acc:.4f} time={time.time()-t0:.1f}s",
            flush=True,
        )

    # Sequence-level greedy accuracy on the val set.
    model.eval()
    seq_correct = 0
    seq_total = 0
    with torch.no_grad():
        for src, tgt in val_loader:
            preds = model.greedy_decode(src, bos_idx=bos_idx, eos_idx=eos_idx,
                                        max_len=max_len)
            for i in range(preds.size(0)):
                pred_tokens = vocab.decode(preds[i].tolist())
                gold_tokens = vocab.decode(tgt[i].tolist())
                if pred_tokens == gold_tokens:
                    seq_correct += 1
                seq_total += 1
    seq_acc = seq_correct / max(1, seq_total)
    print(f"[train] greedy seq-level val acc = {seq_acc:.4f} "
          f"({seq_correct}/{seq_total})", flush=True)

    state = {
        "model_state": model.state_dict(),
        "config": dict(
            vocab_size=len(vocab),
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=n_layers,
            num_decoder_layers=n_layers,
            dim_feedforward=4 * d_model,
            dropout=0.1,
            pad_idx=pad_idx,
            max_len=max(max_len + 8, 64),
        ),
    }
    torch.save(state, model_path)
    meta = {
        "n_samples": n_samples,
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "vocab_size": len(vocab),
        "params": int(n_params),
        "val_tok_acc": v_acc,
        "val_seq_acc": seq_acc,
        "seed": seed,
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"[train] saved {model_path} ({model_path.stat().st_size/1e6:.2f}MB)",
          flush=True)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--samples", type=int, default=20000)
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=5e-4)
    p.add_argument("--d-model", type=int, default=128)
    p.add_argument("--nhead", type=int, default=4)
    p.add_argument("--layers", type=int, default=3)
    p.add_argument("--seed", type=int, default=0xC0FFEE)
    args = p.parse_args(argv)
    train(
        n_samples=args.samples,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        d_model=args.d_model,
        nhead=args.nhead,
        n_layers=args.layers,
        seed=args.seed,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
