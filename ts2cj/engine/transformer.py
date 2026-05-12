"""Transformer: orchestrates the lexer → rule-engine → renderer pipeline.

The transformer applies several waves of rules:

  Wave 0  – textual / token cleanups
  Wave 1  – type-annotation rewrites
  Wave 2  – statement-level rewrites (var decls, control flow, funcs)
  Wave 3  – expression-level rewrites (templates, calls, operators)
  Wave 4  – top-level scan: classify decls vs script statements, wrap in main

After the rewrites a renderer prints the token stream back to source.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .knowledge import (
    GLOBAL_IDENT, METHOD_RENAME, PLAIN_IDENT, escape_id, TYPE_MAP,
)
from .tokenizer import Tok, tokenize
from .types import map_type_string, infer_init_type


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ConversionResult:
    source: str
    rule_fires: int = 0
    confidence: float = 0.0
    notes: List[str] = field(default_factory=list)
    helpers: list = field(default_factory=list)

    @property
    def quality(self) -> float:
        # 0..1: a rough self-rating.  More rules firing on a piece of TS
        # raises confidence; fewer notes raises it; tokens left untouched
        # lower it.
        score = 1.0
        score -= 0.05 * len(self.notes)
        return max(0.0, min(1.0, score))


# ---------------------------------------------------------------------------
# Utilities operating on token lists
# ---------------------------------------------------------------------------

def _strip_trivia(toks: List[Tok]) -> List[Tok]:
    return [t for t in toks if t.kind not in ("ws", "nl", "cmt")]


def _to_text(toks: List[Tok]) -> str:
    return "".join(t.value for t in toks)


def _next_sig(toks: List[Tok], i: int) -> int:
    while i < len(toks) and toks[i].kind in ("ws", "nl", "cmt"):
        i += 1
    return i


def _prev_sig(toks: List[Tok], i: int) -> int:
    j = i - 1
    while j >= 0 and toks[j].kind in ("ws", "nl", "cmt"):
        j -= 1
    return j


def _match_pair(toks: List[Tok], i: int, opn: str, cls: str) -> int:
    """tokens[i] must be `opn`. Return idx of matching close, or -1."""
    if i >= len(toks) or not (toks[i].kind == "punct" and toks[i].value == opn):
        return -1
    depth = 1
    j = i + 1
    while j < len(toks):
        t = toks[j]
        if t.kind == "punct" and t.value == opn:
            depth += 1
        elif t.kind == "punct" and t.value == cls:
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return -1


def _split_top_commas(toks: List[Tok]) -> List[List[Tok]]:
    out: List[List[Tok]] = []
    cur: List[Tok] = []
    p = a = b = br = 0
    for t in toks:
        v = t.value
        if t.kind == "punct":
            if v == "(":
                p += 1
            elif v == ")":
                p -= 1
            elif v == "[":
                b += 1
            elif v == "]":
                b -= 1
            elif v == "{":
                br += 1
            elif v == "}":
                br -= 1
        elif t.kind == "op":
            if v == "<":
                a += 1
            elif v == ">":
                a = max(0, a - 1)
        if (t.kind == "punct" and v == "," and p == a == b == br == 0):
            out.append(cur)
            cur = []
            continue
        cur.append(t)
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------------------
# Statement splitting at the *top level* of a token sequence.
# A statement boundary is a semicolon or a newline that is not inside any
# bracket pair, or the end-of-input.
# ---------------------------------------------------------------------------

def _split_top_statements(toks: List[Tok]) -> List[List[Tok]]:
    """Split a token sequence at top-level statement boundaries.

    Boundaries are:
        * a `;` outside of any bracket pair
        * a `}` that returns the brace-depth to 0 (closing a top-level block),
          UNLESS the next significant token is a *continuation* keyword like
          `else`, `catch`, `finally`, or `while` (for do-while).
    """
    _CONT = {"else", "catch", "finally", "while"}
    stmts: List[List[Tok]] = []
    cur: List[Tok] = []
    p = b = br = a = 0
    for idx, t in enumerate(toks):
        v = t.value
        if t.kind == "punct":
            if v == "(":
                p += 1
            elif v == ")":
                p -= 1
            elif v == "[":
                b += 1
            elif v == "]":
                b -= 1
            elif v == "{":
                br += 1
            elif v == "}":
                br -= 1
        elif t.kind == "op":
            if v == "<":
                a += 1
            elif v == ">":
                a = max(0, a - 1)
        cur.append(t)
        if p == b == br == 0 and t.kind == "punct" and v == ";":
            stmts.append(cur)
            cur = []
        elif p == b == 0 and br == 0 and t.kind == "punct" and v == "}":
            # peek next significant token; if it's a continuation, do not split
            j = idx + 1
            while j < len(toks) and toks[j].kind in ("ws", "nl", "cmt"):
                j += 1
            if j < len(toks) and toks[j].kind == "kw" and toks[j].value in _CONT:
                continue
            stmts.append(cur)
            cur = []
    if cur:
        stmts.append(cur)
    return stmts


# ---------------------------------------------------------------------------
# The transformer
# ---------------------------------------------------------------------------

class Transformer:
    def __init__(self) -> None:
        self.imports: set = set()
        self.helpers: set = set()
        self.notes: List[str] = []
        self.rule_fires = 0
        # accumulating type knowledge during a single conversion
        self.var_types: dict = {}

    # ---- public API ----
    def convert(self, ts_source: str) -> ConversionResult:
        toks = tokenize(ts_source)
        # ---- wave 1: cleanups
        toks = self._drop_imports_exports(toks)
        # ---- wave 2/3: structural rewrites at *top level* and within blocks
        out_decl_toks: List[Tok] = []
        out_top_toks: List[Tok] = []
        # We walk top-level statements
        stmts = _split_top_statements(toks)
        for st in stmts:
            classification, rewritten = self._rewrite_top_statement(st)
            if classification == "decl":
                out_decl_toks.extend(rewritten)
                out_decl_toks.append(Tok("nl", "\n"))
            elif classification == "skip":
                continue
            else:
                out_top_toks.extend(rewritten)
                # Ensure separator between top-level statements
                if not (rewritten and rewritten[-1].kind == "nl"):
                    out_top_toks.append(Tok("nl", "\n"))
        # Render
        body = self._render_main_body(out_top_toks)
        decls = _to_text(out_decl_toks)
        # Build final file
        header_lines = []
        for imp in sorted(self.imports):
            header_lines.append(f"import {imp}")
        header = "\n".join(header_lines)
        helper_block = self._render_helpers()
        # Stitch — preserve some breathing room
        pieces = []
        if header:
            pieces.append(header)
        if helper_block:
            pieces.append(helper_block)
        if decls.strip():
            pieces.append(decls.rstrip())
        # main() wrapper
        if body.strip():
            pieces.append(
                "main(): Int64 {\n" + self._indent(body, "    ") + "\n    return 0\n}"
            )
        else:
            pieces.append("main(): Int64 {\n    return 0\n}")
        text = "\n\n".join(pieces) + "\n"
        text = self._postprocess(text)
        return ConversionResult(
            source=text,
            rule_fires=self.rule_fires,
            confidence=float(self.rule_fires),
            notes=self.notes,
            helpers=list(self.helpers),
        )

    # ---- imports ----
    def _drop_imports_exports(self, toks: List[Tok]) -> List[Tok]:
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.kind == "kw" and t.value in ("import", "export"):
                # consume up to next semicolon or newline
                j = i
                while j < len(toks) and not (toks[j].kind == "punct" and toks[j].value == ";"):
                    if toks[j].kind == "nl" and j > i:
                        # consider EOL as boundary if no semicolon
                        # but keep going until we hit one if it's a re-export of brace
                        break
                    j += 1
                # if export prefixes a decl, keep the decl (just drop `export`)
                if t.value == "export":
                    # consume `export` and optional `default`
                    self.rule_fires += 1
                    i += 1
                    nxt = _next_sig(toks, i)
                    if nxt < len(toks) and toks[nxt].kind == "kw" and toks[nxt].value == "default":
                        i = nxt + 1
                    continue
                # full import statement → drop
                self.rule_fires += 1
                i = j + 1
                continue
            out.append(t)
            i += 1
        return out

    # ---- top-level statement classification ----
    def _rewrite_top_statement(self, st: List[Tok]) -> Tuple[str, List[Tok]]:
        """Classify and rewrite a top-level statement.

        Returns ("decl"|"top"|"skip", rewritten_tokens).
        """
        sig = _strip_trivia(st)
        if not sig:
            return ("top", st)
        first = sig[0]
        # Declarations that stay at top level
        if first.kind == "kw":
            if first.value in ("function",):
                return ("decl", self._rewrite_function_decl(st))
            if first.value == "class":
                return ("decl", self._rewrite_class_decl(st))
            if first.value == "interface":
                return ("decl", self._rewrite_interface_decl(st))
            if first.value == "enum":
                return ("decl", self._rewrite_enum_decl(st))
            if first.value == "type":
                return ("decl", self._rewrite_type_alias(st))
            if first.value == "abstract":
                # `abstract class ...`
                idx = sig.index(first)
                if idx + 1 < len(sig) and sig[idx + 1].kind == "kw" and sig[idx + 1].value == "class":
                    return ("decl", self._rewrite_class_decl(st, abstract=True))
            if first.value == "async":
                # `async function ...`
                nxt = sig[1] if len(sig) > 1 else None
                if nxt and nxt.kind == "kw" and nxt.value == "function":
                    self.notes.append("async function flattened to sync")
                    # drop `async`
                    new_st = list(st)
                    for k, t in enumerate(new_st):
                        if t.kind == "kw" and t.value == "async":
                            new_st.pop(k)
                            break
                    return ("decl", self._rewrite_function_decl(new_st))
            if first.value == "declare":
                return ("skip", [])
        # `const f = (x) => ...` at top level – classify as decl (top-level
        # function-like binding) but still emit as `let`/`func`.
        if first.kind == "kw" and first.value in ("let", "const", "var"):
            # If RHS is a function expression / arrow, treat as decl
            if self._is_fn_binding(sig):
                return ("decl", self._rewrite_fn_binding(st))
            # otherwise it's a top-level executable
            return ("top", self._rewrite_stmt(st))
        # Anything else – executable.  Route through _rewrite_stmt so that
        # control-flow statements (if/for/while/switch/try) are handled.
        return ("top", self._rewrite_stmt(st))

    def _is_fn_binding(self, sig: List[Tok]) -> bool:
        # let/const NAME = function/(...)=>...
        for k, t in enumerate(sig):
            if t.kind == "op" and t.value == "=":
                rest = sig[k + 1:]
                rest_sig = _strip_trivia(rest)
                if not rest_sig:
                    return False
                if rest_sig[0].kind == "kw" and rest_sig[0].value == "function":
                    return True
                # arrow: starts with '(' ... ')' '=>'  OR  'id' '=>'
                if rest_sig[0].kind == "punct" and rest_sig[0].value == "(":
                    close = _match_pair(rest_sig, 0, "(", ")")
                    if close != -1 and close + 1 < len(rest_sig):
                        nxt = rest_sig[close + 1]
                        if nxt.kind == "op" and nxt.value == "=>":
                            return True
                if (rest_sig[0].kind == "id" and len(rest_sig) > 1
                        and rest_sig[1].kind == "op" and rest_sig[1].value == "=>"):
                    return True
                return False
        return False

    # ---- function declarations -------------------------------------------
    def _rewrite_function_decl(self, st: List[Tok]) -> List[Tok]:
        """function NAME<G>(params): RetType { body }  →  func NAME<G>(params): RetType { body }.

        If the parameter list has any default-valued parameters, we also
        generate positional-style overloads so that call sites that pass
        the defaulted parameters positionally still type-check.
        """
        self.rule_fires += 1
        sig = list(st)
        for i, t in enumerate(sig):
            if t.kind == "kw" and t.value == "function":
                sig[i] = Tok("kw", "func")
                break
        # Look for default params; if present, capture func name & decide
        # whether to emit overloads.
        func_name = self._extract_func_name(sig)
        param_info = self._extract_param_info(sig)
        rewritten = self._rewrite_signature_and_body(sig, is_method=False)
        if func_name and any(pi.get("default") for pi in param_info):
            overloads = self._build_default_overloads(func_name, param_info,
                                                     return_type=self._extract_return_type(sig))
            if overloads:
                # Prepend overload decls to the primary one
                ov_tok = [Tok("id", overloads), Tok("nl", "\n")]
                return ov_tok + rewritten
        return rewritten

    def _extract_func_name(self, sig: List[Tok]) -> str:
        for i, t in enumerate(sig):
            if t.kind == "kw" and t.value == "func":
                j = _next_sig(sig, i + 1)
                if j < len(sig) and sig[j].kind in ("id", "kw"):
                    return sig[j].value
        return ""

    def _extract_return_type(self, sig: List[Tok]) -> str:
        """Find `): TYPE {` or `): TYPE` and return the mapped TYPE."""
        # locate `(` ... `)` then optional `: TYPE` up to `{`
        i = 0
        while i < len(sig) and not (sig[i].kind == "punct" and sig[i].value == "("):
            i += 1
        if i >= len(sig):
            return ""
        close = _match_pair(sig, i, "(", ")")
        if close == -1:
            return ""
        j = close + 1
        while j < len(sig) and sig[j].kind in ("ws", "nl", "cmt"):
            j += 1
        if j < len(sig) and sig[j].kind == "punct" and sig[j].value == ":":
            k = j + 1
            while k < len(sig) and not (sig[k].kind == "punct" and sig[k].value == "{"):
                k += 1
            return map_type_string(_to_text(sig[j + 1:k])) or "Unit"
        return "Unit"

    def _extract_param_info(self, sig: List[Tok]) -> list:
        i = 0
        while i < len(sig) and not (sig[i].kind == "punct" and sig[i].value == "("):
            i += 1
        if i >= len(sig):
            return []
        close = _match_pair(sig, i, "(", ")")
        if close == -1:
            return []
        params = _split_top_commas(sig[i + 1:close])
        infos = []
        for p in params:
            ps = _strip_trivia(p)
            if not ps:
                continue
            while ps and ps[0].kind == "kw" and ps[0].value in (
                    "public", "private", "protected", "readonly", "static"):
                ps = ps[1:]
            if not ps:
                continue
            name = ps[0].value
            ps = ps[1:]
            optional = False
            if ps and ps[0].kind == "op" and ps[0].value == "?":
                optional = True
                ps = ps[1:]
            tann = ""
            default = ""
            if ps and ps[0].kind == "punct" and ps[0].value == ":":
                j = 1
                depth = 0
                while j < len(ps):
                    t = ps[j]
                    if t.kind == "punct" and t.value in "([{":
                        depth += 1
                    elif t.kind == "punct" and t.value in ")]}":
                        depth -= 1
                    if depth == 0 and t.kind == "op" and t.value == "=":
                        break
                    j += 1
                tann = map_type_string(_to_text(ps[1:j])) or "Any"
                ps = ps[j:]
            if ps and ps[0].kind == "op" and ps[0].value == "=":
                default = _to_text(self._rewrite_inline_expr(ps[1:]))
            if optional and tann and not tann.startswith("?"):
                tann = "?" + tann
            infos.append({"name": name, "type": tann or "Any",
                          "default": default, "optional": optional})
        return infos

    def _build_default_overloads(self, name: str, params: list, *, return_type: str) -> str:
        """Generate positional overload(s) for functions that have default params.

        For each leading run of required params followed by defaulted params,
        we emit one overload that fills in the defaults from the right.
        """
        # Find the first param that has a default; everything after it is
        # considered defaultable.
        first_default = next((i for i, p in enumerate(params) if p["default"]), -1)
        if first_default < 0:
            return ""
        # Emit overloads for each subset taking 0..len(defaults)-1 of the
        # defaulted params from the left.
        rt = return_type or "Unit"
        lines = []
        # Forwarding overload(s): with fewer args than full, fill rest from defaults.
        for take_extra in range(0, len(params) - first_default):
            n_params = first_default + take_extra
            head = params[:n_params]
            head_sig = ", ".join(f"{escape_id(p['name'])}: {p['type']}" for p in head)
            args = [escape_id(p['name']) for p in head]
            for p in params[n_params:]:
                args.append(p["default"])
            call_args = ", ".join(args)
            lines.append(
                f"func {escape_id(name)}({head_sig}): {rt} {{ return {escape_id(name)}({call_args}) }}"
            )
        return "\n".join(lines)

    def _rewrite_fn_binding(self, st: List[Tok]) -> List[Tok]:
        """`const f = (a) => expr` → `func f(a) { return expr }`"""
        self.rule_fires += 1
        sig = list(st)
        # find name and '='
        # Drop kw, get name, drop '=', rest = function expr
        i = 0
        while i < len(sig) and sig[i].kind in ("ws", "nl", "cmt"):
            i += 1
        kw_idx = i  # let/const/var
        i += 1
        while i < len(sig) and sig[i].kind in ("ws", "nl", "cmt"):
            i += 1
        name_idx = i
        name = sig[name_idx].value
        # find '='
        j = name_idx + 1
        # optional `: Type` annotation
        while j < len(sig) and not (sig[j].kind == "op" and sig[j].value == "="):
            j += 1
        if j >= len(sig):
            return st
        rest = sig[j + 1:]
        # Strip trailing ';'
        rest = self._strip_trailing_semi(rest)
        # rest is either `function (...) {...}` or arrow form
        rest_sig = _strip_trivia(rest)
        out: List[Tok] = [Tok("kw", "func"), Tok("ws", " "), Tok("id", name)]
        if rest_sig and rest_sig[0].kind == "kw" and rest_sig[0].value == "function":
            # find paren onwards
            k = next(k for k, t in enumerate(rest) if t.kind == "punct" and t.value == "(")
            out.extend(self._rewrite_function_signature_body(rest[k:]))
        else:
            # arrow form
            # case A: starts with '('
            if rest_sig[0].kind == "punct" and rest_sig[0].value == "(":
                # locate same in `rest`
                k = next(k for k, t in enumerate(rest) if t.kind == "punct" and t.value == "(")
                close = _match_pair(rest, k, "(", ")")
                if close == -1:
                    return st
                params = rest[k:close + 1]
                # after close: optional ': Ret' then '=>' then body
                after = rest[close + 1:]
                after_sig_i = 0
                # gather return type annotation
                while after_sig_i < len(after) and after[after_sig_i].kind in ("ws", "nl", "cmt"):
                    after_sig_i += 1
                ret_ann_tokens: List[Tok] = []
                if after_sig_i < len(after) and after[after_sig_i].kind == "punct" and after[after_sig_i].value == ":":
                    # collect until '=>'
                    rstart = after_sig_i + 1
                    rj = rstart
                    while rj < len(after) and not (after[rj].kind == "op" and after[rj].value == "=>"):
                        rj += 1
                    ret_ann_tokens = after[rstart:rj]
                    after_sig_i = rj
                # skip '=>'
                while after_sig_i < len(after) and not (after[after_sig_i].kind == "op" and after[after_sig_i].value == "=>"):
                    after_sig_i += 1
                if after_sig_i >= len(after):
                    return st
                body_part = after[after_sig_i + 1:]
                # rewrite params
                params_text = self._rewrite_params(params)
                out.extend(params_text)
                if ret_ann_tokens:
                    out.append(Tok("punct", ":"))
                    out.append(Tok("ws", " "))
                    out.append(Tok("id", map_type_string(_to_text(ret_ann_tokens))))
                out.append(Tok("ws", " "))
                out.extend(self._rewrite_arrow_body_as_func_body(body_part))
            elif rest_sig[0].kind == "id":
                # `x => expr`
                pname = rest_sig[0].value
                # find '=>' in rest
                arrow = next(k for k, t in enumerate(rest)
                             if t.kind == "op" and t.value == "=>")
                body_part = rest[arrow + 1:]
                out.append(Tok("punct", "("))
                out.append(Tok("id", escape_id(pname)))
                out.append(Tok("punct", ":"))
                out.append(Tok("ws", " "))
                out.append(Tok("id", "Int64"))
                out.append(Tok("punct", ")"))
                out.append(Tok("ws", " "))
                out.extend(self._rewrite_arrow_body_as_func_body(body_part))
            else:
                return st
        return out

    def _rewrite_arrow_body_as_func_body(self, body_part: List[Tok]) -> List[Tok]:
        """Like :meth:`_rewrite_arrow_body` but ensures the result is a
        ``{ ... }`` block suitable for a Cangjie ``func`` declaration.

        A TS expression-bodied arrow ``(x) => x * 2`` translates to
        ``func double(x: Int64) { x * 2 }``: the last expression is the
        implicit return value in Cangjie, so no ``return`` is needed.
        """
        sig = _strip_trivia(body_part)
        if sig and sig[0].kind == "punct" and sig[0].value == "{":
            return self._rewrite_arrow_body(body_part)
        inner = self._rewrite_inline_expr_tokens(list(body_part), set())
        return [Tok("punct", "{"), Tok("nl", "\n"), Tok("ws", "    "),
                *inner, Tok("nl", "\n"), Tok("punct", "}")]


    def _rewrite_function_signature_body(self, toks: List[Tok]) -> List[Tok]:
        """toks starts at `(` — params and body."""
        close = _match_pair(toks, 0, "(", ")")
        if close == -1:
            return toks
        params = toks[0:close + 1]
        rest = toks[close + 1:]
        # optional return type
        ret_ann: List[Tok] = []
        i = 0
        while i < len(rest) and rest[i].kind in ("ws", "nl", "cmt"):
            i += 1
        if i < len(rest) and rest[i].kind == "punct" and rest[i].value == ":":
            j = i + 1
            # collect type until '{'
            while j < len(rest) and not (rest[j].kind == "punct" and rest[j].value == "{"):
                j += 1
            ret_ann = rest[i + 1:j]
            i = j
        # body
        body = rest[i:]
        # Rewrite
        out: List[Tok] = []
        out.extend(self._rewrite_params(params))
        if ret_ann:
            ret_str = map_type_string(_to_text(ret_ann)) or "Unit"
            out.append(Tok("punct", ":"))
            out.append(Tok("ws", " "))
            out.append(Tok("id", ret_str))
        out.append(Tok("ws", " "))
        out.extend(self._rewrite_block(body))
        return out

    def _rewrite_signature_and_body(self, sig: List[Tok], *, is_method: bool) -> List[Tok]:
        # find '(' after name and optional generics
        i = 0
        while i < len(sig) and not (sig[i].kind == "punct" and sig[i].value == "("):
            i += 1
        if i >= len(sig):
            return sig
        prefix = sig[:i]
        body = self._rewrite_function_signature_body(sig[i:])
        return prefix + body

    def _rewrite_params(self, toks: List[Tok]) -> List[Tok]:
        """Rewrite a parameter list including surrounding parens."""
        # toks[0] == '(' , toks[-1] == ')'
        if not toks or not (toks[0].kind == "punct" and toks[0].value == "("):
            return toks
        close = _match_pair(toks, 0, "(", ")")
        if close == -1:
            return toks
        inner = toks[1:close]
        params = _split_top_commas(inner)
        out_parts: List[str] = []
        for p in params:
            ptext = self._rewrite_one_param(p)
            if ptext:
                out_parts.append(ptext)
        return [Tok("punct", "("), Tok("id", ", ".join(out_parts)), Tok("punct", ")")] + toks[close + 1:]

    def _rewrite_one_param(self, p: List[Tok]) -> str:
        sig = _strip_trivia(p)
        if not sig:
            return ""
        while sig and sig[0].kind == "kw" and sig[0].value in (
                "public", "private", "protected", "readonly", "static"):
            sig = sig[1:]
        if sig and sig[0].kind == "punct" and sig[0].value in ("{", "["):
            self.notes.append("destructured parameter not fully supported")
            return "_arg: Any"
        is_rest = False
        if sig and sig[0].kind == "op" and sig[0].value == "...":
            is_rest = True
            sig = sig[1:]
        if not sig:
            return ""
        name = sig[0].value
        sig = sig[1:]
        optional = False
        if sig and sig[0].kind == "op" and sig[0].value == "?":
            optional = True
            sig = sig[1:]
        type_str = ""
        default_str = ""
        if sig and sig[0].kind == "punct" and sig[0].value == ":":
            j = 1
            depth = 0
            while j < len(sig):
                t = sig[j]
                if t.kind == "punct" and t.value in "([{":
                    depth += 1
                elif t.kind == "punct" and t.value in ")]}":
                    depth -= 1
                if depth == 0 and t.kind == "op" and t.value == "=":
                    break
                j += 1
            type_str = map_type_string(_to_text(sig[1:j])) or "Any"
            sig = sig[j:]
        if sig and sig[0].kind == "op" and sig[0].value == "=":
            default_str = _to_text(self._rewrite_inline_expr(sig[1:]))
        if not type_str:
            type_str = "Any"
        if optional and not type_str.startswith("?"):
            type_str = f"?{type_str}"
        if is_rest:
            type_str = f"Array<{type_str}>"
        out = f"{escape_id(name)}: {type_str}"
        # NOTE: we *do not* emit `name!: T = default` because we always
        # generate positional overload forwarders that supply the defaults.
        # This keeps positional call sites compiling without changes.
        return out

    def _rewrite_block(self, toks: List[Tok]) -> List[Tok]:
        """Rewrite the contents of a `{...}` block (function body, etc.).

        Performs statement-by-statement rewriting inside.
        """
        # find first '{' and matching '}'
        i = 0
        while i < len(toks) and not (toks[i].kind == "punct" and toks[i].value == "{"):
            i += 1
        if i >= len(toks):
            return toks
        close = _match_pair(toks, i, "{", "}")
        if close == -1:
            return toks
        inner = toks[i + 1:close]
        rewritten_inner = self._rewrite_stmt_list(inner)
        return toks[:i + 1] + rewritten_inner + toks[close:]

    def _rewrite_stmt_list(self, toks: List[Tok]) -> List[Tok]:
        stmts = _split_top_statements(toks)
        out: List[Tok] = []
        for st in stmts:
            r = self._rewrite_stmt(st)
            out.extend(r)
            if not (r and r[-1].kind == "nl"):
                out.append(Tok("nl", "\n"))
        return out

    def _rewrite_stmt(self, st: List[Tok]) -> List[Tok]:
        """Rewrite a single statement inside a function/block body."""
        sig = _strip_trivia(st)
        if not sig:
            return st
        first = sig[0]
        if first.kind == "kw":
            v = first.value
            if v in ("let", "const", "var"):
                return self._rewrite_var_decl(st)
            if v == "if":
                return self._rewrite_if(st)
            if v == "for":
                return self._rewrite_for(st)
            if v == "while":
                return self._rewrite_while(st)
            if v == "do":
                return self._rewrite_do_while(st)
            if v == "return":
                return self._rewrite_return(st)
            if v == "throw":
                return self._rewrite_throw(st)
            if v == "try":
                return self._rewrite_try(st)
            if v == "switch":
                return self._rewrite_switch(st)
            if v == "break" or v == "continue":
                return st
            if v == "function":
                # nested function
                return self._rewrite_function_decl(st)
        # expression statement
        return self._rewrite_expression_stmt(st)

    # ---- variable declarations ------------------------------------------
    def _rewrite_var_decl(self, st: List[Tok]) -> List[Tok]:
        self.rule_fires += 1
        sig = list(st)
        # Find kw
        i = 0
        while i < len(sig) and sig[i].kind in ("ws", "nl", "cmt"):
            i += 1
        kw = sig[i].value  # let/const/var
        # const → let, let/var → var (mutable in TS, but `let` is also reassignable in TS)
        cj_kw = "let" if kw == "const" else "var"
        sig[i] = Tok("kw", cj_kw)
        # Strip trailing ';' for parsing, will re-append at end
        trailing = []
        if sig and sig[-1].kind == "punct" and sig[-1].value == ";":
            trailing = [sig[-1]]
            sig = sig[:-1]
        # Parse name(s)
        j = i + 1
        while j < len(sig) and sig[j].kind in ("ws", "nl", "cmt"):
            j += 1
        if j >= len(sig):
            return sig + trailing
        # Destructuring patterns – degrade
        if sig[j].kind == "punct" and sig[j].value in ("{", "["):
            self.notes.append("destructuring declaration kept verbatim — may need manual fix")
            return sig + trailing
        name = sig[j].value
        # collect optional type annotation
        k = j + 1
        while k < len(sig) and sig[k].kind in ("ws", "nl", "cmt"):
            k += 1
        type_ann: List[Tok] = []
        init: List[Tok] = []
        if k < len(sig) and sig[k].kind == "punct" and sig[k].value == ":":
            # collect type until '=' or end
            t_start = k + 1
            depth = 0
            tj = t_start
            while tj < len(sig):
                t = sig[tj]
                if t.kind == "punct" and t.value in "([{":
                    depth += 1
                elif t.kind == "punct" and t.value in ")]}":
                    depth -= 1
                if depth == 0 and t.kind == "op" and t.value == "=":
                    break
                tj += 1
            type_ann = sig[t_start:tj]
            k = tj
        if k < len(sig) and sig[k].kind == "op" and sig[k].value == "=":
            init = sig[k + 1:]
        # Determine cangjie type
        cj_type = ""
        int_hint = False
        float_hint = False
        if init:
            inf = infer_init_type(init)
            init_sig = _strip_trivia(init)
            if init_sig and init_sig[0].kind == "num":
                if init_sig[0].meta.get("float"):
                    float_hint = True
                else:
                    int_hint = True
            if inf == "Int64":
                int_hint = True
            elif inf == "Float64":
                float_hint = True
            if not type_ann and inf:
                cj_type = inf
        if type_ann:
            cj_type = map_type_string(_to_text(type_ann), int_hint=int_hint) or cj_type
        # Heuristic overrides:
        #   number annot + float literal init  →  Float64
        if cj_type == "Int64" and float_hint:
            cj_type = "Float64"
        # Array<Int64> annot + integer literal init  →  keep Int64 (default)
        # Array<Float64> annot + integer literal init →  switch to Array<Int64>
        if cj_type == "Array<Float64>" and int_hint and not float_hint:
            cj_type = "Array<Int64>"
        # Build result
        out: List[Tok] = [Tok("kw", cj_kw), Tok("ws", " "), Tok("id", escape_id(name))]
        if cj_type:
            out.append(Tok("punct", ":"))
            out.append(Tok("ws", " "))
            out.append(Tok("id", cj_type))
            self.var_types[name] = cj_type
        if init:
            out.append(Tok("ws", " "))
            out.append(Tok("op", "="))
            out.append(Tok("ws", " "))
            init_rewritten = self._rewrite_inline_expr(init, target_type=cj_type)
            out.extend(init_rewritten)
        return out + trailing

    # ---- control flow ---------------------------------------------------
    def _rewrite_if(self, st: List[Tok]) -> List[Tok]:
        """Rewrite an if/else-if/else chain.

        Cangjie requires `{...}` around each branch body; TS allows a bare
        statement.  We detect bare bodies and wrap them in braces.
        """
        self.rule_fires += 1
        out: List[Tok] = []
        i = 0
        while i < len(st):
            t = st[i]
            if t.kind == "kw" and t.value in ("if", "else"):
                out.append(t)
                i += 1
                continue
            if t.kind == "punct" and t.value == "(":
                close = _match_pair(st, i, "(", ")")
                if close != -1:
                    inner = st[i + 1:close]
                    out.append(t)
                    out.extend(self._rewrite_inline_expr(inner))
                    out.append(st[close])
                    i = close + 1
                    # After the condition, the next significant token is
                    # the body — either `{` or a bare statement.  Wrap bare
                    # statement in braces.
                    j = i
                    while j < len(st) and st[j].kind in ("ws", "nl", "cmt"):
                        out.append(st[j]); j += 1
                    if j < len(st):
                        if st[j].kind == "punct" and st[j].value == "{":
                            # already a block; let normal flow handle it
                            i = j
                            continue
                        # Collect a single statement (up to ';' or until
                        # we hit `else` or end).
                        bs = j
                        depth_p = depth_b = depth_br = 0
                        while bs < len(st):
                            bt = st[bs]
                            v = bt.value
                            if bt.kind == "punct":
                                if v == "(":
                                    depth_p += 1
                                elif v == ")":
                                    depth_p -= 1
                                elif v == "[":
                                    depth_b += 1
                                elif v == "]":
                                    depth_b -= 1
                                elif v == "{":
                                    depth_br += 1
                                elif v == "}":
                                    depth_br -= 1
                            if depth_p == depth_b == depth_br == 0:
                                if bt.kind == "punct" and v == ";":
                                    bs += 1
                                    break
                                if bt.kind == "kw" and v == "else":
                                    break
                            bs += 1
                        body_part = st[j:bs]
                        rewritten = self._rewrite_stmt_list(body_part)
                        out.append(Tok("punct", "{"))
                        out.append(Tok("nl", "\n"))
                        out.extend(rewritten)
                        out.append(Tok("punct", "}"))
                        out.append(Tok("ws", " "))
                        i = bs
                        continue
                    continue
            if t.kind == "punct" and t.value == "{":
                close = _match_pair(st, i, "{", "}")
                if close != -1:
                    out.append(t)
                    out.extend(self._rewrite_stmt_list(st[i + 1:close]))
                    out.append(st[close])
                    i = close + 1
                    continue
            out.append(t)
            i += 1
        return out

    def _rewrite_while(self, st: List[Tok]) -> List[Tok]:
        return self._rewrite_if(st)  # same structure handling

    def _rewrite_do_while(self, st: List[Tok]) -> List[Tok]:
        return self._rewrite_if(st)

    def _rewrite_for(self, st: List[Tok]) -> List[Tok]:
        """Rewrite `for (...) { body }`.

        Three TS shapes:
          1) for (init; cond; step)  → for (i in lo..hi)  (best-effort)
          2) for (let x of arr)      → for (x in arr)
          3) for (let x in obj)      → for (x in obj.keys())
        """
        self.rule_fires += 1
        # locate paren
        i = 0
        while i < len(st) and not (st[i].kind == "punct" and st[i].value == "("):
            i += 1
        if i >= len(st):
            return st
        close = _match_pair(st, i, "(", ")")
        if close == -1:
            return st
        head = st[i + 1:close]
        # find body
        bi = close + 1
        while bi < len(st) and not (st[bi].kind == "punct" and st[bi].value == "{"):
            bi += 1
        if bi >= len(st):
            return st
        be = _match_pair(st, bi, "{", "}")
        if be == -1:
            return st
        body_inner = st[bi + 1:be]
        # classify head
        head_sig = _strip_trivia(head)
        # Detect for-of / for-in
        of_idx = -1
        in_idx = -1
        depth = 0
        for k, t in enumerate(head):
            if t.kind == "punct" and t.value in "([{":
                depth += 1
            elif t.kind == "punct" and t.value in ")]}":
                depth -= 1
            elif depth == 0 and t.kind == "kw" and t.value == "of":
                of_idx = k
                break
            elif depth == 0 and t.kind == "kw" and t.value == "in":
                in_idx = k
                break
        rewritten_head: List[Tok]
        if of_idx >= 0 or in_idx >= 0:
            idx = of_idx if of_idx >= 0 else in_idx
            lhs = head[:idx]
            rhs = head[idx + 1:]
            # extract variable name (skip let/const)
            lhs_sig = _strip_trivia(lhs)
            while lhs_sig and lhs_sig[0].kind == "kw" and lhs_sig[0].value in ("let", "const", "var"):
                lhs_sig = lhs_sig[1:]
            if not lhs_sig:
                return st
            # could be destructuring `[a,b]` — degrade to `pair` and unpack via tuple
            var_name = lhs_sig[0].value if lhs_sig[0].kind in ("id", "kw") else "_x"
            iter_expr = _to_text(self._rewrite_inline_expr(rhs))
            if of_idx >= 0:
                rewritten_head = [
                    Tok("punct", "("),
                    Tok("id", f"{escape_id(var_name)} in {iter_expr}"),
                    Tok("punct", ")"),
                ]
            else:
                # for-in over object keys – treat rhs as iterable directly,
                # if HashMap then `.keys()`.
                rewritten_head = [
                    Tok("punct", "("),
                    Tok("id", f"{escape_id(var_name)} in {iter_expr}.keys()"),
                    Tok("punct", ")"),
                ]
        else:
            # C-style for: try to extract i, lo, hi
            rewritten_head = self._rewrite_cstyle_for(head)
        # body
        new_body = self._rewrite_stmt_list(body_inner)
        return ([Tok("kw", "for"), Tok("ws", " ")] + rewritten_head + [
            Tok("ws", " "), Tok("punct", "{")
        ] + new_body + [Tok("punct", "}")])

    _CFOR_RE = re.compile(
        r"^\s*(?:let|var|const)?\s*(\w+)\s*(?::\s*\w+)?\s*=\s*([^;]+);"
        r"\s*\1\s*(<=?|>=?|!=|<|>)\s*([^;]+);"
        r"\s*(?:\1\s*\+\+|\+\+\s*\1|\1\s*\+=\s*1|\1\s*=\s*\1\s*\+\s*1"
        r"|\1\s*--|--\s*\1|\1\s*-=\s*1)\s*$"
    )

    def _rewrite_cstyle_for(self, head: List[Tok]) -> List[Tok]:
        # First, rewrite tokens in the head so `.length` → `.size`,
        # template literals are normalised, etc.  We only run the safe
        # expression-level rewrites.
        head_rew = self._rewrite_method_calls(head)
        text = _to_text(head_rew).strip()
        m = self._CFOR_RE.match(text)
        if not m:
            self.notes.append("complex for(;;) loop fell back to commented form")
            return [
                Tok("punct", "("),
                Tok("id", "_i_ in 0..1"),
                Tok("punct", ")"),
                Tok("cmt", f"/* TODO: for {text} */"),
            ]
        name, lo, op, hi = m.group(1), m.group(2).strip(), m.group(3), m.group(4).strip()
        if op == "<":
            rng = f"{lo}..{hi}"
        elif op == "<=":
            rng = f"{lo}..={hi}"
        elif op == ">":
            rng = f"({lo}-1)..({hi}-1) : -1"
        elif op == ">=":
            rng = f"{lo}..={hi} : -1"
        else:
            rng = f"{lo}..{hi}"
        return [Tok("punct", "("), Tok("id", f"{escape_id(name)} in {rng}"),
                Tok("punct", ")")]

    def _rewrite_return(self, st: List[Tok]) -> List[Tok]:
        # `return EXPR;` – rewrite EXPR
        out: List[Tok] = []
        i = 0
        while i < len(st) and not (st[i].kind == "kw" and st[i].value == "return"):
            out.append(st[i]); i += 1
        if i >= len(st):
            return st
        out.append(st[i]); i += 1
        # gather expr until ';'
        expr_end = len(st)
        if st and st[-1].kind == "punct" and st[-1].value == ";":
            expr_end = len(st) - 1
        expr = st[i:expr_end]
        if _strip_trivia(expr):
            out.append(Tok("ws", " "))
            out.extend(self._rewrite_inline_expr(expr))
        if expr_end < len(st):
            out.append(st[expr_end])
        return out

    def _rewrite_throw(self, st: List[Tok]) -> List[Tok]:
        # `throw new Error(msg)` → `throw Exception(msg)`
        out: List[Tok] = []
        for t in st:
            if t.kind == "kw" and t.value == "new":
                continue
            if t.kind == "id" and t.value == "Error":
                out.append(Tok("id", "Exception"))
                continue
            out.append(t)
        return self._rewrite_inline_expr_tokens(out, preserve_keywords={"throw"})

    def _rewrite_try(self, st: List[Tok]) -> List[Tok]:
        """Rewrite try/catch/finally.  Cangjie: `try { } catch (e: Exception) { } finally { }`."""
        self.rule_fires += 1
        out: List[Tok] = []
        i = 0
        while i < len(st):
            t = st[i]
            if t.kind == "kw" and t.value in ("try", "catch", "finally"):
                if t.value == "catch":
                    # next: `(`name optional `:` type`)` `{...}`
                    out.append(t); i += 1
                    i = _next_sig(st, i)
                    if i < len(st) and st[i].kind == "punct" and st[i].value == "(":
                        close = _match_pair(st, i, "(", ")")
                        inner = st[i + 1:close]
                        inner_sig = _strip_trivia(inner)
                        ename = inner_sig[0].value if inner_sig else "e"
                        out.append(Tok("ws", " "))
                        out.append(Tok("punct", "("))
                        out.append(Tok("id", f"{escape_id(ename)}: Exception"))
                        out.append(Tok("punct", ")"))
                        i = close + 1
                    continue
                out.append(t)
                i += 1
                continue
            if t.kind == "punct" and t.value == "{":
                close = _match_pair(st, i, "{", "}")
                if close != -1:
                    out.append(t)
                    out.extend(self._rewrite_stmt_list(st[i + 1:close]))
                    out.append(st[close])
                    i = close + 1
                    continue
            out.append(t)
            i += 1
        return out

    def _rewrite_switch(self, st: List[Tok]) -> List[Tok]:
        """switch(x) { case a: stmts; break; default: stmts } → match (x) { case a => ...; case _ => ... }."""
        self.rule_fires += 1
        i = 0
        while i < len(st) and not (st[i].kind == "kw" and st[i].value == "switch"):
            i += 1
        # find subject
        p_open = _next_sig(st, i + 1)
        if p_open >= len(st) or not (st[p_open].kind == "punct" and st[p_open].value == "("):
            return st
        p_close = _match_pair(st, p_open, "(", ")")
        if p_close == -1:
            return st
        subj = st[p_open + 1:p_close]
        # find body
        bi = _next_sig(st, p_close + 1)
        if bi >= len(st) or not (st[bi].kind == "punct" and st[bi].value == "{"):
            return st
        be = _match_pair(st, bi, "{", "}")
        if be == -1:
            return st
        body = st[bi + 1:be]
        # Walk body, splitting into case groups
        out: List[Tok] = [Tok("kw", "match"), Tok("ws", " "),
                          Tok("punct", "("), *self._rewrite_inline_expr(subj),
                          Tok("punct", ")"), Tok("ws", " "), Tok("punct", "{"),
                          Tok("nl", "\n")]
        # Tokenize into case-groups separated by `case` / `default`
        groups: List[Tuple[Optional[List[Tok]], List[Tok]]] = []
        cur_label: Optional[List[Tok]] = None
        cur_body: List[Tok] = []
        k = 0
        while k < len(body):
            t = body[k]
            if t.kind == "kw" and t.value in ("case", "default"):
                if cur_label is not None or cur_body:
                    groups.append((cur_label, cur_body))
                cur_body = []
                if t.value == "default":
                    cur_label = None
                    # skip until ':'
                    k += 1
                    while k < len(body) and not (body[k].kind == "punct" and body[k].value == ":"):
                        k += 1
                    k += 1
                    continue
                # case EXPR :
                k += 1
                expr_start = k
                while k < len(body) and not (body[k].kind == "punct" and body[k].value == ":"):
                    k += 1
                cur_label = body[expr_start:k]
                k += 1
                continue
            cur_body.append(t)
            k += 1
        if cur_label is not None or cur_body:
            groups.append((cur_label, cur_body))
        # Emit each group
        for label, gbody in groups:
            # Skip a leading "empty" group with no label and no body — it's
            # an artefact of how we tokenise the switch body.
            if label is None and not _strip_trivia(gbody):
                continue
            cleaned = self._strip_breaks(gbody)
            if label is None:
                pat = "_"
            else:
                pat = _to_text(self._rewrite_inline_expr(label)).strip()
            out.append(Tok("ws", "    "))
            out.append(Tok("kw", "case"))
            out.append(Tok("ws", " "))
            out.append(Tok("id", pat))
            out.append(Tok("ws", " "))
            out.append(Tok("op", "=>"))
            out.append(Tok("ws", " "))
            # Wrap multi-stmt in nested block-like newline structure
            inner = self._rewrite_stmt_list(cleaned)
            if not _strip_trivia(inner):
                out.append(Tok("punct", "("))
                out.append(Tok("punct", ")"))
            else:
                # Multiple statements per case: use a parenthesised expr if
                # multiple, otherwise inline. Easiest: emit as ` { ... }`-ish
                # — Cangjie match arms accept a sequence after `=>`.
                out.extend(inner)
            out.append(Tok("nl", "\n"))
        out.append(Tok("punct", "}"))
        return out

    def _strip_breaks(self, toks: List[Tok]) -> List[Tok]:
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.kind == "kw" and t.value == "break":
                # also consume the following ';' if present
                j = i + 1
                while j < len(toks) and toks[j].kind in ("ws",):
                    j += 1
                if j < len(toks) and toks[j].kind == "punct" and toks[j].value == ";":
                    j += 1
                i = j
                continue
            out.append(t)
            i += 1
        return out

    # ---- expression rewriting ------------------------------------------
    def _rewrite_expression_stmt(self, st: List[Tok]) -> List[Tok]:
        return self._rewrite_inline_expr_tokens(st, preserve_keywords=set())

    def _rewrite_inline_expr(self, toks: List[Tok], target_type: str = "") -> List[Tok]:
        return self._rewrite_inline_expr_tokens(list(toks), preserve_keywords=set())

    def _rewrite_inline_expr_tokens(self, toks: List[Tok],
                                    preserve_keywords: set) -> List[Tok]:
        """Token-level rewrites for expressions/inline code."""
        out = list(toks)
        out = self._rewrite_function_exprs(out)
        out = self._rewrite_ternary(out)
        out = self._rewrite_templates(out)
        out = self._rewrite_arrow_in_expr(out)
        out = self._rewrite_simple_replacements(out, preserve_keywords)
        out = self._rewrite_dotted_globals(out)
        out = self._rewrite_method_calls(out)
        out = self._rewrite_index_access(out)
        out = self._rewrite_typeof(out)
        out = self._rewrite_string_concat(out)
        return out

    def _rewrite_ternary(self, toks: List[Tok]) -> List[Tok]:
        """Rewrite ``cond ? a : b`` to Cangjie ``if (cond) { a } else { b }``.

        We do a single right-to-left scan so nested ternaries collapse
        cleanly (the inner ``?`` is rewritten first because outer ones
        contain it).
        """
        # Locate `?` tokens that are real ternary markers (not part of
        # `?.` or `??`).  Cangjie's optional chaining uses `?` too but we
        # haven't emitted those yet.
        result = list(toks)
        # Find the *last* ternary `?` and rewrite outward.
        changed = True
        max_iter = 32  # protect against runaway loops
        while changed and max_iter > 0:
            changed = False
            max_iter -= 1
            for i in range(len(result) - 1, -1, -1):
                t = result[i]
                if not (t.kind == "op" and t.value == "?"):
                    continue
                # Skip `??` and `?.`
                nxt = result[i + 1] if i + 1 < len(result) else None
                if nxt and nxt.kind == "op" and nxt.value == "?":
                    continue
                if nxt and nxt.kind == "punct" and nxt.value == ".":
                    continue
                # Find matching ':' at the same paren/bracket level
                depth = 0
                colon_idx = -1
                for j in range(i + 1, len(result)):
                    v = result[j].value
                    if result[j].kind == "punct" and v in "([{":
                        depth += 1
                    elif result[j].kind == "punct" and v in ")]}":
                        depth -= 1
                        if depth < 0:
                            break
                    elif depth == 0 and result[j].kind == "punct" and v == ":":
                        colon_idx = j
                        break
                    elif depth == 0 and result[j].kind == "op" and v == "?":
                        # Nested ternary — handle inner first next iteration.
                        break
                if colon_idx == -1:
                    continue
                # Find start of condition: scan backward to find expression boundary.
                start = i - 1
                d = 0
                while start >= 0:
                    rt = result[start]
                    v = rt.value
                    if rt.kind == "punct" and v in ")]}":
                        d += 1
                    elif rt.kind == "punct" and v in "([{":
                        d -= 1
                        if d < 0:
                            break
                    elif d == 0 and (
                        (rt.kind == "punct" and v in (",", ";"))
                        or (rt.kind == "kw" and v in ("return", "throw"))
                    ):
                        break
                    start -= 1
                cond_start = start + 1
                # Find end of else branch: scan forward likewise.
                end = colon_idx + 1
                d = 0
                while end < len(result):
                    rt = result[end]
                    v = rt.value
                    if rt.kind == "punct" and v in "([{":
                        d += 1
                    elif rt.kind == "punct" and v in ")]}":
                        d -= 1
                        if d < 0:
                            break
                    elif d == 0 and rt.kind == "punct" and v in (",", ";"):
                        break
                    end += 1
                # Slices: cond = [cond_start..i), then = [i+1..colon_idx), else = [colon_idx+1..end)
                cond = result[cond_start:i]
                then_part = result[i + 1:colon_idx]
                else_part = result[colon_idx + 1:end]
                replacement: List[Tok] = []
                replacement.append(Tok("kw", "if"))
                replacement.append(Tok("ws", " "))
                replacement.append(Tok("punct", "("))
                replacement.extend(_strip_trivia(cond))
                replacement.append(Tok("punct", ")"))
                replacement.append(Tok("ws", " "))
                replacement.append(Tok("punct", "{"))
                replacement.append(Tok("ws", " "))
                replacement.extend(_strip_trivia(then_part))
                replacement.append(Tok("ws", " "))
                replacement.append(Tok("punct", "}"))
                replacement.append(Tok("ws", " "))
                replacement.append(Tok("kw", "else"))
                replacement.append(Tok("ws", " "))
                replacement.append(Tok("punct", "{"))
                replacement.append(Tok("ws", " "))
                replacement.extend(_strip_trivia(else_part))
                replacement.append(Tok("ws", " "))
                replacement.append(Tok("punct", "}"))
                result = result[:cond_start] + replacement + result[end:]
                self.rule_fires += 1
                changed = True
                break
        return result

    def _rewrite_function_exprs(self, toks: List[Tok]) -> List[Tok]:
        """Rewrite `function (params): RetT { body }` (TS function-expression
        used as a value) into a Cangjie lambda ``{ params => body }``.
        """
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.kind == "kw" and t.value == "function":
                # find '('
                j = _next_sig(toks, i + 1)
                # Optional name between `function` and `(` is dropped — anonymous lambda.
                while j < len(toks) and toks[j].kind == "id":
                    j = _next_sig(toks, j + 1)
                if j >= len(toks) or not (toks[j].kind == "punct" and toks[j].value == "("):
                    out.append(t)
                    i += 1
                    continue
                pclose = _match_pair(toks, j, "(", ")")
                if pclose == -1:
                    out.append(t)
                    i += 1
                    continue
                params = toks[j + 1:pclose]
                after = pclose + 1
                # optional `: RetType`
                ann = _next_sig(toks, after)
                if ann < len(toks) and toks[ann].kind == "punct" and toks[ann].value == ":":
                    # skip until `{`
                    k = ann + 1
                    while k < len(toks) and not (toks[k].kind == "punct" and toks[k].value == "{"):
                        k += 1
                    after = k
                else:
                    after = ann
                if after >= len(toks) or not (toks[after].kind == "punct" and toks[after].value == "{"):
                    out.append(t)
                    i += 1
                    continue
                bclose = _match_pair(toks, after, "{", "}")
                if bclose == -1:
                    out.append(t)
                    i += 1
                    continue
                body = toks[after + 1:bclose]
                # Rewrite params: comma-split & build name: T list
                pp = _split_top_commas(params)
                param_texts: List[str] = []
                for p in pp:
                    psig = _strip_trivia(p)
                    if not psig:
                        continue
                    pname = psig[0].value
                    type_str = "Int64"
                    for kk, st_ in enumerate(psig):
                        if st_.kind == "punct" and st_.value == ":":
                            type_str = map_type_string(_to_text(psig[kk + 1:])) or "Any"
                            break
                    param_texts.append(f"{escape_id(pname)}: {type_str}")
                # Recursively rewrite body as stmt list
                rewritten_body = self._rewrite_stmt_list(body)
                out.append(Tok("punct", "{"))
                out.append(Tok("ws", " "))
                if param_texts:
                    out.append(Tok("id", ", ".join(param_texts)))
                    out.append(Tok("ws", " "))
                out.append(Tok("op", "=>"))
                out.append(Tok("ws", " "))
                out.extend(rewritten_body)
                out.append(Tok("punct", "}"))
                i = bclose + 1
                self.rule_fires += 1
                continue
            out.append(t)
            i += 1
        return out

    def _rewrite_string_concat(self, toks: List[Tok]) -> List[Tok]:
        """Rewrite ``"abc" + EXPR + "xyz"`` chains to ``"abc${EXPR}xyz"``.

        Cangjie's `+` does not auto-coerce mixed types.  When a top-level
        concatenation chain contains *at least one* string literal, we
        collapse the whole chain into a single string with `${}` for the
        non-string operands.
        """
        # Walk tokens; whenever we encounter a `+` at top depth that has a
        # string-or-numeric/identifier neighbour, accumulate the chain and
        # rewrite as one literal.
        out: List[Tok] = []
        i = 0
        n = len(toks)
        while i < n:
            # Try to recognise a concat chain starting at i
            chain, end = self._collect_concat_chain(toks, i)
            if chain is not None and self._chain_contains_string(chain):
                # Emit single string token
                buf = ['"']
                for piece_kind, piece_text in chain:
                    if piece_kind == "str":
                        buf.append(piece_text)
                    else:
                        buf.append("${" + piece_text + "}")
                buf.append('"')
                out.append(Tok("str", "".join(buf)))
                self.rule_fires += 1
                i = end
                continue
            out.append(toks[i])
            i += 1
        return out

    def _collect_concat_chain(self, toks: List[Tok], start: int):
        """Try to read a `+`-chain starting at *start*.

        Returns (pieces, end_index) on success where pieces is a list of
        (kind, text) tuples; kind is "str" for the *contents* of a string
        literal (without surrounding quotes) or "expr" otherwise.  Returns
        (None, start) if no chain was found.
        """
        pieces = []
        i = start
        # We must successfully read OPERAND (+ OPERAND)+ at top depth
        def read_operand(j):
            # Skip leading trivia
            while j < len(toks) and toks[j].kind in ("ws", "nl", "cmt"):
                j += 1
            if j >= len(toks):
                return None
            t = toks[j]
            # An operand is either a simple atom (str/num/id/templ) or a
            # parenthesised expression or a member access on top of those.
            # We accept: optional unary -, then primary, then `.id` or
            # `[...]` or `(...)` suffix chains.
            if t.kind == "op" and t.value in ("-", "+", "!"):
                # only allow unary; nothing fancy
                pass
            start_j = j
            depth_p = depth_b = 0
            while j < len(toks):
                t = toks[j]
                if t.kind == "punct":
                    v = t.value
                    if v == "(":
                        depth_p += 1
                    elif v == ")":
                        if depth_p == 0:
                            break
                        depth_p -= 1
                    elif v == "[":
                        depth_b += 1
                    elif v == "]":
                        if depth_b == 0:
                            break
                        depth_b -= 1
                    elif depth_p == 0 and depth_b == 0 and v in (",", ";", "{", "}"):
                        break
                elif depth_p == 0 and depth_b == 0:
                    if t.kind == "op" and t.value in ("+", "-", "*", "/", "%",
                                                       "==", "!=", "<", ">",
                                                       "<=", ">=", "&&", "||",
                                                       "=", "??", "=>", "?"):
                        break
                    if t.kind == "kw":
                        break
                    if t.kind == "nl":
                        break
                j += 1
            seg = toks[start_j:j]
            seg_sig = _strip_trivia(seg)
            if not seg_sig:
                return None
            return seg, j
        first = read_operand(i)
        if first is None:
            return None, start
        seg, j = first
        seg_sig = _strip_trivia(seg)
        # we require the chain to have >= 1 `+`
        # Inspect operand
        def classify_segment(seg):
            seg_sig = _strip_trivia(seg)
            if len(seg_sig) == 1 and seg_sig[0].kind == "str":
                raw = seg_sig[0].value
                # strip quotes
                if raw and raw[0] in ('"', "'") and raw[-1] == raw[0]:
                    inner = raw[1:-1]
                else:
                    inner = raw
                # Always produce a double-quoted-compatible body
                # Strip leading/trailing whitespace? No, preserve content.
                # Escape any existing ${ and " in the literal
                inner = inner.replace('"', '\\"')
                return ("str", inner)
            text = _to_text(seg).strip()
            return ("expr", text)
        pieces.append(classify_segment(seg))
        chain_found = False
        cur = j
        while cur < len(toks):
            # skip trivia
            k = cur
            while k < len(toks) and toks[k].kind in ("ws", "nl", "cmt"):
                k += 1
            if k >= len(toks):
                break
            if not (toks[k].kind == "op" and toks[k].value == "+"):
                break
            # next operand
            nxt = read_operand(k + 1)
            if nxt is None:
                break
            seg2, j2 = nxt
            pieces.append(classify_segment(seg2))
            chain_found = True
            cur = j2
        if not chain_found:
            return None, start
        return pieces, cur

    def _chain_contains_string(self, chain) -> bool:
        if any(k == "str" for k, _ in chain):
            return True
        # Heuristic: if any expression operand is a *bare identifier* whose
        # variable type is known to be `String`, treat the whole chain as
        # a string concatenation.
        for k, text in chain:
            if k == "expr":
                name = text.strip()
                if name in self.var_types and self.var_types[name] == "String":
                    return True
        return False

    def _rewrite_templates(self, toks: List[Tok]) -> List[Tok]:
        out: List[Tok] = []
        for t in toks:
            if t.kind != "tpl":
                out.append(t)
                continue
            parts = t.meta.get("parts", [])
            buf = ['"']
            for kind, val in parts:
                if kind == "text":
                    buf.append(val.replace("\\", "\\\\").replace('"', '\\"'))
                else:
                    # Expression part: rewrite recursively
                    sub_toks = tokenize(val)
                    sub_rewritten = self._rewrite_inline_expr_tokens(sub_toks, set())
                    expr_text = _to_text(sub_rewritten).strip()
                    buf.append("${")
                    buf.append(expr_text)
                    buf.append("}")
            buf.append('"')
            out.append(Tok("str", "".join(buf)))
            self.rule_fires += 1
        return out

    def _rewrite_simple_replacements(self, toks: List[Tok], preserve_keywords: set) -> List[Tok]:
        # Identifiers that are TS primitive type *names* (lowercase).  In
        # practice these never appear as runtime values in idiomatic TS,
        # so it is safe to globally rewrite them to their Cangjie names.
        # This makes `identity<number>(...)` and `new Map<string, number>()`
        # produce valid Cangjie type arguments without a separate pass.
        _LC_TYPE_MAP = {
            "number": "Int64",
            "string": "String",
            "boolean": "Bool",
            "void": "Unit",
            "any": "Any",
            "unknown": "Any",
            "never": "Nothing",
            "bigint": "Int64",
        }
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.kind == "op" and t.value == "===":
                out.append(Tok("op", "=="))
                self.rule_fires += 1
            elif t.kind == "op" and t.value == "!==":
                out.append(Tok("op", "!="))
                self.rule_fires += 1
            elif t.kind == "kw" and t.value == "null":
                out.append(Tok("id", "None"))
                self.rule_fires += 1
            elif t.kind == "kw" and t.value == "undefined":
                out.append(Tok("id", "None"))
                self.rule_fires += 1
            elif t.kind == "kw" and t.value == "new" and t.value not in preserve_keywords:
                # drop `new`
                self.rule_fires += 1
            elif t.kind == "id" and t.value in PLAIN_IDENT and t.value != "console":
                out.append(Tok("id", PLAIN_IDENT[t.value]))
                self.rule_fires += 1
            elif t.kind == "id" and t.value == "Map":
                self.imports.add("std.collection.*")
                out.append(Tok("id", "HashMap"))
                self.rule_fires += 1
            elif t.kind == "id" and t.value == "Set":
                self.imports.add("std.collection.*")
                out.append(Tok("id", "HashSet"))
                self.rule_fires += 1
            elif t.kind in ("id", "kw") and t.value in _LC_TYPE_MAP:
                out.append(Tok("id", _LC_TYPE_MAP[t.value]))
                self.rule_fires += 1
            else:
                out.append(t)
            i += 1
        return out

    def _rewrite_dotted_globals(self, toks: List[Tok]) -> List[Tok]:
        """`console.log(x)` → `println(x)`, `Math.sqrt(x)` → `sqrt(Float64(x))`, etc."""
        FLOAT_WRAPPED = {"sqrt", "pow", "floor", "ceil", "round"}
        NEEDS_HELPER = {"abs", "max", "min"}
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            j = i
            if (toks[j].kind == "id" and j + 2 < len(toks)
                    and toks[j + 1].kind == "punct" and toks[j + 1].value == "."
                    and toks[j + 2].kind in ("id", "kw")):
                key = f"{toks[j].value}.{toks[j + 2].value}"
                if key in GLOBAL_IDENT:
                    repl = GLOBAL_IDENT[key]
                    if repl in FLOAT_WRAPPED and j + 3 < len(toks) and toks[j + 3].kind == "punct" and toks[j + 3].value == "(":
                        close = _match_pair(toks, j + 3, "(", ")")
                        if close != -1:
                            inner = toks[j + 4:close]
                            inner_rew = self._rewrite_inline_expr_tokens(inner, set())
                            args = _split_top_commas(inner_rew)
                            cast_parts = [f"Float64({_to_text(a).strip()})" for a in args]
                            out.append(Tok("id", repl))
                            out.append(Tok("punct", "("))
                            out.append(Tok("id", ", ".join(cast_parts)))
                            out.append(Tok("punct", ")"))
                            i = close + 1
                            self.rule_fires += 1
                            self.helpers.add(repl)
                            self.imports.add("std.math.*")
                            continue
                    out.append(Tok("id", repl))
                    self.rule_fires += 1
                    i = j + 3
                    if repl in FLOAT_WRAPPED:
                        self.helpers.add(repl)
                        self.imports.add("std.math.*")
                    if repl in NEEDS_HELPER:
                        self.helpers.add(repl)
                    continue
            out.append(toks[i])
            i += 1
        return out

    def _rewrite_method_calls(self, toks: List[Tok]) -> List[Tok]:
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            # `.substring(a, b)` → `[a..b]` (Cangjie String slice operator)
            if (t.kind == "punct" and t.value == "."
                    and i + 2 < len(toks)
                    and toks[i + 1].kind in ("id", "kw") and toks[i + 1].value in ("substring", "substr")
                    and toks[i + 2].kind == "punct" and toks[i + 2].value == "("):
                close = _match_pair(toks, i + 2, "(", ")")
                if close != -1:
                    inner = toks[i + 3:close]
                    args = _split_top_commas(inner)
                    if len(args) == 2:
                        a_txt = _to_text(self._rewrite_inline_expr_tokens(args[0], set())).strip()
                        b_txt = _to_text(self._rewrite_inline_expr_tokens(args[1], set())).strip()
                        out.append(Tok("punct", "["))
                        out.append(Tok("id", f"{a_txt}..{b_txt}"))
                        out.append(Tok("punct", "]"))
                        i = close + 1
                        self.rule_fires += 1
                        continue
                    if len(args) == 1:
                        a_txt = _to_text(self._rewrite_inline_expr_tokens(args[0], set())).strip()
                        out.append(Tok("punct", "["))
                        out.append(Tok("id", f"{a_txt}.."))
                        out.append(Tok("punct", "]"))
                        i = close + 1
                        self.rule_fires += 1
                        continue
            # `.slice(a, b)` (TS Array.slice / String.slice) — same treatment
            if (t.kind == "punct" and t.value == "."
                    and i + 2 < len(toks)
                    and toks[i + 1].kind == "id" and toks[i + 1].value == "slice"
                    and toks[i + 2].kind == "punct" and toks[i + 2].value == "("):
                close = _match_pair(toks, i + 2, "(", ")")
                if close != -1:
                    inner = toks[i + 3:close]
                    args = _split_top_commas(inner)
                    if len(args) == 2:
                        a_txt = _to_text(self._rewrite_inline_expr_tokens(args[0], set())).strip()
                        b_txt = _to_text(self._rewrite_inline_expr_tokens(args[1], set())).strip()
                        out.append(Tok("punct", "["))
                        out.append(Tok("id", f"{a_txt}..{b_txt}"))
                        out.append(Tok("punct", "]"))
                        i = close + 1
                        self.rule_fires += 1
                        continue
            # `.set(k, v)` on a hash-map-like object  →  `[k] = v`
            if (t.kind == "punct" and t.value == "."
                    and i + 2 < len(toks)
                    and toks[i + 1].kind in ("id", "kw") and toks[i + 1].value == "set"
                    and toks[i + 2].kind == "punct" and toks[i + 2].value == "("):
                close = _match_pair(toks, i + 2, "(", ")")
                if close != -1:
                    inner = toks[i + 3:close]
                    args = _split_top_commas(inner)
                    if len(args) == 2:
                        k_txt = _to_text(self._rewrite_inline_expr_tokens(args[0], set())).strip()
                        v_txt = _to_text(self._rewrite_inline_expr_tokens(args[1], set())).strip()
                        out.append(Tok("punct", "["))
                        out.append(Tok("id", k_txt))
                        out.append(Tok("punct", "]"))
                        out.append(Tok("ws", " "))
                        out.append(Tok("op", "="))
                        out.append(Tok("ws", " "))
                        out.append(Tok("id", v_txt))
                        i = close + 1
                        self.rule_fires += 1
                        continue
            # NOTE: we used to rewrite ``.get(k)`` to ``[k]`` here, but
            # Cangjie's HashMap also exposes ``.get(k)`` (returning
            # ``Option<V>``) and user-defined classes commonly define a
            # ``get`` method.  Leaving the syntax untouched is correct
            # for both.  (Indexer ``m[k]`` for HashMap still works
            # naturally because TS users rarely write ``m[k]``.)
            # Method rename via knowledge base
            if (t.kind == "punct" and t.value == "."
                    and i + 1 < len(toks) and toks[i + 1].kind in ("id", "kw")
                    and toks[i + 1].value in METHOD_RENAME):
                name = toks[i + 1].value
                new_name, _kind = METHOD_RENAME[name]
                if i + 2 < len(toks) and toks[i + 2].kind == "punct" and toks[i + 2].value == "(":
                    out.append(t)
                    out.append(Tok("id", new_name))
                    i += 2
                    self.rule_fires += 1
                    continue
            # `.length` → `.size`
            if (t.kind == "punct" and t.value == "."
                    and i + 1 < len(toks) and toks[i + 1].kind == "id"
                    and toks[i + 1].value == "length"):
                out.append(t)
                out.append(Tok("id", "size"))
                i += 2
                self.rule_fires += 1
                continue
            out.append(t)
            i += 1
        return out

    def _rewrite_index_access(self, toks: List[Tok]) -> List[Tok]:
        # Cangjie supports a[i] for Array.  HashMap uses .get/.put — but
        # `m["a"] = 1` looks the same syntactically; the runtime treats it
        # via index operator overloads.  No rewrite needed.
        return toks

    def _rewrite_typeof(self, toks: List[Tok]) -> List[Tok]:
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.kind == "kw" and t.value == "typeof":
                # Best-effort: replace `typeof x === "string"` → `x is String`
                # Find the operand
                j = _next_sig(toks, i + 1)
                if j < len(toks) and toks[j].kind in ("id", "kw"):
                    operand = toks[j].value
                    # peek for === "TYPE"
                    k = _next_sig(toks, j + 1)
                    if (k < len(toks) and toks[k].kind == "op"
                            and toks[k].value in ("===", "==")):
                        m = _next_sig(toks, k + 1)
                        if m < len(toks) and toks[m].kind == "str":
                            ty_lit = toks[m].value.strip("'\"")
                            cj_t = {
                                "string": "String", "number": "Int64",
                                "boolean": "Bool", "object": "Any",
                                "function": "Any", "undefined": "Unit",
                            }.get(ty_lit, "Any")
                            out.append(Tok("id", f"{operand} is {cj_t}"))
                            i = m + 1
                            self.rule_fires += 1
                            continue
                self.notes.append("`typeof` partially translated")
                out.append(Tok("id", "/*typeof*/"))
                i += 1
                continue
            if t.kind == "kw" and t.value == "instanceof":
                out.append(Tok("kw", "is"))
                i += 1
                self.rule_fires += 1
                continue
            out.append(t)
            i += 1
        return out

    # ---- arrow functions in expression context --------------------------
    def _rewrite_arrow_in_expr(self, toks: List[Tok]) -> List[Tok]:
        """Find `(params) => body` and `id => body` and rewrite to Cangjie lambda."""
        out: List[Tok] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            # Case A: `(` params `)` (optional `: RetType`) `=>` body
            if t.kind == "punct" and t.value == "(":
                close = _match_pair(toks, i, "(", ")")
                if close != -1:
                    # skip optional `: ReturnType` after `)`
                    nxt = _next_sig(toks, close + 1)
                    if nxt < len(toks) and toks[nxt].kind == "punct" and toks[nxt].value == ":":
                        # consume return-type annotation up to '=>'
                        rj = nxt + 1
                        depth = 0
                        while rj < len(toks):
                            tt = toks[rj]
                            if tt.kind == "punct" and tt.value in "([{":
                                depth += 1
                            elif tt.kind == "punct" and tt.value in ")]}":
                                depth -= 1
                            if depth == 0 and tt.kind == "op" and tt.value == "=>":
                                break
                            rj += 1
                        nxt = rj
                    if nxt < len(toks) and toks[nxt].kind == "op" and toks[nxt].value == "=>":
                        # extract optional return type between ) and =>
                        # (ignore: not needed for lambda emit)
                        params = toks[i + 1:close]
                        # body: after '=>'
                        body_start = nxt + 1
                        # body is either a single expression up to nearest
                        # statement boundary OR a `{...}` block
                        body_tokens, body_end = self._collect_arrow_body(toks, body_start)
                        # rewrite params: simple param list (no parens)
                        pp = _split_top_commas(params)
                        param_text_parts = []
                        for p in pp:
                            psig = _strip_trivia(p)
                            if not psig:
                                continue
                            name = psig[0].value
                            # skip type annotations etc.
                            # find ':' and type
                            type_str = ""
                            for kk, st_ in enumerate(psig):
                                if st_.kind == "punct" and st_.value == ":":
                                    type_str = map_type_string(_to_text(psig[kk + 1:])) or ""
                                    break
                            if type_str:
                                param_text_parts.append(f"{escape_id(name)}: {type_str}")
                            else:
                                # Cangjie lambdas require typed params – default Int64 if used in arithmetic
                                param_text_parts.append(f"{escape_id(name)}: Int64")
                        body_rewritten = self._rewrite_arrow_body(body_tokens)
                        out.append(Tok("punct", "{"))
                        out.append(Tok("ws", " "))
                        if param_text_parts:
                            out.append(Tok("id", ", ".join(param_text_parts)))
                            out.append(Tok("ws", " "))
                            out.append(Tok("op", "=>"))
                            out.append(Tok("ws", " "))
                        else:
                            out.append(Tok("op", "=>"))
                            out.append(Tok("ws", " "))
                        # if body is a block, splice its inner stmts; else inline
                        bsig = _strip_trivia(body_rewritten)
                        if bsig and bsig[0].kind == "punct" and bsig[0].value == "{":
                            # already a block — strip outer braces
                            bj = 0
                            while bj < len(body_rewritten) and not (
                                    body_rewritten[bj].kind == "punct" and body_rewritten[bj].value == "{"):
                                bj += 1
                            bcl = _match_pair(body_rewritten, bj, "{", "}")
                            inner = body_rewritten[bj + 1:bcl]
                            out.extend(inner)
                        else:
                            out.extend(body_rewritten)
                        out.append(Tok("ws", " "))
                        out.append(Tok("punct", "}"))
                        i = body_end
                        self.rule_fires += 1
                        continue
            # Case B: `id => body`
            if (t.kind == "id" and i + 1 < len(toks)
                    and toks[i + 1].kind == "op" and toks[i + 1].value == "=>"):
                # Avoid mismatch with normal `=>` in match arms; we only
                # rewrite when preceded by a non-`case` context.
                prev = _prev_sig(toks, i)
                if prev < 0 or not (toks[prev].kind == "kw" and toks[prev].value == "case"):
                    body_start = i + 2
                    body_tokens, body_end = self._collect_arrow_body(toks, body_start)
                    body_rewritten = self._rewrite_arrow_body(body_tokens)
                    out.append(Tok("punct", "{"))
                    out.append(Tok("ws", " "))
                    out.append(Tok("id", f"{escape_id(t.value)}: Int64"))
                    out.append(Tok("ws", " "))
                    out.append(Tok("op", "=>"))
                    out.append(Tok("ws", " "))
                    bsig = _strip_trivia(body_rewritten)
                    if bsig and bsig[0].kind == "punct" and bsig[0].value == "{":
                        bj = 0
                        while bj < len(body_rewritten) and not (
                                body_rewritten[bj].kind == "punct" and body_rewritten[bj].value == "{"):
                            bj += 1
                        bcl = _match_pair(body_rewritten, bj, "{", "}")
                        inner = body_rewritten[bj + 1:bcl]
                        out.extend(inner)
                    else:
                        out.extend(body_rewritten)
                    out.append(Tok("ws", " "))
                    out.append(Tok("punct", "}"))
                    i = body_end
                    self.rule_fires += 1
                    continue
            out.append(t)
            i += 1
        return out

    def _collect_arrow_body(self, toks: List[Tok], start: int) -> Tuple[List[Tok], int]:
        i = _next_sig(toks, start)
        if i < len(toks) and toks[i].kind == "punct" and toks[i].value == "{":
            close = _match_pair(toks, i, "{", "}")
            if close != -1:
                return toks[start:close + 1], close + 1
        # Otherwise: gather an expression that stops at the next "outer"
        # `,`, `)`, `]`, `;` or newline.
        depth_p = depth_b = depth_br = 0
        j = i
        while j < len(toks):
            t = toks[j]
            if t.kind == "punct":
                if t.value == "(":
                    depth_p += 1
                elif t.value == ")":
                    if depth_p == 0:
                        break
                    depth_p -= 1
                elif t.value == "[":
                    depth_b += 1
                elif t.value == "]":
                    if depth_b == 0:
                        break
                    depth_b -= 1
                elif t.value == "{":
                    depth_br += 1
                elif t.value == "}":
                    if depth_br == 0:
                        break
                    depth_br -= 1
                elif t.value in (",", ";") and depth_p == depth_b == depth_br == 0:
                    break
            j += 1
        return toks[start:j], j

    def _rewrite_arrow_body(self, body: List[Tok]) -> List[Tok]:
        sig = _strip_trivia(body)
        if sig and sig[0].kind == "punct" and sig[0].value == "{":
            # already a block — rewrite stmts inside
            i = 0
            while i < len(body) and not (body[i].kind == "punct" and body[i].value == "{"):
                i += 1
            close = _match_pair(body, i, "{", "}")
            inner = body[i + 1:close]
            return body[:i + 1] + self._rewrite_stmt_list(inner) + body[close:]
        # else it's an expression — rewrite inline
        return self._rewrite_inline_expr_tokens(body, set())

    # ---- type alias ----
    def _rewrite_type_alias(self, st: List[Tok]) -> List[Tok]:
        # `type X = Y;`  →  `type X = MAPPED;`
        self.rule_fires += 1
        sig = list(st)
        # strip trailing ';'
        trailing = []
        if sig and sig[-1].kind == "punct" and sig[-1].value == ";":
            trailing = [sig[-1]]
            sig = sig[:-1]
        # find '='
        for k, t in enumerate(sig):
            if t.kind == "op" and t.value == "=":
                rhs = sig[k + 1:]
                mapped = map_type_string(_to_text(rhs)) or "Any"
                return sig[:k + 1] + [Tok("ws", " "), Tok("id", mapped)] + trailing
        return st

    # ---- enum ----
    def _rewrite_enum_decl(self, st: List[Tok]) -> List[Tok]:
        """`enum E { A, B = 2, C }` → Cangjie enum with `==`/`!=` operators."""
        self.rule_fires += 1
        out = list(st)
        # Extract enum name
        enum_name = ""
        for k, t in enumerate(out):
            if t.kind == "kw" and t.value == "enum":
                j = _next_sig(out, k + 1)
                if j < len(out):
                    enum_name = out[j].value
                break
        i = 0
        while i < len(out) and not (out[i].kind == "punct" and out[i].value == "{"):
            i += 1
        if i >= len(out):
            return st
        close = _match_pair(out, i, "{", "}")
        if close == -1:
            return st
        inner = out[i + 1:close]
        entries = _split_top_commas(inner)
        names = []
        for e in entries:
            esig = _strip_trivia(e)
            if not esig:
                continue
            names.append(escape_id(esig[0].value))
        # Body: variants + auto-generated == / != operators (so the
        # converted TS code that uses `Color.Red == c` still works).
        variant_line = " | ".join(names)
        if names:
            arms_eq = " | ".join(f"({n}, {n})" for n in names)
            extra = (
                f"\n    public operator func ==(other: {enum_name}): Bool {{\n"
                f"        match ((this, other)) {{\n"
                f"            case {arms_eq} => true\n"
                f"            case _ => false\n"
                f"        }}\n"
                f"    }}\n"
                f"    public operator func !=(other: {enum_name}): Bool {{ !(this == other) }}\n"
            )
        else:
            extra = ""
        body = [Tok("ws", " "), Tok("id", variant_line), Tok("id", extra)]
        return out[:i + 1] + body + out[close:]

    # ---- interface ----
    def _rewrite_interface_decl(self, st: List[Tok]) -> List[Tok]:
        """Rewrite interface members.

        Members like `f(x: number): string;` become `func f(x: Int64): String`.
        Property signatures like `name: string;` are degraded to `prop name: String`.
        """
        self.rule_fires += 1
        out = list(st)
        i = 0
        while i < len(out) and not (out[i].kind == "punct" and out[i].value == "{"):
            i += 1
        if i >= len(out):
            return out
        close = _match_pair(out, i, "{", "}")
        if close == -1:
            return out
        inner = out[i + 1:close]
        # split members by ';' or newline at top level
        members = self._split_interface_members(inner)
        new_inner: List[Tok] = [Tok("nl", "\n")]
        for m in members:
            msig = _strip_trivia(m)
            if not msig:
                continue
            # detect "name(...): type" vs "name: type"
            has_paren = any(t.kind == "punct" and t.value == "(" for t in msig)
            new_inner.append(Tok("ws", "    "))
            if has_paren:
                # method signature
                # find name
                # skip optional modifiers (readonly etc.)
                k = 0
                while k < len(msig) and msig[k].kind == "kw" and msig[k].value in (
                        "readonly", "public", "private", "protected", "static"):
                    k += 1
                name = msig[k].value if k < len(msig) else "f"
                paren_idx = next((idx for idx, t in enumerate(msig)
                                  if t.kind == "punct" and t.value == "("), -1)
                if paren_idx == -1:
                    continue
                # rebuild
                rebuilt = [Tok("kw", "func"), Tok("ws", " "), Tok("id", name)]
                # find matching ')'
                # work on msig
                pclose = _match_pair(msig, paren_idx, "(", ")")
                if pclose == -1:
                    continue
                params = msig[paren_idx:pclose + 1]
                rebuilt.extend(self._rewrite_params(params))
                after = msig[pclose + 1:]
                # optional return type
                ret = ""
                aj = 0
                while aj < len(after) and after[aj].kind in ("ws", "nl", "cmt"):
                    aj += 1
                if aj < len(after) and after[aj].kind == "punct" and after[aj].value == ":":
                    ret = map_type_string(_to_text(after[aj + 1:])) or "Unit"
                if ret:
                    rebuilt.append(Tok("punct", ":"))
                    rebuilt.append(Tok("ws", " "))
                    rebuilt.append(Tok("id", ret))
                new_inner.extend(rebuilt)
            else:
                # property signature → `prop name: Type`
                name = msig[0].value
                k = 1
                if k < len(msig) and msig[k].kind == "op" and msig[k].value == "?":
                    k += 1
                tann = []
                if k < len(msig) and msig[k].kind == "punct" and msig[k].value == ":":
                    tann = msig[k + 1:]
                cj_t = map_type_string(_to_text(tann)) if tann else "Any"
                new_inner.extend([Tok("kw", "prop"), Tok("ws", " "),
                                  Tok("id", escape_id(name)),
                                  Tok("punct", ":"), Tok("ws", " "),
                                  Tok("id", cj_t)])
            new_inner.append(Tok("nl", "\n"))
        # strip `implements` cleanup not needed here
        # also drop `extends` keyword if present in interface header? Cangjie uses `<:`
        # Interface extension TS: `interface A extends B {...}` → `interface A <: B {...}`
        header = out[:i]
        header_str = _to_text(header)
        if " extends " in header_str:
            header_str = header_str.replace(" extends ", " <: ")
            header = [Tok("id", header_str)]
        return header + [Tok("punct", "{")] + new_inner + out[close:]

    def _split_interface_members(self, toks: List[Tok]) -> List[List[Tok]]:
        out: List[List[Tok]] = []
        cur: List[Tok] = []
        p = b = br = 0
        for t in toks:
            v = t.value
            if t.kind == "punct":
                if v == "(":
                    p += 1
                elif v == ")":
                    p -= 1
                elif v == "[":
                    b += 1
                elif v == "]":
                    b -= 1
                elif v == "{":
                    br += 1
                elif v == "}":
                    br -= 1
            if p == b == br == 0 and t.kind == "punct" and v in (";", ","):
                if _strip_trivia(cur):
                    out.append(cur)
                cur = []
                continue
            if p == b == br == 0 and t.kind == "nl":
                if _strip_trivia(cur):
                    out.append(cur)
                    cur = []
                continue
            cur.append(t)
        if _strip_trivia(cur):
            out.append(cur)
        return out

    # ---- class ----
    def _rewrite_class_decl(self, st: List[Tok], *, abstract: bool = False) -> List[Tok]:
        """Rewrite class declaration."""
        self.rule_fires += 1
        out = list(st)
        # collect header up to first '{'
        opener: List[Tok] = []
        i = 0
        while i < len(out) and not (out[i].kind == "punct" and out[i].value == "{"):
            opener.append(out[i])
            i += 1
        header_str = _to_text(opener)
        # `abstract class` is fine as-is; we don't add `open` (it's implied).
        if "abstract" in header_str:
            if not hasattr(self, "_abstract_classes"):
                self._abstract_classes = set()
            m_abs = re.search(r"class\s+([A-Za-z_]\w*)", header_str)
            if m_abs:
                self._abstract_classes.add(m_abs.group(1))
        # extends X → <: X     (and mark this class as a child)
        m = re.search(r"\bextends\s+([\w\.<>,\s]+?)(?=\s+implements\b|\s*\{|$)", header_str)
        super_clause = ""
        if m:
            super_name = m.group(1).strip()
            header_str = header_str[:m.start()].rstrip() + header_str[m.end():]
            super_clause = super_name
            # Remember the parent so that, if its decl is in the same file,
            # we can mark it `open`.
            if not hasattr(self, "_open_parents"):
                self._open_parents = set()
            self._open_parents.add(super_name.split("<")[0].strip())
        # implements I1, I2 → list
        m2 = re.search(r"\bimplements\s+(.+?)(?=\s*\{|$)", header_str)
        iface_list: List[str] = []
        if m2:
            iface_list = [s.strip() for s in m2.group(1).split(",")]
            header_str = header_str[:m2.start()].rstrip()
        bases = ([super_clause] if super_clause else []) + iface_list
        if bases:
            header_str = header_str.rstrip() + " <: " + " & ".join(bases) + " "
        # If we have a super clause, the *methods* may also need `open`/
        # `override`.  We pass this flag downward.
        if super_clause:
            self._has_super = True
        else:
            self._has_super = False
        if i >= len(out):
            return st
        close = _match_pair(out, i, "{", "}")
        if close == -1:
            return st
        body_inner = out[i + 1:close]
        new_body = self._rewrite_class_body(body_inner)
        return [Tok("id", header_str), Tok("punct", "{")] + new_body + out[close:]

    def _rewrite_class_body(self, toks: List[Tok]) -> List[Tok]:
        members = self._split_class_members(toks)
        out: List[Tok] = [Tok("nl", "\n")]
        for m in members:
            rewritten = self._rewrite_class_member(m)
            if rewritten:
                out.append(Tok("ws", "    "))
                out.extend(rewritten)
                out.append(Tok("nl", "\n"))
        return out

    def _split_class_members(self, toks: List[Tok]) -> List[List[Tok]]:
        out: List[List[Tok]] = []
        cur: List[Tok] = []
        p = b = br = 0
        i = 0
        while i < len(toks):
            t = toks[i]
            v = t.value
            if t.kind == "punct":
                if v == "(":
                    p += 1
                elif v == ")":
                    p -= 1
                elif v == "[":
                    b += 1
                elif v == "]":
                    b -= 1
                elif v == "{":
                    br += 1
                elif v == "}":
                    br -= 1
            cur.append(t)
            # Member ends when we hit '}' for a method body (br dropped to 0
            # after a '{...}'), or at a top-level ';' for field decls.
            if p == 0 and b == 0 and br == 0:
                if t.kind == "punct" and v == "}":
                    out.append(cur)
                    cur = []
                elif t.kind == "punct" and v == ";":
                    out.append(cur)
                    cur = []
            i += 1
        if _strip_trivia(cur):
            out.append(cur)
        return out

    def _rewrite_class_member(self, m: List[Tok]) -> List[Tok]:
        sig = _strip_trivia(m)
        if not sig:
            return []
        # Strip access modifiers, collect them
        modifiers: List[str] = []
        k = 0
        while k < len(sig) and sig[k].kind == "kw" and sig[k].value in (
                "public", "private", "protected", "static", "readonly",
                "abstract", "override"):
            modifiers.append(sig[k].value)
            k += 1
        is_readonly = "readonly" in modifiers
        is_static = "static" in modifiers
        is_abstract = "abstract" in modifiers
        is_override = "override" in modifiers
        access = "public"
        for am in ("public", "private", "protected"):
            if am in modifiers:
                access = am
                break
        if not k < len(sig):
            return []
        name_tok = sig[k]
        name = name_tok.value
        # getter/setter (`get foo() { ... }` / `set foo(v) { ... }`) — flatten
        # to plain methods named after the property since Cangjie's `prop`
        # declaration requires a backing field; flat methods avoid that
        # complexity.  We rename them to ``getFoo`` / ``setFoo`` so that
        # call-sites which read ``obj.foo`` still need rewriting (we do that
        # in :meth:`_rewrite_method_calls` below).
        if name in ("get", "set") and k + 1 < len(sig) and sig[k + 1].kind == "id":
            prop_name = sig[k + 1].value
            new_name = ("get" if name == "get" else "set") + prop_name[0].upper() + prop_name[1:]
            # Reconstruct member with new method name in place of `get NAME`/`set NAME`
            # Find indices in m
            # Locate name_tok and the following id in m
            kw_idx = next((j for j, t in enumerate(m)
                           if t.kind == "kw" and t.value == name), -1)
            if kw_idx >= 0 and kw_idx + 1 < len(m):
                # Replace m[kw_idx..kw_idx+1] with single id token = new_name.
                # But there may be whitespace between them; consume up to id.
                end = kw_idx + 1
                while end < len(m) and m[end].kind != "id":
                    end += 1
                m = list(m)
                m[kw_idx:end + 1] = [Tok("id", new_name)]
                # Fall through – continue normal method handling.
                sig = _strip_trivia(m)
                # Re-skip modifiers
                k = 0
                while k < len(sig) and sig[k].kind == "kw" and sig[k].value in (
                        "public", "private", "protected", "static", "readonly",
                        "abstract", "override"):
                    k += 1
                name = sig[k].value if k < len(sig) else new_name
        # constructor → init
        if name == "constructor":
            # find '(' onwards
            idx = next((j for j, t in enumerate(m)
                        if t.kind == "punct" and t.value == "("), -1)
            if idx == -1:
                return []
            out: List[Tok] = []
            out.append(Tok("kw", "init"))
            out.extend(self._rewrite_function_signature_body(m[idx:]))
            return out
        # Detect method vs field by presence of `(` before `=`/`:`/`;`
        rest = sig[k + 1:]
        is_method = False
        for t in rest:
            if t.kind == "punct" and t.value == "(":
                is_method = True
                break
            if t.kind == "op" and t.value == "=":
                break
            if t.kind == "punct" and t.value == ";":
                break
        if is_method:
            # method
            out: List[Tok] = []
            out.extend([Tok("kw", access)])
            if is_static:
                out.append(Tok("ws", " "))
                out.append(Tok("kw", "static"))
            # If this class extends a parent, default to `override` for
            # non-static, non-constructor methods (parent has open methods).
            mark_override = (not is_static and getattr(self, "_has_super", False)
                             and not is_override)
            if is_override or mark_override:
                out.append(Tok("ws", " "))
                out.append(Tok("kw", "redef" if is_static else "override"))
            elif not is_static:
                # mark methods open so subclasses (declared later) can override
                out.append(Tok("ws", " "))
                out.append(Tok("kw", "open"))
            if is_abstract:
                out.append(Tok("ws", " "))
            out.append(Tok("ws", " "))
            out.append(Tok("kw", "func"))
            out.append(Tok("ws", " "))
            out.append(Tok("id", escape_id(name)))
            # find first '(' in original `m`
            paren_idx = next((j for j, t in enumerate(m)
                              if t.kind == "punct" and t.value == "("), -1)
            if paren_idx == -1:
                return []
            out.extend(self._rewrite_function_signature_body(m[paren_idx:]))
            return out
        # field: name (?): type (= init) ;
        # locate the `name` token in `m`
        name_idx_in_m = next((j for j, t in enumerate(m)
                              if t.kind == name_tok.kind and t.value == name), -1)
        if name_idx_in_m == -1:
            return []
        after = m[name_idx_in_m + 1:]
        optional = False
        # ':' type
        type_ann: List[Tok] = []
        init: List[Tok] = []
        i2 = 0
        while i2 < len(after) and after[i2].kind in ("ws", "nl", "cmt"):
            i2 += 1
        if i2 < len(after) and after[i2].kind == "op" and after[i2].value == "?":
            optional = True
            i2 += 1
        if i2 < len(after) and after[i2].kind == "punct" and after[i2].value == ":":
            t_start = i2 + 1
            depth = 0
            tj = t_start
            while tj < len(after):
                t = after[tj]
                if t.kind == "punct" and t.value in "([{":
                    depth += 1
                elif t.kind == "punct" and t.value in ")]}":
                    depth -= 1
                if depth == 0 and ((t.kind == "op" and t.value == "=") or
                                   (t.kind == "punct" and t.value == ";")):
                    break
                tj += 1
            type_ann = after[t_start:tj]
            i2 = tj
        if i2 < len(after) and after[i2].kind == "op" and after[i2].value == "=":
            # init until ';'
            j = i2 + 1
            depth = 0
            while j < len(after):
                t = after[j]
                if t.kind == "punct" and t.value in "([{":
                    depth += 1
                elif t.kind == "punct" and t.value in ")]}":
                    depth -= 1
                if depth == 0 and t.kind == "punct" and t.value == ";":
                    break
                j += 1
            init = after[i2 + 1:j]
        cj_type = map_type_string(_to_text(type_ann)) if type_ann else ""
        if optional and cj_type and not cj_type.startswith("?"):
            cj_type = "?" + cj_type
        if not cj_type and init:
            cj_type = infer_init_type(init) or ""
        kw = "let" if is_readonly else "var"
        out: List[Tok] = [Tok("kw", access), Tok("ws", " ")]
        if is_static:
            out.append(Tok("kw", "static"))
            out.append(Tok("ws", " "))
        out.append(Tok("kw", kw))
        out.append(Tok("ws", " "))
        out.append(Tok("id", escape_id(name)))
        if cj_type:
            out.append(Tok("punct", ":"))
            out.append(Tok("ws", " "))
            out.append(Tok("id", cj_type))
        if init:
            out.append(Tok("ws", " "))
            out.append(Tok("op", "="))
            out.append(Tok("ws", " "))
            out.extend(self._rewrite_inline_expr(init))
        elif not init and (not cj_type or not cj_type.startswith("?")):
            # Provide a default to satisfy Cangjie's "must initialize" rule
            default = self._default_for_cj_type(cj_type)
            if default is not None:
                out.append(Tok("ws", " "))
                out.append(Tok("op", "="))
                out.append(Tok("ws", " "))
                out.append(Tok("id", default))
        return out

    def _default_for_cj_type(self, cj_type: str) -> Optional[str]:
        if not cj_type:
            return "0"
        if cj_type in ("Int64", "Int32", "Int8", "Int16", "UInt64", "UInt32", "UInt16", "UInt8"):
            return "0"
        if cj_type in ("Float64", "Float32"):
            return "0.0"
        if cj_type == "Bool":
            return "false"
        if cj_type == "String":
            return '""'
        if cj_type.startswith("Array<"):
            inner = cj_type[len("Array<"):-1]
            return f"Array<{inner}>()"
        if cj_type.startswith("HashMap<") or cj_type.startswith("HashSet<"):
            return f"{cj_type}()"
        return None

    # ---- helpers / rendering -------------------------------------------
    def _strip_trailing_semi(self, toks: List[Tok]) -> List[Tok]:
        out = list(toks)
        while out and out[-1].kind in ("ws", "nl", "cmt"):
            out.pop()
        if out and out[-1].kind == "punct" and out[-1].value == ";":
            out.pop()
        return out

    def _render_main_body(self, toks: List[Tok]) -> str:
        return _to_text(toks).strip()

    def _indent(self, text: str, prefix: str) -> str:
        return "\n".join(prefix + ln if ln.strip() else ln for ln in text.splitlines())

    def _render_helpers(self) -> str:
        out_lines: List[str] = []
        if "abs" in self.helpers:
            out_lines.append(
                "func abs(x: Int64): Int64 { if (x < 0) { -x } else { x } }\n"
                "func absF(x: Float64): Float64 { if (x < 0.0) { -x } else { x } }"
            )
        if "max" in self.helpers:
            out_lines.append("func max(a: Int64, b: Int64): Int64 { if (a >= b) { a } else { b } }")
        if "min" in self.helpers:
            out_lines.append("func min(a: Int64, b: Int64): Int64 { if (a <= b) { a } else { b } }")
        return "\n".join(out_lines)

    # ---- post-process helpers ----

    @staticmethod
    def _match_close_paren(text: str, open_pos: int) -> int:
        """Return the index of the ``)`` that matches the ``(`` at *open_pos*.

        String/template literals are honoured so a stray ``)`` inside a
        ``"..."`` doesn't fool the scanner.  Returns ``-1`` on mismatch.
        """
        if open_pos < 0 or open_pos >= len(text) or text[open_pos] != "(":
            return -1
        depth = 0
        i = open_pos
        n = len(text)
        in_str: Optional[str] = None
        while i < n:
            c = text[i]
            if in_str:
                if c == "\\" and i + 1 < n:
                    i += 2
                    continue
                if c == in_str:
                    in_str = None
                i += 1
                continue
            if c == '"' or c == "'":
                in_str = c
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return -1

    @staticmethod
    def _match_close_brace(text: str, open_pos: int) -> int:
        """Return the index of the ``}`` that matches ``{`` at *open_pos*.

        Strings and ``${…}`` template interpolations are skipped so a
        ``}`` inside a literal won't close the block.  Returns ``-1`` on
        mismatch.
        """
        if open_pos < 0 or open_pos >= len(text) or text[open_pos] != "{":
            return -1
        depth = 0
        i = open_pos
        n = len(text)
        in_str: Optional[str] = None
        while i < n:
            c = text[i]
            if in_str:
                if c == "\\" and i + 1 < n:
                    i += 2
                    continue
                if c == in_str:
                    in_str = None
                i += 1
                continue
            if c == '"' or c == "'":
                in_str = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return -1

    def _wrap_math_int_funcs(self, text: str) -> str:
        """Wrap ``floor(...)``/``ceil(...)``/``round(...)`` calls in
        ``Int64(...)``.  Uses a balanced-paren scan so deeply-nested
        bodies (e.g. ``floor(Float64(a / gcd(a, b)))``) are handled.
        Skips calls already wrapped — i.e. the immediately preceding
        text is ``Int64(``.
        """
        out: List[str] = []
        i = 0
        n = len(text)
        name_re = re.compile(r"(floor|ceil|round)\(")
        while i < n:
            m = name_re.match(text, i)
            # check word boundary on the left
            if m and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")):
                name = m.group(1)
                paren = i + len(name)
                close = self._match_close_paren(text, paren)
                if close == -1:
                    out.append(text[i])
                    i += 1
                    continue
                body = text[paren + 1:close]
                # If immediately preceded by ``Int64(`` (ignoring spaces)
                # the call is already wrapped — leave it alone.
                left = text[:i].rstrip()
                already = left.endswith("Int64(")
                if already:
                    out.append(f"{name}({body})")
                else:
                    out.append(f"Int64({name}({body}))")
                i = close + 1
                continue
            out.append(text[i])
            i += 1
        return "".join(out)

    def _hashmap_get_to_subscript(self, text: str) -> str:
        """Rewrite ``<var>.get(<expr>)`` to ``<var>[<expr>]`` when ``<var>``
        is a known ``HashMap``.  This avoids the ``Some(v)`` print
        artefact that comes from Cangjie's ``HashMap.get`` returning
        ``Option<V>``.
        """
        hashmap_vars = {
            name for name, ty in self.var_types.items()
            if isinstance(ty, str) and ty.startswith("HashMap<")
        }
        if not hashmap_vars:
            return text
        pat = re.compile(
            r"(?<![A-Za-z_0-9.])(" + "|".join(re.escape(v) for v in hashmap_vars) + r")\.get\("
        )
        out: List[str] = []
        i = 0
        n = len(text)
        while i < n:
            m = pat.search(text, i)
            if not m:
                out.append(text[i:])
                break
            out.append(text[i:m.start()])
            var = m.group(1)
            paren = m.end() - 1  # position of '('
            close = self._match_close_paren(text, paren)
            if close == -1:
                out.append(text[m.start():m.end()])
                i = m.end()
                continue
            body = text[paren + 1:close]
            out.append(f"{var}[{body.strip()}]")
            i = close + 1
        return "".join(out)

    def _fix_immutable_param_reassign(self, text: str) -> str:
        """For each ``func`` body, detect parameters that are reassigned
        and rewrite the function so the param is renamed to ``_<name>``
        and a fresh ``var <name> = _<name>`` is injected at the top of
        the body.  Cangjie parameters are immutable; without this fix
        idiomatic TS like ``b = a - Math.floor(a / b) * b`` won't
        compile.
        """
        func_re = re.compile(r"\bfunc\s+[A-Za-z_]\w*\s*(?:<[^>]*>)?\s*\(")
        pieces: List[str] = []
        i = 0
        n = len(text)
        while i < n:
            m = func_re.search(text, i)
            if not m:
                pieces.append(text[i:])
                break
            pieces.append(text[i:m.start()])
            sig_open_paren = m.end() - 1
            sig_close_paren = self._match_close_paren(text, sig_open_paren)
            if sig_close_paren == -1:
                pieces.append(text[m.start():])
                break
            # locate the body's opening brace (after optional ': RetType')
            body_open = text.find("{", sig_close_paren)
            if body_open == -1:
                pieces.append(text[m.start():sig_close_paren + 1])
                i = sig_close_paren + 1
                continue
            body_close = self._match_close_brace(text, body_open)
            if body_close == -1:
                pieces.append(text[m.start():])
                break
            params_text = text[sig_open_paren + 1:sig_close_paren]
            body_text = text[body_open + 1:body_close]
            param_names: List[str] = []
            for part in params_text.split(","):
                ps = part.strip()
                if not ps:
                    continue
                pm = re.match(r"([A-Za-z_]\w*)", ps)
                if pm:
                    param_names.append(pm.group(1))
            reassigned: List[str] = []
            for name in param_names:
                # Look for `name [op]= expr`, excluding `==`/`<=`/`>=`/
                # `!=` and excluding member access like `this.name = ...`.
                p = re.compile(
                    r"(?<![A-Za-z_0-9.])"
                    + re.escape(name)
                    + r"\s*(?:\+|-|\*|/|%|&|\||\^)?=(?!=)"
                )
                hit = False
                for mm in p.finditer(body_text):
                    # skip `let name =`, `var name =`, `const name =`
                    prefix = body_text[max(0, mm.start() - 12):mm.start()]
                    if re.search(r"\b(let|var|const)\s+$", prefix):
                        continue
                    hit = True
                    break
                if hit:
                    reassigned.append(name)
            if not reassigned:
                pieces.append(text[m.start():body_close + 1])
                i = body_close + 1
                continue
            # Rename params in the signature.  Each occurrence is the
            # parameter declaration, so a once-each substitution scoped
            # to the params slice is precise.
            new_params = params_text
            for name in reassigned:
                new_params = re.sub(
                    r"\b" + re.escape(name) + r"\b",
                    f"_{name}",
                    new_params,
                    count=1,
                )
            # Pick an indent that matches the existing body.
            indent = "    "
            for ln in body_text.splitlines():
                stripped = ln.lstrip()
                if stripped:
                    indent = ln[:len(ln) - len(stripped)]
                    break
            prepend = "".join(f"{indent}var {n_} = _{n_}\n" for n_ in reassigned)
            new_body = "\n" + prepend + body_text.lstrip("\n")
            new_block = (
                text[m.start():sig_open_paren + 1]
                + new_params
                + text[sig_close_paren:body_open + 1]
                + new_body
                + "}"
            )
            pieces.append(new_block)
            i = body_close + 1
        return "".join(pieces)

    def _infer_float_params(self, text: str) -> str:
        """Promote ``Int64`` params/returns to ``Float64`` when the
        function body contains float literals or float-only stdlib calls.

        We walk balanced ``func name(...): T { ... }`` blocks and apply
        a conservative substitution to each one in isolation.
        """
        result: List[str] = []
        i = 0
        n = len(text)
        FLOAT_MARKERS = re.compile(r"\b\d+\.\d|\bsqrt\(|\bpow\(")
        while i < n:
            m = re.search(r"\bfunc\s+[A-Za-z_]\w*\s*\(", text[i:])
            if not m:
                result.append(text[i:])
                break
            start = i + m.start()
            result.append(text[i:start])
            # locate matching ')' of the signature
            popen = i + m.end() - 1
            depth = 1
            k = popen + 1
            while k < n and depth > 0:
                c = text[k]
                if c == "(":
                    depth += 1
                elif c == ")":
                    depth -= 1
                k += 1
            sig_close = k - 1  # index of ')'
            # optional `: RetType` then `{`
            brace = text.find("{", sig_close)
            if brace == -1:
                result.append(text[start:])
                break
            # matching '}'
            d = 1
            kk = brace + 1
            in_str = None
            while kk < n and d > 0:
                ch = text[kk]
                if in_str:
                    if ch == "\\" and kk + 1 < n:
                        kk += 2
                        continue
                    if ch == in_str:
                        in_str = None
                elif ch == '"':
                    in_str = '"'
                elif ch == "{":
                    d += 1
                elif ch == "}":
                    d -= 1
                kk += 1
            body_close = kk - 1
            sig = text[start:brace]
            body = text[brace:body_close + 1]
            # detect float usage in body (ignoring strings — a simple
            # strip is good enough for our purposes since we only care
            # about clear float markers in code)
            body_no_str = re.sub(r'"(?:\\.|[^"\\])*"', '""', body)
            if FLOAT_MARKERS.search(body_no_str):
                # promote `: Int64` → `: Float64` in signature AND in
                # the body's local `let X: Int64 = ...` declarations.
                sig_new = re.sub(r":\s*Int64\b", ": Float64", sig)
                body_new = re.sub(r":\s*Int64\b", ": Float64", body)
                result.append(sig_new + body_new)
            else:
                result.append(sig + body)
            i = body_close + 1
        return "".join(result)

    def _postprocess(self, text: str) -> str:
        """Polish the rendered Cangjie source so it reads as idiomatic code.

        The single-pass token rewriter favours correctness over aesthetics
        and intentionally leaves the output a little rough — semicolons
        survive, every class is marked ``open``, every method is decorated
        with ``public open``, and blank lines accumulate.  This pass
        reshapes the text into something that looks hand-written:

          * drop trailing ``;`` (Cangjie style omits them)
          * collapse runs of blank lines and stray ``}``/``{`` whitespace
          * only mark a class ``open`` when it has a known child in the
            same file (tracked via ``self._open_parents``); otherwise the
            ``public open`` decoration on methods is also dropped
          * drop redundant ``: T = T(...)`` annotations the user can infer
          * align ``}`` braces to the column of their owning ``{``
          * tidy small stylistic ticks (``==  ``, ``return  x``, ...)
        """
        # ---- Strip stray TS modifiers that may have leaked through ----
        text = re.sub(r"\bdeclare\b\s*", "", text)
        text = re.sub(r"\bexport\s+default\s*", "", text)
        text = re.sub(r"\bexport\s+", "", text)

        # ---- `Array<T>(n).fill(v)` → `Array<T>(n, repeat: v)` (Cangjie API)
        text = re.sub(
            r"\bArray<([^<>]+)>\(([^()]+)\)\.fill\(([^()]+)\)",
            r"Array<\1>(\2, repeat: \3)",
            text,
        )
        # ---- ``x == None`` / ``x != None`` won't type-check directly on
        # an ``Option<T>`` because the bare ``None`` has no element type;
        # rewrite to the idiomatic helpers.
        text = re.sub(
            r"(\b(?:this\.)?[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*==\s*None\b",
            r"\1.isNone()",
            text,
        )
        text = re.sub(
            r"(\b(?:this\.)?[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*!=\s*None\b",
            r"\1.isSome()",
            text,
        )
        # ---- Int64 cast around `floor(...)`/`ceil(...)`/`round(...)`.
        # In TS, ``Math.floor`` returns an integer-valued number; the
        # user generally wants it back as ``Int64``.  Cangjie's
        # ``floor``/``ceil``/``round`` return ``Float64``, so wrap.
        # We do this *unconditionally* — wrapping a value that's
        # already Int64 with ``Int64(...)`` is a harmless no-op.
        # Uses a balanced-paren scan so arbitrarily-nested call bodies
        # (e.g. ``floor(Float64(a / gcd(a, b)))``) are matched correctly.
        text = self._wrap_math_int_funcs(text)

        # ---- HashMap`.get(k)` → `[k]` for variables typed as HashMap.
        # Cangjie's ``HashMap.get(k)`` returns ``Option<V>`` (so prints
        # as ``Some(v)``), whereas the indexer ``m[k]`` returns ``V``
        # directly — much closer to the TS semantics that the user
        # expected.  We only rewrite when ``m`` is *known* to be a
        # ``HashMap<...>`` to avoid mangling user classes that define
        # their own ``.get`` method.
        text = self._hashmap_get_to_subscript(text)

        # ---- Cangjie function parameters are immutable.  TS code that
        # reassigns them (``b = a - …; a = t``) is otherwise rejected
        # by ``cjc``.  Detect this case, rename the offending params to
        # ``_<name>`` and inject ``var <name> = _<name>`` at the top of
        # the body so the rest of the function (which uses the original
        # names) continues to work unchanged.
        text = self._fix_immutable_param_reassign(text)

        # ---- Float64 inference: when a function body uses a float
        # literal (digit.digit) or float math builtins (sqrt/pow), the
        # ``number`` parameters that we conservatively typed ``Int64``
        # are almost certainly meant to be ``Float64``.  Walk each
        # ``func`` block and patch its signature/body atomically.
        text = self._infer_float_params(text)

        # ---- Mark only the classes that are actually inherited ----
        opens = {n.split("<", 1)[0].strip()
                 for n in getattr(self, "_open_parents", set())}
        abstracts = {n.split("<", 1)[0].strip()
                     for n in getattr(self, "_abstract_classes", set())}

        def _class_open_replace(m: re.Match) -> str:
            name = m.group("name")
            base = name.split("<", 1)[0]
            prefix = m.group("prefix") or ""
            if "open" in prefix or "abstract" in prefix or base in abstracts:
                return m.group(0)
            if base in opens:
                # Make sure we don't double-mark
                return f"{prefix}open class {name}"
            return m.group(0)

        # The replacement is comment-aware: skip matches that are inside
        # a `// ...` line comment or a `/* ... */` block comment.
        def _is_in_comment(s: str, pos: int) -> bool:
            # block comment
            last_open = s.rfind("/*", 0, pos)
            if last_open >= 0:
                last_close = s.rfind("*/", last_open, pos)
                if last_close < 0:
                    return True
            # line comment
            line_start = s.rfind("\n", 0, pos) + 1
            line = s[line_start:pos]
            # ignore "//" inside strings on the line — best-effort
            if "//" in line and '"' not in line.split("//", 1)[0]:
                return True
            return False

        def _safe_replace(m: re.Match) -> str:
            if _is_in_comment(text, m.start()):
                return m.group(0)
            return _class_open_replace(m)

        text = re.sub(
            r"(?P<prefix>(?:\b(?:open|abstract)\b\s+)*)\bclass\s+(?P<name>[A-Za-z_]\w*)\b",
            _safe_replace,
            text,
        )

        # If a class is NOT marked open, strip "open" from its method
        # signatures (we conservatively emitted it on every method).  We
        # do this by scanning class-by-class.
        text = self._strip_redundant_open_in_classes(text, open_classes=opens | abstracts)

        # avoid `abstract open open class` / `open open class`
        text = text.replace("abstract open open class", "abstract open class")
        text = re.sub(r"\bopen\s+open\s+class\b", "open class", text)

        # ---- We deliberately keep `public` on class members.  Cangjie
        # requires that `open`/`override`/interface-impl methods be at
        # least `public`/`protected` (the implicit default is `internal`),
        # so a blanket strip causes "visibility of deriving member..."
        # errors.  Idiomatic Cangjie projects also write `public func`
        # explicitly on class APIs.
        # We do however drop `public` when redundant on `init` constructors,
        # which are implicitly public.
        text = re.sub(r"^(\s+)public\s+(init\b)", r"\1\2", text, flags=re.MULTILINE)

        # ---- Strip trailing `;` (Cangjie idiom omits them).  We keep
        # them only inside `for (init; cond; step)` style heads, but that
        # form was already rewritten to `for (i in r)`, so plain stripping
        # is safe at this point.
        text = re.sub(r";[ \t]*(?=\n)", "", text)
        text = re.sub(r";[ \t]*$", "", text)
        # also: inside-line `;` followed by space is rare, but harmless to leave

        # ---- Drop redundant ":T = T(...)" annotations.  e.g.
        #         let c: Counter = Counter(10)   →  let c = Counter(10)
        text = re.sub(
            r"(\b(?:let|var)\s+[A-Za-z_]\w*)\s*:\s*([A-Z]\w*)\s*=\s*\2\(",
            r"\1 = \2(", text,
        )

        # ---- Tidy `return  x` (double space) and similar
        text = re.sub(r"\b(return|throw|new)\s\s+", r"\1 ", text)
        text = re.sub(r"(=|=>)\s\s+", r"\1 ", text)
        text = re.sub(r"\(\s\s+", "(", text)
        text = re.sub(r"\s\s+\)", ")", text)
        text = re.sub(r",\s\s+", ", ", text)

        # ---- Collapse trailing whitespace on lines
        text = re.sub(r"[ \t]+\n", "\n", text)
        # ---- Strip leading whitespace inside otherwise-blank lines
        text = re.sub(r"\n[ \t]+\n", "\n\n", text)

        # ---- Collapse 3+ blank lines down to 1
        text = re.sub(r"\n{3,}", "\n\n", text)
        # ---- Inside indented blocks (function/class bodies) collapse
        # blank lines: idiomatic Cangjie code does not pepper bodies with
        # blank lines between consecutive statements.  We *keep* blank
        # lines that separate top-level declarations (those start at
        # column 0).
        text = re.sub(r"\n[ \t]*\n(?=[ \t]+\S)", "\n", text)
        # ---- Empty `}` block: remove blank between last stmt and `}`
        text = re.sub(r"\n\n([ \t]*)}", r"\n\1}", text)
        # ---- Empty body `{\n    \n}` → `{}`
        text = re.sub(r"\{\s*\n\s*\}", "{}", text)
        # ---- And: line `{` followed by indented `}` on its own line → keep but tidy
        # ---- Ensure exactly one blank line between top-level declarations
        # (already mostly handled above)

        # ---- Split `{stmt` onto two lines so the reindenter can do its
        # job (e.g. `func f(): X {return x}` → `func f(): X {\nreturn x}`).
        # We do this only outside of string literals to avoid mangling
        # `"${expr}"` template interpolations.
        text = self._split_braces_outside_strings(text)
        # ---- Re-indent stray closing braces that ended up at column 0
        # but actually belong to a nested block.  A simple heuristic:
        # walk the file and re-indent purely structural `}` lines based
        # on running brace depth.
        text = self._reindent(text)

        # ---- One last cleanup: turn `}\n    \n` style chunks into `}\n`
        text = re.sub(r"\n[ \t]+\n", "\n\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    # ------------------------------------------------------------------
    # postprocess helpers
    # ------------------------------------------------------------------
    def _strip_redundant_open_in_classes(self, text: str, *,
                                         open_classes: set) -> str:
        """For any `class Name {...}` whose Name is NOT in *open_classes*,
        remove the ``open`` modifier from method declarations inside that
        class — those methods cannot be overridden anyway.
        """
        out: List[str] = []
        i = 0
        n = len(text)
        while i < n:
            m = re.search(r"\bclass\s+([A-Za-z_]\w*)", text[i:])
            if not m:
                out.append(text[i:])
                break
            start = i + m.start()
            name = m.group(1)
            # Find the opening `{`
            brace = text.find("{", i + m.end())
            if brace < 0:
                out.append(text[i:])
                break
            # Find the matching `}`
            depth = 1
            j = brace + 1
            while j < n and depth > 0:
                c = text[j]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                j += 1
            close = j  # one past the closing brace
            body = text[brace + 1:close - 1]
            out.append(text[i:brace + 1])
            if name not in open_classes:
                body = re.sub(r"\bopen\s+func\b", "func", body)
            out.append(body)
            out.append("}")
            i = close
        return "".join(out)

    def _reindent(self, text: str) -> str:
        """Pretty-print the text by re-indenting every line according to
        the current brace nesting depth.  Strings and `${...}` template
        bodies are *not* analysed for nesting (the tokenizer already
        handled template parts).

        This is a *whitespace-only* transform — we never reorder or
        re-flow code.  When a non-empty line opens more braces than it
        closes, subsequent lines are indented one level deeper.

        Edge cases handled:
          * A line that *starts* with `}` or `)` is itself dedented by 1.
          * Tokens like `} else {` cancel out within the same line.
          * Lines inside strings preserve their original content.

        The indent unit is four spaces.
        """
        IND = "    "
        out_lines: List[str] = []
        depth = 0
        for raw in text.splitlines():
            stripped = raw.lstrip(" \t")
            if not stripped:
                out_lines.append("")
                continue
            opens, closes = self._count_braces_unquoted(stripped)
            # `closing-first` adjustment: if line begins with `}` we
            # render at depth-1
            leading_close = 0
            i = 0
            while i < len(stripped) and stripped[i] in "})":
                if stripped[i] == "}":
                    leading_close += 1
                i += 1
                # tolerate whitespace between `}` and `}`
                while i < len(stripped) and stripped[i] in " \t":
                    i += 1
            line_depth = max(0, depth - leading_close)
            out_lines.append(IND * line_depth + stripped)
            depth = max(0, depth + opens - closes)
        return "\n".join(out_lines)

    @staticmethod
    def _count_braces_unquoted(line: str) -> Tuple[int, int]:
        """Return ``(opens, closes)`` of structural ``{`` / ``}`` in *line*,
        skipping any inside ``"..."`` / ``'...'`` string literals.
        ``${...}`` interpolations are treated as inside the string (their
        braces do not contribute to structural nesting).
        """
        opens = closes = 0
        i = 0
        in_str = False
        q = ""
        interp = 0
        n = len(line)
        while i < n:
            c = line[i]
            if in_str:
                if c == "\\" and i + 1 < n:
                    i += 2
                    continue
                if c == "$" and i + 1 < n and line[i + 1] == "{":
                    interp += 1
                    i += 2
                    continue
                if c == "}" and interp > 0:
                    interp -= 1
                    i += 1
                    continue
                if c == q and interp == 0:
                    in_str = False
                i += 1
                continue
            if c in ("'", '"'):
                in_str = True
                q = c
                i += 1
                continue
            if c == "{":
                opens += 1
            elif c == "}":
                closes += 1
            i += 1
        return opens, closes

    @staticmethod
    def _split_braces_outside_strings(text: str) -> str:
        """Insert newlines after ``{`` and before ``}`` so each occupies its
        own line, but only when the brace is *not* inside a string literal
        or a ``${ ... }`` template interpolation.

        We track three states:
          * code: normal Cangjie code; braces here are structural
          * string: inside ``"..."``; braces here are part of the literal
            (or of an interpolation we still want to keep intact)
          * interp: inside ``${ ... }`` within a string; braces here are
            structural-looking but logically part of the string
        """
        out: List[str] = []
        i = 0
        n = len(text)
        in_str = False
        str_q = ""
        interp_depth = 0  # nesting of `${` inside the string
        while i < n:
            c = text[i]
            if in_str:
                out.append(c)
                if c == "\\" and i + 1 < n:
                    out.append(text[i + 1])
                    i += 2
                    continue
                if c == "$" and i + 1 < n and text[i + 1] == "{":
                    out.append("{")
                    interp_depth += 1
                    i += 2
                    continue
                if c == "}" and interp_depth > 0:
                    interp_depth -= 1
                    i += 1
                    continue
                if c == str_q and interp_depth == 0:
                    in_str = False
                    str_q = ""
                i += 1
                continue
            # outside string
            if c in ("'", '"'):
                in_str = True
                str_q = c
                out.append(c)
                i += 1
                continue
            if c == "{":
                out.append("{")
                # if next non-whitespace char is `}`, leave `{}` untouched
                k = i + 1
                while k < n and text[k] in " \t":
                    k += 1
                if k < n and text[k] != "\n" and text[k] != "}":
                    out.append("\n")
                i += 1
                continue
            if c == "}":
                # newline before, unless preceded by `{` or already newline
                # find previous non-space char
                k = len(out) - 1
                while k >= 0 and out[k] in (" ", "\t"):
                    k -= 1
                if k >= 0 and out[k] not in ("{", "\n"):
                    # Insert newline before this `}`
                    # (preserve any trailing whitespace we just popped)
                    while out and out[-1] in (" ", "\t"):
                        out.pop()
                    out.append("\n")
                out.append("}")
                i += 1
                continue
            out.append(c)
            i += 1
        return "".join(out)


        opens = closes = 0
        i = 0
        in_str = False
        q = ""
        n = len(line)
        while i < n:
            c = line[i]
            if in_str:
                if c == "\\" and i + 1 < n:
                    i += 2
                    continue
                if c == q:
                    in_str = False
                i += 1
                continue
            if c in ("'", '"'):
                in_str = True
                q = c
                i += 1
                continue
            if c == "{":
                opens += 1
            elif c == "}":
                closes += 1
            i += 1
        return opens, closes
