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
        """function NAME<G>(params): RetType { body }  →  func NAME<G>(params): RetType { body }."""
        self.rule_fires += 1
        sig = list(st)
        # find 'function' keyword
        for i, t in enumerate(sig):
            if t.kind == "kw" and t.value == "function":
                sig[i] = Tok("kw", "func")
                break
        sig = self._rewrite_signature_and_body(sig, is_method=False)
        return sig

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
                out.extend(self._rewrite_arrow_body(body_part))
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
                out.extend(self._rewrite_arrow_body(body_part))
            else:
                return st
        return out

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
        # Drop modifiers: public/private/protected/readonly
        while sig and sig[0].kind == "kw" and sig[0].value in (
                "public", "private", "protected", "readonly", "static"):
            sig = sig[1:]
        # destructured pattern – degrade by name = "arg"
        if sig and sig[0].kind == "punct" and sig[0].value in ("{", "["):
            self.notes.append("destructured parameter not fully supported")
            return "_arg: Any"
        # Spread: ...args  → variadic; Cangjie has variadic only on call site.
        # We pass as Array.
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
            # collect type until '=' or end
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
        if default_str:
            # Cangjie default-value parameters use `!` named-param syntax
            out = f"{escape_id(name)}!: {type_str} = {default_str}"
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
        # Recurse: rewrite condition expressions and block bodies.
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
            # remove `break;` from body
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
        out = self._rewrite_templates(out)
        out = self._rewrite_arrow_in_expr(out)
        out = self._rewrite_simple_replacements(out, preserve_keywords)
        out = self._rewrite_dotted_globals(out)
        out = self._rewrite_method_calls(out)
        out = self._rewrite_index_access(out)
        out = self._rewrite_typeof(out)
        out = self._rewrite_string_concat(out)
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
        return any(k == "str" for k, _ in chain)

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
                # `new Map<K,V>()` already had new dropped — but bare `Map` → `HashMap`
                self.imports.add("std.collection.*")
                out.append(Tok("id", "HashMap"))
                self.rule_fires += 1
            elif t.kind == "id" and t.value == "Set":
                self.imports.add("std.collection.*")
                out.append(Tok("id", "HashSet"))
                self.rule_fires += 1
            elif t.kind == "id" and t.value == "Array":
                out.append(t)
            else:
                out.append(t)
            i += 1
        return out

    def _rewrite_dotted_globals(self, toks: List[Tok]) -> List[Tok]:
        """`console.log(x)` → `println(x)`, `Math.sqrt(x)` → `sqrt(Float64(x))`, etc."""
        FLOAT_WRAPPED = {"sqrt", "pow", "floor", "ceil", "round"}
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
                    # Wrap the next call's arguments in Float64() for math
                    # functions that require it.
                    if repl in FLOAT_WRAPPED and j + 3 < len(toks) and toks[j + 3].kind == "punct" and toks[j + 3].value == "(":
                        close = _match_pair(toks, j + 3, "(", ")")
                        if close != -1:
                            inner = toks[j + 4:close]
                            inner_rew = self._rewrite_inline_expr_tokens(inner, set())
                            inner_text = _to_text(inner_rew).strip()
                            # Split on top-level commas (pow has 2 args)
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
                    if key.startswith("Math.") and repl in FLOAT_WRAPPED:
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
            # `.method(` → `.newname(`
            if (t.kind == "punct" and t.value == "."
                    and i + 1 < len(toks) and toks[i + 1].kind in ("id", "kw")
                    and toks[i + 1].value in METHOD_RENAME):
                name = toks[i + 1].value
                new_name, _kind = METHOD_RENAME[name]
                # Only rewrite if it really is a call (followed by `(`)
                # — but even property access like `.length` matters
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
                                "string": "String", "number": "Float64",
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
            # Case A: `(` params `)` `=>` body
            if t.kind == "punct" and t.value == "(":
                close = _match_pair(toks, i, "(", ")")
                if close != -1:
                    nxt = _next_sig(toks, close + 1)
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
                elif t.kind == "punct" and t.value == ")":
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
        """`enum E { A, B = 2, C }` → `enum E { A | B | C }` (loses explicit values)."""
        self.rule_fires += 1
        out = list(st)
        i = 0
        while i < len(out) and not (out[i].kind == "punct" and out[i].value == "{"):
            i += 1
        if i >= len(out):
            return st
        close = _match_pair(out, i, "{", "}")
        if close == -1:
            return st
        inner = out[i + 1:close]
        # split on commas (top level)
        entries = _split_top_commas(inner)
        names = []
        for e in entries:
            esig = _strip_trivia(e)
            if not esig:
                continue
            # name maybe followed by '=' value — drop value
            n = esig[0].value
            names.append(escape_id(n))
        body = [Tok("ws", " ")]
        for k, n in enumerate(names):
            if k > 0:
                body.append(Tok("ws", " "))
                body.append(Tok("op", "|"))
                body.append(Tok("ws", " "))
            body.append(Tok("id", n))
        body.append(Tok("ws", " "))
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
        """Rewrite class declaration.

        Translates:
          * field declarations  (`x: T = v;` → `var x: T = v`)
          * `constructor(...)`  →  `init(...)`
          * `method(...): T {}` →  `public func method(...): T {}`
          * access modifiers (public/private/protected) preserved
          * `extends Y` → `<: Y`
          * `implements I1, I2` → `<: I1 & I2`
        """
        self.rule_fires += 1
        out = list(st)
        # Drop `abstract`, mark `open`/`abstract`
        opener: List[Tok] = []
        i = 0
        # collect modifiers and the class name + generics + heritage clauses
        while i < len(out) and not (out[i].kind == "punct" and out[i].value == "{"):
            opener.append(out[i])
            i += 1
        # transform header text
        header_str = _to_text(opener)
        # `abstract class` → `abstract open class`? In Cangjie use `abstract`
        header_str = header_str.replace("abstract class", "abstract open class")
        # extends X → <: X
        m = re.search(r"\bextends\s+([\w\.<>,\s]+?)(?=\s+implements\b|\s*\{|$)", header_str)
        super_clause = ""
        if m:
            super_name = m.group(1).strip()
            header_str = header_str[:m.start()].rstrip() + header_str[m.end():]
            super_clause = super_name
        # implements I1, I2 → list
        m2 = re.search(r"\bimplements\s+(.+?)(?=\s*\{|$)", header_str)
        iface_list: List[str] = []
        if m2:
            iface_list = [s.strip() for s in m2.group(1).split(",")]
            header_str = header_str[:m2.start()].rstrip()
        bases = ([super_clause] if super_clause else []) + iface_list
        if bases:
            header_str = header_str.rstrip() + " <: " + " & ".join(bases) + " "
        # body
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
            if is_override:
                out.append(Tok("ws", " "))
                out.append(Tok("kw", "redef" if is_static else "override"))
            if is_abstract:
                # Cangjie: declare without body; method must be in an `open abstract class`
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
            out_lines.append("func abs<T>(x: T): T where T <: Comparable<T> & Neg<T> { if (x < (x - x)) { -x } else { x } }")
        # max/min on numbers
        if "max" in self.helpers:
            out_lines.append("func max(a: Int64, b: Int64): Int64 { if (a >= b) { a } else { b } }")
        if "min" in self.helpers:
            out_lines.append("func min(a: Int64, b: Int64): Int64 { if (a <= b) { a } else { b } }")
        # std.math.* is added via self.imports — don't duplicate here.
        return "\n".join(out_lines)

    def _postprocess(self, text: str) -> str:
        # Collapse leftover semicolons at line-ends (Cangjie tolerates `;` but
        # idiomatic code omits them).  We leave them in place – they parse.
        # Strip stray TS modifiers that may have leaked through
        text = re.sub(r"\bdeclare\b\s*", "", text)
        text = re.sub(r"\bexport\s+default\s*", "", text)
        text = re.sub(r"\bexport\s+", "", text)
        # Collapse blank lines run
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text
