"""Hopfield-style associative memory for symbol mapping.

We use this to translate identifier-level token streams (e.g. property
names, method calls, type names) from Go to Cangjie.  Each
stored "memory" is a (key_vector, value_string) pair.  Recall is a
non-linear competition: the input vector is compared against every
stored key with a softmax, and we either return the winning value or
fall back to identity when no key dominates the field strongly enough.

This is functionally equivalent to a modern Hopfield network with very
high inverse temperature: a single retrieval step, no iteration needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from .embedding import embed_token


@dataclass
class HopfieldMemory:
    temperature: float = 0.25
    confidence_threshold: float = 0.55
    keys: List[np.ndarray] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    # Original surface forms — used for exact-match fast path & dedup.
    surface: List[str] = field(default_factory=list)

    def remember(self, key_token: str, value: str, kind: str = "IDENT") -> None:
        """Store ``key_token`` → ``value``."""

        if key_token in self.surface:
            i = self.surface.index(key_token)
            self.values[i] = value
            return
        self.keys.append(embed_token(key_token, kind))
        self.values.append(value)
        self.surface.append(key_token)

    def recall(self, token: str, kind: str = "IDENT") -> Optional[Tuple[str, float]]:
        """Try to recall the Cangjie equivalent of ``token``.

        Returns ``(value, confidence)`` or ``None`` if no stored pattern
        dominates with sufficient confidence.
        """

        if not self.keys:
            return None
        # Fast path: exact surface match.
        if token in self.surface:
            return self.values[self.surface.index(token)], 1.0
        q = embed_token(token, kind)
        sims = np.array([float(np.dot(q, k)) for k in self.keys], dtype=np.float32)
        # Softmax with low temperature ⇒ strong winner-takes-all.
        m = sims.max()
        exps = np.exp((sims - m) / max(self.temperature, 1e-6))
        probs = exps / exps.sum()
        best = int(probs.argmax())
        if probs[best] >= self.confidence_threshold and sims[best] >= 0.3:
            return self.values[best], float(probs[best])
        return None
