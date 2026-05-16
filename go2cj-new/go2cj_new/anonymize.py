"""Identifier / literal anonymization for the neural translator.

A trained seq2seq model on a small synthetic corpus cannot reliably
*memorise* every identifier or literal the user's Go source may use.
We therefore **anonymize** user identifiers, integer / float / string
literals before invoking the model, and **substitute them back** in
the model's output.

Anonymization scheme:

* Go keywords, built-in types (``int``, ``string`` …), and built-in
  function names (``fmt.Println``, ``len``, ``append``, ``make`` …)
  are **kept verbatim** — the model still needs to translate them.
* Every other identifier becomes ``ID0``, ``ID1``, …
* Every integer / float literal becomes ``NUM0``, ``NUM1``, …
* Every string literal becomes ``STR0``, ``STR1``, …
* Rune literals become ``CHR0``, ``CHR1``, …

The same numbering is used in both the input and the expected output
during training (the corpus generator emits anonymized pairs directly).
At inference time we anonymize the Go chunk, run the model, then
substitute the placeholders back to their original values.

This is a standard NMT-for-code trick (akin to copy mechanisms) that
slashes the effective vocabulary the model has to memorise and makes
identifier preservation **lossless**.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .tokenize import tokenize_text


GO_KEYWORDS = {
    "break", "case", "chan", "const", "continue", "default", "defer",
    "else", "fallthrough", "for", "func", "go", "goto", "if", "import",
    "interface", "map", "package", "range", "return", "select", "struct",
    "switch", "type", "var",
    "nil", "true", "false", "iota",
}

# Go primitive types (also kept verbatim — the model needs to translate
# them to Cangjie type names).
GO_TYPES = {
    "int", "int8", "int16", "int32", "int64",
    "uint", "uint8", "uint16", "uint32", "uint64", "uintptr",
    "byte", "rune", "float32", "float64", "complex64", "complex128",
    "bool", "string", "any", "error",
}

# Cangjie keywords / type names — kept verbatim so the model can produce
# them at the right places.
CJ_KEEPS = {
    "Int64", "Int32", "Int16", "Int8",
    "UInt64", "UInt32", "UInt16", "UInt8",
    "Float64", "Float32", "Bool", "String", "Rune", "Unit", "Any",
    "Exception", "None",
    "ArrayList", "HashMap", "HashSet", "Option", "Array",
    "let", "match", "while", "this", "super", "public", "private",
    "open", "class", "init", "override", "main", "in", "where",
    "size",
}

# Built-in Go functions / packages kept verbatim.  These are the
# tokens that have well-defined semantics in *both* languages — names
# that the model must translate, not just copy.
GO_BUILTINS = {
    # fmt package
    "fmt", "Println", "Print", "Printf", "Sprintf", "Sprintln",
    "Errorf", "Scanln", "Scan",
    # universe builtins
    "len", "cap", "append", "make", "new", "delete", "copy", "close",
    "panic", "recover",
    # Cangjie equivalents the decoder emits
    "print", "println",
    # std packages used in tests
    "os", "strings", "math", "strconv", "errors", "sort", "time", "rand",
    # functions referenced in trainset
    "Args", "Exit", "Getenv",
    "Sqrt", "Pow", "Abs", "Floor", "Ceil", "Max", "Min",
    "MaxInt64", "MinInt64", "Pi",
    "Itoa", "Atoi", "FormatInt", "ParseInt",
    "Contains", "HasPrefix", "HasSuffix", "ToUpper", "ToLower",
    "Split", "Join", "Replace", "Index",
    "Ints", "Strings",
    "New", "Now", "Sleep", "Second", "Intn",
    # Cangjie API surface
    "iterator", "enumerate", "keys", "values", "add", "remove",
    "size", "contains", "startsWith", "endsWith",
    "toAsciiUpper", "toAsciiLower", "split", "join", "replace",
    "indexOf", "toString", "parse", "fromUtf8", "toArray",
    "toRuneArray", "compare", "sortBy", "abs", "floor", "ceil", "sqrt",
    "max", "min", "isNone", "isSome",
    "Some", "Channel", "send", "receive", "spawn", "throw", "try",
    "catch", "finally",
    "Process", "current", "arguments", "exit",
    "EnvironmentVariables", "getOrDefault",
    "DateTime", "Duration", "second", "now",
    "Random", "nextInt64",
    "String", "fromUtf8", "delimiter",
    "Max", "Min",
}

KEEP_TOKENS = GO_KEYWORDS | GO_TYPES | CJ_KEEPS | GO_BUILTINS

# Number / string regexes for token classification.
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+([eE][+-]?\d+)?$|^-?\d*\.\d+$")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class Anonymization:
    """Mapping built by :func:`anonymize` and consumed by
    :func:`deanonymize`."""

    id_map: Dict[str, str] = field(default_factory=dict)      # ID0 → orig
    num_map: Dict[str, str] = field(default_factory=dict)     # NUM0 → orig
    str_map: Dict[str, str] = field(default_factory=dict)     # STR0 → orig
    chr_map: Dict[str, str] = field(default_factory=dict)     # CHR0 → orig


def _classify(tok: str) -> str:
    if tok.startswith('"') and tok.endswith('"'):
        return "str"
    if tok.startswith("'") and tok.endswith("'"):
        return "chr"
    if tok.startswith("`") and tok.endswith("`"):
        return "str"
    if _INT_RE.match(tok) or _FLOAT_RE.match(tok):
        return "num"
    if tok in KEEP_TOKENS:
        return "keep"
    # ``_`` is the universal wildcard / blank-identifier in both Go
    # (``for _, v := range …``) and Cangjie (``case _``).  Anonymising
    # it as a user identifier introduces a phantom placeholder that
    # then fails the strict ``placeholders ⊆ query`` subset check at
    # retrieval time, so we keep it as-is.
    if tok == "_":
        return "keep"
    if _IDENT_RE.match(tok):
        return "id"
    return "keep"


def anonymize_tokens(tokens: List[str]) -> Tuple[List[str], Anonymization]:
    """Replace user identifiers / literals in ``tokens`` with stable
    placeholder tokens.

    Returns the rewritten token list and the substitution table.
    """
    anon = Anonymization()
    id_idx: Dict[str, int] = {}     # orig → ID-index
    num_idx: Dict[str, int] = {}
    str_idx: Dict[str, int] = {}
    chr_idx: Dict[str, int] = {}
    out: List[str] = []
    for tok in tokens:
        kind = _classify(tok)
        if kind == "id":
            if tok not in id_idx:
                id_idx[tok] = len(id_idx)
                ph = f"ID{id_idx[tok]}"
                anon.id_map[ph] = tok
            out.append(f"ID{id_idx[tok]}")
        elif kind == "num":
            if tok not in num_idx:
                num_idx[tok] = len(num_idx)
                ph = f"NUM{num_idx[tok]}"
                anon.num_map[ph] = tok
            out.append(f"NUM{num_idx[tok]}")
        elif kind == "str":
            if tok not in str_idx:
                str_idx[tok] = len(str_idx)
                ph = f"STR{str_idx[tok]}"
                anon.str_map[ph] = tok
            out.append(f"STR{str_idx[tok]}")
        elif kind == "chr":
            if tok not in chr_idx:
                chr_idx[tok] = len(chr_idx)
                ph = f"CHR{chr_idx[tok]}"
                anon.chr_map[ph] = tok
            out.append(f"CHR{chr_idx[tok]}")
        else:
            out.append(tok)
    return out, anon


def deanonymize_tokens(tokens: List[str], anon: Anonymization) -> List[str]:
    out: List[str] = []
    for tok in tokens:
        if tok in anon.id_map:
            out.append(anon.id_map[tok])
        elif tok in anon.num_map:
            out.append(anon.num_map[tok])
        elif tok in anon.str_map:
            out.append(anon.str_map[tok])
        elif tok in anon.chr_map:
            out.append(anon.chr_map[tok])
        else:
            out.append(tok)
    return out


def anonymize_text(text: str) -> Tuple[str, Anonymization]:
    toks, anon = anonymize_tokens(tokenize_text(text))
    return " ".join(toks), anon


def anonymize_pair(go_text: str, cj_text: str) -> Tuple[str, str]:
    """Anonymize a parallel pair, using a *shared* placeholder map so
    the same Go ID maps to the same Cangjie ID."""
    go_toks = tokenize_text(go_text)
    cj_toks = tokenize_text(cj_text)
    anon = Anonymization()
    id_idx: Dict[str, int] = {}
    num_idx: Dict[str, int] = {}
    str_idx: Dict[str, int] = {}
    chr_idx: Dict[str, int] = {}

    def rewrite(toks):
        out = []
        for tok in toks:
            k = _classify(tok)
            if k == "id":
                if tok not in id_idx:
                    id_idx[tok] = len(id_idx)
                    anon.id_map[f"ID{id_idx[tok]}"] = tok
                out.append(f"ID{id_idx[tok]}")
            elif k == "num":
                if tok not in num_idx:
                    num_idx[tok] = len(num_idx)
                    anon.num_map[f"NUM{num_idx[tok]}"] = tok
                out.append(f"NUM{num_idx[tok]}")
            elif k == "str":
                if tok not in str_idx:
                    str_idx[tok] = len(str_idx)
                    anon.str_map[f"STR{str_idx[tok]}"] = tok
                out.append(f"STR{str_idx[tok]}")
            elif k == "chr":
                if tok not in chr_idx:
                    chr_idx[tok] = len(chr_idx)
                    anon.chr_map[f"CHR{chr_idx[tok]}"] = tok
                out.append(f"CHR{chr_idx[tok]}")
            else:
                out.append(tok)
        return out

    go_anon = rewrite(go_toks)
    cj_anon = rewrite(cj_toks)
    return " ".join(go_anon), " ".join(cj_anon)
