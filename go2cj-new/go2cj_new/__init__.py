"""go2cj-new — brain-inspired, gradient-free Go → Cangjie translator.

This package is the experimental third-generation translator in the
X2Cangjie family.  Unlike :mod:`go2cj` (small Transformer trained
from scratch) and :mod:`go2cj_v2` (CodeT5-small fine-tune), this
package's translation core is a **CHIME** engine — see
:mod:`go2cj_new.critical` — built from:

* Hyperdimensional Computing (HDC / VSA — Kanerva 2009)
* Self-Organizing Incremental Neural Network (SOINN — Furao & Hasegawa 2006)
* Self-Organized Criticality (Bak 1987; Beggs & Plenz 2003)
* Predictive Coding (Rao & Ballard 1999; Friston 2010)
* Local Hebbian / STDP learning (Hebb 1949; Hinton 2022 Forward-Forward)

There is **no backpropagation**, **no gradient descent**, **no fixed
parameter count**, and **no multi-epoch training loop**.  The model
substrate (the SOINN graph) grows and rewires as data is observed —
a single online pass over the curated trainset is sufficient.

Public API:

* :func:`convert_source` — convert a Go source string to Cangjie source.
* :class:`ConversionResult` — output text plus per-chunk statistics.
"""

from .converter import convert_source, ConversionResult  # noqa: F401

__all__ = ["convert_source", "ConversionResult"]
__version__ = "0.3.0"
"""0.3.0 — CHIME (Critical Homeostatic Incremental Memory Engine):
HDC + SOINN + SOC + Predictive Coding; no backprop, dynamic topology."""
