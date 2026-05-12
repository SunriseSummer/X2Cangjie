"""Swift tokenizer.

Regex-driven and intentionally permissive (an ``UNKNOWN`` token absorbs any
unrecognised character).  No AST is built; downstream stages operate on the
token stream and use neural similarity to recover structure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, List


# Swift keywords — closed set.  Used so that pattern templates can use
# keywords as literal anchors.
KEYWORDS = {
    "let", "var", "func", "return", "if", "else", "for", "in",
    "while", "repeat", "switch", "case", "default", "break", "continue",
    "class", "struct", "enum", "protocol", "extension", "init", "deinit",
    "self", "super", "import", "public", "private", "internal", "fileprivate",
    "static", "open", "final", "lazy", "weak", "unowned",
    "true", "false", "nil", "as", "is", "where",
    "try", "throw", "throws", "catch", "do", "guard", "defer",
    "inout", "mutating", "nonmutating", "override", "convenience", "required",
    "typealias", "associatedtype", "subscript", "operator",
    "Any", "Self",
    "fallthrough",
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


# Order matters: longer / more specific patterns first.  Note especially that
# Swift's ``..<`` and ``...`` range operators must be lexed as single tokens
# so that pattern anchors can target them by surface form.
_TOKEN_SPEC: List[tuple] = [
    ("COMMENT_BLOCK", r"/\*[\s\S]*?\*/"),
    ("COMMENT_LINE",  r"//[^\n]*"),
    ("WHITESPACE",    r"[ \t\r\f\v]+"),
    ("NEWLINE",       r"\n"),
    # Swift multi-line string literal (triple-quoted).
    ("STRING_TRIPLE", r"\"\"\"[\s\S]*?\"\"\""),
    # Single-line string literal — Swift supports ``\(expr)`` interpolation.
    ("STRING",        r"\"(?:\\\(\s*[^)]*\)|\\.|[^\"\\\n])*\""),
    ("NUMBER",        r"\d+\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?|0[xX][0-9a-fA-F]+"),
    # Multi-char punctuation.  ``...`` and ``..<`` are Swift range ops.
    ("PUNCT",         (
        r"\.\.<|\.\.\.|"
        r"===|!==|==|!=|<=|>=|&&|\|\||\?\?|->|=>|"
        r"\+\+|--|\+=|-=|\*=|/=|%=|<<|>>|\*\*|"
        r"[{}()\[\];,.:?<>+\-*/%=!&|^~@]"
    )),
    ("IDENT",         r"[A-Za-z_][A-Za-z0-9_]*"),
    ("UNKNOWN",       r"."),
]
_TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _TOKEN_SPEC))


def tokenize(source: str) -> List[Token]:
    """Return the full token list for *source*."""

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
        if kind == "STRING_TRIPLE":
            tokens.append(Token("STRING", value, line, col))
            # Update line count for any embedded newlines.
            for ch in value:
                if ch == "\n":
                    line += 1
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
