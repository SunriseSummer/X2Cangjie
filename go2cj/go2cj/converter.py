"""End-to-end Go → Cangjie conversion pipeline.

Pipeline stages:

1.  **Tokenize** the Go source (:mod:`.lexer`).
2.  **Pre-process token-level rewrites** via the Hopfield memory and a
    handful of safe textual substitutions (raw strings → double-quoted
    Cangjie strings, ``\\b`` rewrites, etc.).
3.  **Segment** the meaningful tokens into top-level *chunks* using
    brace / semicolon / newline balance — no AST is built.
4.  For each chunk:

    * embed it with :func:`.embedding.embed_sequence`;
    * use the SOM to retrieve a small set of candidate patterns;
    * for each candidate, attempt **non-linear slot binding** —
      split the chunk according to the pattern's anchor tokens and
      pick the candidate whose binding has highest composite score
      (anchor-match × specificity + cosine similarity + SOM bonus).
    * if the best score is below a threshold the chunk is preserved
      verbatim inside a ``/* go2cj: TODO */`` block and flagged in
      the :class:`ConversionResult`.

5.  **Post-process** the emitted Cangjie source: inject required
    ``import`` statements (``std.collection.*`` when ``ArrayList`` /
    ``HashMap`` are used), promote struct methods to fields, ensure
    a top-level ``main`` exists, etc.

The whole pipeline is deterministic and reproducible (SOM uses a fixed
random seed).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from .embedding import embed_sequence, cosine
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
#  Pattern helpers                                                            #
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
        self.pattern_token_lists = [_pattern_tokens(p.go_template) for p in self.patterns]
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
#  Source-level (text) pre-rewrites                                           #
# --------------------------------------------------------------------------- #
_PRIMITIVE_MAP = {
    "int":     "Int64",
    "int8":    "Int8",
    "int16":   "Int16",
    "int32":   "Int32",
    "int64":   "Int64",
    "uint":    "UInt64",
    "uint8":   "UInt8",
    "uint16":  "UInt16",
    "uint32":  "UInt32",
    "uint64":  "UInt64",
    "uintptr": "UInt64",
    "byte":    "UInt8",
    "rune":    "Rune",
    "float32": "Float32",
    "float64": "Float64",
    "bool":    "Bool",
    "string":  "String",
    "any":     "Any",
    "error":   "Exception",
}
_PRIMITIVE_TYPE_RE = re.compile(
    r"\b(int8|int16|int32|int64|int|uint8|uint16|uint32|uint64|uint|uintptr|"
    r"byte|rune|float32|float64|bool|string|any|error)\b"
)


def _apply_primitive_types(text: str) -> str:
    return _PRIMITIVE_TYPE_RE.sub(lambda m: _PRIMITIVE_MAP[m.group(1)], text)


def _outside_strings_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Apply literal ``str.replace`` rewrites only outside Go string /
    rune / comment regions.

    Recognises ``"..."`` (interpreted strings, with escapes), ``` `...` ```
    (raw strings, no escapes), ``'.'`` runes, ``//`` line comments and
    ``/* */`` block comments.
    """

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "`":
            j = i + 1
            while j < n and src[j] != "`":
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if ch == "'":
            j = i + 1
            while j < n and src[j] != "'":
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


