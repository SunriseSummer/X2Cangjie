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
from typing import List

from .lexer import Token, tokenize
from .lifting import (
    attach_interface_impls,
    promote_methods,
    synthesize_class_inits,
)
from .neural.translator import NeuralTranslator
from .neural.vocab import detokenize


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

    A chunk ends at a top-level ``;`` *or* at the ``}`` that closes a
    previously opened ``{`` — unless followed by ``else``.  We track a
    ``in_for_header`` flag so the ``;`` inside ``for init; cond; step``
    are kept inside the chunk rather than separating it.
    """

    toks = [t for t in tokens
            if t.kind not in ("NEWLINE", "COMMENT_BLOCK", "COMMENT_LINE")]
    chunks: List[List[Token]] = []
    cur: List[Token] = []
    db = dp = ds = 0
    in_for_header = False
    i = 0
    n = len(toks)
    while i < n:
        t = toks[i]
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
                    nxt = toks[i + 1] if i + 1 < n else None
                    if (nxt is not None and nxt.kind == "KEYWORD"
                            and nxt.value == "else"):
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


def _render_chunk(chunk: List[Token]) -> str:
    """Render a chunk's tokens as a single text line for NN input.

    We separate tokens with a single space — matching the tokenizer
    used by :mod:`go2cj.neural.vocab` so the model sees consistent
    spacing.
    """
    parts: List[str] = []
    prev: str = ""
    for t in chunk:
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
    chunks = _segment_chunks(tokens)

    # 2. Skim ``package`` / ``import`` and identify ``func main``.
    translatable: List[List[Token]] = []
    has_user_main = False
    for ch in chunks:
        if not ch:
            continue
        if ch[0].kind == "KEYWORD" and ch[0].value in ("package", "import"):
            continue
        if (len(ch) >= 3 and ch[0].kind == "KEYWORD" and ch[0].value == "func"
                and ch[1].value == "main" and ch[2].value == "("):
            has_user_main = True
        translatable.append(ch)

    result = ConversionResult(source="", notes=notes, chunks=len(translatable))

    if not translatable:
        result.source = ""
        return result

    # 3. Run the trained neural model on every chunk.
    translator = NeuralTranslator.get()
    go_texts = [_render_chunk(ch) for ch in translatable]
    cj_texts = translator.translate_batch(go_texts)

    rendered: List[str] = []
    for cj in cj_texts:
        cj = cj.strip()
        if not cj:
            result.fallback_chunks += 1
            rendered.append("/* go2cj: empty model output */")
        else:
            result.confident_chunks += 1
            rendered.append(cj)

    # 4. Classify into top-level decls vs main-body free statements.
    top_decls: List[str] = []
    main_body: List[str] = []
    for ch, cj in zip(translatable, rendered):
        first = ch[0].value if ch else ""
        if first in ("func", "type", "var", "const", "interface", "class"):
            top_decls.append(cj)
        else:
            main_body.append(cj)

    # 5. Cross-chunk structural lifting (struct init, methods, interfaces).
    top_decls = synthesize_class_inits(top_decls)
    top_decls = promote_methods(top_decls)
    top_decls = attach_interface_impls(top_decls)

    # 6. Assemble.
    parts: List[str] = []
    if top_decls:
        parts.extend(top_decls)
    if wrap_main and not has_user_main and main_body:
        body = "\n".join("    " + ln for ln in "\n".join(main_body).split("\n")
                         if ln.strip())
        parts.append("main(): Unit {\n" + body + "\n    return 0\n}")
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
