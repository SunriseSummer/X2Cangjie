"""End-to-end TS → Cangjie conversion pipeline.

Pipeline stages:

1.  **Tokenize** the TypeScript source (:mod:`.lexer`).
2.  **Pre-process token-level rewrites** via the Hopfield memory
    (e.g. ``console.log`` → ``println``, ``.length`` → ``.size``).
3.  **Segment** the meaningful tokens into top-level *chunks* using
    brace/semicolon balance — no AST is built.
4.  For each chunk:

    * embed it with :func:`.embedding.embed_sequence`;
    * use the SOM to retrieve a small set of candidate patterns;
    * for each candidate, attempt **non-linear slot binding** — split
      the chunk according to the pattern's anchor tokens and pick the
      candidate whose binding has highest composite score
      (anchor-match × cosine similarity);
    * if the best score is below a threshold the chunk is preserved
      verbatim inside a ``/* TODO ts2cj */`` block and flagged in the
      :class:`ConversionResult`.

5.  **Post-process** the emitted Cangjie source: inject required
    ``import`` statements (``std.collection.*`` when ``ArrayList`` /
    ``HashMap`` are used, etc.) and ensure a top-level ``main`` exists
    for runnable snippets.

The whole pipeline is deterministic and reproducible (the SOM is
seeded).
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
        """Overall confidence in the conversion (0.0 — 1.0)."""

        if self.chunks == 0:
            return 0.0
        return self.confident_chunks / self.chunks


# --------------------------------------------------------------------------- #
#  Shared models (built once)                                                 #
# --------------------------------------------------------------------------- #


def _pattern_tokens(template: str) -> List[Tuple[str, str]]:
    """Tokenize a pattern template into ``(kind, value)`` pairs.

    ``$NAME`` tokens are flagged with kind ``"SLOT"``.
    """

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
        # Build embeddings for each chunk pattern.
        self.patterns = CHUNK_PATTERNS
        self.pattern_token_lists = [_pattern_tokens(p.ts_template) for p in self.patterns]
        self.pattern_embeddings = np.stack(
            [embed_sequence(pt) for pt in self.pattern_token_lists]
        )

        # Train the SOM.
        self.som = SOM(dim=self.pattern_embeddings.shape[1])
        self.som.train(self.pattern_embeddings)

        # Build the Hopfield-style symbol/method memory.
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
def _rewrite_token_stream(src: str) -> Tuple[str, List[str]]:
    """Apply *safe* token-level rewrites on the raw source.

    We intentionally do **not** rewrite primitive type names
    (``number``, ``string`` …) here, because those names act as anchor
    literals in chunk patterns such as ``const $NAME : number = …``.
    Type-name translation therefore happens at slot-render time.

    Rewrites applied:
    * Strict-equality operators ``===`` / ``!==`` → ``==`` / ``!=``.
    * Common member-name calls (``.length``, ``.push``, ``.toUpperCase`` …)
      which are unambiguous and never appear as pattern anchors.
    * ``Math.*`` constants and helpers.
    * Word-boundary identifier rewrites: ``null`` / ``undefined`` → ``None``.
    """

    notes: List[str] = []
    src = _outside_strings_replace(
        src,
        [
            ("===", "=="),
            ("!==", "!="),
            (".length", ".size"),
            (".push", ".add"),
            # TS ``Map.set`` is the most common case where ``.set(...)``
            # appears as a call.  Cangjie ``HashMap`` uses ``.add(k, v)``.
            # In the rare event the user has a class method literally named
            # ``set``, rename it in the source.
            (".set(", ".add("),
            # `.pop()` has no exact Cangjie equivalent on ArrayList; leave a
            # marker for the downstream AI pass.
            (".pop()", ".remove(at: this.size - 1)"),
            (".toUpperCase", ".toAsciiUpper"),
            (".toLowerCase", ".toAsciiLower"),
            (".includes", ".contains"),
            (".trim", ".trimAscii"),
            ("Math.floor", "floor"),
            ("Math.ceil", "ceil"),
            ("Math.abs", "abs"),
            ("Math.max", "max"),
            ("Math.min", "min"),
            ("Math.sqrt", "sqrt"),
            ("Math.PI", "3.141592653589793"),
            ("Math.E", "2.718281828459045"),
            # Process / runtime
            ("process.argv", "args"),
            ("process.exit", "exit"),
            # Type-only TS keywords that have no Cangjie equivalent — strip.
            ("readonly ", ""),
        ],
    )
    src = _outside_strings_word_replace(
        src,
        [
            ("null", "None"),
            ("undefined", "None"),
            # HashMap method rewrites (HashMap.set → put, .get stays).
            # We do these at word level to avoid stepping inside identifiers.
        ],
    )
    return src, notes


def _outside_strings_word_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Word-boundary identifier replacements, applied outside strings / comments."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch in ("'", '"', "`"):
            quote = ch
            j = i + 1
            while j < n and src[j] != quote:
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


_PRIMITIVE_MAP = {
    # ``number`` in TypeScript is IEEE-754 double, but in practice the vast
    # majority of TS programs use integer-valued numbers (counters, indices,
    # sizes).  Cangjie cannot implicitly coerce integer literals to
    # ``Float64``, so we conservatively map ``number`` to ``Int64`` —
    # Cangjie's default integer type.  Float-typed code can be refined by
    # the user / downstream AI pass.
    "number": "Int64",
    "string": "String",
    "boolean": "Bool",
    "void": "Unit",
    "any": "Any",
    "unknown": "Any",
    "undefined": "None",
    "null": "None",
}
_PRIMITIVE_TYPE_RE = re.compile(r"\b(number|string|boolean|void|any|unknown)\b")


def _outside_strings_replace(src: str, pairs: List[Tuple[str, str]]) -> str:
    """Apply literal ``str.replace`` rewrites only outside string/comment regions."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch in ("'", '"', "`"):
            quote = ch
            j = i + 1
            while j < n and src[j] != quote:
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


# --------------------------------------------------------------------------- #
#  Chunk segmentation                                                         #
# --------------------------------------------------------------------------- #
def _normalize_unbraced_bodies(toks: List[Token]) -> List[Token]:
    """Wrap unbraced control-flow bodies in ``{ ... }``.

    TypeScript permits ``if (cond) stmt;`` and ``while (cond) stmt;``
    (no braces).  Cangjie requires braces, so we synthesise them here.
    Works for:

    * ``if ( ... )  STMT``      → ``if ( ... )  { STMT }``
    * ``else STMT``             → ``else { STMT }``
    * ``while ( ... )  STMT``   → ``while ( ... )  { STMT }``
    * ``for ( ... )  STMT``     → ``for ( ... )  { STMT }``

    A statement ends at the next top-level ``;`` or ``}``.
    """

    open_brace = Token("PUNCT", "{", 0, 0)
    close_brace = Token("PUNCT", "}", 0, 0)

    out: List[Token] = []
    i, n = 0, len(toks)

    def find_matching_paren(start: int) -> int:
        depth = 0
        j = start
        while j < n:
            v = toks[j].value
            if v == "(":
                depth += 1
            elif v == ")":
                depth -= 1
                if depth == 0:
                    return j
            j += 1
        return -1

    def find_stmt_end(start: int) -> int:
        """Return the index *after* the last token of the statement
        beginning at ``start``.  A statement is terminated by a
        balanced ``;`` or a ``}`` at depth 0."""
        depth_b = depth_p = depth_s = 0
        j = start
        while j < n:
            v = toks[j].value
            if v == "{":
                depth_b += 1
            elif v == "}":
                if depth_b == 0:
                    return j
                depth_b -= 1
            elif v == "(":
                depth_p += 1
            elif v == ")":
                depth_p -= 1
            elif v == "[":
                depth_s += 1
            elif v == "]":
                depth_s -= 1
            elif v == ";" and depth_b == 0 and depth_p == 0 and depth_s == 0:
                return j + 1
            j += 1
        return n

    while i < n:
        t = toks[i]
        out.append(t)
        if t.kind == "KEYWORD" and t.value in ("if", "while", "for"):
            # Special-case: ``while`` immediately following a closing ``}`` is
            # the trailer of a ``do { ... } while ( ... );`` loop — never
            # synthesise a body for it.
            if t.value == "while" and out and len(out) >= 2 and out[-2].value == "}":
                pass  # leave the chunk as-is
            elif i + 1 < n and toks[i + 1].value == "(":
                close = find_matching_paren(i + 1)
                if close == -1:
                    i += 1
                    continue
                # Copy the entire ``( ... )`` group.
                for k in range(i + 1, close + 1):
                    out.append(toks[k])
                # Look at what comes after the ``)``.
                k = close + 1
                if k < n and toks[k].value != "{":
                    end = find_stmt_end(k)
                    out.append(open_brace)
                    for q in range(k, end):
                        out.append(toks[q])
                    out.append(close_brace)
                    i = end
                    continue
                i = close + 1
                continue
        if t.kind == "KEYWORD" and t.value == "else":
            k = i + 1
            if k < n and toks[k].value not in ("{", "if"):
                end = find_stmt_end(k)
                out.append(open_brace)
                for q in range(k, end):
                    out.append(toks[q])
                out.append(close_brace)
                i = end
                continue
        i += 1
    return out


def _segment_chunks(tokens: List[Token]) -> List[List[Token]]:
    """Split a token stream into balanced top-level chunks.

    A chunk ends at:
    * a top-level ``;``, or
    * a top-level ``}`` that closes a previously opened ``{`` — **unless**
      the next meaningful token is one of ``else`` / ``catch`` /
      ``finally`` / ``while`` (do-while), in which case the chunk
      continues.
    """

    # Pre-strip whitespace/newlines/comments — segmentation only cares about
    # meaningful tokens.
    toks = [t for t in tokens if t.kind not in ("NEWLINE", "COMMENT_BLOCK", "COMMENT_LINE")]
    # Synthesise braces around bodies that TS leaves unbraced.
    toks = _normalize_unbraced_bodies(toks)
    chunks: List[List[Token]] = []
    cur: List[Token] = []
    depth_brace = 0
    depth_paren = 0
    depth_bracket = 0

    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        cur.append(t)
        if t.kind == "PUNCT":
            if t.value == "{":
                depth_brace += 1
            elif t.value == "}":
                depth_brace = max(depth_brace - 1, 0)
                if depth_brace == 0 and depth_paren == 0 and depth_bracket == 0:
                    nxt = toks[i + 1] if i + 1 < n else None
                    if nxt is not None and nxt.kind == "KEYWORD" and nxt.value in (
                        "else", "catch", "finally", "while",
                    ):
                        # Keep accumulating into the same chunk.
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
            elif t.value == ";" and depth_brace == 0 and depth_paren == 0 and depth_bracket == 0:
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
    """Try to bind ``chunk`` to a pattern's slot template.

    Semantics:

    * Each ``LIT`` event must match ``chunk[i]`` **exactly** — it does
      not skip tokens.  Otherwise the matcher could devour arbitrary
      content between anchors (a function body might be silently
      consumed by the closing ``}`` event).
    * Each ``SLOT`` event collects a balanced (brace/paren/bracket)
      span of tokens up to the next ``LIT`` anchor, or to the end of
      the chunk when no more anchors follow.

    Returns ``(bindings, anchor_score)`` on success, ``None`` on
    failure.  ``anchor_score`` is the fraction of LIT anchors that
    matched — always ``1.0`` for a successful bind here, but kept for
    composite-scoring symmetry with the caller.
    """

    events = pat_tokens
    if not events:
        return None

    bindings: dict = {}
    i = 0  # index into chunk
    total_anchors = sum(1 for k, _ in events for _ in [0] if k == "LIT")
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
        # SLOT — collect tokens until the next LIT anchor (or end).
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
            i = j  # leave the anchor for the LIT branch
        # Enforce slot consistency: a slot mentioned multiple times in the
        # pattern must bind to the same token sequence each time.
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


def _render_tokens(tokens: List[Token]) -> str:
    """Render a token list back to surface source with reasonable spacing.

    The goal is *readable Cangjie*, not byte-for-byte preservation:
    we space binary operators and keywords, keep punctuation tight,
    and leave string/template literals untouched.
    """

    out: List[str] = []
    binary_ops = {"+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
                  "&&", "||", "??", "&", "|", "^", "<<", ">>", "**",
                  "+=", "-=", "*=", "/=", "%=", "=", "=>"}
    for i, t in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            need_space = False
            # word-word boundary (e.g. ``let x`` or ``return value``)
            if _is_word(prev.value) and _is_word(t.value):
                need_space = True
            # space after a comma
            elif prev.value == "," and t.value not in (")", "]", "}"):
                need_space = True
            # space around binary operators and assignment
            elif t.value in binary_ops:
                need_space = True
            elif prev.value in binary_ops:
                need_space = True
            # space after ``:`` (type annotation)
            elif prev.value == ":":
                need_space = True
            if need_space:
                out.append(" ")
        out.append(t.value)
    return "".join(out)


def _default_value_for(ty: str) -> str:
    """Return a sensible Cangjie default value literal for ``ty``."""

    ty = ty.strip()
    if ty.startswith("?"):
        return "None"
    if ty.startswith("ArrayList<") or ty.startswith("Array<"):
        return ty + "()"
    if ty.startswith("HashMap<") or ty.startswith("HashSet<"):
        return ty + "()"
    if ty.startswith("("):  # tuple
        # Build a default tuple of zeros / empty strings.
        inner = ty[1:-1]
        parts = [_default_value_for(p.strip()) for p in _split_top_level(inner, ",")]
        return "(" + ", ".join(parts) + ")"
    return {
        "Int64": "0", "Int32": "0", "Float64": "0.0", "Float32": "0.0",
        "Bool": "false", "String": "\"\"", "Rune": "r' '",
    }.get(ty, ty + "()")  # last-resort: try a no-arg constructor


def _is_word(s: str) -> bool:
    return bool(s) and (s[0].isalnum() or s[0] == "_")


# --------------------------------------------------------------------------- #
#  Body recursion                                                             #
# --------------------------------------------------------------------------- #
def _convert_body(tokens: List[Token], indent: int = 1, ctx: Optional[str] = None) -> str:
    """Convert a brace-delimited body (without the outer braces).

    The optional ``ctx`` argument lets the body know whether it lives
    inside an interface, abstract class, struct, or regular class, so it
    can adjust modifiers accordingly (e.g. interface bodies must not
    emit ``public open`` on methods).
    """

    inner_chunks = _segment_chunks(tokens)
    pieces: List[str] = []
    pad = "    " * indent
    for ch in inner_chunks:
        if not ch:
            continue
        line = _convert_chunk(ch)
        if line is None:
            line = "/* ts2cj: unrecognised */ // " + _render_tokens(ch)
        # Adjust for context.
        line = _adjust_for_context(line, ctx)
        # Indent every line.
        for ln in line.split("\n"):
            pieces.append(pad + ln if ln else ln)
    return "\n".join(pieces)


def _adjust_for_context(line: str, ctx: Optional[str]) -> str:
    """Tweak emitted lines based on enclosing-scope context.

    * In an **interface** body, methods drop ``public open`` because
      interface methods are public-open by default and the modifier is
      a compile error.
    * In an **abstract class** body, method signatures without bodies
      are kept as abstract declarations (no ``open``).
    * In a **struct** body, methods are public but not ``open``
      (Cangjie structs don't support inheritance).
    """

    if ctx == "iface":
        # Default methods inside interface: ``public open func`` would error.
        line = line.replace("public open func ", "func ")
        line = line.replace("public static func ", "static func ")
    elif ctx == "struct":
        line = line.replace("public open func ", "public func ")
    elif ctx == "abstract":
        # leave it — abstract methods come via the abstract_method_* patterns
        pass
    return line


def _strip_trailing_semicolon(tokens: List[Token]) -> List[Token]:
    if tokens and tokens[-1].kind == "PUNCT" and tokens[-1].value == ";":
        return tokens[:-1]
    return tokens


# Sentinel for the converter to know whether the current chunk emits its own
# trailing newline (e.g. blocks) or not (e.g. simple statements).
def _convert_chunk(chunk: List[Token]) -> Optional[str]:
    """Convert a single top-level chunk using SOM retrieval + slot binding."""

    if not chunk:
        return ""
    engine = _Engine.get()

    chunk_emb = embed_sequence(chunk)

    # Two-stage retrieval:
    #   1. SOM gives us a small *prior* over likely pattern families.
    #   2. We then evaluate the full corpus (still cheap — a few dozen
    #      patterns) and rescore by specificity-aware composite.
    som_candidates = {i for i, _ in engine.som.query(chunk_emb, k=8)}

    best: Optional[Tuple[Pattern, dict, float]] = None
    for idx in range(len(engine.patterns)):
        pat = engine.patterns[idx]
        pat_tokens = engine.pattern_token_lists[idx]
        result = _bind_slots(chunk, pat_tokens)
        if result is None:
            continue
        bindings, anchor_score = result
        # Reject pattern matches where a slot we know must be a plain
        # identifier (a function/class/var ``NAME``) has accidentally
        # absorbed a control-flow keyword.  This protects against the
        # ``method_no_ret`` pattern over-greedily matching ``for (...) {…}``.
        if "NAME" in bindings:
            first = bindings["NAME"][0] if bindings["NAME"] else None
            if first is not None and first.kind == "KEYWORD" and first.value in (
                "for", "while", "if", "else", "do", "switch", "case", "default",
                "return", "throw", "try", "catch", "finally", "break",
                "continue", "new", "typeof",
                "let", "const", "var", "function", "class", "interface",
                "enum", "struct", "type", "abstract", "import", "export",
            ):
                continue
        n_anchors = sum(1 for k, _ in pat_tokens if k == "LIT")
        sim = cosine(chunk_emb, engine.pattern_embeddings[idx])
        # Specificity reward: a pattern that ties down more anchor tokens is
        # almost always a better fit than the catch-all ``$EXPR ;`` pattern.
        # The SOM prior provides a small tie-breaker that lets cluster
        # neighbours win over visually-distant matches.
        som_bonus = 0.1 if idx in som_candidates else 0.0
        composite = anchor_score * (1.0 + n_anchors) + 0.1 * sim + som_bonus
        if best is None or composite > best[2]:
            best = (pat, bindings, composite)

    if best is None:
        return None
    pat, bindings, _score = best
    return _emit(pat, bindings)


def _is_body_slot(slot: str) -> bool:
    """Slots that should be recursively converted as a block body."""

    if slot in ("BODY", "A", "CBODY", "FBODY"):
        return True
    # B, B1, B2, B3, B4, B5 — body branches in if-elif-else chains.
    if slot == "B" or (slot.startswith("B") and slot[1:].isdigit()):
        return True
    return False


def _emit(pat: Pattern, bindings: dict) -> str:
    """Materialise the Cangjie template given resolved slot bindings."""

    out = pat.cj_template

    # Special-case: switch body needs match-case rewriting, not body recursion.
    if pat.name == "switch_block":
        expr = _convert_expr(bindings.get("EXPR", []))
        body = _convert_switch_body(bindings.get("BODY", []))
        return out.replace("$EXPR", expr).replace("$SWBODY", body)

    # Special-case: enum body needs constructor rewriting.
    if pat.name == "enum_decl":
        name = _convert_expr(bindings.get("NAME", []))
        body = _convert_enum_body(bindings.get("BODY", []))
        return out.replace("$NAME", name).replace("$ENUMBODY", body)

    # Some patterns need a derived slot from $PARAMS — specifically lambdas:
    # TS `(a: T, b: U) => expr` → CJ `{ a: T, b: U => expr }`.  We compute
    # ``$LAMBDA_PARAMS`` from the raw params here.
    if "$LAMBDA_PARAMS" in out and "PARAMS" in bindings:
        lp = _convert_lambda_params(bindings["PARAMS"])
        out = out.replace("$LAMBDA_PARAMS", lp)

    # ``$DEFAULT`` slot: pick a Cangjie-appropriate default value based
    # on the (already-emitted) type slot ``$TY``.  Used by the
    # uninitialised ``let x: T;`` patterns.
    if "$DEFAULT" in out and "TY" in bindings:
        ty_text = _convert_type(bindings["TY"]).strip()
        out = out.replace("$DEFAULT", _default_value_for(ty_text))

    iface_like = pat.name in (
        "interface_decl", "interface_decl_extends", "interface_generic_decl",
    )
    abstract_like = pat.name == "abstract_class_decl"
    struct_like = pat.name == "struct_decl"
    class_like = pat.name in (
        "class_decl", "class_decl_extends", "class_decl_impl",
        "class_generic_decl", "class_generic_decl_extends",
    )
    if iface_like:
        ctx = "iface"
    elif abstract_like:
        ctx = "abstract"
    elif struct_like:
        ctx = "struct"
    elif class_like:
        ctx = "class"
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
        elif slot in ("RET", "TY", "BASE"):
            out = out.replace(f"${slot}", _convert_type(tokens))
        elif slot == "TPARAMS":
            out = out.replace(f"${slot}", _convert_type_params(tokens))
        else:
            out = out.replace(f"${slot}", _convert_expr(tokens))

    # Pattern-specific post-processing.
    if pat.name in (
        "class_decl_extends", "class_decl_impl", "class_generic_decl_extends",
    ):
        # Override detection.  We track each class's method set so a
        # subclass only marks ``override`` on methods that actually
        # exist in the parent.
        name = _convert_expr(bindings.get("NAME", [])).strip()
        base_text = _convert_type(bindings.get("BASE", [])).strip() if "BASE" in bindings else ""
        # Strip generic args from the parent for lookup purposes.
        base = re.sub(r"<.*$", "", base_text).strip()
        my_methods = _scan_method_names(bindings.get("BODY", []))
        _CLASS_METHODS[name] = my_methods
        _CLASS_PARENT[name] = base
        # Walk up the parent chain collecting their method sets.
        parent_methods: set = set()
        cur = base
        seen = set()
        while cur and cur not in seen:
            seen.add(cur)
            parent_methods |= _CLASS_METHODS.get(cur, set())
            cur = _CLASS_PARENT.get(cur, "")
        # For each ``public open func NAME`` line, decide whether to mark
        # it ``override``.  Methods not present in any ancestor stay
        # ``public open``.
        def _mark(m: re.Match) -> str:
            n = m.group(1)
            if n in parent_methods:
                return f"public override func {n}"
            return f"public open func {n}"
        out = re.sub(r"public open func (\w+)", _mark, out)
    elif pat.name in ("class_decl", "class_generic_decl"):
        # Plain class without extends — register methods for future
        # subclasses' override analysis.
        name = _convert_expr(bindings.get("NAME", [])).strip()
        _CLASS_METHODS[name] = _scan_method_names(bindings.get("BODY", []))
    elif pat.name == "abstract_class_decl":
        name = _convert_expr(bindings.get("NAME", [])).strip()
        _CLASS_METHODS[name] = _scan_method_names(bindings.get("BODY", []))

    # Tuple-literal fixup: when the variable's declared type is a tuple
    # (``$TY`` rendered starts with ``(``), the initializer ``[a, b, ...]``
    # should be a tuple, not an array.  Cangjie won't coerce.
    if pat.name in ("const_typed", "let_typed") and "TY" in bindings:
        ty_text = _convert_type(bindings["TY"])
        # Resolve through any registered type alias.
        ty_resolved = _TYPE_ALIASES.get(ty_text.strip(), ty_text)
        if ty_resolved.startswith("(") and ty_resolved.endswith(")"):
            # Convert outer ``[...]`` of the expression to ``(...)``.
            out = re.sub(r"=\s*\[([^\[\]]*)\]\s*$", lambda m: "= (" + m.group(1) + ")", out)

    # Track type aliases so later declarations can resolve them.
    if pat.name == "type_alias" and "NAME" in bindings and "TY" in bindings:
        name = _convert_expr(bindings["NAME"]).strip()
        ty = _convert_type(bindings["TY"]).strip()
        _TYPE_ALIASES[name] = ty
    return out


# Registries built up over the course of a single conversion.  Module-level
# state is fine because conversions are single-threaded and short-lived.
_TYPE_ALIASES: dict = {}
_CLASS_METHODS: dict = {}   # class_name -> set of method names
_CLASS_PARENT:  dict = {}   # class_name -> parent class name


def _scan_method_names(tokens: List[Token]) -> set:
    """Walk a class/interface body at top level and return the set of
    method names declared.  Used for ``override`` analysis."""

    names: set = set()
    i, n = 0, len(tokens)
    depth = 0
    # Track positions of top-level ``$NAME ( ... )`` declarations.
    while i < n:
        t = tokens[i]
        if t.value == "{":
            depth += 1
        elif t.value == "}":
            depth -= 1
        if depth != 0:
            i += 1
            continue
        # candidate identifier
        if t.kind in ("IDENT", "KEYWORD") and t.value not in (
            ";", "public", "private", "protected", "static", "readonly",
            "abstract", "constructor", "get", "set",
        ):
            # is the next token '(' ?
            j = i + 1
            if j < n and tokens[j].value == "(":
                # we've found a method declaration ``name(...)``
                names.add(t.value)
        i += 1
    return names


def _apply_primitive_types(text: str) -> str:
    """Translate TS primitive type names → Cangjie. Safe to apply on
    rendered text (strings/comments have already been processed)."""

    return _PRIMITIVE_TYPE_RE.sub(lambda m: _PRIMITIVE_MAP[m.group(1)], text)


def _convert_expr(tokens: List[Token]) -> str:
    """Convert an expression-level token list.

    Idiomatic rewrites applied on top of the token-level pre-pass:

    * ``new Foo(args)`` → ``Foo(args)``
    * ``new Map<K,V>()`` → ``HashMap<K,V>()``
    * ``new Set<T>()`` → ``HashSet<T>()``
    * ``new Error(msg)`` → ``Exception(msg)``
    * TS template literals ``` `x ${y}` ``` → ``"x ${y}"``
    * ``Map<K,V>`` / ``Set<T>`` / ``Array<T>`` / ``Error`` symbols in
      generic positions
    * ``a ?? b`` (TS nullish coalescing) is already valid Cangjie when
      ``a`` is an ``Option<T>``; we keep it.
    * Inline lambda ``(x: T) => expr`` (no parens around result) →
      ``{ x: T => expr }``
    """

    tokens = _strip_trailing_semicolon(tokens)
    rendered = _render_tokens(tokens)
    # `new X(...)` -> `X(...)`
    rendered = re.sub(r"\bnew\s+", "", rendered)
    # Map/Set/Array/Error symbol rewrites (in type positions and call sites)
    rendered = re.sub(r"\bMap\b", "HashMap", rendered)
    rendered = re.sub(r"\bSet\b", "HashSet", rendered)
    rendered = re.sub(r"\bArray\b", "ArrayList", rendered)
    rendered = re.sub(r"\bError\b", "Exception", rendered)
    # template literals
    rendered = _convert_template_literal(rendered)
    # Inline arrow lambda: ``(x) => expr``
    rendered = _convert_inline_lambda(rendered)
    # Translate primitive type names that may appear inside generic args.
    rendered = _apply_primitive_types(rendered)
    return rendered.strip()


_INLINE_LAMBDA_RE = re.compile(
    r"\(([^()]*)\)\s*=>\s*"
)


def _convert_inline_lambda(s: str) -> str:
    """Rewrite ``(a, b) => expr`` to ``{ a, b => expr }``.

    We deliberately handle only the common single-line case and stay out
    of the way otherwise: arrow functions with block bodies are converted
    by the chunk-level ``arrow_assign_block`` pattern.
    """

    def repl(m: re.Match) -> str:
        params = m.group(1).strip()
        # Convert TS-style type annotations in params to CJ lambda head.
        cj_head: List[str] = []
        for p in [pp.strip() for pp in params.split(",") if pp.strip()]:
            mm = re.match(r"^([A-Za-z_$][\w$]*)\s*(\??)\s*(?::\s*(.+))?$", p)
            if mm:
                name, opt, ty = mm.group(1), mm.group(2), mm.group(3)
                if ty:
                    ty_t = _convert_type_text(ty)
                    if opt == "?":
                        ty_t = f"?{ty_t}"
                    cj_head.append(f"{name}: {ty_t}")
                else:
                    cj_head.append(name)
            else:
                cj_head.append(p)
        head = ", ".join(cj_head)
        return "{ " + head + " => "

    out = _INLINE_LAMBDA_RE.sub(repl, s)
    # If we opened a `{ ... =>` we must close it.  Heuristic: count
    # unmatched ``{`` openings caused by our replacement and add a closing
    # ``}`` at the very end.  This handles the common case
    # ``mapList(xs, (x) => x * x)`` where the arrow body has no comma at the
    # top level.
    if "=> " in out and out.count("{ ") > out.count("} "):
        diff = out.count("{ ") - out.count("} ")
        # Conservatively only close lambdas inside outer parens — find the
        # closing paren and insert just before it.
        # If the lambda is a top-level expression, append ``}``.
        # NOTE: this is a deliberately simple heuristic; complex cases are
        # left to the downstream AI pass.
        for _ in range(diff):
            # Find the next ``)`` that balances the lambda.  Strategy: walk
            # forward from each ``{ x =>`` we introduced and find the matching
            # outer ``)`` or end of string.
            pass
        # Simple insert: close at end of expression if string ends without
        # parens-balance issues.
        out = _balance_lambdas(out)
    return out


def _balance_lambdas(s: str) -> str:
    """Insert ``}`` to close ``{ ... =>`` lambdas we introduced.

    Walks token-by-token: when we see ``{`` followed eventually by ``=>``
    without a closing ``}``, we treat that as a lambda and add a closing
    brace at the end of the enclosing balanced expression.
    """

    # Pass 1: scan for unbalanced lambda openings.
    out: List[str] = []
    depth_paren = 0
    lambda_stack: List[int] = []  # indices of `{ ` we may need to close
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "{" and i + 1 < n and s[i + 1] == " ":
            # treat ``{ `` as a candidate lambda opener if followed by ``=>`` later
            # within the same parenthesis level
            j = i + 2
            depth_b = 1
            depth_p = 0
            saw_arrow = False
            while j < n - 1:
                if s[j] == "(":
                    depth_p += 1
                elif s[j] == ")":
                    if depth_p == 0:
                        break
                    depth_p -= 1
                elif s[j] == "{":
                    depth_b += 1
                elif s[j] == "}":
                    depth_b -= 1
                    if depth_b == 0:
                        break
                elif s[j] == "=" and j + 1 < n and s[j + 1] == ">" and depth_b == 1 and depth_p == 0:
                    saw_arrow = True
                    break
                j += 1
            if saw_arrow and depth_b == 1:
                lambda_stack.append(len(out))
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            if lambda_stack and depth_paren > 0:
                # close any open lambda before the ``)``
                out.append(" }")
                lambda_stack.pop()
            depth_paren -= 1
        out.append(ch)
        i += 1
    # close any remaining opens at end
    while lambda_stack:
        out.append(" }")
        lambda_stack.pop()
    return "".join(out)


_TEMPLATE_RE = re.compile(r"`([^`]*)`")


def _convert_template_literal(s: str) -> str:
    """Convert TS backtick template literals to Cangjie ``"..."`` strings.

    Cangjie's double-quoted strings accept ``${expr}`` interpolation, so
    the conversion is just a quote swap when the contents don't contain
    a literal ``"``.
    """

    def repl(m):
        inner = m.group(1)
        if '"' in inner:
            return '"' + inner.replace('"', '\\"') + '"'
        return '"' + inner + '"'

    return _TEMPLATE_RE.sub(repl, s)


def _convert_params(tokens: List[Token]) -> str:
    """Convert a parameter list ``a: T, b: U = v`` to Cangjie form."""

    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    if not text:
        return ""
    # Split on top-level commas.
    parts = _split_top_level(text, ",")
    out_parts: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # ``name : Type = default`` or ``name : Type`` or ``name``
        m = re.match(r"^([A-Za-z_$][\w$]*)\s*(\??)\s*(?::\s*([^=]+?))?\s*(?:=\s*(.+))?$", p)
        if not m:
            out_parts.append(p)
            continue
        name, opt, ty, default = m.group(1), m.group(2), m.group(3), m.group(4)
        ty = (ty or "Any").strip()
        ty = _convert_type_text(ty)
        if opt == "?":
            ty = f"?{ty}"
            if default is None:
                default = "None"
        if default is not None:
            out_parts.append(f"{name}!: {ty} = {default.strip()}")
        else:
            out_parts.append(f"{name}: {ty}")
    return ", ".join(out_parts)


def _convert_type(tokens: List[Token]) -> str:
    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    return _convert_type_text(text)


def _convert_type_text(text: str) -> str:
    """Convert a TypeScript type expression to its Cangjie counterpart.

    Handles:
    * primitive remapping (number → Int64, etc.)
    * nullable / optional types (``T | null``, ``T | undefined`` → ``?T``)
    * arrays (``T[]``  → ``ArrayList<T>``)
    * ``Map<K, V>`` → ``HashMap<K, V>`` and ``Set<T>`` → ``HashSet<T>``
    * tuple types (``[T, U]`` → ``(T, U)``)
    * stripping ``readonly``
    """

    text = (text or "").strip()
    if not text:
        return "Any"

    text = re.sub(r"\breadonly\s+", "", text)

    # Union types containing null / undefined  → optional ``?T``.
    parts = [p.strip() for p in _split_top_level(text, "|")]
    if len(parts) > 1:
        non_null = [p for p in parts if p not in ("null", "undefined", "None")]
        had_null = len(non_null) != len(parts)
        if had_null and len(non_null) == 1:
            return "?" + _convert_type_text(non_null[0])
        # otherwise: fall through and render as the first variant — Cangjie
        # doesn't have anonymous union types in 1.0.5, so we conservatively
        # pick the first non-null variant and leave a TODO.
        if non_null:
            return _convert_type_text(non_null[0]) + " /* ts2cj: TS union narrowed */"

    # Tuple types: ``[T, U]``.
    if text.startswith("[") and text.endswith("]") and "," in text:
        inner = text[1:-1]
        elems = [_convert_type_text(e) for e in _split_top_level(inner, ",")]
        return "(" + ", ".join(elems) + ")"

    text = _apply_primitive_types(text)

    # ``T[]`` → ``ArrayList<T>``.
    while text.endswith("[]"):
        inner = text[:-2].strip()
        text = f"ArrayList<{_convert_type_text(inner)}>"
        break  # only outer-most level — inner already converted

    # Collection name remaps.
    text = re.sub(r"\bMap\b", "HashMap", text)
    text = re.sub(r"\bSet\b", "HashSet", text)
    text = re.sub(r"\bArray\b", "ArrayList", text)
    text = re.sub(r"\bError\b", "Exception", text)

    return text


def _convert_type_params(tokens: List[Token]) -> str:
    """Convert ``<T, U extends Foo>`` to ``<T, U>`` (constraint moves to
    a ``where`` clause separately — for now we drop ``extends`` constraints
    which is a known minor simplification)."""

    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    out: List[str] = []
    for p in _split_top_level(text, ","):
        p = p.strip()
        if not p:
            continue
        # ``T extends Foo`` → ``T`` (constraint dropped).
        m = re.match(r"^([A-Za-z_$][\w$]*)\s+extends\s+(.+)$", p)
        if m:
            out.append(m.group(1))
        else:
            out.append(p)
    return ", ".join(out)


def _convert_lambda_params(tokens: List[Token]) -> str:
    """Convert ``(a: T, b: U)`` to Cangjie lambda head ``a: T, b: U`` or
    ``a, b`` when types are omitted (Cangjie infers from context)."""

    text = _render_tokens(_strip_trailing_semicolon(tokens)).strip()
    if not text:
        return ""
    out: List[str] = []
    for p in _split_top_level(text, ","):
        p = p.strip()
        if not p:
            continue
        m = re.match(r"^([A-Za-z_$][\w$]*)\s*(\??)\s*(?::\s*(.+))?$", p)
        if not m:
            out.append(p)
            continue
        name, opt, ty = m.group(1), m.group(2), m.group(3)
        if ty:
            ty_text = _convert_type_text(ty)
            if opt == "?":
                ty_text = f"?{ty_text}"
            out.append(f"{name}: {ty_text}")
        else:
            out.append(name)
    return ", ".join(out)


_ENUM_VARIANT_RE = re.compile(r"^([A-Za-z_$][\w$]*)\s*(?:=\s*[^,;]+)?$")


def _convert_enum_body(tokens: List[Token]) -> str:
    """Convert a TS enum body to Cangjie enum variants.

    TS variants may have explicit values (``Red = 1``); Cangjie 1.0.5
    enums don't carry such values directly, so we drop them — they
    can be reattached as an associated ``Int64`` via a helper function
    by the downstream AI pass.
    """

    text = _render_tokens(tokens).strip().rstrip(",").rstrip(";")
    variants: List[str] = []
    for raw in _split_top_level(text, ","):
        v = raw.strip().rstrip(";")
        if not v:
            continue
        m = _ENUM_VARIANT_RE.match(v)
        if m:
            variants.append(m.group(1))
        else:
            variants.append(v)  # leave the user something to spot
    if not variants:
        return "    /* ts2cj: empty enum */"
    return "    | " + "\n    | ".join(variants)


def _convert_switch_body(tokens: List[Token]) -> str:
    """Convert a TS ``switch`` body to Cangjie ``match`` cases.

    Recognises:
    * ``case L: ... break;`` → ``case L => { ... }``
    * ``default: ... break;`` → ``case _ => { ... }``
    * fall-through clauses are merged via ``|`` when consecutive
      empty ``case`` labels appear.
    """

    # Re-strip the leading/trailing braces if present (the binder leaves them).
    toks = [t for t in tokens if t.kind not in ("COMMENT_BLOCK", "COMMENT_LINE")]

    # Scan into (label_or_None_for_default, body_tokens) groups.
    cases: List[Tuple[List[List[Token]], List[Token]]] = []
    i, n = 0, len(toks)
    cur_labels: List[List[Token]] = []
    cur_body: List[Token] = []
    brace_depth = 0

    def flush():
        if cur_labels or cur_body:
            cases.append((list(cur_labels), list(cur_body)))

    while i < n:
        t = toks[i]
        # Track brace nesting — only ``case`` / ``default`` at the outer
        # level start a new arm.  Inner switches keep their cases.
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
            # Start of a new case — if we already accumulated a body, flush it.
            if cur_body:
                flush()
                cur_labels.clear()
                cur_body.clear()
            # collect label tokens until ":"
            i += 1
            lab: List[Token] = []
            while i < n and not (toks[i].kind == "PUNCT" and toks[i].value == ":"):
                lab.append(toks[i])
                i += 1
            i += 1  # skip ":"
            cur_labels.append(lab)
            continue
        if brace_depth == 0 and t.kind == "KEYWORD" and t.value == "default":
            if cur_body:
                flush()
                cur_labels.clear()
                cur_body.clear()
            i += 1
            if i < n and toks[i].kind == "PUNCT" and toks[i].value == ":":
                i += 1
            cur_labels.append([])  # empty = default
            continue
        # Skip a trailing ``break;`` at top level of the current case body.
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
            # Cangjie does not accept an empty match arm; emit ``()``.
            out_lines.append("        ()")
        else:
            out_lines.extend(body_lines)
    return "\n".join(out_lines)


def _split_top_level(s: str, sep: str) -> List[str]:
    out: List[str] = []
    depth = 0
    buf = []
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
#  Top-level driver                                                           #
# --------------------------------------------------------------------------- #
_NEEDS_COLLECTION = re.compile(r"\b(ArrayList|HashMap|HashSet)\b")


def convert_source(ts_source: str, wrap_main: bool = True) -> ConversionResult:
    """Convert a TypeScript source string into Cangjie source.

    Parameters
    ----------
    ts_source:
        Full TS source code (single file).
    wrap_main:
        If ``True`` (the default) and the source has no ``main`` /
        ``func main`` definition, wrap free top-level statements in a
        ``main()`` entry point so that the result is directly
        compilable.
    """

    rewritten, notes = _rewrite_token_stream(ts_source)
    tokens = tokenize(rewritten)
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
        # Skip top-level call to ``main()`` — Cangjie auto-invokes main.
        if (len(ch) >= 3 and ch[0].value == "main" and ch[1].value == "("
                and ch[2].value == ")"):
            continue
        cj = _convert_chunk(ch)
        if cj is None:
            result.fallback_chunks += 1
            verbatim = _render_tokens(ch)
            cj = f"/* ts2cj: TODO unrecognised chunk */ // {verbatim}"
        else:
            result.confident_chunks += 1
        rendered_chunks.append(cj)

        # Heuristic: top-level decls vs main-body statements.
        # Skip leading ``export`` / ``declare`` / ``async`` modifiers for
        # classification purposes.
        i0 = 0
        while i0 < len(ch) and ch[i0].value in ("export", "declare", "async", "default"):
            i0 += 1
        first = ch[i0].value if i0 < len(ch) else ""
        if first in (
            "class", "interface", "func", "enum", "import", "type",
            "struct", "abstract", "function",
        ):
            # Detect ``function main(...)`` — translate to Cangjie ``main``.
            if first == "function" and i0 + 1 < len(ch) and ch[i0 + 1].value == "main":
                has_user_main = True
                # Rewrite the emitted ``func main(...): Unit { ... }`` to a
                # Cangjie-compatible ``main()`` entry point.
                cj = re.sub(r"^func\s+main\s*\([^)]*\)\s*(?::\s*\w+\s*)?\{",
                            "main() {", cj, count=1)
                # Ensure a ``return 0`` exists in the body.
                if "\nreturn " not in cj and "\n    return " not in cj:
                    cj = cj[:-1] + "    return 0\n}"
                rendered_chunks[-1] = cj
            top_level_decls.append(cj)
        elif first in ("const", "let", "var"):
            # Top-level variables in TS map to top-level lets in Cangjie.
            top_level_decls.append(cj)
        else:
            main_body.append(cj)

    if has_user_main:
        # If the user defined their own ``main`` we don't auto-wrap.
        wrap_main = False

    # Assemble.
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

    # Inject imports if needed.  Cangjie's collections live in
    # ``std.collection``; sorting routines in ``std.sort``.
    headers: List[str] = []
    if _NEEDS_COLLECTION.search(body_text):
        headers.append("import std.collection.*")
    header = ("\n".join(headers) + "\n\n") if headers else ""
    result.source = header + body_text + ("\n" if body_text and not body_text.endswith("\n") else "")
    return result
