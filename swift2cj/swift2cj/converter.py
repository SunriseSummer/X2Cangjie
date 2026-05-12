"""End-to-end Swift → Cangjie conversion pipeline.

Architecture closely mirrors :mod:`ts2cj.converter` but with Swift-specific
lexing, patterns, and post-processing.  The pipeline is fully deterministic
(the SOM is seeded) and requires no training data — pattern retrieval relies
on a Kohonen self-organizing map trained on the built-in pattern corpus at
import time, while symbol-level rewrites use a Hopfield-style associative
memory.

Pipeline stages:

1. Token-level pre-rewrite (string interpolation, ``.count`` → ``.size``,
   range operators inside string contexts, ``nil`` → ``None`` etc.).
2. Tokenization (:func:`.lexer.tokenize`).
3. Unbraced control-flow bodies are normalised; chunk segmentation finds
   top-level statements via brace / semicolon-equivalent balance.
4. For each chunk: SOM retrieves a candidate-pattern prior, full corpus is
   re-scored by anchor + cosine, slot binding emits Cangjie source.
5. Post-processing: ``import std.collection.*`` injection, ``main()`` wrap,
   ``override`` analysis, generic-bracket whitespace tightening.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from .embedding import embed_sequence, embed_token, cosine
from .hopfield import HopfieldMemory
from .lexer import Token, tokenize
from .patterns import CHUNK_PATTERNS, Pattern, TOKEN_MAPPINGS
from .som import SOM


# --------------------------------------------------------------------------- #
#  Result type                                                                #
# --------------------------------------------------------------------------- #


@dataclass
class ConversionResult:
    """Output of :func:`convert_source`."""

    source: str
    chunks: int = 0
    confident_chunks: int = 0
    fallback_chunks: int = 0
    patterns_used: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        if self.chunks == 0:
            return 0.0
        return self.confident_chunks / self.chunks


# --------------------------------------------------------------------------- #
#  Shared models (built once)                                                 #
# --------------------------------------------------------------------------- #


def _pattern_tokens(template: str) -> List[Tuple[str, str]]:
    """Split a pattern template string into ``(kind, value)`` pairs."""

    pieces = template.split()
    out: List[Tuple[str, str]] = []
    for p in pieces:
        if p.startswith("$"):
            out.append(("SLOT", p[1:]))
        else:
            out.append(("LIT", p))
    return out


class _Engine:
    """Lazy-loaded singleton holding the trained SOM + Hopfield memory."""

    _instance: Optional["_Engine"] = None

    def __init__(self) -> None:
        self.patterns = CHUNK_PATTERNS
        self.pattern_token_lists = [_pattern_tokens(p.swift_template) for p in self.patterns]
        self.pattern_embeddings = np.stack(
            [embed_sequence(pt) for pt in self.pattern_token_lists]
        )
        self.som = SOM(dim=self.pattern_embeddings.shape[1])
        self.som.train(self.pattern_embeddings)
        self.memory = HopfieldMemory()
        for k, v in TOKEN_MAPPINGS:
            self.memory.remember(k, v)

    @classmethod
    def get(cls) -> "_Engine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# --------------------------------------------------------------------------- #
#  Token-level rewriting (pre-pass)                                           #
# --------------------------------------------------------------------------- #


def _outside_strings_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Apply literal ``str.replace`` rewrites only outside string/comment regions."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            # Handle triple-quoted multi-line literal.
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    text = "".join(out)
    for k, v in pairs:
        text = text.replace(k, v)
    return text


def _outside_strings_word_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Apply ``\\bkey\\b`` regex replacements only outside string/comment regions."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    text = "".join(out)
    for k, v in pairs:
        text = re.sub(r"\b" + re.escape(k) + r"\b", v, text)
    return text


def _convert_string_interpolations(src: str) -> str:
    """Rewrite Swift ``\\(expr)`` interpolation to Cangjie ``${expr}``.

    We walk the source character-by-character so that nested parens inside
    an interpolation (e.g. ``"\\(f(x))"``) are matched correctly.  Only
    runs *inside* a string literal — strings start at ``"`` and end at the
    matching unescaped ``"``.  Triple-quoted multi-line strings are left
    alone (rare in idiomatic Swift; downstream AI handles them).
    """

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            # Skip triple-quoted strings verbatim.
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            # Single-line string — scan & rewrite interpolations.
            out.append('"')
            i += 1
            while i < n:
                if src[i] == "\\" and i + 1 < n:
                    if src[i + 1] == "(":
                        # interpolation — collect balanced parens
                        depth = 1
                        j = i + 2
                        while j < n and depth > 0:
                            if src[j] == "(":
                                depth += 1
                            elif src[j] == ")":
                                depth -= 1
                                if depth == 0:
                                    break
                            j += 1
                        expr = src[i + 2:j]
                        out.append("${" + expr + "}")
                        i = j + 1
                        continue
                    # other escape — keep verbatim
                    out.append(src[i:i + 2])
                    i += 2
                    continue
                if src[i] == '"':
                    out.append('"')
                    i += 1
                    break
                if src[i] == "\n":
                    # Unterminated string — bail out preserving content.
                    out.append("\n")
                    i += 1
                    break
                out.append(src[i])
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _rewrite_source(src: str) -> Tuple[str, List[str]]:
    """Apply safe textual rewrites on the raw Swift source.

    Done before tokenization so that:

    * String interpolation ``\\(expr)`` → ``${expr}``
    * Common member-name swaps (``.count`` → ``.size``, ``.append`` → ``.add``)
    * ``nil`` → ``None`` (word-boundary)

    The bulk of type-name translation happens later, at slot-render time,
    so that primitive type names like ``Int``/``String`` remain available as
    pattern anchors.
    """

    notes: List[str] = []
    # 1. String interpolation first — operates inside string literals.
    src = _convert_string_interpolations(src)
    # 2. Literal text replacements (member-name calls etc.).  These are
    #    distinctive enough that they cannot collide with Swift keywords.
    src = _outside_strings_replace(
        src,
        [
            (".count", ".size"),
            (".append(", ".add("),
            (".isEmpty", ".isEmpty()"),
            (".uppercased()", ".toAsciiUpper()"),
            (".lowercased()", ".toAsciiLower()"),
            # Swift super-constructor call ``super.init(...)`` → ``super(...)``.
            ("super.init(", "super("),
            # ``as!`` / ``as?`` Swift casts — keep ``as`` (Cangjie also has
            # ``as``) and drop the optional/forced markers.
            (" as!", " as"),
            (" as?", " as"),
        ],
    )
    # 3. Word-boundary identifier swaps.
    src = _outside_strings_word_replace(
        src,
        [
            ("nil", "None"),
            # Swift's ``self`` is ``this`` in Cangjie.
            ("self", "this"),
            # ``try`` at a call site is a Swift-only marker; Cangjie call
            # expressions don't need it.  Drop the surface keyword (the
            # downstream patterns still treat ``try`` blocks via do/catch).
            ("try", ""),
        ],
    )
    # 4. Swift's leading-dot enum shorthand (``.circle``) has no Cangjie
    #    analogue — strip the dot when the preceding character isn't part
    #    of an expression on the left (i.e. it's not a member access).
    src = _strip_leading_enum_dot(src)
    return src, notes


_LEADING_ENUM_DOT_RE = re.compile(r"(?<![A-Za-z0-9_)\]])\.(?=[A-Za-z_])")


def _strip_leading_enum_dot(src: str) -> str:
    """Strip Swift leading-dot enum shorthand outside string/comment regions."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            if src[i:i + 3] == '"""':
                end = src.find('"""', i + 3)
                end = n if end == -1 else end + 3
                out.append(src[i:end])
                i = end
                continue
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(ch)
        i += 1
    text = "".join(out)
    return _LEADING_ENUM_DOT_RE.sub("", text)


