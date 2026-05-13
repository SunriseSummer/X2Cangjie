"""PyTorch Transformer encoder-decoder for Go → Cangjie chunk translation.

A small model: ``d_model=128``, 4 heads, 3 encoder + 3 decoder layers,
ffn=512.  Total parameter count is well under 2 M, which trains in a
few minutes on a single CPU on the synthetic corpus from
:mod:`.corpus`.

The model is deliberately *vanilla* — it is the trained weights, not
any hand-coded translation rule, that maps Go tokens to Cangjie tokens.
"""

from __future__ import annotations

import math

import torch
from torch import nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div = torch.exp(torch.arange(0, d_model, 2).float() *
                        (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))  # (1, max_len, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, : x.size(1)]


class Seq2SeqTransformer(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 128,
        nhead: int = 4,
        num_encoder_layers: int = 3,
        num_decoder_layers: int = 3,
        dim_feedforward: int = 512,
        dropout: float = 0.1,
        pad_idx: int = 0,
        max_len: int = 512,
    ):
        super().__init__()
        self.pad_idx = pad_idx
        self.d_model = d_model
        self.src_emb = nn.Embedding(vocab_size, d_model, padding_idx=pad_idx)
        self.tgt_emb = nn.Embedding(vocab_size, d_model, padding_idx=pad_idx)
        self.pos = PositionalEncoding(d_model, max_len=max_len)
        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.out_proj = nn.Linear(d_model, vocab_size)
        self.out_proj.weight = self.tgt_emb.weight  # tied weights

    def _embed_src(self, src: torch.Tensor) -> torch.Tensor:
        return self.pos(self.src_emb(src) * math.sqrt(self.d_model))

    def _embed_tgt(self, tgt: torch.Tensor) -> torch.Tensor:
        return self.pos(self.tgt_emb(tgt) * math.sqrt(self.d_model))

    @staticmethod
    def _causal_mask(sz: int, device) -> torch.Tensor:
        return torch.triu(
            torch.full((sz, sz), float("-inf"), device=device), diagonal=1
        )

    def forward(self, src: torch.Tensor, tgt_in: torch.Tensor) -> torch.Tensor:
        src_pad = src == self.pad_idx
        tgt_pad = tgt_in == self.pad_idx
        tgt_mask = self._causal_mask(tgt_in.size(1), src.device)
        h = self.transformer(
            self._embed_src(src),
            self._embed_tgt(tgt_in),
            tgt_mask=tgt_mask,
            src_key_padding_mask=src_pad,
            tgt_key_padding_mask=tgt_pad,
            memory_key_padding_mask=src_pad,
        )
        return self.out_proj(h)

    @torch.no_grad()
    def greedy_decode(
        self,
        src: torch.Tensor,
        bos_idx: int,
        eos_idx: int,
        max_len: int = 256,
    ) -> torch.Tensor:
        """Greedy autoregressive decode.

        ``src`` is ``(B, S)``; returns ``(B, L)`` (without leading BOS).
        """
        self.eval()
        device = src.device
        src_pad = src == self.pad_idx
        memory = self.transformer.encoder(
            self._embed_src(src), src_key_padding_mask=src_pad
        )
        B = src.size(0)
        ys = torch.full((B, 1), bos_idx, dtype=torch.long, device=device)
        finished = torch.zeros(B, dtype=torch.bool, device=device)
        for _ in range(max_len):
            tgt_mask = self._causal_mask(ys.size(1), device)
            out = self.transformer.decoder(
                self._embed_tgt(ys),
                memory,
                tgt_mask=tgt_mask,
                memory_key_padding_mask=src_pad,
            )
            logits = self.out_proj(out[:, -1])  # (B, V)
            next_tok = logits.argmax(-1)
            next_tok = torch.where(
                finished, torch.full_like(next_tok, self.pad_idx), next_tok
            )
            ys = torch.cat([ys, next_tok.unsqueeze(1)], dim=1)
            finished = finished | (next_tok == eos_idx)
            if bool(finished.all()):
                break
        return ys[:, 1:]  # strip BOS
