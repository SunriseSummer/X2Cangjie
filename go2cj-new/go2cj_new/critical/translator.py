"""Inference singleton over a trained :class:`CHIME` engine.

Behaviour mirrors :class:`go2cj.neural.translator.NeuralTranslator` so
the converter can be swapped in without touching the rest of the
pipeline.

The translator anonymizes the incoming Go chunk, queries the CHIME
engine for the anonymized Cangjie template, then de-anonymizes using
the same placeholder map.  When the engine has no memory yet (no
``model/`` directory) the translator returns the input verbatim with
zero confidence — the converter then falls back to the lifted
identity output, which still compiles in many trivial cases.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from ..anonymize import (
    anonymize_text,
    deanonymize_tokens,
)
from ..tokenize import detokenize, tokenize_text
from .engine import CHIME


HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE / "model"


class NeuralTranslator:
    """Process-wide singleton; lazy-loads the trained CHIME engine."""

    _instance: "NeuralTranslator" | None = None

    def __init__(self) -> None:
        if MODEL_DIR.exists():
            self._engine = CHIME.load(MODEL_DIR)
        else:
            self._engine = CHIME()

    @classmethod
    def get(cls) -> "NeuralTranslator":
        if cls._instance is None:
            cls._instance = NeuralTranslator()
        return cls._instance

    # --------------------------------------------------------------- public #

    @property
    def engine(self) -> CHIME:
        return self._engine

    def translate(self, go_text: str) -> Tuple[str, float]:
        """Return ``(cj_text, confidence)``.

        Confidence is the SOINN BMU similarity in [-1, 1]; the
        converter promotes a chunk to *confident* when confidence > 0.
        """
        if not go_text.strip():
            return "", 0.0
        anon_go, anon = anonymize_text(go_text)
        template, conf = self._engine.translate(anon_go)
        if not template:
            return "", 0.0
        # De-anonymize the template back into user identifiers /
        # literals.  We tokenize the template first so placeholder
        # substitution is exact.
        out_tokens = deanonymize_tokens(tokenize_text(template), anon)
        return detokenize(out_tokens), conf

    def translate_batch(self, go_texts: List[str]) -> List[str]:
        return [self.translate(g)[0] for g in go_texts]
