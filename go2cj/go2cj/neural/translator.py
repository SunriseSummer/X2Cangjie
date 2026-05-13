"""Runtime neural translator.

Loads the trained Transformer (``model.pt`` + ``vocab.json``) and
translates Go chunks to Cangjie chunks via greedy autoregressive
decoding.

If the checkpoint was trained with anonymization (``state['anonymize']``
True, the default for v0.3+), the translator:

1. tokenises the input Go chunk;
2. anonymises identifiers / numeric / string / rune literals
   (:func:`.anonymize.anonymize_tokens`);
3. runs the model on the anonymised token stream;
4. substitutes the original literals back into the model's output.

This makes identifier preservation **lossless** regardless of model
quality, and lets the model focus on learning the small canonical
mapping (e.g. ``ID0 := NUM0`` → ``var ID0 = NUM0``).
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import torch

from .anonymize import Anonymization, anonymize_tokens, deanonymize_tokens
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
        # Was the checkpoint trained with anonymization?  Default True
        # for forward compatibility — anonymization is a no-op when the
        # input has no user identifiers / literals.
        self.anonymize = bool(state.get("anonymize", True))

    @classmethod
    def get(cls) -> "NeuralTranslator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # --------------------------------------------------------------------- #
    #  Internal: encode / decode one anonymised token stream.
    # --------------------------------------------------------------------- #
    def _decode_one(self, tokens: List[str]) -> List[str]:
        if not tokens:
            return []
        ids = self.vocab.encode(tokens)
        src = torch.tensor([ids], dtype=torch.long)
        out = self.model.greedy_decode(
            src, bos_idx=self.bos_idx, eos_idx=self.eos_idx,
            max_len=self.max_len,
        )
        return self.vocab.decode(out[0].tolist())

    def _decode_batch(self, token_lists: List[List[str]]) -> List[List[str]]:
        if not token_lists:
            return []
        max_s = max((len(t) for t in token_lists), default=0)
        src = torch.full(
            (len(token_lists), max(1, max_s)), self.pad_idx, dtype=torch.long,
        )
        for i, toks in enumerate(token_lists):
            ids = self.vocab.encode(toks)
            src[i, : len(ids)] = torch.tensor(ids, dtype=torch.long)
        out = self.model.greedy_decode(
            src, bos_idx=self.bos_idx, eos_idx=self.eos_idx,
            max_len=self.max_len,
        )
        return [self.vocab.decode(out[i].tolist())
                for i in range(out.size(0))]

    # --------------------------------------------------------------------- #
    #  Public API.
    # --------------------------------------------------------------------- #
    def translate_tokens(self, go_tokens: List[str]) -> List[str]:
        if self.anonymize:
            anon_in, anon = anonymize_tokens(go_tokens)
        else:
            anon_in, anon = go_tokens, Anonymization()
        out = self._decode_one(anon_in)
        if self.anonymize:
            out = deanonymize_tokens(out, anon)
        return out

    def translate_batch(self, go_texts: List[str]) -> List[str]:
        if not go_texts:
            return []
        tok_lists = [tokenize_text(t) for t in go_texts]
        anon_inputs: List[List[str]] = []
        anons: List[Anonymization] = []
        for toks in tok_lists:
            if self.anonymize:
                a_toks, a = anonymize_tokens(toks)
            else:
                a_toks, a = toks, Anonymization()
            anon_inputs.append(a_toks)
            anons.append(a)
        outs = self._decode_batch(anon_inputs)
        if self.anonymize:
            outs = [deanonymize_tokens(o, a) for o, a in zip(outs, anons)]
        return [detokenize(o) for o in outs]

    def translate(self, go_text: str) -> str:
        toks = tokenize_text(go_text)
        out = self.translate_tokens(toks)
        return detokenize(out)
