"""CHIME engine — the top-level translator brain.

Stitches together the four subsystems:

* :mod:`.hdc`         — hyperdimensional encoder
* :mod:`.soinn`       — dynamic, growing concept graph
* :mod:`.criticality` — homeostatic threshold controller (SOC)
* :mod:`.predictive`  — top-down context HV

and exposes two operations:

* :meth:`CHIME.learn`     — observe a (Go, Cj) anonymized chunk pair.
* :meth:`CHIME.translate` — emit a Cangjie chunk for a Go chunk.

Both operations are **O(|neurons|)** in time and use no gradient
descent, no autodiff, no labelled epochs.  A typical run trains on
~300 curated pairs in seconds (single CPU pass).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from . import hdc
from .criticality import CriticalityController
from .predictive import PredictiveContext
from .soinn import SOINN


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #

_PLACEHOLDER_RE = re.compile(r"\b(ID|NUM|STR|CHR)(\d+)\b")


def _placeholders_of(template: str) -> List[Tuple[str, int]]:
    """Extract ``[(kind, idx), ...]`` for every placeholder in a template."""
    return [(m.group(1), int(m.group(2)))
            for m in _PLACEHOLDER_RE.finditer(template)]


def _remap_template(template: str, mapping: Dict[Tuple[str, int], Tuple[str, int]]) -> str:
    """Apply a placeholder-index remap (used to align two templates'
    placeholder numbering when they are different)."""

    def sub(m: re.Match) -> str:
        key = (m.group(1), int(m.group(2)))
        if key in mapping:
            kind, idx = mapping[key]
            return f"{kind}{idx}"
        return m.group(0)

    return _PLACEHOLDER_RE.sub(sub, template)


# --------------------------------------------------------------------------- #
#  Engine                                                                     #
# --------------------------------------------------------------------------- #


@dataclass
class CHIME:
    """Critical Homeostatic Incremental Memory Engine.

    Stateful: keeps SOINN, predictive context and criticality
    controller as instance fields.
    """

    soinn: SOINN = field(default_factory=SOINN)
    context: PredictiveContext = field(default_factory=PredictiveContext)
    criticality: CriticalityController = field(default_factory=CriticalityController)

    # --------------------------------------------------------------- learn #

    def learn(self, anon_go: str, anon_cj: str) -> None:
        """Register one anonymized (Go, Cj) chunk pair.

        Mutates the SOINN substrate.  A new neuron is grown if the
        Go side is novel; an existing neuron's prototype is shifted
        otherwise.  The Hebbian edge between the BMU and runner-up
        is refreshed.
        """
        if not anon_go.strip() or not anon_cj.strip():
            return
        toks_in = anon_go.split()
        hv_in = hdc.encode_sequence(toks_in)
        # The context HV is intentionally *not* applied at learn time
        # so different training programs share the same memory space.
        bmu, sim = self.soinn.observe(hv_in, anon_go, anon_cj)

        # Record a synthetic avalanche on the just-touched neuron and
        # its immediate Hebbian neighbours: that's the "spread" the
        # criticality controller is steering.
        spread = self._spread_size(bmu)
        branching = spread / 1.0
        self.criticality.update(avalanche_size=spread, branching=branching)

    def _spread_size(self, idx: int) -> int:
        """Single-step BFS from ``idx`` over Hebbian edges, counting
        nodes whose similarity-to-firing-source >= firing threshold.

        Used for SOC bookkeeping.  Caps at 32 to keep tracking cheap
        even on dense graphs."""
        if idx < 0 or idx >= len(self.soinn.neurons):
            return 0
        src = self.soinn.neurons[idx].hv_in
        thr = self.criticality.threshold
        count = 1
        for nb in self.soinn.neighbours(idx)[:32]:
            if hdc.similarity(self.soinn.neurons[nb].hv_in, src) >= thr:
                count += 1
        return count

    # ------------------------------------------------------------ translate #

    def translate(self, anon_go: str, topk: int = 8) -> Tuple[str, float]:
        """Translate one anonymized Go chunk to anonymized Cangjie.

        Returns ``(template, confidence)``.  Empty template + 0.0
        confidence means *no memory available* (the caller should
        treat the chunk as fallback).

        We retrieve the top-k candidates, then filter for those whose
        placeholder set is a **strict subset** of the input's
        placeholder set.  This guarantees the deanonymized output
        contains no dangling placeholders — emitting ``ID3`` in a
        chunk that only defined ``ID0`` is a guaranteed compile
        failure.
        """
        toks_in = anon_go.split()
        if not toks_in:
            return "", 0.0
        hv_in = hdc.encode_sequence(toks_in)
        # Context-modulated retrieval.  We try *both* the raw HV and the
        # context-bound HV and pick the more confident hit; this
        # gracefully degrades to plain HDC lookup when context is the
        # identity (cold start) and lets the predictive layer help on
        # disambiguation.
        candidates: List[Tuple[int, float]] = []
        candidates += self.soinn.best(hv_in, k=topk)
        ctx_hv = self.context.predict(hv_in)
        if ctx_hv is not hv_in:
            candidates += [(i, s * 0.95) for (i, s)
                           in self.soinn.best(ctx_hv, k=topk)]
        if not candidates:
            return "", 0.0

        # Strict placeholder-set check: every placeholder appearing in
        # the candidate template must appear in the input chunk.  Without
        # this, deanonymisation would leak dangling ``ID3`` / ``STR2``
        # tokens into the output and guarantee a compile failure.
        in_set = set(_placeholders_of(anon_go))
        candidates.sort(key=lambda x: x[1], reverse=True)
        seen: set = set()
        best_template = ""
        best_conf = 0.0
        for idx, sim in candidates:
            if idx in seen:
                continue
            seen.add(idx)
            n = self.soinn.neurons[idx]
            if not n.template_out:
                continue
            cand_set = set(_placeholders_of(n.template_out))
            if not cand_set.issubset(in_set):
                continue
            if sim > best_conf:
                best_template = n.template_out
                best_conf = sim

        # Update predictive context with the *input* HV (sequence-level
        # leaky integration) — done even when retrieval fails so the
        # context window stays consistent.
        self.context.update(hv_in)
        return best_template, best_conf

    # ----------------------------------------------------------- persistence #

    def save(self, path: Path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.soinn.save(path / "soinn")
        (path / "criticality.json").write_text(json.dumps({
            "threshold": self.criticality.threshold,
            "branching_ema": self.criticality.branching_ema,
            "sizes": self.criticality.sizes[-2000:],
        }), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "CHIME":
        path = Path(path)
        eng = cls(soinn=SOINN.load(path / "soinn"))
        cj = path / "criticality.json"
        if cj.exists():
            meta = json.loads(cj.read_text(encoding="utf-8"))
            eng.criticality.threshold = float(meta.get("threshold", 0.35))
            eng.criticality.branching_ema = float(meta.get("branching_ema", 1.0))
            eng.criticality.sizes = list(meta.get("sizes", []))
        return eng

    # ----------------------------------------------------------- diagnostics #

    def stats(self) -> Dict[str, float]:
        return {
            "neurons": len(self.soinn),
            "edges": len(self.soinn.edges),
            "fire_threshold": self.criticality.threshold,
            "branching_ema": self.criticality.branching_ema,
            "alpha_hat": self.criticality.power_law_exponent(),
        }
