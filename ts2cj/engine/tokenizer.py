"""TypeScript tokenizer (lexer).

A robust hand-written lexer that produces a flat token stream while preserving
comments, whitespace and original text spans. This is intentionally
non-strict: it tolerates partial / non-canonical TS, fitting the rule-engine
philosophy where downstream stages "soft-match" patterns over tokens.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# Token kinds ----------------------------------------------------------------

KW = {
    # JS/TS keywords we care about
    "var", "let", "const", "function", "return", "if", "else", "for", "while",
    "do", "break", "continue", "switch", "case", "default", "class", "extends",
    "implements", "interface", "new", "this", "super", "true", "false", "null",
    "undefined", "import", "export", "from", "as", "in", "of", "typeof",
    "instanceof", "try", "catch", "finally", "throw", "enum", "type", "public",
    "private", "protected", "static", "readonly", "abstract", "async", "await",
    "yield", "void", "any", "never", "unknown", "namespace", "module", "is",
    "keyof", "declare", "constructor", "get", "set",
}

# Primitive TS type names (treated as identifiers but recognised in context)
TS_PRIMS = {"number", "string", "boolean", "bigint", "symbol", "object"}


@dataclass
class Tok:
    kind: str        # 'kw','id','num','str','tpl','op','punct','cmt','ws','nl','regex','eof'
    value: str
    # Optional metadata used by later stages
    meta: dict = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        v = self.value.replace("\n", "\\n")
        if len(v) > 20:
            v = v[:17] + "..."
        return f"Tok({self.kind},{v!r})"


# Lexer ----------------------------------------------------------------------

_THREE = {"...", "**=", "<<=", ">>=", ">>>", "===", "!==", "??="}
_TWO = {
    "==", "!=", "<=", ">=", "&&", "||", "??", "=>", "++", "--", "+=", "-=",
    "*=", "/=", "%=", "&=", "|=", "^=", "<<", ">>", "**", "?.", "?:",
}
_SINGLE = set("+-*/%=<>!&|^~?:;,.()[]{}@")


class Lexer:
    def __init__(self, src: str) -> None:
        self.src = src
        self.i = 0
        self.n = len(src)
        self.tokens: List[Tok] = []

    def peek(self, k: int = 0) -> str:
        j = self.i + k
        return self.src[j] if j < self.n else ""

    def _is_id_start(self, c: str) -> bool:
        return c.isalpha() or c == "_" or c == "$"

    def _is_id_cont(self, c: str) -> bool:
        return c.isalnum() or c == "_" or c == "$"

    def _last_significant(self) -> Optional[Tok]:
        for t in reversed(self.tokens):
            if t.kind in ("ws", "nl", "cmt"):
                continue
            return t
        return None

    def _regex_allowed(self) -> bool:
        """Decide if a `/` should start a regex (very heuristic)."""
        prev = self._last_significant()
        if prev is None:
            return True
        if prev.kind == "op":
            return True
        if prev.kind == "punct" and prev.value in "(,;[{=:?!&|^~+-*%<>":
            return True
        if prev.kind == "kw" and prev.value in {
            "return", "typeof", "instanceof", "in", "of", "new", "delete",
            "throw", "case", "yield", "await",
        }:
            return True
        return False

    def tokenize(self) -> List[Tok]:
        while self.i < self.n:
            c = self.src[self.i]
            # newline
            if c == "\n":
                self.tokens.append(Tok("nl", "\n"))
                self.i += 1
                continue
            # whitespace
            if c in " \t\r":
                j = self.i
                while j < self.n and self.src[j] in " \t\r":
                    j += 1
                self.tokens.append(Tok("ws", self.src[self.i:j]))
                self.i = j
                continue
            # line comment
            if c == "/" and self.peek(1) == "/":
                j = self.i
                while j < self.n and self.src[j] != "\n":
                    j += 1
                self.tokens.append(Tok("cmt", self.src[self.i:j], {"style": "line"}))
                self.i = j
                continue
            # block comment
            if c == "/" and self.peek(1) == "*":
                j = self.i + 2
                while j < self.n - 1 and not (self.src[j] == "*" and self.src[j + 1] == "/"):
                    j += 1
                j = min(j + 2, self.n)
                self.tokens.append(Tok("cmt", self.src[self.i:j], {"style": "block"}))
                self.i = j
                continue
            # string literal
            if c == '"' or c == "'":
                self._read_string(c)
                continue
            # template literal
            if c == "`":
                self._read_template()
                continue
            # number
            if c.isdigit() or (c == "." and self.peek(1).isdigit()):
                self._read_number()
                continue
            # identifier / keyword
            if self._is_id_start(c):
                self._read_identifier()
                continue
            # regex
            if c == "/" and self._regex_allowed():
                if self._try_read_regex():
                    continue
            # operators (longest match)
            three = self.src[self.i:self.i + 3]
            if three in _THREE:
                self.tokens.append(Tok("op", three))
                self.i += 3
                continue
            two = self.src[self.i:self.i + 2]
            if two in _TWO:
                self.tokens.append(Tok("op", two))
                self.i += 2
                continue
            if c in _SINGLE:
                kind = "punct" if c in "()[]{};,@" else "op"
                # dots and colons treated as punct for easier matching
                if c in ".:":
                    kind = "punct"
                self.tokens.append(Tok(kind, c))
                self.i += 1
                continue
            # unknown — pass through
            self.tokens.append(Tok("op", c))
            self.i += 1
        self.tokens.append(Tok("eof", ""))
        return self.tokens

    def _read_string(self, quote: str) -> None:
        j = self.i + 1
        buf = [quote]
        while j < self.n:
            ch = self.src[j]
            if ch == "\\" and j + 1 < self.n:
                buf.append(ch)
                buf.append(self.src[j + 1])
                j += 2
                continue
            if ch == quote:
                buf.append(ch)
                j += 1
                break
            if ch == "\n":
                # unterminated, stop here for robustness
                break
            buf.append(ch)
            j += 1
        self.tokens.append(Tok("str", "".join(buf), {"quote": quote}))
        self.i = j

    def _read_template(self) -> None:
        j = self.i + 1
        parts: List = []
        cur = []
        depth = 0
        while j < self.n:
            ch = self.src[j]
            if depth == 0 and ch == "`":
                parts.append(("text", "".join(cur)))
                j += 1
                break
            if depth == 0 and ch == "\\" and j + 1 < self.n:
                cur.append(self.src[j + 1])
                j += 2
                continue
            if depth == 0 and ch == "$" and j + 1 < self.n and self.src[j + 1] == "{":
                parts.append(("text", "".join(cur)))
                cur = []
                j += 2
                # collect expression until matching brace
                expr_start = j
                br = 1
                while j < self.n and br > 0:
                    if self.src[j] == "{":
                        br += 1
                    elif self.src[j] == "}":
                        br -= 1
                        if br == 0:
                            break
                    j += 1
                parts.append(("expr", self.src[expr_start:j]))
                j += 1  # skip }
                continue
            cur.append(ch)
            j += 1
        raw = self.src[self.i:j]
        self.tokens.append(Tok("tpl", raw, {"parts": parts}))
        self.i = j

    def _read_number(self) -> None:
        j = self.i
        has_dot = False
        has_e = False
        is_hex = False
        if self.src[j] == "0" and j + 1 < self.n and self.src[j + 1] in "xX":
            is_hex = True
            j += 2
            while j < self.n and (self.src[j].isdigit() or self.src[j] in "abcdefABCDEF_"):
                j += 1
        else:
            while j < self.n:
                ch = self.src[j]
                if ch.isdigit() or ch == "_":
                    j += 1
                elif ch == "." and not has_dot and not has_e:
                    has_dot = True
                    j += 1
                elif ch in "eE" and not has_e:
                    has_e = True
                    has_dot = True  # treat as float
                    j += 1
                    if j < self.n and self.src[j] in "+-":
                        j += 1
                else:
                    break
        # BigInt suffix
        if j < self.n and self.src[j] == "n":
            j += 1
        raw = self.src[self.i:j]
        meta = {"float": has_dot, "hex": is_hex}
        self.tokens.append(Tok("num", raw, meta))
        self.i = j

    def _read_identifier(self) -> None:
        j = self.i + 1
        while j < self.n and self._is_id_cont(self.src[j]):
            j += 1
        name = self.src[self.i:j]
        kind = "kw" if name in KW else "id"
        self.tokens.append(Tok(kind, name))
        self.i = j

    def _try_read_regex(self) -> bool:
        # Attempt to consume a regex literal. If it looks malformed, give up
        # and emit '/' as an operator.
        j = self.i + 1
        in_class = False
        ok = False
        while j < self.n:
            ch = self.src[j]
            if ch == "\\" and j + 1 < self.n:
                j += 2
                continue
            if ch == "[":
                in_class = True
            elif ch == "]":
                in_class = False
            elif ch == "/" and not in_class:
                j += 1
                # flags
                while j < self.n and self.src[j] in "gimsuy":
                    j += 1
                ok = True
                break
            elif ch == "\n":
                break
            j += 1
        if not ok:
            return False
        self.tokens.append(Tok("regex", self.src[self.i:j]))
        self.i = j
        return True


def tokenize(src: str) -> List[Tok]:
    return Lexer(src).tokenize()
