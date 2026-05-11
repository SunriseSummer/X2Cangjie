"""Expert-system knowledge base.

Tables of facts: type mappings, API call mappings, keyword mappings.
Rules elsewhere consult this module to resolve TypeScript surface forms
into Cangjie equivalents.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Type mappings (TypeScript surface name → Cangjie type name)
# ---------------------------------------------------------------------------
#
# `number` is ambiguous (Cangjie distinguishes Int64/Float64). The rule
# engine picks based on heuristics. Default fallback is Float64 since TS
# numbers are IEEE-754 doubles, but if context says "integer", we use Int64.

TYPE_MAP = {
    "number": "Int64",           # default — heuristics may override to Float64
    "string": "String",
    "boolean": "Bool",
    "bigint": "Int64",
    "void": "Unit",
    "any": "Any",
    "unknown": "Any",
    "never": "Nothing",
    "object": "Any",
    "null": "Unit",
    "undefined": "Unit",
    "Array": "Array",
    "ReadonlyArray": "Array",
    "Map": "HashMap",
    "Set": "HashSet",
    "Date": "String",            # crude fallback
    "Error": "Exception",
    "RegExp": "String",
    "Promise": "Future",
}

# Integer-ish names users sometimes write
INT_TYPE_HINTS = {"int", "Int", "Int32", "Int64", "long", "Long"}
FLOAT_TYPE_HINTS = {"float", "Float", "Float32", "Float64", "double", "Double"}


# ---------------------------------------------------------------------------
# Built-in identifier / API mappings
# ---------------------------------------------------------------------------

GLOBAL_IDENT = {
    "console.log": "println",
    "console.error": "println",
    "console.warn": "println",
    "console.info": "println",
    "console.debug": "println",
    "Math.PI": "3.14159265358979323846",
    "Math.E": "2.71828182845904523536",
    "Math.abs": "abs",          # we emit a small abs helper
    "Math.max": "max",
    "Math.min": "min",
    "Math.floor": "floor",
    "Math.ceil": "ceil",
    "Math.round": "round",
    "Math.sqrt": "sqrt",
    "Math.pow": "pow",
    "Math.random": "random",
    "Number.MAX_SAFE_INTEGER": "Int64.Max",
    "Number.MIN_SAFE_INTEGER": "Int64.Min",
    "Number.MAX_VALUE": "Float64.Max",
    "Number.MIN_VALUE": "Float64.Min",
    "JSON.stringify": "/* JSON.stringify */ toString",
    "JSON.parse":     "/* JSON.parse */ String",
}

# Single-token identifier replacements (top-level globals)
PLAIN_IDENT = {
    "undefined": "None",
    "NaN": "Float64.NaN",
    "Infinity": "Float64.Inf",
    "console": "/*console*/",   # used only when not part of console.X
}

# Member-call rewrites: when we see `obj.method(...)`, rewrite the method
# name.  Object identity is not known — these are best-effort.
METHOD_RENAME = {
    # String methods
    "toUpperCase": ("toAsciiUpper", "method"),
    "toLowerCase": ("toAsciiLower", "method"),
    "trim":        ("trimAscii",    "method"),
    "trimStart":   ("trimAsciiStart","method"),
    "trimEnd":     ("trimAsciiEnd",  "method"),
    "includes":    ("contains",     "method"),
    "startsWith":  ("startsWith",   "method"),
    "endsWith":    ("endsWith",     "method"),
    "indexOf":     ("indexOf",      "method"),
    "lastIndexOf": ("lastIndexOf",  "method"),
    "replace":     ("replace",      "method"),
    "concat":      ("concat",       "method"),
    "slice":       ("slice",        "method"),     # handled specially → [a..b]
    "substring":   ("substring",    "method"),     # handled specially → [a..b]
    "substr":      ("substring",    "method"),     # handled specially → [a..b]
    "split":       ("split",        "method"),
    # Array iteration (these become higher-order calls)
    "forEach":     ("forEach",      "method"),
    "map":         ("map",          "method"),
    "filter":      ("filter",       "method"),
    "reduce":      ("reduce",       "method"),
    "find":        ("first",        "method"),
    "some":        ("any",          "method"),
    "every":       ("all",          "method"),
    "push":        ("push",         "method"),    # leave alone (user-defined)
    "pop":         ("pop",          "method"),    # leave alone (user-defined)
    "shift":       ("removeFirst",  "method"),
    "unshift":     ("prepend",      "method"),
    "has":         ("contains",     "method"),    # HashSet / HashMap
    "delete":      ("remove",       "method"),
    "clear":       ("clear",        "method"),
    "join":        ("toString",     "method"),
    "reverse":     ("reverse",      "method"),
    "sort":        ("sort",         "method"),
    "toString":    ("toString",     "method"),
    # Number methods (TS: x.toFixed(2)).  We replace with a textual cast.
    "toFixed":     ("toString",     "method"),
}


# ---------------------------------------------------------------------------
# Cangjie reserved words — escape them when used as identifiers.
# ---------------------------------------------------------------------------

CJ_RESERVED = {
    "Bool", "Rune", "Float16", "Float32", "Float64", "Int8", "Int16", "Int32",
    "Int64", "IntNative", "UInt8", "UInt16", "UInt32", "UInt64", "UIntNative",
    "Array", "VArray", "String", "Nothing", "Unit",
    "break", "case", "catch", "continue", "do", "else", "finally", "for",
    "if", "match", "return", "spawn", "try", "throw", "while",
    "as", "abstract", "class", "const", "enum", "extend", "func", "foreign",
    "import", "init", "interface", "let", "macro", "main", "mut", "open",
    "operator", "override", "package", "private", "prop", "protected",
    "public", "redef", "static", "struct", "super", "synchronized", "this",
    "This", "type", "unsafe", "where",
    "false", "true", "quote",
}


def escape_id(name: str) -> str:
    """Return a Cangjie-safe identifier.

    Cangjie keywords can be used as identifiers by quoting in backticks.
    """
    if name in CJ_RESERVED:
        return f"`{name}`"
    return name
