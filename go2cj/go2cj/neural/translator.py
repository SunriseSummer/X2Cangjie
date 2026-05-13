"""Runtime neural translator.

Loads the trained Transformer checkpoint (``model.pt``) and vocab
(``vocab.json``) and translates Go chunks to Cangjie chunks via greedy
autoregressive decoding.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import torch

from .model import Seq2SeqTransformer
from .vocab import Vocab, detokenize, tokenize_text


PKG_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PKG_DIR / "model.pt"
DEFAULT_VOCAB_PATH = PKG_DIR / "vocab.json"


class NeuralTranslator:
    """Singleton-friendly Go → Cangjie chunk translator backed by a
    trained Transformer."""

    _instance: Optional["NeuralTranslator"] = None

    def __init__(
        self,
        model_path: Path = DEFAULT_MODEL_PATH,
        vocab_path: Path = DEFAULT_VOCAB_PATH,
    ):
        if not model_path.exists() or not vocab_path.exists():
            raise FileNotFoundError(
                f"Trained model not found at {model_path}. "
                "Run `python -m go2cj.neural.train` first."
            )
        self.vocab = Vocab.load(vocab_path)
        state = torch.load(model_path, map_location="cpu", weights_only=False)
        cfg = state["config"]
        self.model = Seq2SeqTransformer(**cfg)
        self.model.load_state_dict(state["model_state"])
        self.model.eval()
        self.pad_idx = cfg["pad_idx"]
        self.bos_idx = self.vocab.stoi["<bos>"]
        self.eos_idx = self.vocab.stoi["<eos>"]
        self.max_len = cfg.get("max_len", 256)

    @classmethod
    def get(cls) -> "NeuralTranslator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def translate_tokens(self, go_tokens: List[str]) -> List[str]:
        if not go_tokens:
            return []
        ids = self.vocab.encode(go_tokens)
        src = torch.tensor([ids], dtype=torch.long)
        out = self.model.greedy_decode(
            src,
            bos_idx=self.bos_idx,
            eos_idx=self.eos_idx,
            max_len=self.max_len,
        )
        return self.vocab.decode(out[0].tolist())

    def translate_batch(self, go_texts: List[str]) -> List[str]:
        if not go_texts:
            return []
        tok_lists = [tokenize_text(t) for t in go_texts]
        max_s = max(len(t) for t in tok_lists) if tok_lists else 0
        src = torch.full(
            (len(tok_lists), max(1, max_s)), self.pad_idx, dtype=torch.long
        )
        for i, toks in enumerate(tok_lists):
            ids = self.vocab.encode(toks)
            src[i, : len(ids)] = torch.tensor(ids, dtype=torch.long)
        out = self.model.greedy_decode(
            src,
            bos_idx=self.bos_idx,
            eos_idx=self.eos_idx,
            max_len=self.max_len,
        )
        return [
            detokenize(self.vocab.decode(out[i].tolist()))
            for i in range(out.size(0))
        ]

    def translate(self, go_text: str) -> str:
        toks = tokenize_text(go_text)
        out = self.translate_tokens(toks)
        return detokenize(out)
