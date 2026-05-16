"""Word-level tokenizer and vocabulary for the seq2seq model.

We deliberately keep tokenization simple: split on whitespace after
inserting spaces around punctuation, and keep multi-character operators
(``==``, ``!=``, ``<=``, ``>=``, ``&&``, ``||``, ``++``, ``--``,
``+=``, ``-=``, ``*=``, ``/=``, ``:=``, ``..``, ``..=``, ``//``,
``/*``, ``*/``, ``->``, ``=>``) as atomic tokens.

The vocab is built from the training corpus.  Out-of-vocabulary tokens
are mapped to ``<unk>`` at encode time; the decoder still preserves
literal characters by emitting ``<copy>`` tokens (a small ``<copy_i>``
family is unused in this minimal version — the model is taught to copy
identifiers explicitly during data generation).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


SPECIALS = ["<pad>", "<bos>", "<eos>", "<unk>"]

# Multi-character operators kept atomic.
_MULTI = [
    "..=", "...",
    "==", "!=", "<=", ">=", "&&", "||",
    "++", "--", "+=", "-=", "*=", "/=", "%=", ":=",
    "<<", ">>", "->", "=>", "::",
    "//", "/*", "*/", "**",
    "..",
]
_MULTI.sort(key=len, reverse=True)

# Single-character punctuation: separated into its own token.
_PUNCT = set('(){}[];:,.+-*/%=<>!&|^~?@#"\'`\\')


def tokenize_text(text: str) -> List[str]:
    """Whitespace + punctuation tokenizer that respects multi-char operators
    and string literals.

    String literals (single ``"..."`` strings, raw ``` `...` ``` strings,
    and Cangjie / Go-flavoured strings) are kept as a *single* token so
    the model doesn't have to learn to balance quotes; the literal is
    output verbatim.
    """

    out: List[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        # String literal — keep atomic.
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(text[i:j + 1])
            i = j + 1
            continue
        if c == "`":
            j = i + 1
            while j < n and text[j] != "`":
                j += 1
            out.append(text[i:j + 1])
            i = j + 1
            continue
        if c == "'":
            j = i + 1
            while j < n and text[j] != "'":
                if text[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(text[i:j + 1])
            i = j + 1
            continue
        # Multi-char operator?
        matched = False
        for op in _MULTI:
            if text.startswith(op, i):
                out.append(op)
                i += len(op)
                matched = True
                break
        if matched:
            continue
        # Punctuation char.
        if c in _PUNCT:
            out.append(c)
            i += 1
            continue
        # Identifier / number run.
        j = i
        while j < n and (text[j].isalnum() or text[j] == "_"):
            j += 1
        if j == i:
            # Unknown single char — keep as token.
            out.append(c)
            i += 1
        else:
            # Float / decimal literal: if the run is purely digits and
            # is followed by ``.<digit>``, glue the fractional part on
            # so floats like ``3.14`` are a single token (the model
            # learns much better with atomic numeric literals).
            token = text[i:j]
            if token.isdigit() and j + 1 < n and text[j] == "." \
                    and text[j + 1].isdigit():
                k = j + 1
                while k < n and text[k].isdigit():
                    k += 1
                # Optional scientific exponent: e[+-]?digits
                if k < n and text[k] in ("e", "E"):
                    k2 = k + 1
                    if k2 < n and text[k2] in ("+", "-"):
                        k2 += 1
                    while k2 < n and text[k2].isdigit():
                        k2 += 1
                    if k2 > k + 1 and text[k2 - 1].isdigit():
                        k = k2
                out.append(text[i:k])
                i = k
            else:
                out.append(token)
                i = j
    return out


def detokenize(tokens: List[str]) -> str:
    """Inverse of :func:`tokenize_text` good enough for source emission.

    Heuristics: no space before ``,;:)]}`` and after ``([{``, no space
    around ``.``, force newlines after ``{`` / ``;`` / ``}`` (caller can
    re-indent).  These are purely cosmetic and do not affect compiler
    acceptance.
    """

    out = []
    prev = ""
    for tok in tokens:
        if not tok:
            continue
        if not out:
            out.append(tok)
            prev = tok
            continue
        no_space_before = tok in {",", ";", ":", ")", "]", "}", ".", "(", "["}
        no_space_after_prev = prev in {"(", "[", "{", ".", "@"}
        if no_space_before or no_space_after_prev:
            out.append(tok)
        elif prev in {"!", "&", "|", "^", "~"} and tok.isalpha():
            out.append(tok)
        else:
            out.append(" " + tok)
        prev = tok
    s = "".join(out)
    # Cosmetic newlines after statement separators / block opens / closes.
    s = re.sub(r" *; *", "\n", s)
    s = re.sub(r"\{ *", "{\n", s)
    s = re.sub(r" *\}", "\n}", s)
    # When two statements got separated only by whitespace inside the
    # template (the common case for multi-line bodies whose newlines
    # were collapsed to spaces during tokenisation), insert a newline
    # between ``}`` and the next non-keyword-continuation token so the
    # rendered Cangjie has one statement per line.  We deliberately
    # don't break before ``else``/``catch``/``,``/``)``/``]``/``;``.
    s = re.sub(r"\}\s+(?=(?!else\b|catch\b|finally\b)[A-Za-z_])",
               "}\n", s)
    # Also break *before* statement-introducing keywords when the
    # previous token sequence was a complete simple statement (i.e.
    # ends with an identifier / literal / ``++``/``--``/``)``).  This
    # recovers newlines that were collapsed to spaces when the
    # multi-statement Cangjie template was tokenised.
    _STMT_KW = r"(?:var|let|const|while|for|if|return|match|break|continue)"
    s = re.sub(r"(?<=[A-Za-z0-9_)\]])\s+(?=" + _STMT_KW + r"\b)",
               "\n", s)
    return s


@dataclass
class Vocab:
    itos: List[str]
    stoi: Dict[str, int]

    @classmethod
    def build(cls, token_lists, min_freq: int = 1) -> "Vocab":
        freq: Dict[str, int] = {}
        for toks in token_lists:
            for t in toks:
                freq[t] = freq.get(t, 0) + 1
        itos = list(SPECIALS)
        for tok, c in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
            if c >= min_freq and tok not in itos:
                itos.append(tok)
        stoi = {t: i for i, t in enumerate(itos)}
        return cls(itos=itos, stoi=stoi)

    def encode(self, tokens: List[str], add_bos: bool = False,
               add_eos: bool = False) -> List[int]:
        ids: List[int] = []
        if add_bos:
            ids.append(self.stoi["<bos>"])
        for t in tokens:
            ids.append(self.stoi.get(t, self.stoi["<unk>"]))
        if add_eos:
            ids.append(self.stoi["<eos>"])
        return ids

    def decode(self, ids) -> List[str]:
        out: List[str] = []
        for i in ids:
            if i < 0 or i >= len(self.itos):
                continue
            t = self.itos[i]
            if t in {"<bos>", "<pad>"}:
                continue
            if t == "<eos>":
                break
            out.append(t)
        return out

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self.itos, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path) -> "Vocab":
        itos = json.loads(path.read_text())
        return cls(itos=itos, stoi={t: i for i, t in enumerate(itos)})

    def __len__(self) -> int:
        return len(self.itos)
