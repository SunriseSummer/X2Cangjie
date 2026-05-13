"""Curated trainset loader.

Loads hand-written Go ↔ Cangjie chunk pairs from
``go2cj/trainset/pairs.jsonl`` plus matched ``programs/*.go`` /
``programs/*.cj`` files.  These pairs are then **augmented** by the
identifier/literal anonymization layer (:mod:`.anonymize`) so each
single curated pair becomes many thousands of variants at training
time — the model sees the canonical translation under arbitrary user
naming.

The loader is intentionally pure-Python with no torch dependency so
it can be tested in isolation.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import List, Optional, Tuple

from .anonymize import anonymize_pair


def trainset_root() -> Path:
    """Return the absolute path to the ``trainset/`` directory.

    Resolved as ``<this-package>/../../trainset`` so the loader works
    from a development checkout *and* from an installed package where
    the layout has been preserved.
    """
    here = Path(__file__).resolve()
    return here.parents[2] / "trainset"


def load_jsonl_pairs(path: Optional[Path] = None) -> List[Tuple[str, str]]:
    """Load chunk-level pairs from ``trainset/pairs.jsonl``."""
    if path is None:
        path = trainset_root() / "pairs.jsonl"
    if not path.is_file():
        return []
    out: List[Tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"{path}:{line_no}: invalid JSON ({e})"
                ) from e
            go = (obj.get("go") or "").strip()
            cj = (obj.get("cj") or "").strip()
            if go and cj:
                out.append((go, cj))
    return out


def _split_program_into_chunks(text: str) -> List[str]:
    """Split a whole-program source into top-level chunks.

    A *very* small splitter — we use it on the curated Go and Cangjie
    programs which are written in a flat, top-level style.  We track
    brace depth and emit a new chunk whenever depth returns to zero.
    Lines starting with ``package`` or ``import`` are dropped.
    """
    chunks: List[str] = []
    cur: List[str] = []
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if cur and depth == 0:
                chunks.append(" ".join(c.strip() for c in cur if c.strip()))
                cur = []
            continue
        if depth == 0 and (
            stripped.startswith("package ") or stripped.startswith("import ")
            or stripped == "package main"
        ):
            continue
        cur.append(stripped)
        for ch in stripped:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(depth - 1, 0)
        if depth == 0 and cur:
            chunks.append(" ".join(c.strip() for c in cur))
            cur = []
    if cur:
        chunks.append(" ".join(c.strip() for c in cur))
    return [c for c in chunks if c]


def load_program_pairs(programs_dir: Optional[Path] = None
                       ) -> List[Tuple[str, str]]:
    """Load matched ``programs/<name>.go`` / ``programs/<name>.cj`` pairs.

    The two files are each split into top-level chunks; pairs are
    formed by **index** so the curated authors are responsible for
    keeping the chunks aligned 1:1.  Mismatched files are skipped
    with a warning rather than raising — training should not break
    if a contributor forgets to update one side.
    """
    if programs_dir is None:
        programs_dir = trainset_root() / "programs"
    if not programs_dir.is_dir():
        return []
    out: List[Tuple[str, str]] = []
    for go_path in sorted(programs_dir.glob("*.go")):
        cj_path = go_path.with_suffix(".cj")
        if not cj_path.is_file():
            continue
        go_chunks = _split_program_into_chunks(go_path.read_text("utf-8"))
        cj_chunks = _split_program_into_chunks(cj_path.read_text("utf-8"))
        if len(go_chunks) != len(cj_chunks):
            # Misaligned — skip (do not poison the training set).
            continue
        for g, c in zip(go_chunks, cj_chunks):
            if g and c:
                out.append((g, c))
    return out


def load_curated_pairs() -> List[Tuple[str, str]]:
    """Concatenate JSONL pairs and program pairs."""
    return load_jsonl_pairs() + load_program_pairs()


def augment_pairs(pairs: List[Tuple[str, str]], factor: int = 50,
                  seed: int = 0xBEEF) -> List[Tuple[str, str]]:
    """Expand ``pairs`` by anonymizing each one ``factor`` times.

    Anonymization assigns deterministic placeholders (``ID0``,
    ``NUM0`` …) per *pair*, but reshuffling the ordering of slot
    occurrences gives the model many surface variants of the same
    semantic mapping.  We additionally permute the identifier
    indexing so the model does not over-learn ``ID0 ≡ first slot``.
    """
    rng = random.Random(seed)
    out: List[Tuple[str, str]] = []
    for go, cj in pairs:
        # Always include the un-anonymized canonical form so the model
        # also learns the raw identifier surface.
        out.append((go, cj))
        # Anonymized canonical form.
        a_go, a_cj = anonymize_pair(go, cj)
        out.append((a_go, a_cj))
        # ``factor`` additional perturbations: random index shuffles by
        # rewriting placeholder digits.
        for _ in range(max(0, factor - 2)):
            perm_go, perm_cj = _shuffle_placeholders(a_go, a_cj, rng)
            out.append((perm_go, perm_cj))
    return out


_PREFIXES = ("ID", "NUM", "STR", "CHR")


def _shuffle_placeholders(go: str, cj: str, rng: random.Random
                          ) -> Tuple[str, str]:
    """Re-number anonymized placeholders so the model sees varied
    indices without changing semantics."""
    go_tokens = go.split(" ")
    cj_tokens = cj.split(" ")
    for prefix in _PREFIXES:
        # Find unique indices on the Go side; assign each to a new
        # random index in [0, 16); apply consistently to both sides.
        seen: List[int] = []
        for tok in go_tokens:
            if tok.startswith(prefix) and tok[len(prefix):].isdigit():
                idx = int(tok[len(prefix):])
                if idx not in seen:
                    seen.append(idx)
        if not seen:
            continue
        new_indices = list(range(16))
        rng.shuffle(new_indices)
        mapping = {old: new_indices[i] for i, old in enumerate(seen)}
        def remap(tokens: List[str]) -> List[str]:
            res = []
            for t in tokens:
                if t.startswith(prefix) and t[len(prefix):].isdigit():
                    idx = int(t[len(prefix):])
                    if idx in mapping:
                        res.append(f"{prefix}{mapping[idx]}")
                        continue
                res.append(t)
            return res
        go_tokens = remap(go_tokens)
        cj_tokens = remap(cj_tokens)
    return " ".join(go_tokens), " ".join(cj_tokens)


def load_curated_corpus(augment_factor: int = 50
                        ) -> List[Tuple[str, str]]:
    """Convenience: load curated pairs and apply augmentation."""
    pairs = load_curated_pairs()
    if augment_factor <= 1:
        return pairs
    return augment_pairs(pairs, factor=augment_factor)


__all__ = [
    "trainset_root",
    "load_jsonl_pairs",
    "load_program_pairs",
    "load_curated_pairs",
    "augment_pairs",
    "load_curated_corpus",
]