_PRIMITIVE_MAP = {
    "Int": "Int64",
    "Int64": "Int64",
    "Int32": "Int32",
    "Int16": "Int16",
    "Int8": "Int8",
    "UInt": "UInt64",
    "UInt64": "UInt64",
    "UInt32": "UInt32",
    "Double": "Float64",
    "Float": "Float32",
    "Float64": "Float64",
    "Bool": "Bool",
    "String": "String",
    "Character": "Rune",
    "Void": "Unit",
    "Any": "Any",
}
_PRIMITIVE_TYPE_RE = re.compile(
    r"\b(Int8|Int16|Int32|Int64|Int|UInt32|UInt64|UInt|Float32|Float64|Float|Double|Bool|String|Character|Void)\b"
)


def _apply_primitive_types(text: str) -> str:
    """Translate Swift primitive type names → Cangjie."""

    return _PRIMITIVE_TYPE_RE.sub(lambda m: _PRIMITIVE_MAP[m.group(1)], text)


# --------------------------------------------------------------------------- #
#  Statement boundary synthesis                                               #
# --------------------------------------------------------------------------- #
#
# Swift uses *newlines* as primary statement terminators rather than ``;``.
# Our chunker expects semicolon-terminated chunks (like the ts2cj baseline),
# so we synthesise a top-level ``;`` token at every newline that lies
# **outside** any brace / paren / bracket group **and** which doesn't
# immediately precede a token that should continue the previous statement
# (``else``, ``catch``, ``while`` of a ``repeat-while``, ``{``, ``.``).
def _insert_semicolons(tokens: List[Token]) -> List[Token]:
    """Walk *tokens* and insert ``;`` tokens at top-level statement breaks."""

    out: List[Token] = []
    depth_b = depth_p = depth_s = 0
    n = len(tokens)
    i = 0
    last_meaningful: Optional[Token] = None

    # tokens that, when starting the *next* line, mean the previous line
    # continues (no ``;`` should be inserted).
    cont_starts = {".", ",", ")", "]", "}", "else", "catch", "where",
                   "?", ":", "&&", "||", "==", "!=", "<", ">", "<=", ">=",
                   "+", "-", "*", "/", "%", "=", "+=", "-=", "*=", "/=",
                   "->", "..<", "...", "??"}
    # tokens that should NEVER receive a synthesised ``;`` after them
    # because they themselves expect a continuation.
    no_semi_after = {"{", "(", "[", ",", ";", ".", "?", ":", "&&", "||",
                     "==", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/",
                     "%", "=", "+=", "-=", "*=", "/=", "->", "..<", "...",
                     "??", "else", "case", "default", "where", "throw",
                     "return", "in", "do", "try", "if", "while", "for",
                     "switch", "repeat", "guard"}

    for tok in tokens:
        if tok.kind == "NEWLINE":
            # Decide whether to flush a ``;`` at this newline.
            if (
                depth_p == 0 and depth_s == 0
                and last_meaningful is not None
                and last_meaningful.value not in no_semi_after
                and last_meaningful.kind not in ("COMMENT_BLOCK", "COMMENT_LINE")
            ):
                # peek ahead for the next meaningful token (skip newlines/comments).
                pass  # handled below by scanning the *out* stream
                out.append(Token("PUNCT", ";", tok.line, tok.col))
                last_meaningful = out[-1]
            continue
        if tok.kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
            continue
        if tok.value == "{":
            depth_b += 1
        elif tok.value == "}":
            depth_b = max(depth_b - 1, 0)
        elif tok.value == "(":
            depth_p += 1
        elif tok.value == ")":
            depth_p = max(depth_p - 1, 0)
        elif tok.value == "[":
            depth_s += 1
        elif tok.value == "]":
            depth_s = max(depth_s - 1, 0)
        out.append(tok)
        last_meaningful = tok
        i += 1

    # Second pass: remove inserted ``;`` that ended up adjacent to a
    # continuation start token (e.g. ``...\n.foo()`` or ``...\nelse {``).
    cleaned: List[Token] = []
    j = 0
    m = len(out)
    while j < m:
        t = out[j]
        if t.kind == "PUNCT" and t.value == ";":
            # Look at next meaningful token.
            k = j + 1
            while k < m and out[k].kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
                k += 1
            if k < m:
                nxt = out[k]
                if nxt.value in cont_starts:
                    j += 1
                    continue
            # collapse multiple ``;`` in a row
            if cleaned and cleaned[-1].kind == "PUNCT" and cleaned[-1].value == ";":
                j += 1
                continue
        cleaned.append(t)
        j += 1
    return cleaned


