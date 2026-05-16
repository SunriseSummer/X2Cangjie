"""Neural Go → Cangjie converter (entry point).

Pipeline:

1. **Pre-process**: convert Go raw strings to Cangjie double-quoted
   strings (purely a lexical normalization), then run the regex Go
   lexer (:mod:`.lexer`).
2. **Segment** the token stream into top-level chunks by brace /
   semicolon balance (a syntactic operation, not a translation rule).
3. For each chunk, route the chunk's source text through the **trained
   Transformer** (:class:`go2cj.neural.translator.NeuralTranslator`).
   The model emits a Cangjie chunk.
4. **Lift** cross-chunk structural artefacts (struct constructors,
   free-method attachment, implicit interface satisfaction) — see
   :mod:`.lifting`.  These require multi-chunk awareness and so are
   handled separately from the neural translator.
5. **Assemble** the file: drop ``package`` / ``import`` declarations
   (they have no single-file Cangjie equivalent), inject
   ``import std.collection.*`` if the body uses ``ArrayList`` /
   ``HashMap``, and ensure a ``main()`` entry exists if the original
   Go had ``func main``.

There is **no rule-based translation table** in this module — the
mapping ``Go-chunk`` → ``Cangjie-chunk`` is learnt by the neural model
from the synthetic training corpus.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .lexer import Token, tokenize


_NO_SEMI_AFTER = {
    "(", "[", "{", ",", ".", ";", ":", "?", "@",
    "+", "-", "*", "/", "%", "&", "|", "^", "!", "<", ">", "=",
    "==", "!=", "<=", ">=", "&&", "||", ":=", "<<", ">>", "+=", "-=",
    "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>=", "&^", "&^=",
    "...",
    "if", "else", "for", "switch", "case", "default", "func", "var",
    "const", "type", "struct", "interface", "map", "chan", "go", "defer",
    "return", "range", "import", "package", "select",
}


def _inject_semis(tokens: List[Token]) -> List[Token]:
    """Insert Go's auto-inserted ``;`` tokens at line ends.

    Walks the token stream including ``NEWLINE`` markers; emits a
    ``;`` whenever Go's spec would auto-insert one (i.e. the previous
    meaningful token is not in :data:`_NO_SEMI_AFTER` and we are not
    inside parens / brackets).  This is a *lexical* preprocessing step
    — not a translation rule.
    """
    out: List[Token] = []
    prev = None
    dp = ds = 0
    for t in tokens:
        if t.kind == "NEWLINE":
            if (prev is not None and prev.value not in _NO_SEMI_AFTER
                    and dp == 0 and ds == 0):
                out.append(Token("PUNCT", ";", t.line, t.col))
                prev = out[-1]
            continue
        if t.kind in ("COMMENT_BLOCK", "COMMENT_LINE"):
            continue
        if t.value == "(":
            dp += 1
        elif t.value == ")":
            dp = max(dp - 1, 0)
        elif t.value == "[":
            ds += 1
        elif t.value == "]":
            ds = max(ds - 1, 0)
        out.append(t)
        prev = t
    return out


from .lifting import (
    attach_interface_impls,
    promote_methods,
    synthesize_class_inits,
)
from .critical.translator import NeuralTranslator
from .tokenize import detokenize


@dataclass
class ConversionResult:
    source: str
    chunks: int = 0
    confident_chunks: int = 0
    fallback_chunks: int = 0
    notes: List[str] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        if self.chunks == 0:
            return 0.0
        return self.confident_chunks / self.chunks


# --------------------------------------------------------------------------- #
#  Pre-processing (lexical normalisation, not translation)                    #
# --------------------------------------------------------------------------- #


def _convert_raw_strings(src: str) -> str:
    """Replace Go raw strings ``` `...` ``` with escaped Cangjie
    double-quoted strings — a purely lexical normalization step."""

    out: List[str] = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == "`":
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
        if c == '"':
            j = i + 1
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    j += 2
                    continue
                j += 1
            out.append(src[i:j + 1])
            i = j + 1
            continue
        if c == "/" and i + 1 < n and src[i + 1] in ("/", "*"):
            if src[i + 1] == "/":
                end = src.find("\n", i)
                end = n if end == -1 else end
            else:
                end = src.find("*/", i)
                end = n if end == -1 else end + 2
            out.append(src[i:end])
            i = end
            continue
        out.append(c)
        i += 1
    return "".join(out)


# --------------------------------------------------------------------------- #
#  Chunk segmentation                                                         #
# --------------------------------------------------------------------------- #


def _segment_chunks(tokens: List[Token]) -> List[List[Token]]:
    """Split a Go token stream into top-level chunks by brace balance.

    A chunk ends at any of:

    * a top-level ``;`` (Go's explicit statement terminator);
    * a ``NEWLINE`` token at depth 0 (Go's de-facto statement
      terminator — present in the lexer's token stream but stripped
      from chunk contents);
    * the ``}`` that closes a previously opened ``{`` (unless the
      next token is ``else``).

    A ``in_for_header`` flag suppresses the ``;`` rule inside the
    ``for init; cond; step`` clause head.

    Keeping NEWLINE-as-separator is crucial: without it,
    ``package main`` + ``import "fmt"`` + ``func main(){…}`` collapse
    into one mega-chunk (since Go doesn't write ``;`` between top-level
    decls), and statements inside ``main`` (``z := 15``, bare
    ``fmt.Println(x)``) don't split either — both of which defeat the
    statement-level retrieval CHIME relies on.
    """

    # Keep newline markers (we use them as separators) but drop
    # comments.
    toks = [t for t in tokens
            if t.kind not in ("COMMENT_BLOCK", "COMMENT_LINE")]
    chunks: List[List[Token]] = []
    cur: List[Token] = []
    db = dp = ds = 0
    in_for_header = False
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
        if t.kind == "NEWLINE":
            # Newline at depth 0 → top-level statement boundary.  At
            # depth > 0 we *keep* the NEWLINE token in the running
            # chunk: it carries no meaning to a trained CHIME neuron
            # (rendering filters it out again), but it preserves the
            # statement boundaries inside ``{ … }`` so that when
            # ``_unfold_main`` recursively segments the body, the
            # inner pass can still see them.
            if db == 0 and dp == 0 and ds == 0:
                if cur and not in_for_header:
                    chunks.append(cur)
                    cur = []
            else:
                cur.append(t)
            i += 1
            continue
        cur.append(t)
        if t.kind == "KEYWORD" and t.value == "for" and db == dp == ds == 0:
            in_for_header = True
        if t.kind == "PUNCT":
            if t.value == "{":
                db += 1
                if in_for_header and db == 1:
                    in_for_header = False
            elif t.value == "}":
                db = max(db - 1, 0)
                if db == 0 and dp == 0 and ds == 0:
                    # Look ahead past whitespace for ``else``.
                    j = i + 1
                    while j < n and toks[j].kind == "NEWLINE":
                        j += 1
                    nxt = toks[j] if j < n else None
                    if (nxt is not None and nxt.kind == "KEYWORD"
                            and nxt.value == "else"):
                        # Re-attach the bridge tokens we just looked
                        # past to the running chunk — they're whitespace
                        # so dropping them is fine.
                        i = j - 1
                        i += 1
                        continue
                    chunks.append(cur)
                    cur = []
            elif t.value == "(":
                dp += 1
            elif t.value == ")":
                dp = max(dp - 1, 0)
            elif t.value == "[":
                ds += 1
            elif t.value == "]":
                ds = max(ds - 1, 0)
            elif (t.value == ";" and db == 0 and dp == 0 and ds == 0
                  and not in_for_header):
                chunks.append(cur[:-1])
                cur = []
        i += 1
    if cur:
        chunks.append(cur)
    return [c for c in chunks if c]


def _is_func_main(chunk: List[Token]) -> bool:
    """``func main () { ... }`` heuristic."""
    return (len(chunk) >= 6
            and chunk[0].kind == "KEYWORD" and chunk[0].value == "func"
            and chunk[1].value == "main"
            and chunk[2].value == "("
            and chunk[3].value == ")"
            and chunk[4].value == "{"
            and chunk[-1].value == "}")


def _func_split(chunk: List[Token]) -> Optional[Tuple[str, List[Token], List[Token]]]:
    """If ``chunk`` is a ``func NAME(...) <ret>? { body }`` declaration,
    return ``(name, header_tokens_incl_open_brace, body_tokens)``.

    The header includes everything up to and including the opening
    ``{``; the body excludes both the opening ``{`` and the closing
    ``}``.  Returns ``None`` for non-function chunks (top-level
    ``type`` / ``var`` / ``const`` decls etc.).
    """
    if (len(chunk) < 6
            or chunk[0].kind != "KEYWORD" or chunk[0].value != "func"
            or chunk[1].kind != "IDENT"
            or chunk[-1].value != "}"):
        return None
    name = chunk[1].value
    # Walk forward to the *first* ``{`` at brace-depth 0 *that opens
    # the function body* — skip generic ``<...>`` and parameter ``(...)``
    # without descending into them.  We track paren / bracket depth so
    # composite-literal-looking ``{`` inside parameter defaults can't
    # confuse us.
    paren_depth = bracket_depth = 0
    body_brace_index = -1
    for i, tok in enumerate(chunk):
        if tok.value == "(":
            paren_depth += 1
        elif tok.value == ")":
            paren_depth = max(paren_depth - 1, 0)
        elif tok.value == "[":
            bracket_depth += 1
        elif tok.value == "]":
            bracket_depth = max(bracket_depth - 1, 0)
        elif (tok.value == "{" and paren_depth == 0
              and bracket_depth == 0 and i > 1):
            body_brace_index = i
            break
    if body_brace_index < 0:
        return None
    header = chunk[:body_brace_index + 1]
    body = chunk[body_brace_index + 1:-1]
    return name, header, body


def _block_split(chunk: List[Token]) -> Optional[Tuple[List[Token], List[Token]]]:
    """If ``chunk`` has shape ``<header> { <body> }`` — that is, a single
    outermost block whose opening ``{`` matches the chunk's terminal
    ``}`` and whose body contains at least one top-level ``;`` —
    return ``(header_incl_open_brace, body_tokens)``.  Otherwise return
    ``None``.

    Used by :func:`_expand_block` to recursively decompose nested
    ``for {…}`` / ``if {…}`` / ``while {…}`` etc. into per-statement
    chunks.  The semicolon-presence check distinguishes a real
    statement block from a composite literal like ``[]int{1,2,3}``.

    ``if … {…} else {…}`` is left intact (its terminal ``}`` does
    *not* match its first ``{``).  The else-branch handling is the
    converter's responsibility through CHIME templates.
    """
    paren = bracket = 0
    i = 0
    while i < len(chunk):
        v = chunk[i].value
        if v == "(":
            paren += 1
        elif v == ")":
            paren = max(paren - 1, 0)
        elif v == "[":
            bracket += 1
        elif v == "]":
            bracket = max(bracket - 1, 0)
        elif v == "{" and paren == 0 and bracket == 0:
            break
        i += 1
    if i >= len(chunk) or chunk[i].value != "{":
        return None
    if not chunk or chunk[-1].value != "}":
        return None
    if i == 0:
        return None  # bare ``{ body }`` — no header
    # Walk forward to the matching ``}`` for ``chunk[i]``; if it isn't
    # the very last token, this is a multi-brace chunk (if/else, switch
    # with cases) and we shouldn't naively split it.
    depth = 1
    j = i + 1
    while j < len(chunk) and depth > 0:
        v = chunk[j].value
        if v == "{":
            depth += 1
        elif v == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    if j != len(chunk) - 1:
        return None
    body = chunk[i + 1:j]
    # Body must contain at least one top-level ``;`` to count as a
    # statement block (rules out ``{1,2,3}`` composite literals).
    body_depth = 0
    has_semi = False
    for t in body:
        v = t.value
        if v in ("{", "(", "["):
            body_depth += 1
        elif v in ("}", ")", "]"):
            body_depth = max(body_depth - 1, 0)
        elif v == ";" and body_depth == 0:
            has_semi = True
            break
    if not has_semi:
        return None
    header = chunk[:i + 1]
    return header, body


def _expand_block(chunk: List[Token], tag: Optional[str],
                  out: List[List[Token]],
                  tags: List[Optional[str]]) -> None:
    """Recursively expand any nested ``<header>{body}`` blocks within
    a statement chunk, appending the expanded sub-chunks (and a
    parallel ``tag`` for each) to ``out`` / ``tags``.

    Blocks whose body has ``;`` separated statements are split into
    header / per-statement body / footer.  Composite literals,
    statement chunks without inner blocks, and if-else chunks are
    appended unchanged.  All sub-chunks inherit the parent ``tag`` so
    the splicer keeps them inside the enclosing function body.
    """
    bs = _block_split(chunk)
    if bs is None:
        out.append(chunk)
        tags.append(tag)
        return
    header, body = bs
    out.append(header)
    tags.append(tag)
    for sub in _segment_chunks(body):
        _expand_block(sub, tag, out, tags)
    out.append([Token("PUNCT", "}", 0, 0)])
    tags.append(tag)


def _unfold_functions(
    chunks: List[List[Token]],
) -> Tuple[List[List[Token]], List[Optional[str]]]:
    """Replace every ``func NAME(...) {body}`` chunk with a flat
    sequence ``[header, *per_stmt_body_chunks, footer]`` and return a
    parallel ``from_func`` tag list.

    Recursive Block Unfolding (RBU): the same decomposition that
    ``_unfold_main`` does for ``main()`` is applied uniformly to every
    user-defined function as well.  Without this, any non-trivial
    function (e.g. a 30-line knapsack DP, a 50-line quicksort) enters
    CHIME as a single 100+-token chunk that has no chance of matching
    the statement-level templates the engine was trained on.  With RBU,
    every statement inside every function is independently translated,
    and the function's structure is reconstructed at assembly time.

    Tag semantics (``from_func[i]``):

    * ``None``  — top-level decl (``type``, ``var``, ``const``,
      ``interface``, free-standing ``func`` header / footer, etc.).
    * ``"main"`` — body statement inside ``func main`` (re-wrapped by
      the synthesised ``main() { … return 0 }`` block).
    * ``"<name>"`` — body statement inside ``func <name>`` (re-wrapped
      between the translated header / closing brace of that function).
    """
    out: List[List[Token]] = []
    tags: List[Optional[str]] = []
    for ch in chunks:
        if _is_func_main(ch):
            # main: body statements are *not* recursively block-
            # expanded (see :func:`go2cj_new.critical.train._unfold_main_body`
            # for the rationale — trainset main bodies typically use
            # literal loop bounds, whereas inside a user function the
            # bound is a parameter identifier, so the placeholder
            # signatures of bare ``for {`` headers diverge).
            body = ch[5:-1]
            for sub in _segment_chunks(body):
                out.append(sub)
                tags.append("main")
            continue
        split = _func_split(ch)
        if split is None:
            out.append(ch)
            tags.append(None)
            continue
        name, header, body = split
        # Emit the function header (the part *up to and including* the
        # opening ``{``) as its own top-level chunk so CHIME / fallback
        # can translate the signature.  Body statements get
        # *recursively* unfolded and tagged ``from_func=name`` — nested
        # ``for {…}`` / ``if {…}`` blocks split into header chunk,
        # per-statement body chunks (which can themselves contain
        # inner blocks), and a footer ``}`` chunk, all routed through
        # CHIME at statement granularity.  Placeholder-kind mismatches
        # between literal-bounded (``i < 5``) and identifier-bounded
        # (``i < n``) loops are resolved by the positional alignment
        # in :func:`go2cj_new.critical.engine._align_placeholders`.
        out.append(header)
        tags.append(None)
        for sub in _segment_chunks(body):
            _expand_block(sub, name, out, tags)
        out.append([Token("PUNCT", "}", 0, 0)])
        tags.append(None)
    return out, tags


# Keep the old name as an alias so any external callers don't break.
_unfold_main = _unfold_functions


def _is_header_only_chunk(chunk: List[Token]) -> bool:
    """A chunk produced by RBU that is just a function signature
    ending in ``{`` (no body, no closing ``}``).  These should always
    take the deterministic ``_rewrite_func_signature`` path to avoid
    being matched against whole-function neurons in CHIME.
    """
    meaningful = [t for t in chunk if t.kind != "NEWLINE"]
    if len(meaningful) < 4:
        return False
    if meaningful[0].kind != "KEYWORD" or meaningful[0].value != "func":
        return False
    if meaningful[-1].value != "{":
        return False
    # Reject if a closing ``}`` is also present (full function chunk
    # that happens to end with another ``{``, shouldn't really happen).
    return not any(t.value == "}" for t in meaningful)


def _is_close_brace_chunk(chunk: List[Token]) -> bool:
    """A chunk consisting of a single ``}`` (RBU function footer)."""
    meaningful = [t for t in chunk if t.kind != "NEWLINE"]
    return len(meaningful) == 1 and meaningful[0].value == "}"


def _render_chunk(chunk: List[Token]) -> str:
    """Render a chunk's tokens as a single text line for NN input.

    We separate tokens with a single space — matching the tokenizer
    used by :mod:`go2cj.neural.vocab` so the model sees consistent
    spacing.
    """
    parts: List[str] = []
    prev: str = ""
    for t in chunk:
        # NEWLINE tokens are retained inside chunks (so recursive
        # segmenters can still split on them) but they carry no
        # rendered content and must not leak into the model's input.
        if t.kind == "NEWLINE":
            continue
        v = t.value
        if not parts:
            parts.append(v)
        else:
            parts.append(" " + v)
        prev = v
    return "".join(parts).strip()


# --------------------------------------------------------------------------- #
#  Output post-processing (cosmetic, not translation)                         #
# --------------------------------------------------------------------------- #


_NEEDS_COLLECTION = re.compile(r"\b(?:ArrayList|HashMap|HashSet)\b")


# --------------------------------------------------------------------------- #
#  Fallback rewrites                                                          #
# --------------------------------------------------------------------------- #
#
# When the CHIME associative memory has no clean match for a chunk, we emit
# the chunk's Go text verbatim and rely on overlap between the two languages
# (binary ops, calls, indexing, var := …).  These tiny lexical rewrites
# bridge the most common idioms that *don't* overlap so the surrounding
# program still has a chance of compiling.  These are deliberately kept
# small and conservative — they are not intended to be a rule-based
# translator, only to keep the fallback path useful.

_FALLBACK_RULES = [
    # fmt.Println(x)  →  println(x)   (also Print/Printf as best-effort)
    (re.compile(r"\bfmt\s*\.\s*Println\s*\("), "println("),
    (re.compile(r"\bfmt\s*\.\s*Print\s*\("),   "print("),
    (re.compile(r"\bfmt\s*\.\s*Printf\s*\("),  "print("),
    # Function decls:  func name(a int, b int) int {  →
    #                   func name(a: Int64, b: Int64): Int64 {
    # Conservative: only rewrites when the entire chunk *starts* with
    # `func` and we can find ``)`` before ``{``.  Keeps `func main()`
    # untouched (no return type to inject) — that's handled at assemble
    # time.
    (re.compile(r"\b(int|int64)\b"),       "Int64"),
    (re.compile(r"\b(int32)\b"),           "Int32"),
    (re.compile(r"\b(float32)\b"),         "Float32"),
    (re.compile(r"\b(float64)\b"),         "Float64"),
    (re.compile(r"\bbool\b"),              "Bool"),
    (re.compile(r"\bstring\b"),            "String"),
    # Go short var:  x := expr  →  var x = expr   (only when at chunk start
    # so we don't break `for i := 0;` headers etc.).
    (re.compile(r"^\s*([A-Za-z_]\w*)\s*:=\s*"), r"var \1 = "),
    # ``len(x)``  →  ``x.size``   — applied last so any preceding
    # rewrites still see the parentheses-form when relevant.
    (re.compile(r"\blen\s*\(\s*([A-Za-z_]\w*(?:\s*\.\s*[A-Za-z_]\w*)*)\s*\)"),
     r"\1.size"),
]


# --------------------------------------------------------------------------- #
#  Control-flow header rewrites.                                               #
#                                                                              #
#  Cangjie requires ``if (cond) {``, ``while (cond) {`` and ``for (var in     #
#  iter) {`` — parenthesised conditions and an ``in``-style for.  These are   #
#  pure-syntax transforms (no semantic translation needed) that ride on the   #
#  fallback path when CHIME has no matching template.                          #
#                                                                              #
#  Each rule is shape-restricted (anchored, balanced-brace-aware) so it does  #
#  not corrupt unrelated chunks like ``var x = if(cond) {…}`` (Cangjie's      #
#  if-expression form, which already has parens).                              #
# --------------------------------------------------------------------------- #


def _parenthesise_condition(text: str, keyword: str,
                            replacement_keyword: Optional[str] = None) -> str:
    """Add Cangjie-style parentheses around the *condition* of a Go
    control-flow header.

    Handles ``if cond { … }``, ``else if cond { … }``, and ``for cond { … }``
    (Go's ``for`` with no init/step is Cangjie's ``while``).  The
    condition is taken as everything between the keyword and the matching
    ``{`` that opens the body, with brace / bracket balance respected so
    embedded composite literals don't trip the parser.  Returns ``text``
    unchanged when the shape doesn't match.
    """
    out = replacement_keyword if replacement_keyword is not None else keyword
    pattern = re.compile(
        rf"(^|[^A-Za-z0-9_])\b{re.escape(keyword)}\b(?!\s*[(])"
    )
    result: List[str] = []
    last = 0
    for m in pattern.finditer(text):
        start = m.end()
        # Walk forward to the matching ``{`` (depth 0 in (), []).
        paren = bracket = brace = 0
        i = start
        n = len(text)
        in_str = False
        str_ch = ""
        while i < n:
            c = text[i]
            if in_str:
                if c == "\\" and i + 1 < n:
                    i += 2
                    continue
                if c == str_ch:
                    in_str = False
                i += 1
                continue
            if c in '"\'`':
                in_str = True
                str_ch = c
                i += 1
                continue
            if c == "(":
                paren += 1
            elif c == ")":
                paren = max(paren - 1, 0)
            elif c == "[":
                bracket += 1
            elif c == "]":
                bracket = max(bracket - 1, 0)
            elif c == "{" and paren == 0 and bracket == 0:
                brace = 1
                break
            i += 1
        if brace != 1:
            continue
        cond = text[start:i].strip()
        if not cond:
            continue
        # Already parenthesised — leave alone (would otherwise produce
        # ``if ((cond)) {``).
        if cond.startswith("(") and cond.endswith(")"):
            # Only skip when the outer parens enclose the *whole* cond.
            depth = 0
            ok = True
            for k, ch in enumerate(cond):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0 and k != len(cond) - 1:
                        ok = False
                        break
            if ok:
                # Still rewrite the keyword (e.g. ``for`` → ``while``)
                # without altering the parenthesised condition.
                result.append(text[last:m.start()])
                result.append(m.group(1))
                result.append(out)
                result.append(text[m.end():i])
                result.append("{")
                last = i + 1
                continue
        result.append(text[last:m.start()])
        result.append(m.group(1))
        result.append(out)
        result.append(" (")
        result.append(cond)
        result.append(") {")
        last = i + 1
    if last == 0:
        return text
    result.append(text[last:])
    return "".join(result)

_FUNC_SIG_RE = re.compile(
    r"^func\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*"
    r"(\[\s*\]\s*[A-Za-z_]\w*"        # ``[]int`` slice return
    r"|\([^)]*\)"                      # ``(int, int)`` tuple return
    r"|[A-Za-z_]\w*"                  # plain identifier return
    r")?\s*\{",
    flags=re.S,
)


def _translate_go_type(go_type: str) -> str:
    """Translate a single Go type fragment to its Cangjie equivalent.

    Supports the common shapes that appear in trainset / test cases:
    primitive renames (``int`` → ``Int64`` etc.), single-dimensional
    slice ``[]T`` → ``ArrayList<T>``, and two-dimensional slice
    ``[][]T`` → ``ArrayList<ArrayList<T>>``.  Unknown shapes pass
    through unchanged.
    """
    t = go_type.strip()
    # Match ``[][]T`` first to avoid the outer ``[]`` clobbering the
    # inner pattern.
    m2 = re.match(r"^\[\s*\]\s*\[\s*\]\s*(.+)$", t)
    if m2:
        return f"ArrayList<ArrayList<{_translate_go_type(m2.group(1))}>>"
    m1 = re.match(r"^\[\s*\]\s*(.+)$", t)
    if m1:
        return f"ArrayList<{_translate_go_type(m1.group(1))}>"
    return {
        "int": "Int64", "int64": "Int64", "int32": "Int32",
        "int16": "Int16", "int8": "Int8",
        "uint": "UInt64", "uint64": "UInt64", "uint32": "UInt32",
        "uint16": "UInt16", "uint8": "UInt8", "byte": "UInt8",
        "float32": "Float32", "float64": "Float64",
        "bool": "Bool", "string": "String", "rune": "Rune",
    }.get(t, t)


def _rewrite_func_signature(text: str) -> str:
    """Rewrite a leading Go ``func`` signature into Cangjie shape.

    Handles four common parameter / return-type shapes:

    * single typed param ``a int``;
    * shared-type group ``a, b int`` → ``a: Int64, b: Int64``;
    * slice param ``xs []int`` → ``xs: ArrayList<Int64>``;
    * tuple return ``(int, int)`` → ``: (Int64, Int64)``.

    Cangjie's ``func main`` is left untouched (no return type
    needed — Cangjie infers from ``return 0``).
    """
    m = _FUNC_SIG_RE.match(text.lstrip())
    if not m:
        return text
    name, params, ret = m.group(1), m.group(2), m.group(3)
    if name == "main":
        return text
    new_params: List[str] = []
    # First pass: split on commas, then merge ``a , b , c int`` shared-
    # type groups by walking left-to-right and back-filling missing
    # types from the next-named-type group.
    raw_parts = [p.strip() for p in params.split(",") if p.strip()]
    pending_names: List[str] = []
    for part in raw_parts:
        bits = part.split()
        if len(bits) == 1:
            # name only, type will come from a later group
            pending_names.append(bits[0])
        elif len(bits) >= 2:
            type_str = " ".join(bits[1:])
            cj_type = _translate_go_type(type_str)
            for nm in pending_names:
                new_params.append(f"{nm}: {cj_type}")
            pending_names = []
            new_params.append(f"{bits[0]}: {cj_type}")
        else:
            new_params.append(part)
    # Unfinished pending names — keep as-is so cjc raises a clear error.
    for nm in pending_names:
        new_params.append(nm)
    rewritten_head = f"func {name}({', '.join(new_params)})"
    if ret:
        ret = ret.strip()
        if ret.startswith("(") and ret.endswith(")"):
            # tuple return — translate each component
            inner = ret[1:-1]
            comps = [_translate_go_type(c) for c in inner.split(",") if c.strip()]
            rewritten_head += f": ({', '.join(comps)})"
        else:
            rewritten_head += f": {_translate_go_type(ret)}"
    rewritten_head += " {"
    return _FUNC_SIG_RE.sub(lambda _: rewritten_head, text.lstrip(), count=1)


def _fallback_rewrite(go_text: str) -> str:
    """Apply a pinch of string-level rewrites to a Go chunk.

    The goal is to make the *fallback* (no-CHIME-match) path produce
    something Cangjie has a chance of compiling, without pretending to
    be a real translator.  Bigger transformations stay the
    responsibility of the CHIME engine.
    """
    text = _rewrite_func_signature(go_text)
    for pat, sub in _FALLBACK_RULES:
        text = pat.sub(sub, text)
    # Add Cangjie ``(`` / ``)`` around the condition of bare Go
    # ``if`` / ``else if`` / ``for cond`` block openers.  These are
    # cheap, shape-restricted transforms that turn a CHIME miss
    # (which would otherwise leak raw Go syntax into the output) into
    # a syntactically-correct Cangjie chunk.  ``for`` becomes
    # ``while`` only when its condition is *not* a Go C-style header
    # (``for init; cond; step``) — those have their own template
    # neurons in CHIME and shouldn't be touched here.
    # ``for cond`` becomes ``while (cond)`` *only* when the condition
    # is genuinely a simple Go boolean (no ``;`` for the C-style
    # ``init; cond; step`` header, no ``,`` or ``range``/``:=`` for
    # range loops).  Those compound shapes have their own CHIME
    # templates and shouldn't be mangled by the fallback.
    m_for = re.search(r"\bfor\b\s+([^{;]+)\{", text)
    if m_for:
        cond = m_for.group(1)
        is_range_or_cstyle = (
            "," in cond
            or re.search(r"\brange\b", cond) is not None
            or ":=" in cond
        )
        if not is_range_or_cstyle:
            text = _parenthesise_condition(text, "for", "while")
    text = _parenthesise_condition(text, "if")
    return text


def _cosmetic(text: str) -> str:
    # Collapse "Name < T >" → "Name<T>" for generic types we emit.
    text = re.sub(r"\b(ArrayList|HashMap|HashSet|Option|Array)\s+<\s*", r"\1<",
                  text)
    text = re.sub(r"\s+>\s*\(", ">(", text)
    # Collapse multiple blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # No space before comma.
    text = re.sub(r"\s+,", ",", text)
    # Strip trailing spaces.
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text


# --------------------------------------------------------------------------- #
#  RBU assembly: splice per-function body statements between header / footer  #
# --------------------------------------------------------------------------- #


_FUNC_HEADER_RE = re.compile(
    r"^\s*func\s+([A-Za-z_]\w*)\s*[<(]",
)


def _splice_func_bodies(top_stream: List[str],
                        func_bodies: Dict[str, List[str]]) -> List[str]:
    """Walk the linear stream of top-level decl chunks; whenever we hit
    a ``func F(...) … {`` header chunk, splice ``func_bodies[F]``
    between the header and the *next* footer ``}`` chunk, collapsing
    the three into a single multi-line function declaration.

    Body statements are indented four spaces.  If no header is found
    for a tagged body, the leftover statements are appended at the end
    of the stream (a defensive fallback — should never happen in
    practice once RBU is consistent).
    """
    out: List[str] = []
    i = 0
    n = len(top_stream)
    used: set = set()
    while i < n:
        decl = top_stream[i].rstrip()
        match = _FUNC_HEADER_RE.match(decl)
        if match and decl.rstrip().endswith("{"):
            fn = match.group(1)
            # Find the matching ``}`` footer chunk (first subsequent
            # chunk whose stripped text is just ``}``).
            j = i + 1
            while j < n and top_stream[j].strip() != "}":
                j += 1
            body_stmts = func_bodies.get(fn, [])
            used.add(fn)
            indented = "\n".join(
                "    " + ln for ln in "\n".join(body_stmts).split("\n")
                if ln.strip()
            )
            block = decl + ("\n" + indented if indented else "") + "\n}"
            out.append(block)
            i = j + 1 if j < n else n
            continue
        out.append(top_stream[i])
        i += 1
    # Any function body whose header didn't appear (e.g. CHIME emitted
    # something unparseable) — emit verbatim so debugging stays
    # tractable.
    for fn, stmts in func_bodies.items():
        if fn in used or not stmts:
            continue
        out.append("// orphan body for " + fn + ":\n" + "\n".join(stmts))
    return out


# --------------------------------------------------------------------------- #
#  Main entry point                                                           #
# --------------------------------------------------------------------------- #


def convert_source(go_source: str, wrap_main: bool = True) -> ConversionResult:
    """Convert a single Go source file to Cangjie source.

    All per-chunk translation is delegated to the trained Transformer
    in :mod:`.neural.translator`.  Pre-processing converts raw
    strings; chunk segmentation runs on the lexed token stream; cross-
    chunk structural lifting runs after the neural pass.
    """
    notes: List[str] = []

    # 1. Lexical pre-processing.
    src = _convert_raw_strings(go_source)
    tokens = tokenize(src)
    tokens = _inject_semis(tokens)
    chunks = _segment_chunks(tokens)

    # 1b. Recursive Block Unfolding (RBU).  Replace every ``func F(){…}``
    # chunk with its header, per-statement body chunks, and footer ``}``.
    # ``main`` body statements get a special ``"main"`` tag because the
    # synthesised ``main() { … return 0 }`` wrapper differs from a user
    # function (no header chunk; trailing ``return 0`` is added).
    # Other user functions get tagged with their name so the assembler
    # can group their body statements back under their translated
    # header.  Without RBU, any non-trivial user function (e.g. a
    # 30-line knapsack DP) enters CHIME as one giant chunk that has no
    # chance of matching the statement-level templates the engine was
    # trained on.
    chunks, chunk_func = _unfold_functions(chunks)

    # 2. Skim ``package`` / ``import`` and identify ``func main``.
    translatable: List[List[Token]] = []
    translatable_func: List[Optional[str]] = []
    has_user_main = False  # set True only if a non-unfolded main remains
    for ch, fn in zip(chunks, chunk_func):
        if not ch:
            continue
        if ch[0].kind == "KEYWORD" and ch[0].value in ("package", "import"):
            continue
        if (len(ch) >= 3 and ch[0].kind == "KEYWORD" and ch[0].value == "func"
                and ch[1].value == "main" and ch[2].value == "("):
            has_user_main = True
        translatable.append(ch)
        translatable_func.append(fn)

    result = ConversionResult(source="", notes=notes, chunks=len(translatable))

    if not translatable:
        result.source = ""
        return result

    # 3. Run the trained neural model on every chunk.
    translator = NeuralTranslator.get()
    go_texts = [_render_chunk(ch) for ch in translatable]
    cj_texts = translator.translate_batch(go_texts)

    rendered: List[str] = []
    for ch, cj in zip(translatable, cj_texts):
        cj = cj.strip()
        # Detect RBU-emitted function header / footer chunks and force
        # them through the deterministic fallback rewriter.  Reason: a
        # header chunk like ``func F ( a int ) int {`` has high HD
        # similarity to *whole-function* neurons (``func F(a int) int
        # { return ... }``) stored from the pairs.jsonl curated set,
        # and the CHIME retrieval will happily return the longer
        # template — which then duplicates the body that the per-stmt
        # body chunks are *also* about to translate, breaking the
        # splicer.  Lexical signature rewriting is unambiguous so it
        # gives a clean header every time.
        if _is_header_only_chunk(ch):
            result.fallback_chunks += 1
            rendered.append(_fallback_rewrite(_render_chunk(ch)))
            continue
        if _is_close_brace_chunk(ch):
            # A solitary ``}`` is identical in both languages.
            result.confident_chunks += 1
            rendered.append("}")
            continue
        if not cj:
            # Fallback: emit the chunk's Go text verbatim, then run a
            # tiny set of textual rewrites bridging the most common
            # idioms (fmt.Println, primitive type names, ``x := …``
            # short var, Go-style func signature).  Many Go expressions
            # (binary ops, function calls, indexing) are already valid
            # Cangjie syntax, so this gives a real chance of compiling
            # even when the associative memory had no confident match.
            result.fallback_chunks += 1
            rendered.append(_fallback_rewrite(_render_chunk(ch)))
        else:
            result.confident_chunks += 1
            rendered.append(cj)

    # 4. Classify each rendered chunk into one of three buckets:
    #
    # * top-level decls — emitted before ``main()`` (``type``, ``var``
    #   / ``const`` block, ``interface``, the *header* chunk of a user
    #   function, the closing ``}`` footer of a user function, etc.).
    #   These need to stay in their original linear order so a function
    #   body assembled in between makes sense.
    # * ``main`` body statements — wrapped in the synthesised
    #   ``main() { … return 0 }``.
    # * user-function body statements — gathered in the order they
    #   appeared and spliced between the function's header and footer.
    #
    # We assemble the top-level stream in one linear pass; when we hit
    # a chunk tagged ``from_func == fn`` we keep accumulating until the
    # next chunk's ``from_func`` differs, then we splice the accumulated
    # body statements right after the corresponding header chunk we
    # already emitted.  The header chunk's identity is the very last
    # output line that begins with ``func <fn>`` and ends with ``{``.
    top_stream: List[str] = []
    main_body: List[str] = []
    # Indexed by function name → list of rendered body statements (in
    # source order).  Spliced into the top stream at assembly time.
    func_bodies: Dict[str, List[str]] = {}
    for ch, cj, fn in zip(translatable, rendered, translatable_func):
        if fn == "main":
            main_body.append(cj)
        elif fn is not None:
            func_bodies.setdefault(fn, []).append(cj)
        else:
            top_stream.append(cj)

    # 5. Cross-chunk structural lifting (struct init, methods, interfaces).
    # Lifting only inspects top-level decls, so apply it on the linear
    # stream of decl-like chunks.
    top_stream = synthesize_class_inits(top_stream)
    top_stream = promote_methods(top_stream)
    top_stream = attach_interface_impls(top_stream)

    # 5b. Splice each function's body statements between its translated
    # header and its closing ``}`` footer.  We walk the top stream and
    # collect every contiguous block ``func F(...) { → … → }`` into a
    # single composite declaration.
    top_decls = _splice_func_bodies(top_stream, func_bodies)

    # 6. Assemble.
    parts: List[str] = []
    if top_decls:
        parts.extend(top_decls)
    if wrap_main and not has_user_main and main_body:
        body = "\n".join("    " + ln for ln in "\n".join(main_body).split("\n")
                         if ln.strip())
        parts.append("main() {\n" + body + "\n    return 0\n}")
    elif not wrap_main:
        parts.extend(main_body)

    body_text = "\n\n".join(p for p in parts if p)
    body_text = _cosmetic(body_text)

    header = ""
    if _NEEDS_COLLECTION.search(body_text):
        header = "import std.collection.*\n\n"

    out = header + body_text
    if out and not out.endswith("\n"):
        out += "\n"
    result.source = out
    return result
