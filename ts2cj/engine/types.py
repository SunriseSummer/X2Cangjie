"""Type-mapping helpers used by the transformer.

These helpers are deliberately *fuzzy* – they make a best-effort decision
based on the surface form of a TS type annotation, without performing real
type inference.  The whole converter is built around the premise that small
mis-decisions are acceptable.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .knowledge import TYPE_MAP, INT_TYPE_HINTS, FLOAT_TYPE_HINTS, escape_id
from .tokenizer import Tok, tokenize


def _strip_trivia(tokens: List[Tok]) -> List[Tok]:
    return [t for t in tokens if t.kind not in ("ws", "nl", "cmt")]


def map_type_string(ts_type: str, *, int_hint: bool = False) -> str:
    """Translate a TypeScript type expression string into Cangjie syntax."""
    # quick reject empty
    if not ts_type or not ts_type.strip():
        return ""
    # Tokenize on the fly so we handle `Array<number>`, `number[]`,
    # `string | null`, `Map<string, number>`, function types, etc.
    toks = _strip_trivia(tokenize(ts_type))
    return _map_type_tokens(toks, int_hint=int_hint)[0]


def _map_type_tokens(toks: List[Tok], *, int_hint: bool = False) -> Tuple[str, int]:
    """Return (cangjie type, consumed token count)."""
    if not toks:
        return "Unit", 0
    parts: List[str] = []
    # parse alternatives separated by '|' (top level only)
    alt: List[str] = []
    i = 0
    while i < len(toks):
        out, used = _map_one_type(toks, i, int_hint=int_hint)
        alt.append(out)
        i += used
        if i < len(toks) and toks[i].kind == "op" and toks[i].value == "|":
            i += 1
            continue
        break
    # collapse `string | null` / `T | undefined` to `?T`
    nulls = {"Unit", "None"}
    non_null = [a for a in alt if a not in nulls]
    has_null = any(a in nulls for a in alt)
    if has_null and len(non_null) == 1:
        result = f"?{non_null[0]}"
    elif len(alt) == 1:
        result = alt[0]
    else:
        # Cangjie has no union; degrade to Any
        result = "Any"
    return result, i


def _map_one_type(toks: List[Tok], i: int, *, int_hint: bool = False) -> Tuple[str, int]:
    if i >= len(toks):
        return "Unit", 0
    t = toks[i]

    # parenthesised group or function type:  (x: T) => R
    if t.kind == "punct" and t.value == "(":
        depth = 1
        j = i + 1
        while j < len(toks) and depth > 0:
            if toks[j].kind == "punct" and toks[j].value == "(":
                depth += 1
            elif toks[j].kind == "punct" and toks[j].value == ")":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        inner = toks[i + 1:j]
        rest_start = j + 1
        # Function type?
        if rest_start < len(toks) and toks[rest_start].kind == "op" and toks[rest_start].value == "=>":
            ret_tokens = toks[rest_start + 1:]
            ret_type = _map_type_tokens(ret_tokens, int_hint=int_hint)[0] or "Unit"
            params = _split_params(inner)
            cj_params = []
            for p in params:
                # strip param name and optional marker
                ptype = _extract_param_type(p)
                cj_params.append(_map_type_tokens(ptype)[0] if ptype else "Any")
            return f"({', '.join(cj_params)}) -> {ret_type}", len(toks) - i
        # Just a parenthesised type – recurse
        inner_t, _ = _map_type_tokens(inner, int_hint=int_hint)
        consumed = j - i + 1
        # post-fix `[]`
        while rest_start + 0 < len(toks) and rest_start < len(toks) and toks[rest_start].kind == "punct" and toks[rest_start].value == "[":
            if rest_start + 1 < len(toks) and toks[rest_start + 1].kind == "punct" and toks[rest_start + 1].value == "]":
                inner_t = f"Array<{inner_t}>"
                rest_start += 2
                consumed = rest_start - i
            else:
                break
        return inner_t, consumed

    # literal type: string/number literal — degrade
    if t.kind in ("str", "num", "tpl"):
        return "Any", 1

    # bare identifier
    if t.kind in ("id", "kw"):
        name = t.value
        # 'null' / 'undefined' / 'void'
        if name in ("null", "undefined"):
            return "Unit", 1
        if name == "void":
            return "Unit", 1
        if name == "this":
            return "This", 1
        consumed = 1
        # generic args
        generic = ""
        # check for `<...>`
        # (Cannot reliably distinguish `<` from comparison in arbitrary
        # contexts but in *type position* it's safe.)
        if i + 1 < len(toks) and toks[i + 1].kind == "op" and toks[i + 1].value == "<":
            depth = 1
            j = i + 2
            while j < len(toks) and depth > 0:
                v = toks[j].value
                if v == "<":
                    depth += 1
                elif v == ">":
                    depth -= 1
                    if depth == 0:
                        break
                elif v == ">>":
                    depth -= 2
                    if depth <= 0:
                        break
                j += 1
            inner = toks[i + 2:j]
            # split on top-level commas
            args = _split_top_commas(inner)
            cj_args = [_map_type_tokens(a)[0] for a in args]
            generic = f"<{', '.join(cj_args)}>"
            consumed = j - i + 1
        mapped = TYPE_MAP.get(name)
        if mapped is None:
            if name in INT_TYPE_HINTS:
                mapped = "Int64"
            elif name in FLOAT_TYPE_HINTS:
                mapped = "Float64"
            else:
                mapped = name  # user-defined type, keep as-is
        # Adjust number → Int64 if int_hint
        if mapped == "Float64" and int_hint:
            mapped = "Int64"
        out = mapped + generic
        # Handle `T[]`
        while consumed + i < len(toks) and toks[i + consumed].kind == "punct" and toks[i + consumed].value == "[":
            if i + consumed + 1 < len(toks) and toks[i + consumed + 1].kind == "punct" and toks[i + consumed + 1].value == "]":
                out = f"Array<{out}>"
                consumed += 2
            else:
                break
        return out, consumed

    # `[T, U, ...]` tuple type → Cangjie `(T, U, ...)`
    if t.kind == "punct" and t.value == "[":
        depth = 1
        j = i + 1
        while j < len(toks) and depth > 0:
            if toks[j].kind == "punct" and toks[j].value == "[":
                depth += 1
            elif toks[j].kind == "punct" and toks[j].value == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        inner = toks[i + 1:j]
        # If inner contains top-level commas it's a tuple; otherwise it's
        # actually an empty array marker handled elsewhere.
        parts = _split_top_commas(inner)
        if len(parts) >= 2:
            mapped_parts = []
            for p in parts:
                mp, _ = _map_type_tokens(p, int_hint=int_hint)
                mapped_parts.append(mp or "Any")
            return f"({', '.join(mapped_parts)})", j - i + 1
        # fall through — treat as Any
        return "Any", j - i + 1

    # `{...}` object type – degrade to Any
    if t.kind == "punct" and t.value == "{":
        depth = 1
        j = i + 1
        while j < len(toks) and depth > 0:
            if toks[j].kind == "punct" and toks[j].value == "{":
                depth += 1
            elif toks[j].kind == "punct" and toks[j].value == "}":
                depth -= 1
            j += 1
        return "Any", j - i

    # unknown — degrade
    return "Any", 1


def _split_params(toks: List[Tok]) -> List[List[Tok]]:
    return _split_top_commas(toks)


def _split_top_commas(toks: List[Tok]) -> List[List[Tok]]:
    out: List[List[Tok]] = []
    cur: List[Tok] = []
    depth_paren = depth_ang = depth_bracket = depth_brace = 0
    for t in toks:
        v = t.value
        if t.kind == "punct" and v == "(":
            depth_paren += 1
        elif t.kind == "punct" and v == ")":
            depth_paren -= 1
        elif t.kind == "punct" and v == "[":
            depth_bracket += 1
        elif t.kind == "punct" and v == "]":
            depth_bracket -= 1
        elif t.kind == "punct" and v == "{":
            depth_brace += 1
        elif t.kind == "punct" and v == "}":
            depth_brace -= 1
        elif t.kind == "op" and v == "<":
            depth_ang += 1
        elif t.kind == "op" and v == ">":
            depth_ang = max(0, depth_ang - 1)
        if (t.kind == "punct" and v == "," and depth_paren == depth_ang
                == depth_bracket == depth_brace == 0):
            out.append(cur)
            cur = []
            continue
        cur.append(t)
    if cur:
        out.append(cur)
    return out


def _extract_param_type(p: List[Tok]) -> List[Tok]:
    """Return tokens after the first ':' (the type annotation)."""
    for k, t in enumerate(p):
        if t.kind == "punct" and t.value == ":":
            return p[k + 1:]
    return []


# Heuristic: given an initializer token stream, infer a likely CJ type.
def infer_init_type(init_toks: List[Tok]) -> Optional[str]:
    sig = _strip_trivia(init_toks)
    if not sig:
        return None
    # array literal
    if sig[0].kind == "punct" and sig[0].value == "[":
        # peek first element kind
        for t in sig[1:]:
            if t.kind in ("ws", "nl", "cmt"):
                continue
            if t.kind == "num":
                return "Array<Int64>" if not t.meta.get("float") else "Array<Float64>"
            if t.kind == "str" or t.kind == "tpl":
                return "Array<String>"
            if t.kind == "kw" and t.value in ("true", "false"):
                return "Array<Bool>"
            break
        return None
    if sig[0].kind == "str" or sig[0].kind == "tpl":
        return "String"
    if sig[0].kind == "kw" and sig[0].value in ("true", "false"):
        return "Bool"
    if sig[0].kind == "num":
        return "Int64" if not sig[0].meta.get("float") else "Float64"
    if sig[0].kind == "kw" and sig[0].value == "new":
        # `new Map<K,V>()` etc.
        if len(sig) > 1 and sig[1].kind in ("id", "kw"):
            ctor = sig[1].value
            mapped = TYPE_MAP.get(ctor, ctor)
            # gather generics
            rest = sig[2:]
            if rest and rest[0].kind == "op" and rest[0].value == "<":
                # find matching '>'
                depth = 1
                j = 1
                while j < len(rest) and depth > 0:
                    if rest[j].kind == "op" and rest[j].value == "<":
                        depth += 1
                    elif rest[j].kind == "op" and rest[j].value == ">":
                        depth -= 1
                    j += 1
                gens = rest[1:j - 1]
                arg_strs = [_map_type_tokens(a)[0] for a in _split_top_commas(gens)]
                return f"{mapped}<{', '.join(arg_strs)}>"
            return mapped
    return None


__all__ = ["map_type_string", "infer_init_type", "escape_id"]