# --------------------------------------------------------------------------- #
#  Chunk segmentation                                                         #
# --------------------------------------------------------------------------- #
def _segment_chunks(tokens: List[Token]) -> List[List[Token]]:
    """Split a token stream into balanced top-level chunks.

    A chunk ends at a top-level ``;`` or at a top-level ``}`` that closes a
    previously opened ``{`` — **unless** the next meaningful token is one of
    ``else`` / ``catch`` / ``while`` (``repeat-while`` trailer), in which
    case the chunk continues.
    """

    toks = [t for t in tokens if t.kind not in ("NEWLINE", "COMMENT_BLOCK", "COMMENT_LINE")]
    chunks: List[List[Token]] = []
    cur: List[Token] = []
    depth_b = depth_p = depth_s = 0

    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        cur.append(t)
        if t.kind == "PUNCT":
            if t.value == "{":
                depth_b += 1
            elif t.value == "}":
                depth_b = max(depth_b - 1, 0)
                if depth_b == 0 and depth_p == 0 and depth_s == 0:
                    nxt = toks[i + 1] if i + 1 < n else None
                    if nxt is not None and nxt.kind == "KEYWORD" and nxt.value in (
                        "else", "catch", "while",
                    ):
                        i += 1
                        continue
                    chunks.append(cur)
                    cur = []
            elif t.value == "(":
                depth_p += 1
            elif t.value == ")":
                depth_p = max(depth_p - 1, 0)
            elif t.value == "[":
                depth_s += 1
            elif t.value == "]":
                depth_s = max(depth_s - 1, 0)
            elif t.value == ";" and depth_b == 0 and depth_p == 0 and depth_s == 0:
                # drop the ``;`` itself (we synthesised it as a separator).
                cur.pop()
                if cur:
                    chunks.append(cur)
                cur = []
        i += 1
    if cur:
        chunks.append(cur)
    return chunks


# --------------------------------------------------------------------------- #
#  Slot binding                                                               #
# --------------------------------------------------------------------------- #
def _bind_slots(
    chunk: List[Token],
    pat_tokens: List[Tuple[str, str]],
) -> Optional[Tuple[dict, float]]:
    """Try to bind *chunk* to a pattern template.

    Each ``LIT`` event must match ``chunk[i]`` exactly.  Each ``SLOT`` event
    collects a brace/paren/bracket-balanced token span up to the next ``LIT``
    anchor (or the end of the chunk).  A slot mentioned multiple times must
    bind to the same token sequence each time.
    """

    events = pat_tokens
    if not events:
        return None

    bindings: dict = {}
    i = 0
    total_anchors = sum(1 for k, _ in events if k == "LIT")
    matched_anchors = 0

    e = 0
    while e < len(events):
        kind, val = events[e]
        if kind == "LIT":
            if i >= len(chunk) or chunk[i].value != val:
                return None
            i += 1
            matched_anchors += 1
            e += 1
            continue
        nxt = None
        for k in range(e + 1, len(events)):
            if events[k][0] == "LIT":
                nxt = events[k][1]
                break
        slot_tokens: List[Token] = []
        if nxt is None:
            slot_tokens = chunk[i:]
            i = len(chunk)
        else:
            depth_b = depth_p = depth_s = 0
            j = i
            while j < len(chunk):
                tv = chunk[j].value
                if tv == nxt and depth_b == 0 and depth_p == 0 and depth_s == 0:
                    break
                if tv == "{":
                    depth_b += 1
                elif tv == "}":
                    depth_b -= 1
                elif tv == "(":
                    depth_p += 1
                elif tv == ")":
                    depth_p -= 1
                elif tv == "[":
                    depth_s += 1
                elif tv == "]":
                    depth_s -= 1
                slot_tokens.append(chunk[j])
                j += 1
            if j >= len(chunk):
                return None
            i = j
        if val in bindings:
            prev = bindings[val]
            if len(prev) != len(slot_tokens) or any(
                a.value != b.value for a, b in zip(prev, slot_tokens)
            ):
                return None
        else:
            bindings[val] = slot_tokens
        e += 1

    if i != len(chunk):
        return None

    score = (matched_anchors / total_anchors) if total_anchors else 1.0
    return bindings, score


# --------------------------------------------------------------------------- #
#  Rendering helpers                                                          #
# --------------------------------------------------------------------------- #
def _is_word(s: str) -> bool:
    return bool(s) and (s[0].isalnum() or s[0] == "_")


def _render_tokens(tokens: List[Token]) -> str:
    """Render a token list back to surface source with reasonable spacing."""

    binary_ops = {"+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                  "&&", "||", "??", "&", "|", "^", "<<", ">>", "**",
                  "+=", "-=", "*=", "/=", "%=", "=", "=>", "->"}
    out: List[str] = []
    for i, t in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            need_space = False
            if _is_word(prev.value) and _is_word(t.value):
                need_space = True
            elif prev.value == "," and t.value not in (")", "]", "}"):
                need_space = True
            elif t.value in binary_ops:
                need_space = True
            elif prev.value in binary_ops:
                need_space = True
            elif prev.value == ":":
                need_space = True
            if need_space:
                out.append(" ")
        out.append(t.value)
    return "".join(out)


def _strip_trailing_semicolon(tokens: List[Token]) -> List[Token]:
    if tokens and tokens[-1].kind == "PUNCT" and tokens[-1].value == ";":
        return tokens[:-1]
    return tokens


