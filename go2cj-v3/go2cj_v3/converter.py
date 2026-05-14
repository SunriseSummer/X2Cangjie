"""Go → Cangjie converter (CodeT5-small fine-tuned backbone).

End-to-end pipeline (mirrors go2cj v1 — only the per-chunk translation
core changed):

1. **Pre-process** raw strings, lex with the Go regex lexer.
2. **Segment** the token stream into top-level chunks by brace / `;` balance.
3. **Render** each chunk back to Go source text (CodeT5's byte-level BPE
   prefers natural source over space-separated token streams).
4. Call the fine-tuned **CodeT5-small** in batch to translate every chunk.
5. **Lift** cross-chunk structural artefacts (struct → class, free methods,
   implicit interfaces).
6. **Assemble**: drop ``package`` / ``import``, inject ``import std.collection.*``
   when needed, wrap free statements into ``main()`` when no user ``func main``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

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
from .translator import NeuralTranslator


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
#  Pre-processing                                                             #
# --------------------------------------------------------------------------- #
def _convert_raw_strings(src: str) -> str:
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


# Tokens that should not have a leading space when rendering back to source.
_NO_SPACE_BEFORE = {",", ";", ":", ")", "]", "}", ".", "(", "["}
_NO_SPACE_AFTER = {".", "(", "[", "!"}


def _render_chunk(chunk: List[Token]) -> str:
    """Render a chunk's tokens back to compact Go source text.

    We assemble with single spaces between tokens, but suppress the
    space before / after punctuation that conventionally has none.
    This makes the text we feed to CodeT5 look like real Go source
    (which is what the model saw during pre-training).
    """
    parts: List[str] = []
    for i, t in enumerate(chunk):
        v = t.value
        if not parts:
            parts.append(v)
            continue
        prev = chunk[i - 1].value
        if v in _NO_SPACE_BEFORE or prev in _NO_SPACE_AFTER:
            parts.append(v)
        else:
            parts.append(" " + v)
    return "".join(parts).strip()


# --------------------------------------------------------------------------- #
#  Cosmetic post-processing                                                   #
# --------------------------------------------------------------------------- #
_NEEDS_COLLECTION = re.compile(r"\b(?:ArrayList|HashMap|HashSet)\b")


def _split_statements(text: str) -> str:
    """Break a possibly single-line Cangjie source into multi-line form.

    The fine-tuned model — trained on chunks rendered as flat,
    space-separated source text — tends to emit its translations on
    one line.  Cangjie's parser is line-sensitive in many places
    (``} return ...``, ``} var ...``, etc. all need either ``;`` or a
    newline between the closing brace and the next statement).  This
    helper inserts newlines at the canonical statement boundaries.

    We walk the text and track string + brace context so we never split
    inside a string literal or function-call parenthesis list.
    """
    out: List[str] = []
    i = 0
    n = len(text)
    paren = bracket = 0
    in_str = False
    str_ch = ""
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == str_ch:
                in_str = False
            i += 1
            continue
        if c in ('"', "'"):
            in_str = True
            str_ch = c
            out.append(c)
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
        out.append(c)
        # Break after ';' or '}' at top level (outside () and []).
        if paren == 0 and bracket == 0:
            if c == ";":
                # Skip following whitespace, then insert newline if not already.
                j = i + 1
                while j < n and text[j] in (" ", "\t"):
                    j += 1
                if j < n and text[j] != "\n":
                    out.append("\n")
                i = j
                # Drop trailing semicolon's trailing spaces consumed above.
                continue
            if c == "}":
                # Look ahead: if next non-space token starts a new statement
                # (NOT one of else/catch/finally/while/,/;/)/]/}/./?), insert NL.
                j = i + 1
                while j < n and text[j] in (" ", "\t"):
                    j += 1
                if j < n and text[j] != "\n":
                    nxt = text[j]
                    if nxt in (",", ";", ")", "]", "}", ".", "?"):
                        pass  # legitimate continuation, no break
                    else:
                        # Peek the next word token.
                        m = re.match(r"[A-Za-z_]\w*", text[j:])
                        word = m.group(0) if m else ""
                        if word not in ("else", "catch", "finally", "while"):
                            out.append("\n")
                            i = j
                            continue
        i += 1
    return "".join(out)


def _indent_block(text: str, indent: str = "    ") -> str:
    """Indent a brace-delimited body for readability.

    Walks each line, decrements indent on lines starting with ``}`` and
    increments after lines ending with ``{``.  Mainly cosmetic — Cangjie
    doesn't care about indentation, but it makes the generated code and
    cjc diagnostics readable.
    """
    out: List[str] = []
    depth = 0
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            out.append("")
            continue
        d = depth
        if line.startswith("}") or line.startswith(")"):
            d = max(depth - 1, 0)
        out.append(indent * d + line)
        # Update depth from net braces on this line.
        for ch in line:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(depth - 1, 0)
    return "\n".join(out)


def _cosmetic(text: str) -> str:
    text = re.sub(r"\b(ArrayList|HashMap|HashSet|Option|Array)\s+<\s*",
                  r"\1<", text)
    text = re.sub(r"\s+>\s*\(", ">(", text)
    text = re.sub(r"\s+,", ",", text)
    text = _split_statements(text)
    text = _indent_block(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text


# --------------------------------------------------------------------------- #
#  Main entry point                                                           #
# --------------------------------------------------------------------------- #
def convert_source(go_source: str, wrap_main: bool = True) -> ConversionResult:
    notes: List[str] = []

    src = _convert_raw_strings(go_source)
    tokens = tokenize(src)
    tokens = _inject_semis(tokens)
    chunks = _segment_chunks(tokens)

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
        return result

    translator = NeuralTranslator.get()
    go_texts = [_render_chunk(ch) for ch in translatable]
    cj_texts = translator.translate_batch(go_texts)

    rendered: List[str] = []
    for cj in cj_texts:
        cj = (cj or "").strip()
        if not cj:
            result.fallback_chunks += 1
            rendered.append("/* go2cj_v3: empty model output */")
        else:
            result.confident_chunks += 1
            rendered.append(cj)

    top_decls: List[str] = []
    main_body: List[str] = []
    for ch, cj in zip(translatable, rendered):
        first = ch[0].value if ch else ""
        if first in ("func", "type", "var", "const", "interface", "class"):
            top_decls.append(cj)
        else:
            main_body.append(cj)

    top_decls = synthesize_class_inits(top_decls)
    top_decls = promote_methods(top_decls)
    top_decls = attach_interface_impls(top_decls)

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
