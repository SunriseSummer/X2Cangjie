"""ts2cj — Neural / self-organizing TypeScript → Cangjie source converter.

This package implements a hybrid neuro-symbolic transpiler that does **not**
rely on a classical compiler frontend nor on GPU-trained neural models.
It uses:

* a fast regex tokenizer (the only purely-classical step);
* deterministic hashing-trick token embeddings (no training data needed);
* a Kohonen self-organizing map (SOM) trained on a built-in pattern corpus;
* a Hopfield-style associative memory for symbol/method translation;
* template slot binding via non-linear similarity matching.

The full pipeline is exposed through :func:`ts2cj.converter.convert_source`.
"""

from .converter import convert_source, ConversionResult  # noqa: F401

__all__ = ["convert_source", "ConversionResult"]
__version__ = "0.1.0"
