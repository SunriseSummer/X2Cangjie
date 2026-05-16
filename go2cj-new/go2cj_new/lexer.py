"""Go tokenizer.

Regex-driven lexer for Go source.  We do *not* build a full AST —
downstream stages operate on the token stream and use neural similarity
to recover structure.

The tokenizer is intentionally permissive: it never raises on unknown
characters (it emits an ``UNKNOWN`` token instead), which contributes to
the converter's robustness against unusual or partial input.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, List


# Go keywords.  Used by the tokenizer to up-cast IDENT tokens to KEYWORD,
# and by pattern templates as anchor literals.
KEYWORDS = {
    "break", "case", "chan", "const", "continue", "default", "defer",
    "else", "fallthrough", "for", "func", "go", "goto", "if", "import",
    "interface", "map", "package", "range", "return", "select", "struct",
    "switch", "type", "var",
    # Predeclared identifiers that behave keyword-like for our purposes:
    "true", "false", "nil", "iota",
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
    # Raw string literal — backtick-delimited.  Treated as a single token
    # so downstream re-quotes it to a Cangjie double-quoted string.
    ("RAW_STRING",    r"`[^`]*`"),
    ("STRING",        r"\"(?:\\.|[^\"\\\n])*\""),
    ("RUNE",          r"'(?:\\.|[^'\\\n])'"),
    ("NUMBER", (
        r"\d+\.\d+(?:[eE][+-]?\d+)?|"
        r"\d+(?:[eE][+-]?\d+)?|"
        r"0[xX][0-9a-fA-F]+|"
        r"0[oO]?[0-7]+|"
        r"0[bB][01]+"
    )),
    # Multi-char punctuation.  Order matters within this single PUNCT
    # branch (longer first).
    ("PUNCT", (
        r":=|<<=|>>=|&\^=|&\^|<<|>>|"
        r"==|!=|<=|>=|&&|\|\||<-|\.\.\.|"
        r"\+\+|--|\+=|-=|\*=|/=|%=|&=|\|=|\^=|"
        r"[{}()\[\];,.:?<>+\-*/%=!&|^~@]"
    )),
    ("IDENT",         r"[A-Za-z_][A-Za-z0-9_]*"),
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