def _default_value_for(ty: str) -> str:
    """Pick a Cangjie default-value literal for ``ty``."""

    ty = ty.strip()
    if ty.startswith("?"):
        return "None"
    if ty.startswith("ArrayList<") or ty.startswith("Array<"):
        return ty + "()"
    if ty.startswith("HashMap<") or ty.startswith("HashSet<"):
        return ty + "()"
    if ty.startswith("("):
        inner = ty[1:-1]
        parts = [_default_value_for(p.strip()) for p in _split_top_level(inner, ",")]
        return "(" + ", ".join(parts) + ")"
    return {
        "Int64": "0", "Int32": "0", "Int16": "0", "Int8": "0",
        "UInt64": "0", "UInt32": "0",
        "Float64": "0.0", "Float32": "0.0",
        "Bool": "false", "String": "\"\"", "Rune": "r' '",
    }.get(ty, ty + "()")


def _split_top_level(s: str, sep: str) -> List[str]:
    out: List[str] = []
    depth = 0
    buf: List[str] = []
    for ch in s:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth = max(depth - 1, 0)
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


# --------------------------------------------------------------------------- #
#  Body recursion                                                             #
# --------------------------------------------------------------------------- #
def _convert_body(tokens: List[Token], indent: int = 1, ctx: Optional[str] = None) -> str:
    inner_chunks = _segment_chunks(tokens)
    pieces: List[str] = []
    pad = "    " * indent
    for ch in inner_chunks:
        if not ch:
            continue
        line = _convert_chunk(ch, ctx=ctx)
        if line is None:
            line = "/* swift2cj: unrecognised */ // " + _render_tokens(ch)
        line = _adjust_for_context(line, ctx)
        for ln in line.split("\n"):
            pieces.append(pad + ln if ln else ln)
    return "\n".join(pieces)


def _adjust_for_context(line: str, ctx: Optional[str]) -> str:
    if ctx == "iface":
        line = line.replace("public open func ", "func ")
        line = line.replace("public static func ", "static func ")
    elif ctx == "struct":
        line = line.replace("public open func ", "public func ")
    return line


# --------------------------------------------------------------------------- #
#  Chunk → Cangjie                                                            #
# --------------------------------------------------------------------------- #
def _convert_if_chain(chunk: List[Token]) -> Optional[str]:
    """Convert a Swift ``if … else if … else …`` chain of any depth.

    Returns ``None`` if the chunk doesn't look like an if-chain, letting
    the caller fall back to pattern retrieval (e.g. for ``if let``
    guards which need different handling).
    """

    n = len(chunk)
    i = 0
    arms: List[Tuple[Optional[List[Token]], List[Token]]] = []
    # tuple (condition_tokens_or_None_for_else, body_tokens)

    def find_matching_brace(start: int) -> int:
        # ``chunk[start]`` must be ``{``.  Return index of matching ``}``.
        depth = 0
        j = start
        while j < n:
            v = chunk[j].value
            if v == "{":
                depth += 1
            elif v == "}":
                depth -= 1
                if depth == 0:
                    return j
            j += 1
        return -1

    while i < n:
        t = chunk[i]
        if t.kind == "KEYWORD" and t.value == "if":
            # Collect condition tokens up to next top-level ``{``.
            i += 1
            cond: List[Token] = []
            depth_p = depth_s = 0
            while i < n:
                v = chunk[i].value
                if v == "{" and depth_p == 0 and depth_s == 0:
                    break
                if v == "(":
                    depth_p += 1
                elif v == ")":
                    depth_p -= 1
                elif v == "[":
                    depth_s += 1
                elif v == "]":
                    depth_s -= 1
                cond.append(chunk[i])
                i += 1
            if i >= n or chunk[i].value != "{":
                return None
            brace_end = find_matching_brace(i)
            if brace_end == -1:
                return None
            body = chunk[i + 1:brace_end]
            arms.append((cond, body))
            i = brace_end + 1
            # Look for ``else`` or end.
            if i < n and chunk[i].value == "else":
                i += 1
                if i < n and chunk[i].value == "if":
                    continue  # next iteration handles ``if`` arm
                if i < n and chunk[i].value == "{":
                    brace_end = find_matching_brace(i)
                    if brace_end == -1:
                        return None
                    body = chunk[i + 1:brace_end]
                    arms.append((None, body))
                    i = brace_end + 1
                    continue
                return None
            continue
        # unexpected trailing tokens
        return None

    if not arms:
        return None

    # Emit Cangjie source.
    parts: List[str] = []
    for idx, (cond, body) in enumerate(arms):
        body_text = _convert_body(body, indent=1)
        if cond is None:  # else arm
            parts.append("else {\n" + body_text + "\n}")
        else:
            cond_text = _convert_expr(cond)
            kw = "if" if idx == 0 else "else if"
            parts.append(f"{kw} ({cond_text}) " + "{\n" + body_text + "\n}")
    return " ".join(parts)


