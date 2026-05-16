"""Self-Organized Criticality (SOC) controller.

Background
----------
* Bak P., Tang C., Wiesenfeld K., 1987. *Self-organized criticality:
  An explanation of the 1/f noise*. Phys. Rev. Lett. 59 (4): 381-384.
* Beggs J. M., Plenz D., 2003. *Neuronal Avalanches in Neocortical
  Circuits*.  J. Neurosci. 23 (35): 11167-11177.
* Levina A., Herrmann J. M., Geisel T., 2007. *Dynamical synapses
  causing self-organized criticality in neural networks*.  Nature
  Physics 3: 857-860.

Cortical networks *in vivo* exhibit neuronal avalanches whose sizes
follow a power-law distribution :math:`P(s) \\propto s^{-3/2}`, the
universal signature of self-organized criticality.  At the critical
point the *branching ratio* :math:`\\sigma = E[\\#\\text{spawn} /
\\#\\text{ancestor}]` equals 1: each firing neuron triggers, on
average, exactly one further firing.  Sub-critical (σ<1) networks
relax to silence too fast; super-critical (σ>1) ones blow up and
saturate.  Critical networks **maximise** information transmission
range, dynamic range, and computational capacity (Shew & Plenz 2013).

Mechanism in CHIME
------------------
Each chunk-translation event causes an avalanche on the SOINN graph:
the BMU "fires", then propagates activation to its Hebbian neighbours
above a global *firing threshold* :math:`\\theta`.  We record the
realised branching ratio per event and adjust :math:`\\theta` with a
slow homeostatic rule (Turrigiano-style synaptic scaling, see
Turrigiano 2008 *The Self-Tuning Neuron*):

    :math:`\\theta_{t+1} = \\theta_t + \\eta\\,(\\sigma_t - 1)`

This drives the system toward :math:`\\sigma \\to 1` without any
external supervision — pure SOC.  We additionally track the
**avalanche-size distribution** so we can verify online that the
network indeed lives at the critical point.

This controller does **not** affect translation correctness directly;
it shapes how widely the activation spreads, which in turn determines
how much *contextual* (neighbouring-template) information is fused
into the final readout.  Empirically critical regimes give the
broadest useful context window.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import List


@dataclass
class CriticalityController:
    """Tracks avalanche statistics and adapts the firing threshold."""

    # Initial firing threshold (HD-similarity units; same scale as
    # SOINN.insert_thresh).  Starts permissive: avalanches will be
    # somewhat super-critical and the controller will pull them
    # back to ρ ≈ 1 over the course of training.
    threshold: float = 0.35
    target_branching: float = 1.0
    # Learning rate of the homeostatic update.  Slow — many events.
    eta: float = 0.01
    # Capped because avalanches on a sparse small graph can otherwise
    # diverge during the first few hundred events.
    min_threshold: float = 0.10
    max_threshold: float = 0.80

    # Statistics (read-only externally).
    sizes: List[int] = field(default_factory=list)
    branching_ema: float = 1.0

    def update(self, avalanche_size: int, branching: float) -> None:
        """Register one avalanche; adjust the firing threshold.

        ``branching`` should be the empirical σ for the just-finished
        avalanche (#spawned-children / #parents).  EMA-smoothed.
        """
        self.sizes.append(int(avalanche_size))
        self.branching_ema = 0.95 * self.branching_ema + 0.05 * branching
        # Turrigiano-style adjustment.
        self.threshold += self.eta * (self.branching_ema - self.target_branching)
        self.threshold = max(self.min_threshold,
                             min(self.max_threshold, self.threshold))

    # ----- introspection -------------------------------------------------- #

    def power_law_exponent(self) -> float:
        """Maximum-likelihood power-law exponent of the avalanche-size
        distribution (Clauset, Shalizi & Newman 2009).

        Returns ``nan`` if there is too little data; otherwise the
        estimated :math:`\\hat\\alpha`.  A critical SOC system should
        yield :math:`\\hat\\alpha \\approx 1.5`.
        """
        ss = [s for s in self.sizes if s >= 1]
        if len(ss) < 30:
            return float("nan")
        s_min = 1
        n = len(ss)
        denom = sum(math.log(s / (s_min - 0.5)) for s in ss)
        if denom <= 0:
            return float("nan")
        return 1.0 + n / denom

    def size_histogram(self, bins: int = 8) -> Counter:
        """Return a log-binned histogram of avalanche sizes (for the
        history report).  Bins are powers of two."""
        hist: Counter = Counter()
        for s in self.sizes:
            if s < 1:
                continue
            b = int(math.log2(s)) if s > 1 else 0
            b = min(b, bins - 1)
            hist[b] += 1
        return hist
