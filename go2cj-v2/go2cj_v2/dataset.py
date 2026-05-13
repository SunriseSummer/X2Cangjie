"""Curated trainset loader for go2cj-v2.

Mirrors ``go2cj.neural.curated`` but **without anonymization**.  CodeT5's
byte-level BPE tokenizer handles arbitrary user identifiers and literals
natively (they tokenise to a short sequence of subword pieces), so we
feed raw Go source text and expect raw Cangjie source text.  Augmentation
is achieved instead by **identifier renaming**: each curated pair is
expanded by substituting its user identifiers with random alternatives
drawn from a small pool, producing a few dozen surface variants per
canonical mapping.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple


_PKG = Path(__file__).resolve().parent
_REPO_ROOT = _PKG.parent  # go2cj-v2/


def trainset_root() -> Path:
    return _REPO_ROOT / "trainset"


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def load_jsonl_pairs(path: Optional[Path] = None) -> List[Tuple[str, str]]:
    if path is None:
        path = trainset_root() / "pairs.jsonl"
    if not path.is_file():
        return []
    out: List[Tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for ln_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            obj = json.loads(line)
            go = (obj.get("go") or "").strip()
            cj = (obj.get("cj") or "").strip()
            if go and cj:
                out.append((go, cj))
    return out


def _split_program(text: str) -> List[str]:
    chunks: List[str] = []
    cur: List[str] = []
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if cur and depth == 0:
                joined = " ".join(s for s in cur if s)
                if joined:
                    chunks.append(joined)
                cur = []
            continue
        if depth == 0 and (
            stripped.startswith("package ") or stripped.startswith("import ")
            or stripped == "package main"
        ):
            continue
        cur.append(stripped)
        for ch in stripped:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth = max(depth - 1, 0)
        if depth == 0 and cur:
            chunks.append(" ".join(s for s in cur if s))
            cur = []
    if cur:
        chunks.append(" ".join(s for s in cur if s))
    return [c for c in chunks if c]


def load_program_pairs(programs_dir: Optional[Path] = None
                       ) -> List[Tuple[str, str]]:
    if programs_dir is None:
        programs_dir = trainset_root() / "programs"
    if not programs_dir.is_dir():
        return []
    out: List[Tuple[str, str]] = []
    for go_path in sorted(programs_dir.glob("*.go")):
        cj_path = go_path.with_suffix(".cj")
        if not cj_path.is_file():
            continue
        gs = _split_program(go_path.read_text("utf-8"))
        cs = _split_program(cj_path.read_text("utf-8"))
        if len(gs) != len(cs):
            continue
        for g, c in zip(gs, cs):
            if g and c:
                out.append((g, c))
    return out


def load_curated_pairs() -> List[Tuple[str, str]]:
    return load_jsonl_pairs() + load_program_pairs()


# ----------------------------------------------------------------------------
# Augmentation by identifier renaming
# ----------------------------------------------------------------------------
# Go / Cangjie keywords and built-ins we MUST NOT rename — same as the v1
# anonymization layer's "keep verbatim" set.
_PROTECTED: Set[str] = {
    # Go keywords
    "break", "case", "chan", "const", "continue", "default", "defer",
    "else", "fallthrough", "for", "func", "go", "goto", "if", "import",
    "interface", "map", "package", "range", "return", "select", "struct",
    "switch", "type", "var",
    # Go built-in types
    "bool", "byte", "rune", "string", "int", "int8", "int16", "int32",
    "int64", "uint", "uint8", "uint16", "uint32", "uint64", "uintptr",
    "float32", "float64", "complex64", "complex128", "error", "any",
    "true", "false", "nil", "iota",
    # Go std API tokens the model still needs to translate
    "fmt", "Println", "Printf", "Print", "Sprintf", "Sprintln", "Errorf",
    "strings", "strconv", "math", "os", "errors", "sort", "len", "cap",
    "append", "make", "new", "copy", "delete", "panic", "recover", "print",
    "Sprint", "Atoi", "Itoa", "Sqrt", "Pow", "Abs", "Floor", "Ceil", "Min",
    "Max", "Contains", "HasPrefix", "HasSuffix", "Index", "Split", "Join",
    "Replace", "ToUpper", "ToLower", "TrimSpace", "Trim", "Repeat",
    # Cangjie keywords / built-ins (so we don't rename them on the cj side)
    "let", "main", "Unit", "Int8", "Int16", "Int32", "Int64", "Int", "UInt8",
    "UInt16", "UInt32", "UInt64", "Float32", "Float64", "Bool", "Rune",
    "String", "Array", "ArrayList", "HashMap", "HashSet", "Option",
    "this", "super", "init", "println", "print", "match", "where",
    "open", "override", "operator", "abstract", "public", "private",
    "protected", "internal", "class", "extend", "throw", "throws",
    "try", "catch", "finally", "in", "out", "is", "as", "Some", "None",
    "Ok", "Err", "true", "false",
    "fromUtf8", "toString", "size", "isEmpty", "get", "put", "add",
    "remove", "contains", "containsKey", "keys", "values", "subString",
    "subStr",
}


_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"')


def _collect_user_idents(go: str, cj: str) -> List[str]:
    """Return the deterministic list of user identifiers that appear in
    BOTH the Go and Cangjie sides — these are safe to rename together."""
    def names(s: str) -> Set[str]:
        # Mask strings so identifiers inside strings don't get renamed.
        masked = _STRING_RE.sub('""', s)
        return {m.group(0) for m in _IDENT_RE.finditer(masked)
                if m.group(0) not in _PROTECTED}

    g = names(go)
    c = names(cj)
    common = sorted(g & c)
    return common


_POOL = [
    "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
    "m", "n", "p", "q", "r", "s", "t", "u", "v", "w",
    "alpha", "beta", "gamma", "delta", "lhs", "rhs", "lo", "hi", "mid",
    "src", "dst", "buf", "tmp", "acc", "cnt", "tot", "sum", "avg", "cur",
    "prev", "next", "head", "tail", "node", "item", "elem", "data", "arr",
    "vec", "list", "stack", "queue", "key", "val", "kv", "name", "msg",
    "out", "ret", "res", "result", "answer", "ok", "flag", "found",
    "first", "second", "third", "left", "right", "top", "bot", "row", "col",
    "Foo", "Bar", "Baz", "Quux", "Point", "Pair", "Box", "Item", "User",
    "Node", "Cell", "Shape", "Animal", "Counter", "Stack", "Queue",
]


def _rename_in_text(text: str, mapping) -> str:
    # Tokenise lightly: protect strings so we don't rename inside them.
    spans = []
    last = 0
    parts: List[str] = []
    for m in _STRING_RE.finditer(text):
        spans.append((m.start(), m.end()))
    for s, e in spans:
        parts.append(_apply_mapping(text[last:s], mapping))
        parts.append(text[s:e])
        last = e
    parts.append(_apply_mapping(text[last:], mapping))
    return "".join(parts)


def _apply_mapping(text: str, mapping) -> str:
    def sub(m):
        name = m.group(0)
        return mapping.get(name, name)
    return _IDENT_RE.sub(sub, text)


def augment_pairs(pairs: List[Tuple[str, str]], factor: int = 16,
                  seed: int = 0xBEEF) -> List[Tuple[str, str]]:
    """Expand pairs by random consistent identifier renaming.

    For each pair, ``factor`` variants are produced (plus the original).
    Each variant picks a random alternative name from ``_POOL`` for every
    user identifier that appears in both sides.
    """
    rng = random.Random(seed)
    out: List[Tuple[str, str]] = []
    for go, cj in pairs:
        out.append((go, cj))
        idents = _collect_user_idents(go, cj)
        if not idents:
            # Still emit ``factor`` copies of the canonical form to keep
            # batch weighting consistent.
            for _ in range(max(0, factor - 1)):
                out.append((go, cj))
            continue
        for _ in range(max(0, factor - 1)):
            pool = list(_POOL)
            rng.shuffle(pool)
            mapping = {old: pool[i % len(pool)] for i, old in enumerate(idents)}
            # Avoid mapping a name to itself or to another existing source name.
            forbidden = set(idents) | _PROTECTED
            for old, new in list(mapping.items()):
                if new == old or new in forbidden - {old}:
                    # Pick a replacement deterministically from the pool.
                    for cand in pool:
                        if cand != old and cand not in forbidden:
                            mapping[old] = cand
                            break
            out.append(
                (_rename_in_text(go, mapping),
                 _rename_in_text(cj, mapping)),
            )
    return out


def load_curated_corpus(augment_factor: int = 16
                        ) -> List[Tuple[str, str]]:
    pairs = load_curated_pairs()
    if augment_factor <= 1:
        return pairs
    return augment_pairs(pairs, factor=augment_factor)


__all__ = [
    "trainset_root",
    "load_jsonl_pairs",
    "load_program_pairs",
    "load_curated_pairs",
    "augment_pairs",
    "load_curated_corpus",
]