def _word_replace_outside(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Word-boundary replacement that stays outside string/rune/comment regions."""

    spans: List[Tuple[int, int]] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == '"':
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            spans.append((i, j + 1))
            i = j + 1
            continue
        if ch == "`":
            j = i + 1
            while j < n and src[j] != "`":
                j += 1
            spans.append((i, j + 1))
            i = j + 1
            continue
        if ch == "'":
            j = i + 1
            while j < n and src[j] != "'":
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            spans.append((i, j + 1))
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            spans.append((i, end))
            i = end
            continue
        i += 1

    # Build a mask of "is inside string/comment" then apply word replace
    # to the unprotected substring only.
    def is_protected(p: int) -> bool:
        for s, e in spans:
            if s <= p < e:
                return True
        return False

    # We do this token-by-token using a finditer over identifiers.
    def repl_one(text: str, k: str, v: str) -> str:
        regex = re.compile(r"\b" + re.escape(k) + r"\b")
        out: List[str] = []
        last = 0
        for m in regex.finditer(text):
            if is_protected(m.start()):
                continue
            out.append(text[last:m.start()])
            out.append(v)
            last = m.end()
        out.append(text[last:])
        return "".join(out)

    text = src
    for k, v in pairs:
        text = repl_one(text, k, v)
        # spans must be recomputed if text length changes; do simply by
        # processing one rewrite at a time and re-collecting.
        if len(text) != n:
            return _word_replace_outside(text, pairs[pairs.index((k, v)) + 1:])
    return text


def _convert_raw_strings(src: str) -> str:
    """Translate Go raw strings ``` `...` ``` to Cangjie double-quoted strings.

    Raw strings preserve newlines verbatim; Cangjie accepts ``\\n`` inside
    a regular string, so we escape special characters.
    """

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch == "`":
            j = i + 1
            while j < n and src[j] != "`":
                j += 1
            inner = src[i + 1:j]
            esc = (
                inner.replace("\\", "\\\\")
                     .replace("\"", "\\\"")
                     .replace("\n", "\\n")
                     .replace("\t", "\\t")
                     .replace("\r", "\\r")
            )
            out.append('"' + esc + '"')
            i = j + 1
            continue
        if ch == '"':
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
    return "".join(out)


# Hand-rolled printf format-string → Cangjie interpolation.  Supports the
# tiny but workable subset {%d, %v, %s, %f, %t, %x, %q} and converts the
# trailing argument list, in order, into ``${arg}`` interpolation slots.
_PRINTF_RE = re.compile(r'fmt\.(Printf|Sprintf|Println)\s*\(\s*"((?:\\.|[^"\\])*)"\s*(,|\))')


def _rewrite_printf_calls(src: str) -> str:
    """Rewrite ``fmt.Printf("...", a, b)`` to ``print("..." with interpolation)``.

    Algorithm:
    * Locate ``fmt.{Printf|Sprintf|Println}("…", a, b)`` calls.
    * Parse the format string for ``%v / %d / %s / %f / %t / %x / %q``
      verbs and replace each with ``${argN}`` referring to a positional
      argument.
    * Strip the trailing argument list.
    * For ``Println`` we additionally strip the format string and append
      arguments with spaces — but we only enter the Println branch when
      the call has a format string AND extra args; the plain
      ``fmt.Println(x)`` shape is handled by the chunk pattern.
    """

    def parse_args(text: str, start: int) -> Tuple[List[str], int]:
        depth = 0
        cur: List[str] = []
        args: List[str] = []
        i = start
        while i < len(text):
            ch = text[i]
            if ch == "(":
                depth += 1
                cur.append(ch)
            elif ch == ")":
                if depth == 0:
                    if cur:
                        args.append("".join(cur).strip())
                    return args, i
                depth -= 1
                cur.append(ch)
            elif ch == "," and depth == 0:
                args.append("".join(cur).strip())
                cur = []
            elif ch == '"':
                # consume string
                cur.append(ch)
                i += 1
                while i < len(text) and text[i] != '"':
                    if text[i] == "\\" and i + 1 < len(text):
                        cur.append(text[i])
                        cur.append(text[i + 1])
                        i += 2
                        continue
                    cur.append(text[i])
                    i += 1
                if i < len(text):
                    cur.append(text[i])
            else:
                cur.append(ch)
            i += 1
        return args, len(text)

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        m = _PRINTF_RE.search(src, i)
        if not m:
            out.append(src[i:])
            break
        out.append(src[i:m.start()])
        kind = m.group(1)
        fmtstr = m.group(2)
        if m.group(3) == ")":
            # No args — pass the string through (escape %% if any).
            if kind == "Println":
                out.append(f'println("{fmtstr}")')
            elif kind == "Print":
                out.append(f'print("{fmtstr}")')
            elif kind == "Sprintf":
                out.append(f'"{fmtstr}"')
            else:  # Printf
                out.append(f'print("{fmtstr}")')
            i = m.end()
            continue
        args, end_idx = parse_args(src, m.end())
        # Replace format verbs with interpolation.
        verb_re = re.compile(r"%[+\-#0-9]*\.?[0-9]*[vdsftqxXbeEgGcUop%]")
        new_str: List[str] = []
        pos = 0
        ai = 0
        for vm in verb_re.finditer(fmtstr):
            new_str.append(fmtstr[pos:vm.start()])
            verb = vm.group(0)
            if verb == "%%":
                new_str.append("%")
            else:
                if ai < len(args):
                    new_str.append("${" + args[ai] + "}")
                    ai += 1
                else:
                    new_str.append("${?}")  # missing arg
            pos = vm.end()
        new_str.append(fmtstr[pos:])
        rebuilt = "".join(new_str)
        if kind == "Println":
            out.append(f'println("{rebuilt}")')
        elif kind == "Print":
            out.append(f'print("{rebuilt}")')
        elif kind == "Sprintf":
            out.append(f'"{rebuilt}"')
        else:
            out.append(f'print("{rebuilt}")')
        i = end_idx + 1  # skip closing ``)``
    return "".join(out)


def _rewrite_token_stream(src: str) -> Tuple[str, List[str]]:
    """Apply safe text-level rewrites on the raw Go source.

    * Convert raw-string literals to regular Cangjie strings.
    * Lower ``fmt.Printf`` / ``fmt.Sprintf`` / multi-arg ``fmt.Println``
      to Cangjie's interpolation syntax.
    * Map a handful of unambiguous standard-library helpers (``len(x)``
      → ``x.size``, ``append(a, b)`` → ``a.add(b)``, ``nil`` → ``None``).

    We intentionally do **not** rewrite primitive type names here:
    those names act as anchor literals in chunk patterns (e.g.
    ``var $NAME int = …``).  Type-name translation happens at slot
    render time inside :func:`_convert_type_text`.
    """

    notes: List[str] = []
    src = _convert_raw_strings(src)
    src = _rewrite_printf_calls(src)
    src = _rewrite_var_const_decls(src)

    # len(x) -> (x).size — only when not a definition (e.g. ``len`` as id
    # cannot accidentally be a Cangjie keyword).  We use a regex that
    # matches the *outermost* parenthesised expression and rewrites to a
    # ``.size`` method access.
    def repl_len(m: re.Match) -> str:
        inner = m.group(1)
        return f"({inner}).size"
    src = _outside_strings_replace(src, [])  # no-op pass for symmetry
    # The conservative len() / cap() rewriter is regex-based and operates
    # only on the textual form ``len(...)`` / ``cap(...)`` outside strings.
    src = _re_outside_strings(src, re.compile(r"\blen\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"), repl_len)
    src = _re_outside_strings(src, re.compile(r"\bcap\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"), repl_len)

    # append(slice, x, y, ...) → repeated .add(...) — but the trailing
    # call form is convenient.  Cangjie ArrayList.add only takes one arg;
    # we model multi-arg append by spreading.
    def repl_append(m: re.Match) -> str:
        inner = m.group(1)
        # Split top-level commas.
        parts = _split_top_level_text(inner, ",")
        if len(parts) < 2:
            return m.group(0)
        head = parts[0].strip()
        rest = [p.strip() for p in parts[1:]]
        body = "; ".join([f"{head}.add({r})" for r in rest])
        # Wrap in a block so its return value is the slice itself for
        # ``xs = append(xs, …)`` (Cangjie's add returns Unit so the
        # original assignment becomes a no-op after rewrite — we strip
        # the surrounding ``xs =`` later when needed).
        # In statement position the simple ``xs.add(v)`` form is most
        # idiomatic; we emit just that and rely on the assignment LHS
        # being dropped by ``_drop_self_append_assignment``.
        return body
    src = _re_outside_strings(src, re.compile(r"\bappend\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)"), repl_append)

    # ``xs = xs.add(v)`` happens as a side-effect of the append rewrite
    # above (Go ``xs = append(xs, v)`` is the common idiom).  Cangjie's
    # ``ArrayList.add`` returns ``Unit``, so the surrounding ``xs =``
    # would be a type error.  Strip it.
    src = _re_outside_strings(
        src,
        re.compile(r"\b([A-Za-z_]\w*)\s*=\s*\1\s*\.add\("),
        lambda m: f"{m.group(1)}.add(",
    )

    # `nil` → `None` (word boundary, outside strings).
    src = _word_replace_outside(src, [
        ("nil", "None"),
    ])

    return src, notes


def _rewrite_var_const_decls(src: str) -> str:
    """Pre-rewrite ``var name TYPE = expr`` and ``var name TYPE`` to
    a colon-typed form ``var name : TYPE = expr`` so chunk patterns can
    match cleanly (two adjacent slots are otherwise unbindable).

    Also flattens ``const ( … )`` and ``var ( … )`` group declarations
    into a sequence of single-line declarations, because Go uses
    newlines (not ``;``) as separators inside those parens and our
    lexer would otherwise treat the whole group as one chunk.
    """

    src = _flatten_decl_groups(src, "const")
    src = _flatten_decl_groups(src, "var")
    type_re = r"(?:\*?\[?\d*\]?\s*\*?(?:map\[[^\]]+\]\s*)?[\w.<>\[\]]+)"
    pats = [
        (re.compile(rf"\b(var|const)\s+([A-Za-z_]\w*)\s+({type_re})\s*=\s*"),
         r"\1 \2 : \3 = "),
        (re.compile(rf"\b(var)\s+([A-Za-z_]\w*)\s+({type_re})(?=\s*(?:;|\n|$))"),
         r"\1 \2 : \3"),
    ]
    for regex, repl in pats:
        src = _re_outside_strings(src, regex, lambda m, _r=repl: m.expand(_r))
    return src


def _flatten_decl_groups(src: str, kw: str) -> str:
    """Rewrite ``<kw> ( a = 1\\n b = 2 )`` → ``<kw> a = 1; <kw> b = 2;``.

    Only matches at top-level (outside strings/comments).  Group bodies
    may span multiple lines.
    """

    pat = re.compile(rf"\b{kw}\s*\(\s*([^)]*?)\s*\)", re.DOTALL)

    def repl(m: re.Match) -> str:
        body = m.group(1)
        lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
        if not lines:
            return ""
        return "; ".join(f"{kw} {ln.rstrip(';')}" for ln in lines)

    return _re_outside_strings(src, pat, repl)


def _re_outside_strings(src: str, regex: re.Pattern, repl) -> str:
    """Apply ``regex.sub(repl, src)`` only to non-string/comment regions."""

    # Identify protected ranges.
    spans: List[Tuple[int, int]] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch in ('"', '`'):
            quote = ch
            j = i + 1
            while j < n and src[j] != quote:
                if quote == '"' and src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            spans.append((i, j + 1))
            i = j + 1
            continue
        if ch == "'":
            j = i + 1
            while j < n and src[j] != "'":
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            spans.append((i, j + 1))
            i = j + 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            spans.append((i, end))
            i = end
            continue
        i += 1

    def protected(p: int) -> bool:
        for s, e in spans:
            if s <= p < e:
                return True
        return False

    out: List[str] = []
    last = 0
    for m in regex.finditer(src):
        if protected(m.start()):
            continue
        out.append(src[last:m.start()])
        out.append(repl(m) if callable(repl) else repl)
        last = m.end()
    out.append(src[last:])
    return "".join(out)


def _split_top_level_text(s: str, sep: str) -> List[str]:
    out: List[str] = []
    depth = 0
    buf: List[str] = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == '"':
            buf.append(ch)
            i += 1
            while i < n and s[i] != '"':
                if s[i] == "\\" and i + 1 < n:
                    buf.append(s[i]); buf.append(s[i + 1]); i += 2; continue
                buf.append(s[i]); i += 1
            if i < n:
                buf.append(s[i]); i += 1
            continue
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth = max(depth - 1, 0)
        if ch == sep and depth == 0:
            out.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    if buf:
        out.append("".join(buf))
    return out


# --------------------------------------------------------------------------- #
#  Statement boundary recovery                                                #
# --------------------------------------------------------------------------- #
# Go uses newline-based statement termination (with automatic semicolon
# insertion).  We inject explicit ``;`` tokens at end-of-statement
# locations so the existing chunk segmenter (which understands ``;``) can
# treat Go like a TS/Java-style language.

# These token values, if they appear at the *end* of a line, suppress
# semicolon insertion (matching Go spec section "Semicolons").
_NO_SEMI_AFTER = {
    "(", "[", "{", ",", ".", ";", ":", "?", "@",
    "+", "-", "*", "/", "%", "&", "|", "^", "!", "<", ">", "=",
    "==", "!=", "<=", ">=", "&&", "||", ":=", "<<", ">>", "+=", "-=",
    "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "&^", "&^=",
    "...",
    # Keywords that always have something after them.
    "if", "else", "for", "switch", "case", "default", "func", "var",
    "const", "type", "struct", "interface", "map", "chan", "go", "defer",
    "return", "range", "import", "package", "select",
}
# These token values, if they appear *first* on a new line, mean the
# previous line did NOT end a statement.  Currently empty but kept for
# future extension.


def _inject_semis(tokens: List[Token]) -> List[Token]:
    """Insert ``;`` PUNCT tokens at end-of-statement positions.

    The algorithm walks the original token stream including ``NEWLINE``
    markers.  For each newline:
    * if the most-recent meaningful token's value is in
      :data:`_NO_SEMI_AFTER`, suppress;
    * if we're inside ``(``, ``[``  brackets, suppress (Go suppresses
      semicolon insertion inside parens — relevant for multi-line
      function calls and composite literals);
    * otherwise, emit ``;``.

    Returns a list where NEWLINE tokens are removed and ``;`` tokens
    have been spliced in where appropriate.
    """

    out: List[Token] = []
    prev_meaningful: Optional[Token] = None
    depth_paren = 0
    depth_bracket = 0
    for t in tokens:
        if t.kind == "NEWLINE":
            if (prev_meaningful is not None
                    and prev_meaningful.value not in _NO_SEMI_AFTER
                    and depth_paren == 0 and depth_bracket == 0):
                out.append(Token("PUNCT", ";", t.line, t.col))
                prev_meaningful = out[-1]
            continue
        if t.kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
            continue
        if t.value == "(":
            depth_paren += 1
        elif t.value == ")":
            depth_paren = max(depth_paren - 1, 0)
        elif t.value == "[":
            depth_bracket += 1
        elif t.value == "]":
            depth_bracket = max(depth_bracket - 1, 0)
        out.append(t)
        prev_meaningful = t
    return out


# --------------------------------------------------------------------------- #
#  Chunk segmentation                                                         #
# --------------------------------------------------------------------------- #


def _segment_chunks(tokens: List[Token]) -> List[List[Token]]:
    """Split a token stream into balanced top-level chunks.

    A chunk ends at:
    * a top-level ``;``, or
    * a top-level ``}`` that closes a previously opened ``{`` — unless
      the next meaningful token is one of ``else`` / ``catch`` /
      ``finally`` (TS-style continuations).  Go's ``else`` and ``case``
      are the relevant continuations here.

    Additionally, ``;`` tokens occurring inside the *header* of a
    ``for init ; cond ; step { … }`` (i.e. before the body's opening
    ``{``) are not chunk boundaries — they are part of the for chunk.
    We track this with a ``for_header_depth`` counter.
    """

    toks = [t for t in tokens if t.kind not in ("NEWLINE", "COMMENT_BLOCK", "COMMENT_LINE")]
    chunks: List[List[Token]] = []
    cur: List[Token] = []
    depth_brace = 0
    depth_paren = 0
    depth_bracket = 0
    in_for_header = False  # True between ``for`` and its body's ``{``

    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        cur.append(t)
        if t.kind == "KEYWORD" and t.value == "for" and depth_brace == 0 \
                and depth_paren == 0 and depth_bracket == 0:
            in_for_header = True
        if t.kind == "PUNCT":
            if t.value == "{":
                depth_brace += 1
                if in_for_header and depth_brace == 1:
                    in_for_header = False
            elif t.value == "}":
                depth_brace = max(depth_brace - 1, 0)
                if depth_brace == 0 and depth_paren == 0 and depth_bracket == 0:
                    nxt = toks[i + 1] if i + 1 < n else None
                    if nxt is not None and nxt.kind == "KEYWORD" and nxt.value in ("else",):
                        i += 1
                        continue
                    chunks.append(cur)
                    cur = []
            elif t.value == "(":
                depth_paren += 1
            elif t.value == ")":
                depth_paren = max(depth_paren - 1, 0)
            elif t.value == "[":
                depth_bracket += 1
            elif t.value == "]":
                depth_bracket = max(depth_bracket - 1, 0)
            elif (t.value == ";" and depth_brace == 0 and depth_paren == 0
                  and depth_bracket == 0 and not in_for_header):
                chunks.append(cur[:-1])  # drop the ``;`` itself
                cur = []
        i += 1
    if cur:
        chunks.append(cur)
    return [c for c in chunks if c]


# --------------------------------------------------------------------------- #
#  Slot binding                                                               #
# --------------------------------------------------------------------------- #


def _bind_slots(
    chunk: List[Token],
    pat_tokens: List[Tuple[str, str]],
) -> Optional[Tuple[dict, float]]:
    """Try to bind ``chunk`` to a pattern's slot template.

    * Each ``LIT`` event must match ``chunk[i]`` exactly.
    * Each ``SLOT`` event collects a balanced span of tokens up to the
      next ``LIT`` anchor (or to the end of the chunk).

    Returns ``(bindings, anchor_score)`` on success, ``None`` on
    failure.
    """

    events = pat_tokens
    if not events:
        return None

    bindings: dict = {}
    i = 0
    matched_anchors = 0
    total_anchors = sum(1 for k, _ in events if k == "LIT")

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
        # SLOT — collect tokens until the next LIT anchor (balanced).
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
        # Slot consistency: a slot mentioned multiple times must bind to
        # the same token sequence each time.
        if val in bindings:
            prev = bindings[val]
            if len(prev) != len(slot_tokens) or any(
                a.value != b.value for a, b in zip(prev, slot_tokens)
            ):
                return None
        else:
            bindings[val] = slot_tokens
        # Reject when the *first* slot of the chunk binds to no tokens —
        # that means an opening LIT anchor matched at position 0, which
        # for patterns like ``$LHS = $RHS`` would let ``= 1`` accidentally
        # bind to ``LHS=∅, RHS=1``.  Internal empty slots (e.g. an empty
        # parameter list ``()``) remain legal.
        if e == 0 and not slot_tokens:
            return None
        e += 1

    if i != len(chunk):
        return None

    score = (matched_anchors / total_anchors) if total_anchors else 1.0
    return bindings, score


# --------------------------------------------------------------------------- #
#  Token rendering                                                            #
# --------------------------------------------------------------------------- #


def _is_word(s: str) -> bool:
    return bool(s) and (s[0].isalnum() or s[0] == "_")


def _render_tokens(tokens: List[Token]) -> str:
    """Render a token list back to source with reasonable spacing."""

    out: List[str] = []
    binary_ops = {"+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                  "&&", "||", "&", "|", "^", "<<", ">>",
                  "+=", "-=", "*=", "/=", "%=", "=", ":=",
                  "&=", "|=", "^=", "<<=", ">>=", "&^", "&^="}
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


# --------------------------------------------------------------------------- #
#  Body recursion / chunk dispatch                                            #
# --------------------------------------------------------------------------- #


def _convert_body(tokens: List[Token], indent: int = 1, ctx: Optional[str] = None) -> str:
    """Convert a brace-delimited body (without the outer braces)."""

    inner_chunks = _segment_chunks(tokens)
    pieces: List[str] = []
    pad = "    " * indent
    for ch in inner_chunks:
        if not ch:
            continue
        if ctx == "struct":
            line = _convert_struct_field(ch)
        elif ctx == "iface":
            line = _convert_interface_member(ch)
        elif ctx == "const_group":
            line = _convert_const_group_line(ch)
        elif ctx == "var_group":
            line = _convert_var_group_line(ch)
        else:
            line = _convert_chunk(ch)
        if line is None:
            line = "// go2cj: unrecognised // " + _render_tokens(ch)
        for ln in line.split("\n"):
            pieces.append(pad + ln if ln else ln)
    return "\n".join(pieces)


def _convert_chunk(chunk: List[Token]) -> Optional[str]:
    """Convert a single top-level chunk via SOM retrieval + slot binding."""

    if not chunk:
        return ""
    engine = _Engine.get()
    chunk_emb = embed_sequence(chunk)
    som_candidates = {i for i, _ in engine.som.query(chunk_emb, k=8)}

    best: Optional[Tuple[Pattern, dict, float]] = None
    for idx in range(len(engine.patterns)):
        pat = engine.patterns[idx]
        pat_tokens = engine.pattern_token_lists[idx]
        result = _bind_slots(chunk, pat_tokens)
        if result is None:
            continue
        bindings, anchor_score = result
        # Reject obvious mis-binds where a NAME slot ate a control-flow
        # keyword.
        if "NAME" in bindings:
            first = bindings["NAME"][0] if bindings["NAME"] else None
            if first is not None and first.kind == "KEYWORD":
                continue
            # A bare NAME slot must not contain a comma — that's a
            # multi-name declaration and should be routed to a different
            # pattern (``short_decl_multi``).
            if any(t.value == "," for t in bindings["NAME"]):
                continue
        # NAMES slot must actually contain a comma (multi-name destructure).
        if "NAMES" in bindings:
            if not any(t.value == "," for t in bindings["NAMES"]):
                continue
        if "LHS" in bindings:
            first = bindings["LHS"][0] if bindings["LHS"] else None
            if first is not None and first.kind == "KEYWORD" and first.value not in (
                "this", "true", "false", "iota",
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
    return _emit(pat, bindings)


# --------------------------------------------------------------------------- #
#  Pattern emission                                                           #
# --------------------------------------------------------------------------- #
_STRUCT_FIELDS: dict = {}   # struct_name -> [(field_name, cj_type)]
_METHOD_RECEIVERS: dict = {}  # method_name -> set(receiver_type)


def _is_body_slot(slot: str) -> bool:
    if slot in ("BODY", "A", "B", "B1", "B2", "B3", "B4"):
        return True
    return False


def _emit(pat: Pattern, bindings: dict) -> str:
    """Materialise the Cangjie template given resolved slot bindings."""

    out = pat.cj_template

    # Special-case: struct body becomes a class with fields + init.
    if pat.name == "struct_decl":
        name_text = _convert_expr(bindings.get("NAME", [])).strip()
        fields = _parse_struct_fields(bindings.get("BODY", []))
        _STRUCT_FIELDS[name_text] = fields
        return _emit_class_from_struct(name_text, fields)

    if pat.name == "interface_decl":
        name_text = _convert_expr(bindings.get("NAME", [])).strip()
        body_text = _convert_body(bindings.get("BODY", []), indent=1, ctx="iface")
        return f"interface {name_text} {{\n{body_text}\n}}"

    if pat.name == "switch_block":
        return _emit_switch(bindings.get("EXPR", []), bindings.get("BODY", []))
    if pat.name == "switch_no_expr":
        return _emit_switch_no_expr(bindings.get("BODY", []))

    if pat.name == "const_group":
        body_text = _convert_body(bindings.get("BODY", []), indent=0, ctx="const_group")
        return body_text
    if pat.name == "var_group":
        body_text = _convert_body(bindings.get("BODY", []), indent=0, ctx="var_group")
        return body_text

    if pat.name in ("method_decl_ret", "method_decl_noret", "method_decl_multi_ret"):
        return _emit_method(pat, bindings)

    if pat.name == "fmt_sprintf_assign":
        # ``name := fmt.Sprintf("…", a)`` → already lowered by
        # ``_rewrite_printf_calls``; this pattern shouldn't normally fire
        # but if it does, fall back to a simple assign.
        name = _convert_expr(bindings.get("NAME", [])).strip()
        expr = _convert_expr(bindings.get("EXPR", []))
        return f"let {name} = {expr}"

    if pat.name in ("type_def", "type_alias"):
        name = _convert_expr(bindings.get("NAME", [])).strip()
        ty = _convert_type(bindings.get("TY", []))
        return f"type {name} = {ty}"

    if pat.name == "func_decl_multi_ret":
        return _emit_func_multi_ret(bindings)

    # Slot substitution loop.
    iface_like = pat.name == "interface_decl"
    if iface_like:
        ctx = "iface"
    elif pat.name == "struct_decl":
        ctx = "struct"
    else:
        ctx = None

    for slot in pat.slots:
        if slot not in bindings:
            continue
        tokens = bindings[slot]
        if _is_body_slot(slot):
            body_text = _convert_body(tokens, indent=1, ctx=ctx)
            out = out.replace(f"${slot}", body_text)
        elif slot == "PARAMS":
            out = out.replace(f"${slot}", _convert_params(tokens))
        elif slot in ("RET", "TY"):
            out = out.replace(f"${slot}", _convert_type(tokens))
        elif slot == "RETS":
            out = out.replace(f"${slot}", _convert_returns(tokens))
        elif slot == "RECV":
            out = out.replace(f"${slot}", _convert_receiver(tokens))
        elif slot == "NAMES":
            # Multiple LHS for ``a, b := expr``.
            names = ", ".join(t.value for t in tokens if t.value not in (",",))
            out = out.replace(f"${slot}", names)
        elif slot == "COND":
            out = out.replace(f"${slot}", _convert_expr(tokens))
        elif slot == "DEFAULT":
            pass  # handled below
        else:
            out = out.replace(f"${slot}", _convert_expr(tokens))

    # Inject default value for uninitialised typed var pattern.
    if pat.name == "var_typed" and "TY" in bindings:
        ty_text = _convert_type(bindings["TY"]).strip()
        out = out.replace("$DEFAULT", _default_value_for(ty_text))

    return out


def _convert_receiver(tokens: List[Token]) -> str:
    """Convert a Go method receiver ``r T`` or ``r *T`` to a Cangjie
    leading parameter ``r: T``.  Pointers are dropped: Cangjie has no
    explicit address-of."""

    text = _render_tokens(tokens).strip()
    # Strip a leading ``*`` on the type.
    m = re.match(r"^([A-Za-z_]\w*)\s+\*?\s*([A-Za-z_]\w*)$", text)
    if m:
        return f"{m.group(1)}: {m.group(2)}"
    return text


def _emit_method(pat: Pattern, bindings: dict) -> str:
    """Emit a Go method as a Cangjie free function.

    The receiver is prepended to the parameter list.  We also record the
    receiver type so a later post-process step can group methods by
    receiver into class methods.
    """

    name = _convert_expr(bindings.get("NAME", [])).strip()
    recv = _convert_receiver(bindings.get("RECV", []))
    params = _convert_params(bindings.get("PARAMS", []))
    body = _convert_body(bindings.get("BODY", []), indent=1)
    if "RET" in bindings:
        ret = _convert_type(bindings["RET"])
    elif "RETS" in bindings:
        ret = "(" + _convert_returns(bindings["RETS"]) + ")"
    else:
        ret = "Unit"

    # Extract receiver type for later grouping.
    m = re.match(r"^([A-Za-z_]\w*)\s*:\s*([A-Za-z_]\w*)", recv)
    if m:
        _METHOD_RECEIVERS.setdefault(name, set()).add(m.group(2))

    full_params = recv + (", " + params if params else "")
    return f"func {name}({full_params}): {ret} {{\n{body}\n}}"


def _emit_func_multi_ret(bindings: dict) -> str:
    name = _convert_expr(bindings.get("NAME", [])).strip()
    params = _convert_params(bindings.get("PARAMS", []))
    rets = _convert_returns(bindings.get("RETS", []))
    body = _convert_body(bindings.get("BODY", []), indent=1)
    return f"func {name}({params}): ({rets}) {{\n{body}\n}}"


def _parse_struct_fields(tokens: List[Token]) -> List[Tuple[str, str]]:
    """Parse a Go struct body into ``[(field_name, cj_type), ...]``.

    Each field is ``Name Type`` or ``Name1, Name2 Type``.  We split by
    semicolons (already inserted by :func:`_inject_semis`) or by newlines
    if the body straddled lines.
    """

    chunks = _segment_chunks(tokens)
    out: List[Tuple[str, str]] = []
    for ch in chunks:
        text = _render_tokens(ch).strip()
        if not text:
            continue
        # Strip embedded struct tags (the backtick segment is now a
        # Cangjie string literal — drop it).
        text = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"$', "", text).strip()
        # Skip embedded interface methods (parens form) — TODO.
        parts = text.split(None, 1)
        if len(parts) < 2:
            # Embedded field (anonymous) — fold into a field with same
            # type name.
            ty = _convert_type_text(parts[0])
            out.append((parts[0], ty))
            continue
        names_part, ty_part = parts
        # Multiple comma-separated names.
        for nm in [s.strip() for s in names_part.split(",") if s.strip()]:
            out.append((nm, _convert_type_text(ty_part.strip())))
    return out


def _emit_class_from_struct(name: str, fields: List[Tuple[str, str]]) -> str:
    """Render a Go struct as an ``open class`` with var fields and a
    Cangjie ``init(...)`` accepting one positional arg per field."""

    if not fields:
        return f"open class {name} {{\n    public init() {{}}\n}}"
    field_decls = "\n".join(f"    public var {fn}: {ft}" for fn, ft in fields)
    init_params = ", ".join(f"{fn}: {ft}" for fn, ft in fields)
    init_body = "\n".join(f"        this.{fn} = {fn}" for fn, _ in fields)
    return (
        f"open class {name} {{\n"
        f"{field_decls}\n"
        f"    public init({init_params}) {{\n{init_body}\n    }}\n"
        f"}}"
    )


def _convert_struct_field(chunk: List[Token]) -> str:
    """One field inside a struct body.  Kept for legacy callers; the
    real path is :func:`_parse_struct_fields`."""

    text = _render_tokens(chunk).strip()
    return "// " + text


def _convert_interface_member(chunk: List[Token]) -> str:
    """One method signature inside an interface body."""

    text = _render_tokens(chunk).strip()
    # Skip embedded interfaces (just a type name) for now.
    m = re.match(r"^([A-Za-z_]\w*)\s*\((.*?)\)\s*(\(.*\))?\s*([^()]*)?$", text)
    if not m:
        return "// go2cj: iface " + text
    name = m.group(1)
    params = m.group(2) or ""
    multi_ret = m.group(3) or ""
    single_ret = (m.group(4) or "").strip()
    cj_params = _convert_params_text(params)
    if multi_ret:
        inner = multi_ret.strip()[1:-1]
        ret = "(" + _convert_returns_text(inner) + ")"
    elif single_ret:
        ret = _convert_type_text(single_ret)
    else:
        ret = "Unit"
    return f"func {name}({cj_params}): {ret}"


def _convert_const_group_line(chunk: List[Token]) -> str:
    text = _render_tokens(chunk).strip()
    if not text:
        return ""
    # Forms: ``NAME = EXPR``, ``NAME TY = EXPR``, or just ``NAME`` (iota).
    m = re.match(r"^([A-Za-z_]\w*)\s*(?:([A-Za-z_]\w*(?:\[[^\]]*\])?))?\s*=\s*(.+)$", text)
    if m:
        name, ty, expr = m.group(1), m.group(2), m.group(3)
        cj_expr = _convert_expr_text(expr)
        if ty:
            return f"let {name}: {_convert_type_text(ty)} = {cj_expr}"
        return f"let {name} = {cj_expr}"
    # ``NAME`` alone (continues previous iota).  Cangjie has no iota.
    m = re.match(r"^([A-Za-z_]\w*)\s*$", text)
    if m:
        return f"let {m.group(1)} = 0  /* go2cj: iota continuation */"
    return "// go2cj: const " + text


def _convert_var_group_line(chunk: List[Token]) -> str:
    text = _render_tokens(chunk).strip()
    if not text:
        return ""
    m = re.match(r"^([A-Za-z_]\w*)\s+([A-Za-z_]\w*(?:\[[^\]]*\])?)\s*=\s*(.+)$", text)
    if m:
        name, ty, expr = m.group(1), m.group(2), m.group(3)
        return f"var {name}: {_convert_type_text(ty)} = {_convert_expr_text(expr)}"
    m = re.match(r"^([A-Za-z_]\w*)\s+([A-Za-z_]\w*(?:\[[^\]]*\])?)\s*$", text)
    if m:
        name, ty = m.group(1), m.group(2)
        ty_cj = _convert_type_text(ty)
        return f"var {name}: {ty_cj} = {_default_value_for(ty_cj)}"
    m = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", text)
    if m:
        return f"var {m.group(1)} = {_convert_expr_text(m.group(2))}"
    return "// go2cj: var " + text


# --------------------------------------------------------------------------- #
#  Switch handling                                                            #
# --------------------------------------------------------------------------- #


def _emit_switch(expr_tokens: List[Token], body_tokens: List[Token]) -> str:
    expr = _convert_expr(expr_tokens)
    cases = _split_switch_cases(body_tokens)
    if not cases:
        return f"match ({expr}) {{\n    case _ => ()\n}}"
    lines = [f"match ({expr}) {{"]
    has_default = False
    for labels, body in cases:
        body_text = _convert_body(body, indent=2)
        if labels is None:
            has_default = True
            lines.append("    case _ =>")
        else:
            lab = " | ".join(_convert_expr_text(l) for l in labels)
            lines.append(f"    case {lab} =>")
        if not body_text.strip():
            lines.append("        ()")
        else:
            lines.append(body_text)
    if not has_default:
        lines.append("    case _ => ()")
    lines.append("}")
    return "\n".join(lines)


def _emit_switch_no_expr(body_tokens: List[Token]) -> str:
    """``switch { case cond1: ...; case cond2: ...; default: ... }`` →
    an if/else-if chain in Cangjie."""

    cases = _split_switch_cases(body_tokens)
    if not cases:
        return "// go2cj: empty switch"
    parts: List[str] = []
    for i, (labels, body) in enumerate(cases):
        body_text = _convert_body(body, indent=1)
        if labels is None:
            parts.append(f"else {{\n{body_text}\n}}")
        else:
            cond = " || ".join(f"({_convert_expr_text(l)})" for l in labels)
            kw = "if" if i == 0 else "else if"
            parts.append(f"{kw} ({cond}) {{\n{body_text}\n}}")
    return " ".join(parts)


def _split_switch_cases(tokens: List[Token]) -> List[Tuple[Optional[List[str]], List[Token]]]:
    """Walk a switch body and group into ``(labels, body_tokens)`` pairs.

    ``labels`` is ``None`` for ``default``; otherwise it's the list of
    raw label strings (rendered as text, fall-through merge via ``|``).
    """

    cases: List[Tuple[Optional[List[str]], List[Token]]] = []
    cur_labels: Optional[List[str]] = None
    cur_body: List[Token] = []
    i, n = 0, len(tokens)
    brace = 0

    def flush():
        nonlocal cur_labels, cur_body
        if cur_labels is not None or cur_body:
            # Strip trailing ``break`` from body.
            while (cur_body and cur_body[-1].kind == "PUNCT" and cur_body[-1].value == ";"):
                cur_body.pop()
            if cur_body and cur_body[-1].kind == "KEYWORD" and cur_body[-1].value == "break":
                cur_body.pop()
            cases.append((cur_labels, list(cur_body)))
        cur_labels = None
        cur_body = []

    while i < n:
        t = tokens[i]
        if t.kind == "PUNCT" and t.value == "{":
            brace += 1
            cur_body.append(t)
            i += 1
            continue
        if t.kind == "PUNCT" and t.value == "}":
            brace -= 1
            cur_body.append(t)
            i += 1
            continue
        if brace == 0 and t.kind == "KEYWORD" and t.value == "case":
            flush()
            i += 1
            lab_buf: List[Token] = []
            depth = 0
            while i < n:
                tt = tokens[i]
                if tt.kind == "PUNCT" and tt.value == ":" and depth == 0:
                    i += 1
                    break
                if tt.value in "([{":
                    depth += 1
                elif tt.value in ")]}":
                    depth -= 1
                lab_buf.append(tt)
                i += 1
            # Split by top-level commas to allow multi-label cases.
            labels: List[str] = []
            cur_l: List[Token] = []
            d = 0
            for tt in lab_buf:
                if tt.value == "," and d == 0:
                    labels.append(_render_tokens(cur_l).strip())
                    cur_l = []
                    continue
                if tt.value in "([{":
                    d += 1
                elif tt.value in ")]}":
                    d -= 1
                cur_l.append(tt)
            if cur_l:
                labels.append(_render_tokens(cur_l).strip())
            cur_labels = labels
            cur_body = []
            continue
        if brace == 0 and t.kind == "KEYWORD" and t.value == "default":
            flush()
            i += 1
            if i < n and tokens[i].kind == "PUNCT" and tokens[i].value == ":":
                i += 1
            cur_labels = None  # sentinel: re-use None for default; flush
            cur_labels = []  # marker: empty list will be turned into None below
            cur_body = []
            # Tag as default by using marker; we'll switch to None on flush.
            # Re-purpose: keep an explicit sentinel.
            cur_labels = ["__DEFAULT__"]
            continue
        cur_body.append(t)
        i += 1
    flush()

    # Normalise the default sentinel.
    out: List[Tuple[Optional[List[str]], List[Token]]] = []
    for labels, body in cases:
        if labels == ["__DEFAULT__"]:
            out.append((None, body))
        else:
            out.append((labels, body))
    return out


# --------------------------------------------------------------------------- #
#  Expressions, params, types                                                 #
# --------------------------------------------------------------------------- #


def _strip_trailing_semicolon(tokens: List[Token]) -> List[Token]:
    if tokens and tokens[-1].kind == "PUNCT" and tokens[-1].value == ";":
        return tokens[:-1]
    return tokens


def _convert_expr(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_expr_text(text)


_COMPOSITE_LITERAL_RE = re.compile(r"\[\s*\]\s*([A-Za-z_]\w*(?:\.\w+)?)\s*\{")
_MAP_LITERAL_RE = re.compile(r"\bmap\s*\[\s*([^\]]+?)\s*\]\s*([A-Za-z_]\w*(?:\.\w+)?(?:\[[^\]]*\])?)\s*\{")
_MAKE_SLICE_RE = re.compile(r"\bmake\s*\(\s*\[\s*\]\s*([^,)]+?)\s*(?:,[^)]+)?\)")
_MAKE_MAP_RE = re.compile(r"\bmake\s*\(\s*map\s*\[\s*([^\]]+?)\s*\]\s*([^,)]+?)\s*(?:,[^)]+)?\)")
_NEW_STRUCT_RE = re.compile(r"\b([A-Z]\w*)\s*\{")
_NEW_PTR_RE = re.compile(r"\bnew\s*\(\s*([A-Za-z_]\w*)\s*\)")
_TYPE_CAST_RE = re.compile(
    r"\b(int8|int16|int32|int64|int|uint8|uint16|uint32|uint64|uint|uintptr|"
    r"byte|rune|float32|float64|bool|string)\s*\(([^()]*)\)"
)


def _convert_expr_text(text: str) -> str:
    if not text:
        return ""
    # ``& foo`` → drop address-of, ``* foo`` → drop deref (best-effort).
    text = re.sub(r"(?<!&)&\s*([A-Za-z_])", r"\1", text)
    # Pointer dereference at expr position: ``*p`` → ``p``.  Be careful
    # with multiplication: only rewrite when ``*`` is at the start of the
    # token or immediately follows ``(`` / ``,`` / ``=`` / ``return``.
    text = re.sub(r"(^|[(,=]|return\s)\*\s*([A-Za-z_])", r"\1\2", text)

    # ``make([]T, n)`` → ``ArrayList<T>()`` (best-effort; we drop the
    # size).
    text = _MAKE_SLICE_RE.sub(
        lambda m: f"ArrayList<{_convert_type_text(m.group(1).strip())}>()", text
    )
    # ``make(map[K]V)`` → ``HashMap<K, V>()``.
    text = _MAKE_MAP_RE.sub(
        lambda m: f"HashMap<{_convert_type_text(m.group(1).strip())}, "
                  f"{_convert_type_text(m.group(2).strip())}>()", text
    )
    # ``new(T)`` → ``T()``.
    text = _NEW_PTR_RE.sub(r"\1()", text)

    # ``[]T{a, b}`` → ``ArrayList<T>([a, b])``.
    def repl_slice_lit(m: re.Match) -> str:
        ty = _convert_type_text(m.group(1))
        # We need to find the matching ``}``.  Reconstruct here is hard;
        # the post-regex pass below handles it more carefully.
        return f"ArrayList<{ty}>(["
    text = _COMPOSITE_LITERAL_RE.sub(repl_slice_lit, text)
    # Convert dangling ``}`` from the slice literal opener back to ``])``.
    text = _close_array_list_literal(text)

    # ``map[K]V{…}`` → ``{ let __m = HashMap<K, V>(); __m[…]=…; __m }``
    # Simpler: emit a HashMap constructor with no entries — populate
    # via post-pass.  We at least replace the type.
    def repl_map_lit(m: re.Match) -> str:
        k = _convert_type_text(m.group(1))
        v = _convert_type_text(m.group(2))
        return f"HashMap<{k}, {v}>({{=>"
    text = _MAP_LITERAL_RE.sub(repl_map_lit, text)
    text = _close_hashmap_literal(text)

    # ``int(x)`` / ``string(x)`` etc — Cangjie has ``Int64(x)`` style.
    text = _TYPE_CAST_RE.sub(lambda m: f"{_PRIMITIVE_MAP[m.group(1)]}({m.group(2)})", text)

    # Composite literal for a struct ``Foo{a, b}`` → ``Foo(a, b)`` (only
    # for type names starting with an uppercase letter — Go's exported
    # naming).  We must avoid clobbering map/slice literals (already
    # rewritten above) and ``case Foo:``.
    text = _rewrite_struct_literal(text)

    # ``len(x)`` already rewritten to ``(x).size`` in pre-pass.
    # ``append(xs, v)`` rewritten to ``xs.add(v)`` in pre-pass.

    # ``Println(a, b)`` style fmt args already handled.

    return text.strip()


def _close_array_list_literal(text: str) -> str:
    """After ``_COMPOSITE_LITERAL_RE`` we have ``ArrayList<T>([`` but a
    dangling ``}``; walk to the matching brace and replace with ``])``."""

    out: List[str] = []
    i, n = 0, len(text)
    while i < n:
        # Look for the marker.
        if text[i:i + 2] == "([" and i > 0 and text[i - 1] == ">":
            # Already converted opener at i; find matching ``}`` ahead.
            depth = 0
            j = i + 2
            # We need to find the next top-level ``}`` (which was the
            # closing brace of the original ``{…}``).
            while j < n:
                if text[j] in "([{":
                    depth += 1
                elif text[j] == "]":
                    depth = max(depth - 1, 0)
                elif text[j] == ")":
                    depth = max(depth - 1, 0)
                elif text[j] == "}" and depth == 0:
                    # Replace with ``])``.
                    out.append(text[i:j])
                    out.append("])")
                    i = j + 1
                    break
                j += 1
            else:
                out.append(text[i:])
                return "".join(out)
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _close_hashmap_literal(text: str) -> str:
    """Close the marker we left after ``_MAP_LITERAL_RE`` (``({{=>``)."""

    marker = "({{=>"
    out: List[str] = []
    i, n = 0, len(text)
    while i < n:
        idx = text.find(marker, i)
        if idx == -1:
            out.append(text[i:])
            break
        out.append(text[i:idx])
        # Find matching closing ``}``.
        j = idx + len(marker)
        depth = 0
        while j < n:
            if text[j] in "([{":
                depth += 1
            elif text[j] in ")]":
                depth = max(depth - 1, 0)
            elif text[j] == "}" and depth == 0:
                break
            j += 1
        inner = text[idx + len(marker):j].strip()
        # Map literal entries are ``key: value`` pairs separated by ``,``.
        # Cangjie has no map literal in 1.0.5: we lower to constructor + adds
        # wrapped in an IIFE-like expression isn't natural.  Simpler: emit
        # a constructor with no entries plus an inline comment.
        constructor_close = ")"
        if inner:
            out.append("/* go2cj: map literal — populate below */ ")
            out.append(constructor_close)
            # Append the populating block after the expression as a
            # following statement is messy; instead inline as comma-joined
            # ``__m.add(k, v); ...`` via a block expression.  For now we
            # emit the entries as a side-effect comment so the file still
            # compiles when the map is constructed empty.
            entries = []
            for pair in _split_top_level_text(inner, ","):
                p = pair.strip()
                if not p:
                    continue
                kv = _split_top_level_text(p, ":")
                if len(kv) == 2:
                    entries.append(f"// .add({kv[0].strip()}, {kv[1].strip()})")
            if entries:
                out.append("\n" + "\n".join(entries))
        else:
            out.append(constructor_close)
        i = j + 1
    return "".join(out)


def _rewrite_struct_literal(text: str) -> str:
    """Rewrite ``Foo{a, b}`` to ``Foo(a, b)`` for known struct types.

    We only act when *all* of the following hold:
    * the name precedes ``{`` (no space allowed for ``case`` labels);
    * the name starts with an uppercase letter (Go-exported);
    * we've registered it in :data:`_STRUCT_FIELDS` *or* it is a bare
      identifier without an enclosing ``case ... :`` context.

    Heuristic-only: false positives in non-trivial code stay TODO-able.
    """

    out: List[str] = []
    i, n = 0, len(text)
    while i < n:
        m = re.match(r"([A-Z]\w*)\s*\{", text[i:])
        if m and (i == 0 or not text[i - 1].isalnum() and text[i - 1] != "."):
            name = m.group(1)
            # Find matching brace.
            depth = 0
            j = i + len(m.group(0)) - 1  # index of ``{``
            k = j + 1
            saw_kv = False
            while k < n:
                if text[k] == "{":
                    depth += 1
                elif text[k] == "}":
                    if depth == 0:
                        break
                    depth -= 1
                elif text[k] == ":" and depth == 0:
                    saw_kv = True
                k += 1
            if k >= n:
                out.append(text[i:])
                break
            inner = text[j + 1:k]
            if saw_kv:
                # Named-field literal: ``Point{X: 1, Y: 2}``.  Cangjie's
                # constructor uses positional args, so map labels back
                # to the struct's declared field order.
                kv_pairs = []
                for part in _split_top_level_text(inner, ","):
                    p = part.strip()
                    if not p:
                        continue
                    kv = _split_top_level_text(p, ":")
                    if len(kv) == 2:
                        kv_pairs.append((kv[0].strip(), kv[1].strip()))
                    else:
                        kv_pairs.append((None, p))
                fields = _STRUCT_FIELDS.get(name)
                if fields and all(k is not None for k, _ in kv_pairs):
                    by_name = dict(kv_pairs)
                    args = ", ".join(
                        by_name.get(fn, _default_value_for(ft))
                        for fn, ft in fields
                    )
                else:
                    args = ", ".join(
                        v if k is None else f"{k}: {v}" for k, v in kv_pairs
                    )
            else:
                args = inner.strip()
            out.append(f"{name}({args})")
            i = k + 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _convert_params(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_params_text(text)


def _convert_params_text(text: str) -> str:
    """Convert a Go parameter list to Cangjie form.

    Go allows shared type for trailing names: ``a, b int`` → both are int.
    We process groups by walking commas and looking for the last name
    in each group that has a type.
    """

    text = text.strip()
    if not text:
        return ""
    parts = _split_top_level_text(text, ",")
    # Walk right-to-left: each part whose type can be parsed sets the
    # type for any preceding name-only parts.
    out: List[Tuple[str, str]] = []
    pending_names: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Try ``name type`` — type may begin with ``[``, ``*``, ``map``,
        # or an identifier (no space required after the name).
        m = re.match(r"^([A-Za-z_]\w*)(\s+|(?=[\[*]))(.+)$", p)
        if m:
            name, ty = m.group(1), m.group(3).strip()
            ty_cj = _convert_type_text(ty)
            for nm in pending_names:
                out.append((nm, ty_cj))
            out.append((name, ty_cj))
            pending_names = []
        else:
            pending_names.append(p)
    # Any pending names with no type at all default to Any.
    for nm in pending_names:
        out.append((nm, "Any"))
    return ", ".join(f"{nm}: {ty}" for nm, ty in out)


def _convert_returns(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_returns_text(text)


def _convert_returns_text(text: str) -> str:
    """Convert a Go multi-return type list to a Cangjie tuple element list.

    Handles bare types ``(int, string)`` and named-return ``(n int, err error)``.
    """

    text = text.strip()
    if not text:
        return ""
    parts = _split_top_level_text(text, ",")
    out: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        m = re.match(r"^[A-Za-z_]\w*\s+(.+)$", p)
        if m:
            out.append(_convert_type_text(m.group(1).strip()))
        else:
            out.append(_convert_type_text(p))
    return ", ".join(out)


def _convert_type(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_type_text(text)


def _convert_type_text(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "Any"
    # Strip leading ``*`` (pointer).
    while text.startswith("*"):
        text = text[1:].strip()
    # ``[]T`` → ``ArrayList<T>``.
    if text.startswith("[]"):
        return f"ArrayList<{_convert_type_text(text[2:].strip())}>"
    # ``[N]T`` (fixed array) → ``Array<T>``.
    m = re.match(r"^\[\s*\d+\s*\]\s*(.+)$", text)
    if m:
        return f"Array<{_convert_type_text(m.group(1).strip())}>"
    # ``map[K]V`` → ``HashMap<K, V>``.
    m = re.match(r"^map\s*\[\s*([^\]]+?)\s*\]\s*(.+)$", text)
    if m:
        return f"HashMap<{_convert_type_text(m.group(1).strip())}, "\
               f"{_convert_type_text(m.group(2).strip())}>"
    # ``chan T`` — Cangjie doesn't have channels; leave a placeholder.
    if text.startswith("chan "):
        return f"/* go2cj: chan */ Any"
    # ``func(...) ...`` → leave as ``Any`` (best-effort).
    if text.startswith("func"):
        return "Any  /* go2cj: function type */"
    # ``interface{}`` → ``Any``.
    if text in ("interface{}", "interface { }"):
        return "Any"
    # Apply primitive renames at word boundaries.
    return _apply_primitive_types(text)


def _default_value_for(ty: str) -> str:
    """Cangjie default value literal for ``ty``."""

    ty = ty.strip()
    if ty.startswith("?"):
        return "None"
    if ty.startswith("ArrayList<"):
        return f"{ty}()"
    if ty.startswith("HashMap<") or ty.startswith("HashSet<"):
        return f"{ty}()"
    if ty.startswith("Array<"):
        inner = ty[len("Array<"):-1]
        return f"Array<{inner}>()"
    return {
        "Int64": "0", "Int32": "0", "Int16": "0", "Int8": "0",
        "UInt64": "0", "UInt32": "0", "UInt16": "0", "UInt8": "0",
        "Float64": "0.0", "Float32": "0.0",
        "Bool": "false", "String": "\"\"",
        "Rune": "r' '",
    }.get(ty, f"{ty}()")


# --------------------------------------------------------------------------- #
#  Top-level driver                                                           #
# --------------------------------------------------------------------------- #
_NEEDS_COLLECTION = re.compile(r"\b(ArrayList|HashMap|HashSet|Array)\b")


def convert_source(go_source: str, wrap_main: bool = True) -> ConversionResult:
    """Convert a Go source string into Cangjie source.

    Parameters
    ----------
    go_source:
        Full Go source code (single file).
    wrap_main:
        If ``True`` and the source has no ``main`` definition, wrap
        free top-level statements in a ``main()`` entry.
    """

    rewritten, notes = _rewrite_token_stream(go_source)
    tokens = tokenize(rewritten)
    tokens = _inject_semis(tokens)

    _STRUCT_FIELDS.clear()
    _METHOD_RECEIVERS.clear()

    chunks = _segment_chunks(tokens)
    result = ConversionResult(source="", notes=notes)
    # Count only chunks that actually participate in conversion — drop
    # ``package`` / ``import`` housekeeping from the denominator.
    counted = [c for c in chunks if c and not (
        c[0].kind == "KEYWORD" and c[0].value in ("package", "import")
    )]
    result.chunks = len(counted)

    rendered_chunks: List[str] = []
    has_user_main = False
    top_level_decls: List[str] = []
    main_body: List[str] = []
    has_package_main = False

    for ch in chunks:
        if not ch:
            continue
        # Drop top-level ``package …`` (Cangjie has no equivalent at the
        # single-file level).
        if ch[0].kind == "KEYWORD" and ch[0].value == "package":
            if len(ch) >= 2 and ch[1].value == "main":
                has_package_main = True
            continue
        # Drop ``import "…"`` and ``import ( … )`` — Cangjie's stdlib
        # imports are handled separately.
        if ch[0].kind == "KEYWORD" and ch[0].value == "import":
            continue
        # Detect ``func main() { … }``.
        if (len(ch) >= 3 and ch[0].kind == "KEYWORD" and ch[0].value == "func"
                and ch[1].value == "main" and ch[2].value == "("):
            has_user_main = True

        cj = _convert_chunk(ch)
        if cj is None:
            result.fallback_chunks += 1
            cj = "/* go2cj: TODO unrecognised chunk */ // " + _render_tokens(ch)
        else:
            result.confident_chunks += 1
        rendered_chunks.append(cj)

        # Classify for top-level vs main-body placement.
        first = ch[0].value
        if first in ("func", "type", "class", "interface", "enum", "struct",
                     "var", "const"):
            # ``func main`` → wrap to Cangjie main signature.
            if first == "func" and len(ch) >= 2 and ch[1].value == "main":
                cj = re.sub(r"^func\s+main\s*\([^)]*\)\s*(?::\s*[\w()<>,\s]+)?\s*\{",
                            "main() {", cj, count=1)
                if not re.search(r"\breturn\b", cj):
                    cj = cj[:-1].rstrip() + "\n    return 0\n}"
                else:
                    # Ensure a final ``return 0`` if no top-level return.
                    pass
                rendered_chunks[-1] = cj
            top_level_decls.append(cj)
        else:
            main_body.append(cj)

    if has_user_main:
        wrap_main = False

    # Promote struct + methods into class bodies.
    top_level_decls = _promote_methods_into_classes(top_level_decls)
    top_level_decls = _attach_interface_implementations(top_level_decls)

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
    body_text = _polish_output(body_text)

    headers: List[str] = []
    if _NEEDS_COLLECTION.search(body_text):
        headers.append("import std.collection.*")
    header = ("\n".join(headers) + "\n\n") if headers else ""
    result.source = header + body_text + ("\n" if body_text and not body_text.endswith("\n") else "")
    return result


def _promote_methods_into_classes(decls: List[str]) -> List[str]:
    """Move ``func methodName(recv: T, …)`` lines whose receiver type
    matches a previously declared class into that class as a method
    (``public func methodName(…)``).
    """

    # First pass: collect class names and their textual ranges.
    classes: dict = {}  # name -> index in decls
    for i, d in enumerate(decls):
        m = re.match(r"^open class (\w+)\s*\{", d)
        if m:
            classes[m.group(1)] = i

    if not classes:
        return decls

    method_re = re.compile(
        r"^func (\w+)\(([^,)]*?):\s*(\w+)((?:,\s*[^)]*)?)\):\s*([^{]+)\{(.*)$",
        re.DOTALL,
    )

    new_decls: List[str] = []
    moved = set()
    for i, d in enumerate(decls):
        m = method_re.match(d)
        if m:
            method_name = m.group(1)
            recv_name = m.group(2).strip()
            recv_type = m.group(3).strip()
            tail_params = m.group(4).strip().lstrip(",").strip()
            ret_type = m.group(5).strip()
            body_and_close = m.group(6)
            if recv_type in classes:
                # Build method text.
                # Body content (everything inside the outer braces of the func).
                # Find the matching closing brace.
                body_inner = body_and_close
                # Strip the final closing brace of the function.
                last_brace = body_inner.rfind("}")
                if last_brace != -1:
                    body_inner = body_inner[:last_brace]
                # Rewrite ``recv_name.`` → ``this.`` so the method reads
                # naturally inside the class.
                if recv_name:
                    body_inner = re.sub(
                        r"\b" + re.escape(recv_name) + r"\b", "this", body_inner
                    )
                method_text = (
                    f"    public func {method_name}({tail_params}): {ret_type.strip()} {{"
                    f"{body_inner}    }}"
                )
                idx = classes[recv_type]
                decls[idx] = decls[idx].rstrip()
                # Insert before the final ``}`` of the class.
                last = decls[idx].rfind("}")
                if last != -1:
                    decls[idx] = decls[idx][:last] + method_text + "\n" + decls[idx][last:]
                moved.add(i)
        new_decls = []
    out: List[str] = []
    for i, d in enumerate(decls):
        if i in moved:
            continue
        out.append(d)
    return out


def _attach_interface_implementations(decls: List[str]) -> List[str]:
    """Add ``<: Interface`` to classes that implement every method of
    a previously declared interface.

    Go uses *structural* (implicit) interface satisfaction; Cangjie
    requires explicit ``<:`` clauses.  We bridge the two by inspecting
    each class body's method signatures, and for every interface whose
    full method set is a subset, we append the interface name to the
    class's super-type list.  Methods inside a class look like
    ``public func Name(...): RetType``; interface methods look like
    ``func Name(...): RetType``.
    """

    iface_re = re.compile(r"^interface (\w+)\s*\{([\s\S]*?)\}", re.MULTILINE)
    class_re = re.compile(
        r"^open class (\w+)((?:\s+<:[^{]*)?)\s*\{([\s\S]*?)\n\}", re.MULTILINE
    )

    def _sigs(body: str, prefix: str) -> List[str]:
        out = []
        for m in re.finditer(
            rf"{prefix}func\s+(\w+)\s*\(([^)]*)\)\s*:\s*([^{{\n]+)", body,
        ):
            name, params, ret = m.group(1), m.group(2), m.group(3).strip()
            # Normalise whitespace.
            params = re.sub(r"\s+", " ", params).strip()
            out.append(f"{name}|{params}|{ret}")
        return out

    interfaces: List[Tuple[str, List[str]]] = []
    full = "\n\n".join(decls)
    for m in iface_re.finditer(full):
        interfaces.append((m.group(1), _sigs(m.group(2), "")))

    if not interfaces:
        return decls

    new_decls = []
    for d in decls:
        cm = class_re.match(d.strip())
        if not cm:
            new_decls.append(d)
            continue
        cname, existing_sup, body = cm.group(1), cm.group(2), cm.group(3)
        class_sigs = set(_sigs(body, "public "))
        implemented = []
        for iname, isigs in interfaces:
            if isigs and all(s in class_sigs for s in isigs):
                implemented.append(iname)
        if not implemented:
            new_decls.append(d)
            continue
        sup = existing_sup.strip()
        if sup:
            sup = sup + ", " + ", ".join(implemented)
        else:
            sup = "<: " + " & ".join(implemented)
        new_decl = d.replace(
            f"open class {cname}{existing_sup} {{",
            f"open class {cname} {sup} {{",
            1,
        )
        # Mark interface-method overrides with ``public override``.
        for iname, isigs in interfaces:
            if iname not in implemented:
                continue
            for sig in isigs:
                mname = sig.split("|", 1)[0]
                new_decl = re.sub(
                    rf"(\n\s*)public func {re.escape(mname)}\b",
                    rf"\1public override func {mname}",
                    new_decl,
                )
        new_decls.append(new_decl)
    return new_decls


_GENERIC_NAMES = (
    "ArrayList", "HashMap", "HashSet", "Array", "Option",
    "Iterator", "List", "Queue", "Stack", "Box",
)


def _tighten_generic_spacing(text: str) -> str:
    """Collapse ``Name < T, U >`` → ``Name<T, U>`` for known generic names.

    Unlike ts2cj, Go has no user-facing generics in our scope and all of
    our emitted generic types (``ArrayList<T>``, ``HashMap<K,V>`` …) are
    constructed by direct string concatenation in :func:`_convert_type_text`
    — so we only need the *opener* normalisation here.  We deliberately
    do **not** run the close-side regex because it would also collapse
    ``x > 5`` (a Go comparison) into ``x> 5``.
    """

    name_alt = "|".join(_GENERIC_NAMES)
    pat_open = re.compile(rf"\b({name_alt})\s+<\s*")
    for _ in range(4):
        new = pat_open.sub(r"\1<", text)
        if new == text:
            break
        text = new
    return text


def _polish_output(text: str) -> str:
    """Final cosmetic polish on emitted Cangjie source."""

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+,", ",", text)
    # Wrap multi-return ``return a, b`` in a tuple literal so it parses.
    def repl_return(m: re.Match) -> str:
        body = m.group(1).strip()
        # Only wrap if the body has a top-level comma and is not already
        # wrapped in parens.
        if body.startswith("(") and body.endswith(")"):
            return m.group(0)
        parts = _split_top_level_text(body, ",")
        if len(parts) >= 2:
            inner = ", ".join(p.strip() for p in parts)
            return f"return ({inner})"
        return m.group(0)
    text = re.sub(r"\breturn\s+([^\n}]+?)(?=\n|$)", repl_return, text)
    return text
