"""Hyperdimensional Computing (HDC) encoder.

Background
----------
Hyperdimensional Computing — also called Vector Symbolic Architectures
(VSA) — represents symbols and structures as random high-dimensional
vectors. The classical references:

* Kanerva 1988 — *Sparse Distributed Memory* (MIT Press).
* Plate 1995 — *Holographic Reduced Representations*.
* Kanerva 2009 — *Hyperdimensional Computing: An Introduction to
  Computing in Distributed Representation with High-Dimensional Random
  Vectors*. Cognitive Computation 1(2).

For binary (±1) hypervectors of dimension :math:`D \\gtrsim 10^3`, two
random vectors are nearly orthogonal w.p. ~1, and the following algebra
holds approximately under cosine / Hamming similarity:

* **Bundling** ``a + b`` (element-wise majority): superposition that
  *preserves* similarity to both operands. Good for sets / multisets.
* **Binding** ``a * b`` (element-wise XOR for binary): produces a vector
  *dissimilar* to either operand. Invertible: ``(a * b) * b == a``.
* **Permutation** :math:`\\rho(a)` (cyclic shift): another invertible
  dissimilar transform; used for *ordering* — ``\\rho(a) * b`` is the
  HD analogue of "a then b".

These three operations let us encode arbitrary syntactic structures
(token sequences, n-grams, role-filler bindings) into a single fixed-
size vector that supports cheap nearest-neighbour retrieval in
constant time regardless of structure depth. This is dramatically
more parameter-efficient than learned embeddings: the dimensionality
is fixed once (here, 2048 bits) and *all* compositions land in the
same space.

Why not learned embeddings?
---------------------------
Transformer / CodeT5 embeddings (go2cj v1/v2) need gradient descent
and a held-out validation loop to converge. HDC vectors are
**fixed once at vocabulary registration** and never change — there
are no parameters to train, no over-fitting, no catastrophic
forgetting. New tokens get fresh random hypervectors on first sight.
"""

from __future__ import annotations

import hashlib
from typing import Iterable, List

import numpy as np


# Dimension of every hypervector. 2048 bits is well above the
# orthogonality threshold (~32 bits) yet tiny enough that 1024
# neurons cost 1024*2048/8 = 256 KiB.
DIM = 2048
NGRAM = 3   # token n-gram window for sequence encoding


def _seed_from_token(token: str) -> int:
    """Deterministic 64-bit seed from a token string.

    Deterministic seeding means the same token always gets the same
    hypervector — no need to checkpoint the vocabulary.  This is the
    "random indexing" trick used in HDC literature.
    """
    h = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(h, "little", signed=False)


def hv_for_token(token: str, dim: int = DIM) -> np.ndarray:
    """Materialise the bipolar (±1) hypervector for ``token``.

    Implemented as a deterministic Rademacher draw seeded by the
    token's hash.  No vocabulary table is required.
    """
    rng = np.random.default_rng(_seed_from_token(token))
    # Use packed uint8 for bandwidth; convert to int8 ±1 lazily.
    return np.where(rng.random(dim) < 0.5, np.int8(-1), np.int8(1))


def bundle(vectors: Iterable[np.ndarray]) -> np.ndarray:
    """Element-wise majority (with random tie-break) — bipolar bundling.

    The bundle of a set of HVs is similar to each member and acts as
    the HD-equivalent of *unordered set*.  Empty input → zero vector.
    """
    vs = list(vectors)
    if not vs:
        return np.zeros(DIM, dtype=np.int8)
    # Sum in int32 to avoid overflow.
    s = np.zeros(DIM, dtype=np.int32)
    for v in vs:
        s += v.astype(np.int32)
    # Sign function with deterministic tie-break to +1 (negligible bias
    # for non-trivial inputs).
    out = np.where(s >= 0, np.int8(1), np.int8(-1))
    return out


def bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Element-wise XOR-equivalent for bipolar vectors: ``a * b``."""
    return (a.astype(np.int8) * b.astype(np.int8)).astype(np.int8)


def permute(v: np.ndarray, k: int = 1) -> np.ndarray:
    """Cyclic shift by ``k`` — the HD "ordering" operator."""
    return np.roll(v, k)


def encode_sequence(tokens: List[str], ngram: int = NGRAM) -> np.ndarray:
    """Encode a token sequence as the bundle of all positional n-grams.

    Each n-gram :math:`(t_i, t_{i+1}, \\dots, t_{i+n-1})` is encoded as

        :math:`\\rho^{n-1}(\\text{hv}(t_i)) \\cdot
                \\rho^{n-2}(\\text{hv}(t_{i+1})) \\cdots
                \\text{hv}(t_{i+n-1}))`

    (binding is commutative for bipolar HVs, the permutations encode the
    position) and then all n-grams are bundled into the sequence HV.

    This is the standard HDC text-encoding recipe; see e.g. Joshi et al.
    2017 *Language Geometry using Random Indexing* and Najafabadi et al.
    2019 *Hyperdimensional Computing for NLP*.
    """
    if not tokens:
        return np.zeros(DIM, dtype=np.int8)
    n = min(ngram, len(tokens))
    grams: List[np.ndarray] = []
    for i in range(len(tokens) - n + 1):
        gram = permute(hv_for_token(tokens[i]), n - 1)
        for j in range(1, n):
            gram = bind(gram, permute(hv_for_token(tokens[i + j]), n - 1 - j))
        grams.append(gram)
    # Also bundle the bag-of-tokens (n=1) so short chunks still match.
    grams.extend(hv_for_token(t) for t in tokens)
    return bundle(grams)


def similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine-like similarity in [-1, 1] for bipolar HVs.

    For bipolar vectors this is simply the normalised dot product.
    Two independent random HVs have similarity ≈ 0 (std ≈ 1/√D).
    """
    if a.size == 0 or b.size == 0:
        return 0.0
    return float(np.dot(a.astype(np.int32), b.astype(np.int32))) / DIM
