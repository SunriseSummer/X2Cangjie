"""Kohonen Self-Organizing Map (SOM).

A small SOM is trained on the embedded patterns from
:mod:`go2cj.patterns`.  After training, each neuron in the 2-D grid
becomes a *prototype* for a translation pattern.  At conversion time we
look up the best-matching unit (BMU) for an input chunk and use the
patterns associated with that neuron as candidates.

This gives us the "non-linear" pattern retrieval the user asked for:
similar Go snippets get routed to the same SOM region and thus to the
same Cangjie template family, even when their surface tokens differ
significantly from any single stored pattern.

The implementation is intentionally compact (pure NumPy, ~50 lines of
substantive code) and trains in well under a second on the built-in
corpus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np


@dataclass
class SOM:
    grid_w: int = 6
    grid_h: int = 6
    dim: int = 64
    rng_seed: int = 1337
    iterations: int = 800
    learn_rate0: float = 0.5
    radius0: float = 3.0
    weights: np.ndarray = field(default=None, repr=False)  # type: ignore[assignment]
    # Mapping from BMU coordinates to indices in the original training set.
    bmu_index: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.rng_seed)
        # Initialise on the unit sphere so that cosine distance is meaningful.
        w = rng.standard_normal((self.grid_h, self.grid_w, self.dim)).astype(np.float32)
        norms = np.linalg.norm(w, axis=2, keepdims=True)
        norms[norms == 0] = 1.0
        self.weights = w / norms

    # ---------- training -----------------------------------------------------
    def train(self, samples: np.ndarray) -> None:
        """Train the SOM on row-vectors ``samples`` (already L2-normalised)."""

        rng = np.random.default_rng(self.rng_seed + 1)
        n = samples.shape[0]
        if n == 0:
            return
        for it in range(self.iterations):
            t = it / max(self.iterations - 1, 1)
            lr = self.learn_rate0 * (1.0 - t)
            radius = max(self.radius0 * (1.0 - t), 0.5)
            x = samples[rng.integers(0, n)]
            bmu_y, bmu_x = self._bmu(x)
            # Vectorised neighbourhood update.
            ys, xs = np.indices((self.grid_h, self.grid_w))
            d2 = (ys - bmu_y) ** 2 + (xs - bmu_x) ** 2
            theta = np.exp(-d2 / (2.0 * radius * radius)).astype(np.float32)
            delta = lr * theta[..., None] * (x[None, None, :] - self.weights)
            self.weights += delta
            # Re-normalise so cosine similarity stays well-behaved.
            norms = np.linalg.norm(self.weights, axis=2, keepdims=True)
            norms[norms == 0] = 1.0
            self.weights /= norms

        # Record which training sample maps to which BMU.
        self.bmu_index = {}
        for i in range(n):
            y, x = self._bmu(samples[i])
            self.bmu_index.setdefault((int(y), int(x)), []).append(i)

    def _bmu(self, x: np.ndarray) -> Tuple[int, int]:
        sims = np.tensordot(self.weights, x, axes=([2], [0]))  # (H, W)
        idx = int(np.argmax(sims))
        return divmod(idx, self.grid_w)

    # ---------- inference ----------------------------------------------------
    def query(self, x: np.ndarray, k: int = 3) -> List[Tuple[int, float]]:
        """Return up to *k* candidate training-sample indices for ``x``.

        Candidates are gathered from the BMU and its immediate neighbours;
        we then rank by similarity to ``x`` itself.  This is the
        self-organizing recall step: similar inputs hit overlapping
        neighbourhoods and thus surface the same pattern family.
        """

        bmu_y, bmu_x = self._bmu(x)
        candidates: List[int] = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                y2, x2 = bmu_y + dy, bmu_x + dx
                if 0 <= y2 < self.grid_h and 0 <= x2 < self.grid_w:
                    candidates.extend(self.bmu_index.get((y2, x2), []))
        # Deduplicate, preserve order.
        seen = set()
        unique = [c for c in candidates if not (c in seen or seen.add(c))]
        return [(i, 0.0) for i in unique[:k]]  # similarity computed by caller
