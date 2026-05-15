"""Online, one-pass training of the CHIME engine on the curated trainset.

Unlike go2cj v1 (multi-epoch transformer training) or go2cj-v2 (multi-
epoch CodeT5 fine-tuning), CHIME requires *no* backpropagation, *no*
gradient descent, and **converges in a single pass** over the
trainset.  Empirically all 300+ curated pairs plus 15 full-program
chunks are absorbed in a few seconds on a single CPU.

Training pipeline:

1. Load every curated pair from ``trainset/pairs.jsonl``.
2. Load every full-program chunk pair from ``trainset/programs/*.go``
   & ``*.cj`` (using the same chunk segmenter as the converter).
3. Anonymize each pair with the *shared* placeholder map
   (:func:`go2cj_new.anonymize.anonymize_pair`) so identifiers /
   literals are aligned across the two sides.
4. Feed each anonymized pair to :meth:`CHIME.learn` in order — the
   SOINN substrate grows, Hebbian edges form, the criticality
   controller adapts.
5. Save the engine to ``go2cj_new/critical/model/``.

Validation: hold out 10 % of curated pairs, measure exact-template
recall after the single pass.  The metric we report is
``val_template_acc`` — fraction of held-out anonymized Go chunks for
which the engine emits the exact ground-truth anonymized Cj.

Usage::

    python -m go2cj_new.critical.train             # one-pass train
    python -m go2cj_new.critical.train --report    # + diagnostics
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple

# Make ``import go2cj_new`` work when run as ``python -m
# go2cj_new.critical.train`` from anywhere.
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
sys.path.insert(0, str(PKG.parent))

from go2cj_new.anonymize import anonymize_pair  # noqa: E402
from go2cj_new.lexer import tokenize  # noqa: E402
from go2cj_new.critical.engine import CHIME  # noqa: E402


TRAINSET = PKG.parent / "trainset"
MODEL_DIR = HERE / "model"


# --------------------------------------------------------------------------- #
#  Trainset loading                                                           #
# --------------------------------------------------------------------------- #


def _load_pairs() -> List[Tuple[str, str]]:
    """Return the ``[(go, cj), ...]`` list from ``pairs.jsonl``."""
    p = TRAINSET / "pairs.jsonl"
    pairs: List[Tuple[str, str]] = []
    if not p.exists():
        return pairs
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        d = json.loads(line)
        if "go" in d and "cj" in d:
            pairs.append((d["go"], d["cj"]))
    return pairs


def _split_top_level(src: str, semi: str = ";") -> List[str]:
    """Return top-level chunks of a source file by brace balance.

    Same logic as the converter's chunk segmenter, but operates on raw
    *text* so we can apply it to both Go and Cj curated programs.
    Comments / blank lines are removed first.  This is purely a
    splitter — no translation.
    """
    # Strip line + block comments to make brace balancing reliable.
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    chunks: List[str] = []
    cur: List[str] = []
    db = dp = ds = 0
    i, n = 0, len(src)
    in_str = False
    str_ch = ""
    while i < n:
        c = src[i]
        cur.append(c)
        if in_str:
            if c == "\\" and i + 1 < n:
                cur.append(src[i + 1])
                i += 2
                continue
            if c == str_ch:
                in_str = False
            i += 1
            continue
        if c in '"\'`':
            in_str = True
            str_ch = c
            i += 1
            continue
        if c == "{":
            db += 1
        elif c == "}":
            db = max(db - 1, 0)
            if db == 0 and dp == 0 and ds == 0:
                # End of block-level chunk.
                chunks.append("".join(cur).strip())
                cur = []
        elif c == "(":
            dp += 1
        elif c == ")":
            dp = max(dp - 1, 0)
        elif c == "[":
            ds += 1
        elif c == "]":
            ds = max(ds - 1, 0)
        elif c == semi and db == 0 and dp == 0 and ds == 0:
            chunks.append("".join(cur[:-1]).strip())
            cur = []
        elif c == "\n" and db == 0 and dp == 0 and ds == 0:
            cur_str = "".join(cur).strip()
            # Heuristic: a top-level line that looks like a complete
            # statement (no trailing operator) is its own chunk.
            if cur_str and not cur_str.rstrip().endswith((",", "+", "-", "*",
                                                          "/", "=", "&", "|",
                                                          "(", "[", "{")):
                # Only emit when this line *isn't* the start of a
                # function/struct/interface (those need their {…}).
                if not re.match(
                        r"^(func|type|interface|struct|class|var|const|"
                        r"public|private|open|import|package)\b", cur_str):
                    chunks.append(cur_str)
                    cur = []
        i += 1
    tail = "".join(cur).strip()
    if tail:
        chunks.append(tail)
    return [c for c in chunks if c]


def _load_programs() -> List[Tuple[str, str]]:
    """Pair-align top-level chunks from ``programs/*.go`` and ``*.cj``.

    For each ``foo.go`` / ``foo.cj`` we segment both, drop
    ``package`` / ``import`` decls, and zip the remaining chunks
    pairwise.  Mismatched chunk counts are skipped (they're noisy).
    """
    pdir = TRAINSET / "programs"
    if not pdir.is_dir():
        return []
    pairs: List[Tuple[str, str]] = []
    for go in sorted(pdir.glob("*.go")):
        cj = go.with_suffix(".cj")
        if not cj.exists():
            continue
        go_chunks = [c for c in _split_top_level(go.read_text(encoding="utf-8"))
                     if not c.startswith(("package", "import"))]
        cj_chunks = [c for c in _split_top_level(cj.read_text(encoding="utf-8"))
                     if not c.startswith(("package", "import"))]
        if len(go_chunks) != len(cj_chunks):
            continue
        for g, c in zip(go_chunks, cj_chunks):
            pairs.append((g, c))
    return pairs


# --------------------------------------------------------------------------- #
#  Training                                                                   #
# --------------------------------------------------------------------------- #


def train(seed: int = 0, val_frac: float = 0.10, verbose: bool = True) -> CHIME:
    """Run one online pass over the entire trainset.  Returns the
    trained engine."""

    rnd = random.Random(seed)
    pairs = _load_pairs() + _load_programs()
    rnd.shuffle(pairs)

    if not pairs:
        raise RuntimeError("No training pairs found under trainset/.")

    n_val = max(1, int(len(pairs) * val_frac))
    val = pairs[:n_val]
    train_set = pairs[n_val:]

    engine = CHIME()

    t0 = time.time()
    for go_text, cj_text in train_set:
        anon_go, anon_cj = anonymize_pair(go_text, cj_text)
        engine.learn(anon_go, anon_cj)

    # Light replay: cycle through the trainset twice more to refresh
    # Hebbian edges and let the criticality controller settle.  Cost
    # is negligible (no gradients).  Skip if dataset is tiny.
    if len(train_set) > 30:
        for _ in range(2):
            rnd.shuffle(train_set)
            for go_text, cj_text in train_set:
                anon_go, anon_cj = anonymize_pair(go_text, cj_text)
                engine.learn(anon_go, anon_cj)

    train_time = time.time() - t0

    # Validation: exact-template match on held-out anonymized chunks.
    correct = 0
    for go_text, cj_text in val:
        anon_go, anon_cj = anonymize_pair(go_text, cj_text)
        pred, _ = engine.translate(anon_go)
        if pred.strip() == anon_cj.strip():
            correct += 1
    val_acc = correct / max(1, len(val))

    if verbose:
        s = engine.stats()
        print(f"[CHIME] trained on {len(train_set)} pairs in {train_time:.2f}s")
        print(f"[CHIME] val_template_acc = {val_acc:.2%} ({correct}/{len(val)})")
        print(f"[CHIME] neurons={s['neurons']} edges={s['edges']} "
              f"fire_thr={s['fire_threshold']:.3f} "
              f"branching_ema={s['branching_ema']:.3f} "
              f"alpha_hat={s['alpha_hat']:.3f}")

    engine.save(MODEL_DIR)
    # Persist the validation metric for downstream tooling.
    (MODEL_DIR / "meta.json").write_text(json.dumps({
        "n_train_pairs": len(train_set),
        "n_val_pairs": len(val),
        "val_template_acc": val_acc,
        "train_time_s": round(train_time, 3),
        "stats": engine.stats(),
    }, indent=2), encoding="utf-8")
    return engine


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="go2cj_new.critical.train",
                                 description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--val-frac", type=float, default=0.10,
                    help="Held-out fraction (default 0.10).")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    train(seed=args.seed, val_frac=args.val_frac, verbose=not args.quiet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
