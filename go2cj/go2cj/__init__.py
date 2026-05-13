"""go2cj — Neural-network Go → Cangjie source converter.

A single-file source-to-source transpiler from Go to the Cangjie
programming language driven by a **trained Transformer encoder-decoder**
(PyTorch, CPU-only).  See :mod:`.neural` for the model, the synthetic
training-corpus generator, and the training script.

Public API:

* :func:`convert_source` — convert a Go source string to Cangjie source.
* :class:`ConversionResult` — output text plus per-chunk statistics.
"""

# Re-exported lazily so that ``import go2cj`` does not import torch on
# users that only want to inspect package metadata.  The translator is
# loaded the first time :func:`convert_source` is called.
from .converter import convert_source, ConversionResult  # noqa: F401

__all__ = ["convert_source", "ConversionResult"]
__version__ = "0.2.0"
"""0.2.0 — switched per-chunk translation from rule-based slot binding
to a trained Transformer seq2seq."""
