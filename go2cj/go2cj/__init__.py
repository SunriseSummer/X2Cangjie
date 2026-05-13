"""go2cj — Neural / self-organizing Go → Cangjie source converter.

A single-file source-to-source transpiler from Go to the Cangjie
programming language.  The pipeline uses the same non-linear /
neuro-symbolic architecture as ``ts2cj``:

* a regex-driven Go tokenizer (the only purely classical step);
* deterministic hashing-trick token embeddings (no training data);
* a Kohonen self-organizing map (SOM) trained on a built-in pattern
  corpus of Go ↔ Cangjie chunk templates;
* a Hopfield-style associative memory for symbol / method translation
  (e.g. ``fmt.Println`` → ``println``, ``len`` → ``.size``);
* non-linear template slot binding with composite scoring.

Public API:

* :func:`convert_source` — convert a Go source string to Cangjie.
* :class:`ConversionResult` — dataclass with the output text plus
  chunk-coverage statistics used to gate quality downstream.
"""

from .converter import convert_source, ConversionResult  # noqa: F401

__all__ = ["convert_source", "ConversionResult"]
__version__ = "0.1.0"