def _convert_chunk(chunk: List[Token], ctx: Optional[str] = None) -> Optional[str]:
    if not chunk:
        return ""
    engine = _Engine.get()

    # ------- structural pre-pass: if / else-if / else chain ------- #
    # Handle arbitrary-depth ``if ... { ... } else if ... { ... } ... else
    # { ... }`` chains directly — built-in patterns only cover two and
    # three-arm forms.
    if chunk and chunk[0].kind == "KEYWORD" and chunk[0].value == "if":
        chain = _convert_if_chain(chunk)
        if chain is not None:
            return chain

    chunk_emb = embed_sequence(chunk)
    som_candidates = {i for i, _ in engine.som.query(chunk_emb, k=8)}

    # Context-driven pattern gating.  In an interface/protocol body we want
    # the ``proto_method_*`` patterns to win over ``expr_stmt``; inside a
    # class / struct body we want the ``method_*`` / ``init_*`` patterns
    # rather than the top-level ``function_*`` ones (and vice versa at the
    # top level).  Sets enumerated explicitly for clarity.
    method_pats = {
        "method_typed", "method_throws_typed", "method_no_ret",
        "method_throws_no_ret", "method_generic_typed",
        "static_method_typed", "static_method_no_ret",
        "private_method_typed", "private_method_no_ret",
        "override_method_typed", "override_method_no_ret",
        "init_decl", "init_throws_decl",
        "override_init_decl", "convenience_init_decl",
        "field_var_typed_with_init", "field_let_typed_with_init",
        "field_var_typed", "field_let_typed",
        "proto_method_typed", "proto_method_no_ret",
    }
    function_pats = {
        "function_typed", "function_throws_typed", "function_no_ret",
        "function_throws_no_ret",
        "function_generic_typed", "function_generic_no_ret",
    }
    proto_pats = {"proto_method_typed", "proto_method_no_ret"}

    best: Optional[Tuple[Pattern, dict, float]] = None
    for idx in range(len(engine.patterns)):
        pat = engine.patterns[idx]
        # Apply context filtering.
        if ctx in ("class", "struct"):
            if pat.name in function_pats:
                continue
        elif ctx == "iface":
            # In a protocol body, only signature-only proto patterns plus
            # a few generic catch-alls make sense; suppress full-body ones.
            if pat.name in function_pats:
                continue
            if pat.name in ("method_typed", "method_throws_typed",
                            "method_no_ret", "method_throws_no_ret"):
                # Allow as default-method, but proto_method_* should win on
                # signature-only chunks via the anchor count.
                pass
        else:  # top-level
            if pat.name in method_pats:
                continue
            # proto_method_* patterns are no-body and very catchy; suppress.
            if pat.name in proto_pats:
                continue

        pat_tokens = engine.pattern_token_lists[idx]
        result = _bind_slots(chunk, pat_tokens)
        if result is None:
            continue
        bindings, anchor_score = result
        if "NAME" in bindings:
            first = bindings["NAME"][0] if bindings["NAME"] else None
            if first is not None and first.kind == "KEYWORD" and first.value in (
                "for", "while", "if", "else", "do", "switch", "case", "default",
                "return", "throw", "try", "catch", "repeat", "guard", "break",
                "continue", "let", "var", "func", "class", "struct", "enum",
                "protocol", "extension", "init", "import", "typealias",
            ):
                continue
        n_anchors = sum(1 for k, _ in pat_tokens if k == "LIT")
        sim = cosine(chunk_emb, engine.pattern_embeddings[idx])
        som_bonus = 0.1 if idx in som_candidates else 0.0
        composite = anchor_score * (1.0 + n_anchors) + 0.1 * sim + som_bonus
        if best is None or composite > best[2]:
            best = (pat, bindings, composite)

    if best is None:
        return None
    pat, bindings, _score = best
    return _emit(pat, bindings, ctx=ctx)


def _is_body_slot(slot: str) -> bool:
    if slot in ("BODY", "A", "CBODY", "FBODY"):
        return True
    if slot == "B" or (slot.startswith("B") and slot[1:].isdigit()):
        return True
    if slot == "C" or (slot.startswith("C") and slot[1:].isdigit()):
        # C1/C2 are *conditions* — expressions, not bodies.
        return False
    return False


_TYPE_ALIASES: dict = {}
_CLASS_METHODS: dict = {}
_CLASS_PARENT: dict = {}


