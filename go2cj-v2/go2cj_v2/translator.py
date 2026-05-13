"""Inference-time neural translator for go2cj-v2.

Loads the fine-tuned ``CodeT5-small`` checkpoint (or, if a fine-tuned
checkpoint is not yet present, falls back to the raw base model) and
translates Go chunks to Cangjie chunks via T5 greedy / beam decoding.

The directory layout used throughout the package is::

    go2cj-v2/
    ├── base_model/                # downloaded by scripts/download_base.sh
    │   ├── config.json
    │   ├── pytorch_model.bin
    │   ├── vocab.json
    │   └── ...
    └── go2cj_v2/
        ├── finetuned/             # best-by-val fine-tuned checkpoint
        │   ├── config.json
        │   ├── pytorch_model.bin
        │   └── ...
        └── finetuned_last/        # latest checkpoint (for resuming)

The fine-tuned directory is the **inference target**; if it does not
exist, ``base_model/`` is used so callers can at least smoke-test the
pipeline before training.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import torch

_PKG = Path(__file__).resolve().parent
_REPO_ROOT = _PKG.parent  # go2cj-v2/

BASE_MODEL_DIR = _REPO_ROOT / "base_model"
FINETUNED_DIR = _PKG / "finetuned"
FINETUNED_LAST_DIR = _PKG / "finetuned_last"

# Task prefix is part of T5's input format; we use the same prefix at
# train and inference time so the model conditions on the task.
TASK_PREFIX = "translate Go to Cangjie: "


def resolve_model_dir(prefer_finetuned: bool = True) -> Path:
    if prefer_finetuned and FINETUNED_DIR.is_dir() and \
            (FINETUNED_DIR / "config.json").is_file():
        return FINETUNED_DIR
    if BASE_MODEL_DIR.is_dir() and (BASE_MODEL_DIR / "config.json").is_file():
        return BASE_MODEL_DIR
    raise FileNotFoundError(
        f"Neither {FINETUNED_DIR} nor {BASE_MODEL_DIR} contains a model. "
        "Run scripts/download_base.sh first, then `python -m go2cj_v2.train`."
    )


class NeuralTranslator:
    """Singleton-friendly Go → Cangjie chunk translator backed by a
    fine-tuned CodeT5-small."""

    _instance: Optional["NeuralTranslator"] = None

    def __init__(self, model_dir: Optional[Path] = None,
                 num_beams: int = 4, max_input_len: int = 384,
                 max_new_tokens: int = 384):
        from transformers import RobertaTokenizer, T5ForConditionalGeneration

        self.model_dir = Path(model_dir) if model_dir else resolve_model_dir()
        self.tokenizer = RobertaTokenizer.from_pretrained(str(self.model_dir))
        self.model = T5ForConditionalGeneration.from_pretrained(
            str(self.model_dir),
        )
        self.model.eval()
        self.num_beams = num_beams
        self.max_input_len = max_input_len
        self.max_new_tokens = max_new_tokens

    @classmethod
    def get(cls) -> "NeuralTranslator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @torch.no_grad()
    def translate_batch(self, go_texts: List[str]) -> List[str]:
        if not go_texts:
            return []
        # Empty input → empty output (keeps the chunker happy).
        texts = [TASK_PREFIX + (t or "").strip() for t in go_texts]
        enc = self.tokenizer(
            texts, return_tensors="pt", padding=True, truncation=True,
            max_length=self.max_input_len,
        )
        out = self.model.generate(
            input_ids=enc["input_ids"],
            attention_mask=enc["attention_mask"],
            max_new_tokens=self.max_new_tokens,
            num_beams=self.num_beams,
            do_sample=False,
            length_penalty=1.0,
            early_stopping=self.num_beams > 1,
        )
        return [self.tokenizer.decode(o, skip_special_tokens=True) for o in out]

    def translate(self, go_text: str) -> str:
        return self.translate_batch([go_text])[0]


__all__ = ["NeuralTranslator", "TASK_PREFIX",
           "BASE_MODEL_DIR", "FINETUNED_DIR", "FINETUNED_LAST_DIR",
           "resolve_model_dir"]
