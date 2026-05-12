"""Hashing-trick token embeddings.

The converter never needs a corpus of millions of programs to train word
embeddings: we synthesise them deterministically from token surface form
using a feature-hashing scheme.  Each token is converted into a fixed-size
vector by hashing its character n-grams into vector slots with random
signs.  The resulting vector space behaves very similarly to a learned
embedding: tokens with overlapping n-grams (e.g. ``console`` and
``consol``) end up close together, while unrelated tokens are
quasi-orthogonal.

The vectors are L2-normalised so that downstream cosine similarity reduces
to a plain dot product.
"""

from __future__ import annotations

import hashlib
import math
from typing import Iterable, List

import numpy as np

EMBED_DIM = 64  # plenty for our small SOM


def _stable_hash(s: str) -> int:
    """A reproducible 64-bit hash (Python's built-in ``hash`` is salted)."""

    return int.from_bytes(hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest(), "big")


def embed_token(value: str, kind: str = "") -> np.ndarray:
    """Return the embedding vector of a single token.

    ``kind`` (e.g. ``"KEYWORD"``, ``"STRING"``) is concatenated into the
    hash key so that a string literal ``"if"`` does not collide with the
    keyword ``if``.
    """

    vec = np.zeros(EMBED_DIM, dtype=np.float32)
    payload = f"{kind}:{value}"
    # Whole-token feature (strongest signal).
    h = _stable_hash(payload)
    vec[h % EMBED_DIM] += 1.0 if (h >> 32) & 1 else -1.0
    # Character n-gram features (n = 2, 3).
    padded = f"^{value}$"
    for n in (2, 3):
        if len(padded) < n:
            continue
        for i in range(len(padded) - n + 1):
            g = padded[i:i + n]
            h = _stable_hash(f"{kind}#{n}:{g}")
            vec[h % EMBED_DIM] += 0.5 if (h >> 32) & 1 else -0.5
    norm = float(np.linalg.norm(vec))
    if norm > 0:
        vec /= norm
    return vec


def embed_sequence(tokens: Iterable) -> np.ndarray:
    """Bag-of-tokens embedding of a sequence (mean + L2 normalised).

    Accepts an iterable of :class:`swift2cj.lexer.Token` objects or simple
    ``(kind, value)`` pairs.
    """

    acc = np.zeros(EMBED_DIM, dtype=np.float32)
    n = 0
    for t in tokens:
        if hasattr(t, "value"):
            kind, value = t.kind, t.value
        else:
            kind, value = t
        acc += embed_token(value, kind)
        n += 1
    if n == 0:
        return acc
    acc /= n
    norm = float(np.linalg.norm(acc))
    if norm > 0:
        acc /= norm
    return acc


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two already-L2-normalised vectors.

    For non-normalised inputs we fall back to the safe formulation.
    """

    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def softmax(xs: List[float], temperature: float = 0.5) -> List[float]:
    """Numerically stable softmax used for non-linear pattern voting."""

    if not xs:
        return []
    m = max(xs)
    exps = [math.exp((x - m) / max(temperature, 1e-6)) for x in xs]
    s = sum(exps)
    return [e / s for e in exps]
