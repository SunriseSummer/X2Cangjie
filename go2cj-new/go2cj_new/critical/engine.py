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


def _ordered_placeholders(template: str) -> List[Tuple[str, int]]:
    """Distinct placeholders in *first-appearance* order.

    Used by :func:`_align_placeholders` to align two templates'
    placeholder slots positionally even when their kinds differ
    (e.g. a candidate has ``ID1`` where the query has ``NUM0`` — both
    refer to the same structural position in the chunk).
    """
    seen: set = set()
    out: List[Tuple[str, int]] = []
    for kind, idx in _placeholders_of(template):
        key = (kind, idx)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _align_placeholders(
    cand_in: str,
    query_in: str,
) -> Optional[Dict[Tuple[str, int], Tuple[str, int]]]:
    """Return a positional substitution that rewrites placeholders in
    a candidate template to use the query's placeholder names, or
    ``None`` when the two structurally differ.

    Both templates contribute a list of distinct placeholders in
    first-appearance order; the substitution maps the *k*-th candidate
    placeholder to the *k*-th query placeholder.  The substitution is
    valid only when the *anonymised* chunks become identical after
    rewriting (otherwise the candidate is not a structural match).

    This is the bridge that lets a chunk ``for ID0 := 0 ; ID0 < ID1 ;
    ID0 ++ {`` retrieve as an exact structural match for a query
    ``for ID0 := 0 ; ID0 < NUM0 ; ID0 ++ {`` — they differ only in
    placeholder kinds (``ID1`` vs ``NUM0``) but encode the same
    program structure.
    """
    cand_ph = _ordered_placeholders(cand_in)
    query_ph = _ordered_placeholders(query_in)
    if len(cand_ph) != len(query_ph):
        return None
    mapping: Dict[Tuple[str, int], Tuple[str, int]] = dict(zip(cand_ph, query_ph))
    if _remap_template(cand_in, mapping) != query_in:
        return None
    return mapping


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

    # Minimum HD-similarity for a retrieved template to be trusted.  Below
    # this threshold the engine declines the match and returns "" so the
    # caller (converter) routes the chunk to the structural fallback /
    # recursive sub-statement path.  This implements the
    # "SOC-as-output-gate" idea from comment.md §15: the threshold floor
    # is co-driven by the criticality controller's homeostatic theta —
    # the more the network deviates from σ ≈ 1, the more conservative
    # we are about emitting a stored template.
    MIN_CONFIDENCE: float = 0.45

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
        failure.  Candidates whose similarity is below
        :attr:`MIN_CONFIDENCE` are also rejected to avoid hallucinated
        templates on OOD chunks (exact-template hits short-circuit
        this gate since they're unambiguous).
        """
        toks_in = anon_go.split()
        if not toks_in:
            return "", 0.0
        # Exact-template short-circuit.  When the query's anonymised
        # form is byte-identical to a stored neuron's ``template_in``,
        # that is an unambiguous, deterministic hit and we should
        # short-cut HD-similarity retrieval entirely.  This is
        # particularly valuable on a small trainset where HD lookup
        # can otherwise rank a *near*-match higher than the
        # *exact*-match it should always prefer.
        exact_idx = self.soinn._by_template_in.get(anon_go)
        if exact_idx is not None:
            n = self.soinn.neurons[exact_idx]
            if n.template_out:
                # Still enforce the placeholder-subset rule so
                # symmetric cases (a stored chunk with extra
                # placeholders not in the query) can't leak.
                in_set = set(_placeholders_of(anon_go))
                cand_set = set(_placeholders_of(n.template_out))
                if cand_set.issubset(in_set):
                    # Refresh context with the input HV before
                    # returning — keep the leaky integrator consistent.
                    hv_in = hdc.encode_sequence(toks_in)
                    self.context.update(hv_in)
                    return n.template_out, 1.0
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
        # SOC-gated minimum: refuse a stored template when its HD
        # similarity falls below the floor.  This is the difference
        # between "I know this code" and "I'm guessing".  The gate
        # uses ``max(MIN_CONFIDENCE, criticality.threshold * 0.5)`` so
        # the homeostatic theta gradually pulls the floor up when the
        # network drifts super-critical.
        gate = max(self.MIN_CONFIDENCE,
                   0.5 * float(self.criticality.threshold))
        q_len = len(toks_in)
        # Shape constraint: a chunk ending in ``{`` (block header,
        # produced by recursive RBU) must only match a template *also*
        # ending in ``{``.  Without this guard, ``for i := 0; i < n;
        # i++ {`` retrieves the whole one-statement for-template
        # ``for i := 0; i < n; i++ { count += i }``, duplicating the
        # body the splicer is *also* about to emit from the per-
        # statement body chunk.  Same for chunks ending in ``}`` —
        # they should map to templates ending in ``}``.  Composite
        # literal queries ending in ``}`` (e.g. ``[]int{1,2,3}``) are
        # rare at this granularity and naturally satisfy the
        # constraint.
        q_last = toks_in[-1] if toks_in else ""
        q_is_header = q_last == "{" and "}" not in toks_in
        for idx, sim in candidates:
            if idx in seen:
                continue
            seen.add(idx)
            n = self.soinn.neurons[idx]
            if not n.template_out:
                continue
            # Positional placeholder alignment — see
            # :func:`_align_placeholders`.  Lets a candidate with
            # ``ID1`` retrieve for a query with ``NUM0`` if the rest
            # of the structure matches.  When alignment succeeds we
            # use the *aligned* template_out for the rest of the
            # match; when it fails we fall back to strict subset.
            align = _align_placeholders(n.template_in, anon_go)
            if align is not None:
                cand_out = _remap_template(n.template_out, align)
            else:
                cand_out = n.template_out
                cand_set = set(_placeholders_of(cand_out))
                if not cand_set.issubset(in_set):
                    continue
            if sim < gate:
                continue
            cand_tokens = n.template_in.split()
            cand_last = cand_tokens[-1] if cand_tokens else ""
            cand_is_header = cand_last == "{" and "}" not in cand_tokens
            if q_is_header != cand_is_header:
                continue
            cand_len = max(1, len(cand_tokens))
            if cand_len > 2 * q_len + 4 or cand_len * 2 + 4 < q_len:
                continue
            if sim > best_conf:
                best_template = cand_out
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
