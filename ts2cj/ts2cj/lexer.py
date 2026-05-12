"""TypeScript tokenizer.

A regex-driven lexer.  We do *not* build a full AST — downstream stages
operate on token streams and use neural similarity to recover structure.

The tokenizer is intentionally permissive: it never raises on unknown
characters (instead emitting an ``UNKNOWN`` token), which is one source of
the converter's robustness against incomplete or syntactically dubious
input.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, List


# Token kinds.  Plain strings make pattern construction in :mod:`patterns`
# significantly more readable than an Enum would.
KEYWORDS = {
    "let", "const", "var", "function", "return", "if", "else", "for",
    "while", "do", "switch", "case", "default", "break", "continue",
    "class", "interface", "extends", "implements", "new", "this",
    "super", "import", "export", "from", "as", "type", "typeof",
    "instanceof", "in", "of", "true", "false", "null", "undefined",
    "void", "any", "number", "string", "boolean", "never", "unknown",
    "public", "private", "protected", "readonly", "static", "abstract",
    "enum", "namespace", "module", "declare", "async", "await", "yield",
    "throw", "try", "catch", "finally", "delete", "get", "set",
}


@dataclass
class Token:
    """A single lexical token."""

    kind: str
    value: str
    line: int
    col: int

    def __repr__(self) -> str:  # pragma: no cover - debug only
        return f"Token({self.kind!r}, {self.value!r}@{self.line}:{self.col})"


# Order matters: longer / more specific patterns first.
_TOKEN_SPEC: List[tuple] = [
    ("COMMENT_BLOCK", r"/\*[\s\S]*?\*/"),
    ("COMMENT_LINE",  r"//[^\n]*"),
    ("WHITESPACE",    r"[ \t\r\f\v]+"),
    ("NEWLINE",       r"\n"),
    # Template literal — keep `${...}` markers; we re-lex the inside later.
    ("TEMPLATE",      r"`(?:\\.|\$\{[^}]*\}|[^`\\])*`"),
    ("STRING",        r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'"),
    ("NUMBER",        r"\d+\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?|0[xX][0-9a-fA-F]+"),
    # Multi-char punctuation.
    ("PUNCT",         (
        r"===|!==|==|!=|<=|>=|&&|\|\||\?\?|=>|"
        r"\+\+|--|\+=|-=|\*=|/=|%=|<<|>>|\*\*|"
        r"\.\.\.|"
        r"[{}()\[\];,.:?<>+\-*/%=!&|^~]"
    )),
    ("IDENT",         r"[A-Za-z_$][A-Za-z0-9_$]*"),
    ("UNKNOWN",       r"."),
]
_TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _TOKEN_SPEC))


def tokenize(source: str) -> List[Token]:
    """Return the full token list for *source*.

    Whitespace tokens are dropped but newlines are preserved (kind
    ``NEWLINE``) so that downstream layers can recover line-oriented
    structure when needed.
    """

    tokens: List[Token] = []
    line, col_start = 1, 0
    for match in _TOKEN_RE.finditer(source):
        kind = match.lastgroup or "UNKNOWN"
        value = match.group()
        col = match.start() - col_start + 1
        if kind == "NEWLINE":
            tokens.append(Token(kind, value, line, col))
            line += 1
            col_start = match.end()
            continue
        if kind == "WHITESPACE":
            continue
        if kind == "IDENT" and value in KEYWORDS:
            kind = "KEYWORD"
        tokens.append(Token(kind, value, line, col))
    return tokens


def iter_meaningful(tokens: List[Token]) -> Iterator[Token]:
    """Yield tokens excluding whitespace, comments, and newlines."""

    for t in tokens:
        if t.kind in ("NEWLINE", "COMMENT_BLOCK", "COMMENT_LINE"):
            continue
        yield t