def _emit(pat: Pattern, bindings: dict, ctx: Optional[str] = None) -> str:
    out = pat.cj_template

    if pat.name == "switch_block":
        expr = _convert_expr(bindings.get("EXPR", []))
        body = _convert_switch_body(bindings.get("BODY", []))
        return out.replace("$EXPR", expr).replace("$SWBODY", body)

    if pat.name == "enum_decl":
        name = _convert_expr(bindings.get("NAME", [])).strip()
        body = _convert_enum_body(bindings.get("BODY", []))
        return out.replace("$NAME", name).replace("$ENUMBODY", body)

    if pat.name == "import_decl":
        # Drop imports entirely (Cangjie has its own module system; we inject
        # std.collection later if needed).
        return ""

    if "$DEFAULT" in out and "TY" in bindings:
        ty_text = _convert_type(bindings["TY"]).strip()
        out = out.replace("$DEFAULT", _default_value_for(ty_text))

    iface_like = pat.name in ("protocol_decl", "protocol_decl_inherit")
    struct_like = pat.name in ("struct_decl", "struct_impl_decl")
    class_like = pat.name in (
        "class_decl", "class_decl_inherit", "class_generic_decl",
        "class_generic_decl_inherit", "extension_decl",
    )
    if iface_like:
        sub_ctx = "iface"
    elif struct_like:
        sub_ctx = "struct"
    elif class_like:
        sub_ctx = "class"
    else:
        sub_ctx = None

    # In a protocol body, method-without-body chunks are emitted using the
    # ``proto_method_*`` patterns — but the slot binder needs help: those
    # patterns will be retried with ctx propagation below.
    for slot in pat.slots:
        if slot not in bindings:
            continue
        tokens = bindings[slot]
        if _is_body_slot(slot):
            body_text = _convert_body(tokens, indent=1, ctx=sub_ctx)
            out = out.replace(f"${slot}", body_text)
        elif slot == "PARAMS":
            out = out.replace(f"${slot}", _convert_params(tokens))
        elif slot in ("RET", "TY", "BASE"):
            out = out.replace(f"${slot}", _convert_type(tokens))
        elif slot == "TPARAMS":
            out = out.replace(f"${slot}", _convert_type_params(tokens))
        else:
            out = out.replace(f"${slot}", _convert_expr(tokens))

    # Override / inheritance bookkeeping.
    if pat.name in ("class_decl_inherit", "class_generic_decl_inherit"):
        name = _convert_expr(bindings.get("NAME", [])).strip()
        base_text = _convert_type(bindings.get("BASE", [])).strip() if "BASE" in bindings else ""
        base = re.sub(r"<.*$", "", base_text).strip()
        my_methods = _scan_method_names(bindings.get("BODY", []))
        _CLASS_METHODS[name] = my_methods
        _CLASS_PARENT[name] = base
        parent_methods: set = set()
        cur = base
        seen: set = set()
        while cur and cur not in seen:
            seen.add(cur)
            parent_methods |= _CLASS_METHODS.get(cur, set())
            cur = _CLASS_PARENT.get(cur, "")

        def _mark(m: re.Match) -> str:
            n = m.group(1)
            if n in parent_methods:
                return f"public override func {n}"
            return f"public open func {n}"

        out = re.sub(r"public open func (\w+)", _mark, out)
    elif pat.name in ("class_decl", "class_generic_decl"):
        name = _convert_expr(bindings.get("NAME", [])).strip()
        _CLASS_METHODS[name] = _scan_method_names(bindings.get("BODY", []))

    if pat.name == "typealias_decl" and "NAME" in bindings and "TY" in bindings:
        name = _convert_expr(bindings["NAME"]).strip()
        ty = _convert_type(bindings["TY"]).strip()
        _TYPE_ALIASES[name] = ty

    # Auto-synthesize a memberwise initialiser for structs / classes that
    # declare fields but no explicit ``init``.  Swift gives structs an
    # implicit memberwise init; Cangjie does not.
    if pat.name in ("struct_decl", "struct_impl_decl", "class_decl",
                    "class_decl_inherit", "class_generic_decl",
                    "class_generic_decl_inherit"):
        out = _ensure_memberwise_init(out)


    # Post-substitution: wrap bare collection literals to match a typed
    # collection annotation:
    #   ``let xs: ArrayList<Int64> = [1,2,3]``  →
    #   ``let xs: ArrayList<Int64> = ArrayList<Int64>([1,2,3])``
    # Cangjie 1.x has no implicit conversion from ``Array`` literals.
    if pat.name in (
        "let_typed_init", "var_typed_init",
        "field_var_typed_with_init", "field_let_typed_with_init",
    ) and "TY" in bindings:
        ty_text = _convert_type(bindings["TY"]).strip()
        if ty_text.startswith(("ArrayList<", "HashSet<", "HashMap<")):
            m = re.search(r"=\s*\[(.*)\]\s*$", out, flags=re.DOTALL)
            if m:
                inner = m.group(1).strip()
                if ty_text.startswith("HashMap<"):
                    # Swift dict literal ``[k1: v1, k2: v2]`` → list of pairs.
                    pairs = []
                    for kv in _split_top_level(inner, ","):
                        kv = kv.strip()
                        if not kv:
                            continue
                        parts = _split_top_level(kv, ":")
                        if len(parts) == 2:
                            pairs.append(f"({parts[0].strip()}, {parts[1].strip()})")
                    body = ", ".join(pairs)
                    out = out[:m.start()] + f"= {ty_text}([{body}])" + out[m.end():]
                else:
                    out = out[:m.start()] + f"= {ty_text}([{inner}])" + out[m.end():]
    return out


def _scan_method_names(tokens: List[Token]) -> set:
    names: set = set()
    i, n = 0, len(tokens)
    depth = 0
    while i < n:
        t = tokens[i]
        if t.value == "{":
            depth += 1
        elif t.value == "}":
            depth -= 1
        if depth != 0:
            i += 1
            continue
        # look for ``func NAME``
        if t.kind == "KEYWORD" and t.value == "func":
            if i + 1 < n and tokens[i + 1].kind == "IDENT":
                names.add(tokens[i + 1].value)
        i += 1
    return names


_FIELD_LINE_RE = re.compile(
    r"^\s*(?:public\s+|private\s+|static\s+)*(var|let)\s+([A-Za-z_]\w*)\s*:\s*([^=\n]+?)(?:\s*=\s*([^\n]+))?\s*$",
    re.MULTILINE,
)


def _ensure_memberwise_init(class_text: str) -> str:
    """If a class/struct body has no ``init``, synthesize a memberwise one.

    Swift gives structs an implicit memberwise initialiser; Cangjie has no
    such mechanism so we emit one explicitly using the declared fields.
    Constructor body assigns ``this.FIELD = FIELD`` for every var/let field.
    """

    if "public init(" in class_text or "init(" in class_text:
        return class_text
    # Find the body between the first ``{`` and the last ``}``.
    m = re.search(r"\{\n(.*)\n\}\s*$", class_text, flags=re.DOTALL)
    if not m:
        return class_text
    body = m.group(1)
    fields = _FIELD_LINE_RE.findall(body)
    if not fields:
        return class_text
    params = []
    assigns = []
    for _kw, name, ty, _default in fields:
        params.append(f"{name}!: {ty.strip()}")
        assigns.append(f"        this.{name} = {name}")
    init_text = (
        "    public init(" + ", ".join(params) + ") {\n"
        + "\n".join(assigns) + "\n    }"
    )
    # Append the init at the end of the body.
    new_body = body.rstrip() + "\n" + init_text
    return class_text[:m.start()] + "{\n" + new_body + "\n}" + class_text[m.end():]


# --------------------------------------------------------------------------- #
#  Expression rewriting                                                       #
# --------------------------------------------------------------------------- #
def _convert_expr(tokens: List[Token]) -> str:
    """Render an expression's token list to Cangjie surface syntax."""

    tokens = _strip_trailing_semicolon(tokens)
    rendered = _render_tokens(tokens)
    # Drop any stray ``try`` (Swift call-site marker — Cangjie has no analogue).
    rendered = re.sub(r"\btry\s*[!?]?\s*", "", rendered)
    # Swift array literal type-form ``[Int]()`` → ``ArrayList<Int64>()``.
    rendered = re.sub(r"\[\s*([^\[\]:,]+?)\s*\]\s*\(\s*\)",
                      lambda m: f"ArrayList<{_convert_type_text(m.group(1))}>()",
                      rendered)
    # Swift dictionary literal type-form ``[K: V]()`` → ``HashMap<K, V>()``.
    rendered = re.sub(
        r"\[\s*([^\[\]]+?)\s*:\s*([^\[\]]+?)\s*\]\s*\(\s*\)",
        lambda m: f"HashMap<{_convert_type_text(m.group(1))}, {_convert_type_text(m.group(2))}>()",
        rendered,
    )
    rendered = _apply_primitive_types(rendered)
    return rendered.strip()


