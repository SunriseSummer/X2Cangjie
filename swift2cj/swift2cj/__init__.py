"""swift2cj — Neural / self-organizing Swift → Cangjie source converter.

Hybrid neuro-symbolic transpiler implemented in pure Python.  No GPU and no
training data are required: a Kohonen self-organizing map (SOM) is trained
at import time on a built-in pattern corpus, and a Hopfield-style associative
memory provides token-level symbol translation.

The public API is :func:`swift2cj.convert_source`.
"""

from .converter import convert_source, ConversionResult  # noqa: F401

__all__ = ["convert_source", "ConversionResult"]
__version__ = "0.1.0"
