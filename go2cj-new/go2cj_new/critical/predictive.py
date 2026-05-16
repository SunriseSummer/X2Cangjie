"""Predictive Coding hierarchy.

Background
----------
* Rao R. P. N., Ballard D. H., 1999. *Predictive coding in the
  visual cortex: a functional interpretation of some extra-classical
  receptive-field effects.* Nat. Neurosci. 2(1): 79-87.
* Friston K., 2010. *The free-energy principle: a unified brain
  theory?*  Nat. Rev. Neurosci. 11(2): 127-138.
* Millidge B., Tschantz A., Buckley C. L., 2022. *Predictive Coding:
  a Theoretical and Experimental Review.* arXiv:2107.12979.

Predictive coding posits that each cortical layer maintains a
*generative model* of the layer below.  The brain's principal currency
is **prediction error**: only the *unexplained* fraction of the
bottom-up signal propagates upward.  The model parameters are updated
by gradient-free local rules that drive prediction error to zero.

Use in CHIME
------------
We add a thin context layer above the SOINN substrate.  For every
program (a sequence of chunks) we maintain a running *context
hypervector* that is the bundled superposition of the program's
already-seen chunks.  Before consulting the SOINN cleanup memory we
*bind* the incoming chunk HV with the context HV — this gives every
chunk a position-aware, history-aware fingerprint.

After translation we *update* the context with the new chunk HV,
weighted by a freshness factor that decays older chunks (a discrete
analogue of leaky integration).  This is mathematically equivalent
to maintaining a top-down "predicted next" HV and explaining away
the part of the incoming signal already accounted for by context.

The key benefit on this task is **chunk disambiguation**: two
identical Go fragments (``var x = 1``) appearing in different
program contexts (after a struct decl vs. after a print) can map to
slightly different preferred neurons in the SOINN graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import hdc


@dataclass
class PredictiveContext:
    """A leaky-integrated context HV used to bias retrieval."""

    decay: float = 0.85
    # Bipolar HV — starts zero.  Use float for accumulation
    # then sign() for sampling.
    _accum: np.ndarray = field(default_factory=lambda: np.zeros(hdc.DIM, dtype=np.float32))

    def reset(self) -> None:
        self._accum = np.zeros(hdc.DIM, dtype=np.float32)

    @property
    def state(self) -> np.ndarray:
        """Current context as a bipolar HV (sign of the accumulator)."""
        if not np.any(self._accum):
            # Identity element: a vector of +1 leaves bind() a no-op.
            return np.ones(hdc.DIM, dtype=np.int8)
        return np.where(self._accum >= 0, np.int8(1), np.int8(-1))

    def update(self, hv: np.ndarray) -> None:
        """Leaky update: ``s_t = decay * s_{t-1} + (1-decay) * hv``."""
        self._accum = self.decay * self._accum + (1.0 - self.decay) * hv.astype(np.float32)

    def predict(self, hv: np.ndarray) -> np.ndarray:
        """Project ``hv`` into context-conditioned coordinates.

        Returns ``bind(hv, context)`` — a vector that is similar to
        the analogous bind of a *training* chunk only if both *the
        chunk itself and its surrounding history* were similar.
        Falling back to plain ``hv`` when the context is the identity
        keeps cold-start behaviour sensible.
        """
        ctx = self.state
        if not np.any(self._accum):
            return hv
        return hdc.bind(hv, ctx)

    def residual(self, hv: np.ndarray, predicted: np.ndarray) -> np.ndarray:
        """Prediction *error* between an actual chunk HV and a
        top-down prediction.  Computed as :math:`hv \\oplus
        \\text{sign}(predicted)`, i.e. the XOR-residual."""
        ph = np.where(predicted >= 0, np.int8(1), np.int8(-1))
        return hdc.bind(hv, ph)
