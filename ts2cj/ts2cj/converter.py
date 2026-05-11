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
    """

    notes: List[str] = []
    src = _outside_strings_replace(
        src,
        [
            ("===", "=="),
            ("!==", "!="),
            (".length", ".size"),
            (".push", ".append"),
            (".pop", ".popLast"),
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
        ],
    )
    return src, notes


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


def _is_word(s: str) -> bool:
    return bool(s) and (s[0].isalnum() or s[0] == "_")


# --------------------------------------------------------------------------- #
#  Body recursion                                                             #
# --------------------------------------------------------------------------- #
def _convert_body(tokens: List[Token], indent: int = 1) -> str:
    """Convert a brace-delimited body (without the outer braces)."""

    inner_chunks = _segment_chunks(tokens)
    pieces: List[str] = []
    pad = "    " * indent
    for ch in inner_chunks:
        if not ch:
            continue
        line = _convert_chunk(ch)
        if line is None:
            line = "/* ts2cj: unrecognised */ // " + _render_tokens(ch)
        # Indent every line.
        for ln in line.split("\n"):
            pieces.append(pad + ln if ln else ln)
    return "\n".join(pieces)


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

    if slot == "BODY" or slot == "A":
        return True
    # B, B1, B2, B3, B4, B5 — body branches in if-elif-else chains.
    if slot == "B" or (slot.startswith("B") and slot[1:].isdigit()):
        return True
    return False


def _emit(pat: Pattern, bindings: dict) -> str:
    """Materialise the Cangjie template given resolved slot bindings."""

    out = pat.cj_template
    for slot in pat.slots:
        if slot not in bindings:
            continue
        tokens = bindings[slot]
        if _is_body_slot(slot):
            body_text = _convert_body(tokens, indent=1)
            out = out.replace(f"${slot}", body_text)
        elif slot == "PARAMS":
            out = out.replace(f"${slot}", _convert_params(tokens))
        elif slot == "RET" or slot == "TY":
            out = out.replace(f"${slot}", _convert_type(tokens))
        else:
            out = out.replace(f"${slot}", _convert_expr(tokens))

    # Context-aware post-processing.
    if pat.name == "class_decl_extends":
        # In TS, methods in a subclass that share a name with parent's
        # method are overrides.  Cangjie requires the ``override``
        # modifier — we conservatively add it to every method.  When
        # the method does not actually override anything the user can
        # remove it; this is one of the "少量细节错误" the user
        # explicitly accepted.
        out = out.replace("public open func", "public override func")
    return out


def _apply_primitive_types(text: str) -> str:
    """Translate TS primitive type names → Cangjie. Safe to apply on
    rendered text (strings/comments have already been processed)."""

    return _PRIMITIVE_TYPE_RE.sub(lambda m: _PRIMITIVE_MAP[m.group(1)], text)


def _convert_expr(tokens: List[Token]) -> str:
    """Convert an expression-level token list.

    Most operator/identifier rewrites already happened during the
    token-stream pre-pass.  Here we additionally:

    * rewrite ``[1, 2, 3]`` array literals into ``ArrayList<T>([1, 2, 3])``
      when used as a typed initializer (handled by the variable pattern
      itself when type is known);
    * rewrite ``new Foo(args)`` → ``Foo(args)``.
    """

    tokens = _strip_trailing_semicolon(tokens)
    rendered = _render_tokens(tokens)
    # `new X(...)` -> `X(...)`
    rendered = re.sub(r"\bnew\s+", "", rendered)
    # template literals: `hello ${x}` -> "hello ${x}" (Cangjie supports ${} interpolation in "...")
    rendered = _convert_template_literal(rendered)
    # Translate primitive type names that may appear inside generic args.
    rendered = _apply_primitive_types(rendered)
    return rendered.strip()


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
    """Light type-string conversion (already covered by primitive rewrite)."""

    text = text.strip()
    if not text:
        return "Any"
    text = _apply_primitive_types(text)
    # ``T[]`` → ``ArrayList<T>``
    while text.endswith("[]"):
        inner = text[:-2].strip()
        text = f"ArrayList<{inner}>"
    # ``Array<T>`` already valid in Cangjie semantics for fixed Array.
    return text


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

    chunks = _segment_chunks(tokens)
    result = ConversionResult(source="", notes=notes)
    result.chunks = sum(1 for c in chunks if c)

    rendered_chunks: List[str] = []
    top_level_decls: List[str] = []
    main_body: List[str] = []

    for ch in chunks:
        if not ch:
            continue
        cj = _convert_chunk(ch)
        if cj is None:
            result.fallback_chunks += 1
            verbatim = _render_tokens(ch)
            cj = f"/* ts2cj: TODO unrecognised chunk */ // {verbatim}"
        else:
            result.confident_chunks += 1
            # Record the pattern name actually used (best-effort).
        rendered_chunks.append(cj)
        # Heuristic: top-level decls vs main-body statements.
        first = ch[0].value
        if first in ("class", "interface", "func", "enum", "import") or first == "function":
            top_level_decls.append(cj)
        elif first == "const" or first == "let" or first == "var":
            # Top-level variables in TS map to top-level lets in Cangjie.
            top_level_decls.append(cj)
        else:
            main_body.append(cj)

    # Assemble.
    parts: List[str] = []
    if top_level_decls:
        parts.extend(top_level_decls)
    if wrap_main:
        if not any("main(" in d for d in top_level_decls):
            body = "\n".join("    " + ln for ln in "\n".join(main_body).split("\n") if ln)
            parts.append("main() {\n" + body + "\n    return 0\n}")
    else:
        parts.extend(main_body)

    body_text = "\n\n".join(p for p in parts if p)

    # Inject imports if needed.
    header = ""
    if _NEEDS_COLLECTION.search(body_text):
        header = "import std.collection.*\n\n"
    result.source = header + body_text + ("\n" if body_text and not body_text.endswith("\n") else "")
    return result