def _convert_params(tokens: List[Token]) -> str:
    """Convert a Swift parameter list to Cangjie form.

    Swift allows external + internal labels (``func f(_ x: Int)`` /
    ``func f(label x: Int)``).  Cangjie uses a single parameter name; we
    drop the external label (the underscore ``_`` is a Swift "no external
    label" marker, and a distinct ``label`` external would conflict with
    Cangjie's call-site syntax — the downstream AI pass can recover named
    arguments where needed).
    """

    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    if not text:
        return ""
    parts = _split_top_level(text, ",")
    out_parts: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Swift forms:
        #   ``name: Type``
        #   ``ext name: Type``         (external + internal label)
        #   ``_ name: Type``           (no external label)
        #   ``name: Type = default``
        #   ``inout name: Type``
        p = re.sub(r"^inout\s+", "", p)
        m = re.match(
            r"^(?:(_|[A-Za-z_][\w]*)\s+)?([A-Za-z_][\w]*)\s*:\s*([^=]+?)\s*(?:=\s*(.+))?$",
            p,
        )
        if not m:
            out_parts.append(p)
            continue
        _ext, name, ty, default = m.group(1), m.group(2), m.group(3), m.group(4)
        ty_t = _convert_type_text(ty.strip())
        if default is not None:
            out_parts.append(f"{name}!: {ty_t} = {default.strip()}")
        else:
            out_parts.append(f"{name}: {ty_t}")
    return ", ".join(out_parts)


def _convert_type(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_type_text(text)


def _convert_type_text(text: str) -> str:
    """Translate a Swift type expression to Cangjie.

    * ``Int`` / ``Double`` / etc.  → ``Int64`` / ``Float64`` / etc.
    * ``T?``                       → ``?T``
    * ``[T]``                      → ``ArrayList<T>``
    * ``[K: V]``                   → ``HashMap<K, V>``
    * ``(T, U)``                   → ``(T, U)`` (Cangjie tuple)
    """

    text = (text or "").strip()
    if not text:
        return "Any"

    # Optional ``T?`` (allow chained ``T??`` collapsed to ``?T``).
    if text.endswith("?"):
        return "?" + _convert_type_text(text[:-1].strip())

    # Dictionary ``[K: V]``.
    if text.startswith("[") and text.endswith("]") and ":" in text:
        inner = text[1:-1]
        parts = _split_top_level(inner, ":")
        if len(parts) == 2:
            k = _convert_type_text(parts[0].strip())
            v = _convert_type_text(parts[1].strip())
            return f"HashMap<{k}, {v}>"

    # Array ``[T]``.
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return f"ArrayList<{_convert_type_text(inner)}>"

    # Tuple ``(T, U)`` — Cangjie tuples share the same surface form.
    if text.startswith("(") and text.endswith(")") and "," in text:
        inner = text[1:-1]
        elems = [_convert_type_text(e.strip()) for e in _split_top_level(inner, ",")]
        return "(" + ", ".join(elems) + ")"

    text = _apply_primitive_types(text)
    return text


def _convert_type_params(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    out: List[str] = []
    for p in _split_top_level(text, ","):
        p = p.strip()
        if not p:
            continue
        # ``T: Foo`` (Swift conformance constraint) → drop constraint.
        m = re.match(r"^([A-Za-z_][\w]*)\s*(?::\s*(.+))?$", p)
        if m:
            out.append(m.group(1))
        else:
            out.append(p)
    return ", ".join(out)


# --------------------------------------------------------------------------- #
#  Enum / switch helpers                                                      #
# --------------------------------------------------------------------------- #
def _convert_enum_body(tokens: List[Token]) -> str:
    """Convert a Swift enum body into Cangjie ``| Var1 | Var2`` form.

    Swift enums look like::

        case a
        case b, c
        case d(Int)

    We split on each ``case`` keyword and collect comma-separated variant
    names; payload types in parentheses are preserved verbatim.
    """

    variants: List[str] = []
    i, n = 0, len(tokens)
    while i < n:
        t = tokens[i]
        if t.kind == "KEYWORD" and t.value == "case":
            i += 1
            # collect tokens until ``;`` (already inserted) or another ``case``
            # or end.
            buf: List[Token] = []
            while i < n:
                tt = tokens[i]
                if tt.kind == "PUNCT" and tt.value == ";":
                    i += 1
                    break
                if tt.kind == "KEYWORD" and tt.value == "case":
                    break
                buf.append(tt)
                i += 1
            # Split on top-level commas.
            text = _render_tokens(buf).strip()
            for v in _split_top_level(text, ","):
                v = v.strip()
                if v:
                    variants.append(v)
            continue
        i += 1
    if not variants:
        return "    /* swift2cj: empty enum */"
    return "    | " + "\n    | ".join(variants)


def _convert_switch_body(tokens: List[Token]) -> str:
    """Convert a Swift ``switch`` body into Cangjie ``match`` arms."""

    toks = [t for t in tokens if t.kind not in ("COMMENT_BLOCK", "COMMENT_LINE")]

    cases: List[Tuple[List[List[Token]], List[Token]]] = []
    cur_labels: List[List[Token]] = []
    cur_body: List[Token] = []
    brace_depth = 0

    def flush():
        if cur_labels or cur_body:
            cases.append((list(cur_labels), list(cur_body)))

    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if t.kind == "PUNCT" and t.value == "{":
            brace_depth += 1
            cur_body.append(t)
            i += 1
            continue
        if t.kind == "PUNCT" and t.value == "}":
            brace_depth -= 1
            cur_body.append(t)
            i += 1
            continue
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "case":
            if cur_body:
                flush()
                cur_labels.clear()
                cur_body.clear()
            i += 1
            # In Swift ``case Foo, Bar:`` the labels are comma-separated then ``:``.
            lab_tokens: List[Token] = []
            while i < n and not (toks[i].kind == "PUNCT" and toks[i].value == ":"):
                lab_tokens.append(toks[i])
                i += 1
            i += 1  # skip ``:``
            # Split labels by top-level commas.
            buf: List[Token] = []
            for tt in lab_tokens:
                if tt.kind == "PUNCT" and tt.value == ",":
                    if buf:
                        cur_labels.append(buf)
                    buf = []
                else:
                    buf.append(tt)
            if buf:
                cur_labels.append(buf)
            continue
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "default":
            if cur_body:
                flush()
                cur_labels.clear()
                cur_body.clear()
            i += 1
            if i < n and toks[i].kind == "PUNCT" and toks[i].value == ":":
                i += 1
            cur_labels.append([])
            continue
        # Drop any synthesised ``;`` at this level — match arms use newlines.
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "break":
            j = i + 1
            if j < n and toks[j].kind == "PUNCT" and toks[j].value == ";":
                i = j + 1
                continue
        cur_body.append(t)
        i += 1
    flush()

    if not cases:
        return "    case _ => ()"

    out_lines: List[str] = []
    for labels, body in cases:
        is_default = any(len(l) == 0 for l in labels)
        body_text = _convert_body(body, indent=2)
        if is_default:
            label_str = "_"
        else:
            label_str = " | ".join(_convert_expr(l) for l in labels if l)
        out_lines.append(f"    case {label_str} =>")
        body_lines = [ln for ln in body_text.split("\n") if ln.strip()]
        if not body_lines:
            out_lines.append("        ()")
        else:
            out_lines.extend(body_lines)
    return "\n".join(out_lines)


# --------------------------------------------------------------------------- #
#  Top-level driver                                                           #
# --------------------------------------------------------------------------- #
_NEEDS_COLLECTION = re.compile(r"\b(ArrayList|HashMap|HashSet)\b")
_GENERIC_NAMES = (
    "ArrayList", "HashMap", "HashSet", "Array", "Map", "Set",
    "Option", "Iterator", "List", "Queue", "Stack", "Box",
)


def _tighten_generic_spacing(text: str) -> str:
    name_alt = "|".join(_GENERIC_NAMES)
    pat_open = re.compile(rf"\b({name_alt})\s+<\s*")
    pat_close = re.compile(r"([\w\)>\]])\s+>")
    pat_call = re.compile(rf"\b({name_alt})(<[^<>\n]*(?:<[^<>\n]*>[^<>\n]*)*>)\s+\(")
    for _ in range(6):
        new = pat_open.sub(r"\1<", text)
        new = pat_close.sub(r"\1>", new)
        new = pat_call.sub(r"\1\2(", new)
        if new == text:
            break
        text = new
    return text


def convert_source(swift_source: str, wrap_main: bool = True) -> ConversionResult:
    """Convert a Swift source string into Cangjie source."""

    rewritten, notes = _rewrite_source(swift_source)
    tokens = tokenize(rewritten)
    # Synthesise statement-terminating ``;`` tokens at top-level newlines.
    tokens = _insert_semicolons(tokens)
    _TYPE_ALIASES.clear()
    _CLASS_METHODS.clear()
    _CLASS_PARENT.clear()

    chunks = _segment_chunks(tokens)
    result = ConversionResult(source="", notes=notes)
    result.chunks = sum(1 for c in chunks if c)

    rendered_chunks: List[str] = []
    top_level_decls: List[str] = []
    main_body: List[str] = []
    has_user_main = False

    for ch in chunks:
        if not ch:
            continue
        cj = _convert_chunk(ch)
        if cj is None:
            result.fallback_chunks += 1
            verbatim = _render_tokens(ch)
            cj = f"/* swift2cj: TODO unrecognised chunk */ // {verbatim}"
        elif cj == "":
            # Empty emission (e.g. ``import``) — count as confident but skip.
            result.confident_chunks += 1
            continue
        else:
            result.confident_chunks += 1
        rendered_chunks.append(cj)

        # Top-level classification.
        i0 = 0
        while i0 < len(ch) and ch[i0].value in (
            "public", "private", "internal", "fileprivate", "open", "final",
            "static",
        ):
            i0 += 1
        first = ch[i0].value if i0 < len(ch) else ""
        if first in (
            "class", "struct", "enum", "protocol", "extension",
            "func", "typealias", "import",
        ):
            if first == "func" and i0 + 1 < len(ch) and ch[i0 + 1].value == "main":
                has_user_main = True
                cj = re.sub(
                    r"^func\s+main\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{",
                    "main() {", cj, count=1,
                )
                if "\nreturn " not in cj and "\n    return " not in cj:
                    cj = cj[:-1] + "    return 0\n}"
                rendered_chunks[-1] = cj
            top_level_decls.append(cj)
        elif first in ("let", "var"):
            top_level_decls.append(cj)
        else:
            main_body.append(cj)

    if has_user_main:
        wrap_main = False

    parts: List[str] = []
    if top_level_decls:
        parts.extend(top_level_decls)
    if wrap_main:
        if not any(re.search(r"^main\s*\(", d, re.MULTILINE) for d in top_level_decls):
            body = "\n".join("    " + ln for ln in "\n".join(main_body).split("\n") if ln)
            parts.append("main() {\n" + body + "\n    return 0\n}")
    else:
        parts.extend(main_body)

    body_text = "\n\n".join(p for p in parts if p)
    body_text = _tighten_generic_spacing(body_text)

    headers: List[str] = []
    if _NEEDS_COLLECTION.search(body_text):
        headers.append("import std.collection.*")
    header = ("\n".join(headers) + "\n\n") if headers else ""
    result.source = header + body_text + ("\n" if body_text and not body_text.endswith("\n") else "")
    return result
