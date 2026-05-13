"""Synthetic Go → Cangjie training corpus generator.

This module *generates* a few-thousand-sample parallel corpus by
randomly substituting slot fillings (identifiers, types, literals,
expressions, statement bodies) into a small set of Go chunk skeletons
and producing the Cangjie counterpart in lock-step.

Crucially, the **same generator** writes both sides of every pair —
which is what trains the neural seq2seq model.  The generator itself
is purely a data source; the model is the thing that learns the
mapping.

We support recursive slot expansion (a body slot may contain
expression slots, etc.) so that the generator emits genuinely varied
multi-statement programs, not just one-line patterns.
"""

from __future__ import annotations

import random
from typing import List, Tuple


# --------------------------------------------------------------------------- #
#  Slot dictionaries                                                          #
# --------------------------------------------------------------------------- #
IDENTS = [
    "x", "y", "z", "i", "j", "k", "n", "m", "a", "b", "c", "d", "v", "u",
    "result", "total", "count", "sum", "value", "data", "item", "key",
    "name", "msg", "buf", "num", "tmp", "out", "ret", "obj", "node",
    "head", "tail", "first", "last", "left", "right", "mid", "p", "q",
    "row", "col", "idx", "size", "step", "delta", "ok", "flag",
]
GO_PRIM = ["int", "int64", "int32", "int16", "int8",
           "uint", "uint64", "uint32", "uint16", "uint8",
           "float32", "float64", "bool", "string", "byte", "rune"]
GO_TO_CJ = {
    "int": "Int64", "int64": "Int64", "int32": "Int32",
    "int16": "Int16", "int8": "Int8",
    "uint": "UInt64", "uint64": "UInt64", "uint32": "UInt32",
    "uint16": "UInt16", "uint8": "UInt8",
    "float32": "Float32", "float64": "Float64",
    "bool": "Bool", "string": "String",
    "byte": "UInt8", "rune": "Rune",
    "error": "Exception", "any": "Any",
}
DEFAULTS = {
    "Int64": "0", "Int32": "0", "Int16": "0", "Int8": "0",
    "UInt64": "0", "UInt32": "0", "UInt16": "0", "UInt8": "0",
    "Float32": "0.0", "Float64": "0.0",
    "Bool": "false", "String": "\"\"", "Rune": "r'\\0'", "Any": "None",
}


def _cj_type(go_ty: str) -> str:
    go_ty = go_ty.strip()
    if go_ty.startswith("[]"):
        inner = _cj_type(go_ty[2:])
        return f"ArrayList<{inner}>"
    if go_ty.startswith("map["):
        end = go_ty.index("]")
        k = _cj_type(go_ty[4:end])
        v = _cj_type(go_ty[end + 1:])
        return f"HashMap<{k}, {v}>"
    return GO_TO_CJ.get(go_ty, go_ty)


# --------------------------------------------------------------------------- #
#  Expression / value / statement samplers                                    #
# --------------------------------------------------------------------------- #


class Sampler:
    def __init__(self, rng: random.Random):
        self.rng = rng

    def ident(self) -> str:
        return self.rng.choice(IDENTS)

    def int_lit(self) -> str:
        # Bias towards small / common numbers.
        return str(self.rng.choice([0, 1, 2, 3, 5, 7, 10, 12, 20, 50, 100,
                                    self.rng.randint(0, 999)]))

    def float_lit(self) -> str:
        return f"{self.rng.uniform(0, 100):.2f}"

    def bool_lit(self) -> str:
        return self.rng.choice(["true", "false"])

    def str_lit(self) -> str:
        choices = ["hello", "world", "ok", "yes", "no", "value",
                   "test", "abc", "foo", "bar"]
        return f'"{self.rng.choice(choices)}"'

    def primitive_type_go(self) -> str:
        return self.rng.choice(GO_PRIM)

    def expr_int(self, depth: int = 0) -> Tuple[str, str]:
        """Return matching (go_expr, cj_expr) for an integer expression."""
        if depth >= 2 or self.rng.random() < 0.55:
            choices = ["lit", "ident"]
        else:
            choices = ["lit", "ident", "add", "sub", "mul", "call"]
        kind = self.rng.choice(choices)
        if kind == "lit":
            v = self.int_lit()
            return v, v
        if kind == "ident":
            v = self.ident()
            return v, v
        if kind == "call":
            name = self.ident()
            a_go, a_cj = self.expr_int(depth + 1)
            return f"{name}({a_go})", f"{name}({a_cj})"
        op = {"add": "+", "sub": "-", "mul": "*"}[kind]
        a_go, a_cj = self.expr_int(depth + 1)
        b_go, b_cj = self.expr_int(depth + 1)
        return f"{a_go} {op} {b_go}", f"{a_cj} {op} {b_cj}"

    def expr_bool(self) -> Tuple[str, str]:
        a_go, a_cj = self.expr_int()
        b_go, b_cj = self.expr_int()
        op = self.rng.choice(["==", "!=", "<", ">", "<=", ">="])
        return f"{a_go} {op} {b_go}", f"{a_cj} {op} {b_cj}"

    def expr_any(self) -> Tuple[str, str]:
        kind = self.rng.choice(["int", "bool", "str", "float"])
        if kind == "int":
            return self.expr_int()
        if kind == "bool":
            return self.expr_bool()
        if kind == "float":
            v = self.float_lit()
            return v, v
        v = self.str_lit()
        return v, v

    # ----- statement-level samplers ----- #
    def stmt(self, depth: int = 0) -> Tuple[str, str]:
        kinds = ["assign", "println", "incr", "return"]
        if depth < 1:
            kinds += ["if", "for_range", "short_decl"]
        kind = self.rng.choice(kinds)
        if kind == "assign":
            lhs = self.ident()
            rhs_go, rhs_cj = self.expr_int()
            return f"{lhs} = {rhs_go}", f"{lhs} = {rhs_cj}"
        if kind == "short_decl":
            lhs = self.ident()
            rhs_go, rhs_cj = self.expr_int()
            return f"{lhs} := {rhs_go}", f"var {lhs} = {rhs_cj}"
        if kind == "println":
            e_go, e_cj = self.expr_any()
            return f"fmt.Println({e_go})", f"println({e_cj})"
        if kind == "incr":
            x = self.ident()
            return f"{x}++", f"{x} += 1"
        if kind == "return":
            e_go, e_cj = self.expr_int()
            return f"return {e_go}", f"return {e_cj}"
        if kind == "if":
            c_go, c_cj = self.expr_bool()
            b_go, b_cj = self.stmt(depth + 1)
            return (f"if {c_go} {{ {b_go} }}",
                    f"if ({c_cj}) {{ {b_cj} }}")
        if kind == "for_range":
            v = self.ident()
            xs = self.ident()
            b_go, b_cj = self.stmt(depth + 1)
            return (f"for _, {v} := range {xs} {{ {b_go} }}",
                    f"for ({v} in {xs}) {{ {b_cj} }}")
        # Fallback
        return self.stmt(depth + 1)

    def body(self, n: int = None, depth: int = 0) -> Tuple[str, str]:
        if n is None:
            n = self.rng.randint(1, 3)
        gos, cjs = [], []
        for _ in range(n):
            g, c = self.stmt(depth)
            gos.append(g)
            cjs.append(c)
        return "; ".join(gos), "; ".join(cjs)

    def params_typed(self) -> Tuple[str, str]:
        n = self.rng.randint(0, 3)
        gos, cjs = [], []
        seen = set()
        for _ in range(n):
            name = self.ident()
            while name in seen:
                name = self.ident()
            seen.add(name)
            go_ty = self.primitive_type_go()
            cj_ty = _cj_type(go_ty)
            gos.append(f"{name} {go_ty}")
            cjs.append(f"{name}: {cj_ty}")
        return ", ".join(gos), ", ".join(cjs)


# --------------------------------------------------------------------------- #
#  Skeleton-based pair generators                                             #
# --------------------------------------------------------------------------- #


def _gen_var_typed(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    go_ty = s.primitive_type_go()
    cj_ty = _cj_type(go_ty)
    if s.rng.random() < 0.5:
        # With initializer.
        if "int" in go_ty or "uint" in go_ty or "byte" in go_ty or "rune" in go_ty:
            v_go, v_cj = s.expr_int()
        elif "float" in go_ty:
            v = s.float_lit()
            v_go = v_cj = v
        elif go_ty == "bool":
            v = s.bool_lit()
            v_go = v_cj = v
        else:
            v = s.str_lit()
            v_go = v_cj = v
        return (f"var {name} {go_ty} = {v_go}",
                f"var {name}: {cj_ty} = {v_cj}")
    # Without initializer — use Cangjie default value.
    default = DEFAULTS.get(cj_ty, "0")
    return f"var {name} {go_ty}", f"var {name}: {cj_ty} = {default}"


def _gen_short_decl(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    e_go, e_cj = s.expr_any()
    return f"{name} := {e_go}", f"var {name} = {e_cj}"


def _gen_const(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    e_go, e_cj = s.expr_any()
    return f"const {name} = {e_go}", f"let {name} = {e_cj}"


def _gen_assign(s: Sampler) -> Tuple[str, str]:
    lhs = s.ident()
    op = s.rng.choice(["=", "+=", "-=", "*=", "/="])
    rhs_go, rhs_cj = s.expr_int()
    return f"{lhs} {op} {rhs_go}", f"{lhs} {op} {rhs_cj}"


def _gen_incr(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    op = s.rng.choice(["++", "--"])
    cj = "+= 1" if op == "++" else "-= 1"
    return f"{name}{op}", f"{name} {cj}"


def _gen_println(s: Sampler) -> Tuple[str, str]:
    if s.rng.random() < 0.2:
        return "fmt.Println()", 'println("")'
    e_go, e_cj = s.expr_any()
    return f"fmt.Println({e_go})", f"println({e_cj})"


def _gen_print(s: Sampler) -> Tuple[str, str]:
    e_go, e_cj = s.expr_any()
    return f"fmt.Print({e_go})", f"print({e_cj})"


def _gen_printf_simple(s: Sampler) -> Tuple[str, str]:
    """fmt.Printf("...%d...\n", x) → print("...${x}...\n")."""
    a_go, a_cj = s.expr_any()
    fmt_pre = s.rng.choice(["sum=", "value=", "x=", "result=", ""])
    fmt_suf = s.rng.choice(["\\n", "", " done\\n"])
    if a_go.replace(".", "").replace("-", "").isdigit() or a_go.isdigit():
        verb = "%d"
    else:
        verb = s.rng.choice(["%d", "%v", "%s"])
    go = f'fmt.Printf("{fmt_pre}{verb}{fmt_suf}", {a_go})'
    cj = f'print("{fmt_pre}${{{a_cj}}}{fmt_suf}")'
    return go, cj


def _gen_if(s: Sampler) -> Tuple[str, str]:
    c_go, c_cj = s.expr_bool()
    b_go, b_cj = s.body()
    return (f"if {c_go} {{ {b_go} }}",
            f"if ({c_cj}) {{ {b_cj} }}")


def _gen_if_else(s: Sampler) -> Tuple[str, str]:
    c_go, c_cj = s.expr_bool()
    a_go, a_cj = s.body()
    b_go, b_cj = s.body()
    return (f"if {c_go} {{ {a_go} }} else {{ {b_go} }}",
            f"if ({c_cj}) {{ {a_cj} }} else {{ {b_cj} }}")


def _gen_if_elif_else(s: Sampler) -> Tuple[str, str]:
    c1_go, c1_cj = s.expr_bool()
    c2_go, c2_cj = s.expr_bool()
    a_go, a_cj = s.body()
    b_go, b_cj = s.body()
    c_go, c_cj = s.body()
    return (
        f"if {c1_go} {{ {a_go} }} else if {c2_go} {{ {b_go} }} else {{ {c_go} }}",
        f"if ({c1_cj}) {{ {a_cj} }} else if ({c2_cj}) {{ {b_cj} }} else {{ {c_cj} }}",
    )


def _gen_for_classic(s: Sampler) -> Tuple[str, str]:
    i = s.ident()
    start = s.int_lit()
    end_go, end_cj = s.expr_int()
    op = s.rng.choice(["<", "<="])
    rng_op = ".." if op == "<" else "..="
    b_go, b_cj = s.body()
    return (
        f"for {i} := {start}; {i} {op} {end_go}; {i}++ {{ {b_go} }}",
        f"for ({i} in {start}{rng_op}{end_cj}) {{ {b_cj} }}",
    )


def _gen_for_cond(s: Sampler) -> Tuple[str, str]:
    c_go, c_cj = s.expr_bool()
    b_go, b_cj = s.body()
    return (f"for {c_go} {{ {b_go} }}",
            f"while ({c_cj}) {{ {b_cj} }}")


def _gen_for_inf(s: Sampler) -> Tuple[str, str]:
    b_go, b_cj = s.body()
    return f"for {{ {b_go} }}", f"while (true) {{ {b_cj} }}"


def _gen_for_range_underscore(s: Sampler) -> Tuple[str, str]:
    v = s.ident()
    xs = s.ident()
    b_go, b_cj = s.body()
    return (f"for _, {v} := range {xs} {{ {b_go} }}",
            f"for ({v} in {xs}) {{ {b_cj} }}")


def _gen_for_range_iv(s: Sampler) -> Tuple[str, str]:
    i = s.ident()
    v = s.ident()
    while v == i:
        v = s.ident()
    xs = s.ident()
    b_go, b_cj = s.body()
    return (f"for {i}, {v} := range {xs} {{ {b_go} }}",
            f"for (({i}, {v}) in {xs}.iterator().enumerate()) {{ {b_cj} }}")


def _gen_func(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    p_go, p_cj = s.params_typed()
    has_ret = s.rng.random() < 0.7
    if has_ret:
        go_ty = s.primitive_type_go()
        cj_ty = _cj_type(go_ty)
        b_go, b_cj = s.body()
        e_go, e_cj = s.expr_int()
        return (
            f"func {name}({p_go}) {go_ty} {{ {b_go}; return {e_go} }}",
            f"func {name}({p_cj}): {cj_ty} {{ {b_cj}; return {e_cj} }}",
        )
    b_go, b_cj = s.body()
    return (
        f"func {name}({p_go}) {{ {b_go} }}",
        f"func {name}({p_cj}): Unit {{ {b_cj} }}",
    )


def _gen_func_multi_ret(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    p_go, p_cj = s.params_typed()
    t1 = s.primitive_type_go()
    t2 = s.primitive_type_go()
    e1_go, e1_cj = s.expr_int()
    e2_go, e2_cj = s.expr_int()
    return (
        f"func {name}({p_go}) ({t1}, {t2}) {{ return {e1_go}, {e2_go} }}",
        f"func {name}({p_cj}): ({_cj_type(t1)}, {_cj_type(t2)}) "
        f"{{ return ({e1_cj}, {e2_cj}) }}",
    )


def _gen_return_tuple(s: Sampler) -> Tuple[str, str]:
    a_go, a_cj = s.expr_int()
    b_go, b_cj = s.expr_int()
    return f"return {a_go}, {b_go}", f"return ({a_cj}, {b_cj})"


def _gen_return(s: Sampler) -> Tuple[str, str]:
    e_go, e_cj = s.expr_any()
    return f"return {e_go}", f"return {e_cj}"


def _gen_break(s: Sampler) -> Tuple[str, str]:
    return "break", "break"


def _gen_continue(s: Sampler) -> Tuple[str, str]:
    return "continue", "continue"


def _gen_len(s: Sampler) -> Tuple[str, str]:
    x = s.ident()
    name = s.ident()
    return f"{name} := len({x})", f"var {name} = ({x}).size"


def _gen_append(s: Sampler) -> Tuple[str, str]:
    xs = s.ident()
    e_go, e_cj = s.expr_int()
    return f"{xs} = append({xs}, {e_go})", f"{xs}.add({e_cj})"


def _gen_slice_decl(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    ty = s.primitive_type_go()
    cj = _cj_type(ty)
    nums = [s.int_lit() for _ in range(s.rng.randint(1, 4))]
    return (
        f"{name} := []{ty}{{{', '.join(nums)}}}",
        f"var {name} = ArrayList<{cj}>([{', '.join(nums)}])",
    )


def _gen_map_decl(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    k = "string"
    v = s.primitive_type_go()
    return (
        f"{name} := make(map[{k}]{v})",
        f"var {name} = HashMap<{_cj_type(k)}, {_cj_type(v)}>()",
    )


def _gen_nil(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    return f"{name} = nil", f"{name} = None"


def _gen_string_concat(s: Sampler) -> Tuple[str, str]:
    a = s.str_lit()
    b = s.str_lit()
    return f"{a} + {b}", f"{a} + {b}"


def _gen_string_concat_ident(s: Sampler) -> Tuple[str, str]:
    a = s.str_lit()
    b = s.ident()
    return f"{a} + {b}", f"{a} + {b}"


def _gen_call(s: Sampler) -> Tuple[str, str]:
    name = s.ident()
    nargs = s.rng.randint(0, 3)
    args_go, args_cj = [], []
    for _ in range(nargs):
        g, c = s.expr_any()
        args_go.append(g)
        args_cj.append(c)
    return (f"{name}({', '.join(args_go)})",
            f"{name}({', '.join(args_cj)})")


def _gen_method_call(s: Sampler) -> Tuple[str, str]:
    o = s.ident()
    m = s.ident()
    a_go, a_cj = s.expr_any()
    return f"{o}.{m}({a_go})", f"{o}.{m}({a_cj})"


def _gen_struct_decl(s: Sampler) -> Tuple[str, str]:
    name = s.ident().capitalize() or "T"
    nfields = s.rng.randint(1, 3)
    fields = []
    cj_fields = []
    for _ in range(nfields):
        f = s.ident()
        ty = s.primitive_type_go()
        cj = _cj_type(ty)
        fields.append(f"{f} {ty}")
        cj_fields.append((f, cj))
    body_go = "; ".join(fields)
    body_cj = "; ".join(f"public var {f}: {t}" for f, t in cj_fields)
    init_params = ", ".join(f"{f}: {t}" for f, t in cj_fields)
    init_body = "; ".join(f"this.{f} = {f}" for f, _ in cj_fields)
    return (
        f"type {name} struct {{ {body_go} }}",
        f"open class {name} {{ {body_cj}; public init({init_params}) "
        f"{{ {init_body} }} }}",
    )


def _gen_interface_decl(s: Sampler) -> Tuple[str, str]:
    name = s.ident().capitalize() or "I"
    nm = s.rng.randint(1, 2)
    methods_go = []
    methods_cj = []
    for _ in range(nm):
        m = s.ident()
        p_go, p_cj = s.params_typed()
        ty = s.primitive_type_go()
        cj = _cj_type(ty)
        methods_go.append(f"{m}({p_go}) {ty}")
        methods_cj.append(f"func {m}({p_cj}): {cj}")
    return (
        f"type {name} interface {{ {'; '.join(methods_go)} }}",
        f"interface {name} {{ {'; '.join(methods_cj)} }}",
    )


def _gen_switch_block(s: Sampler) -> Tuple[str, str]:
    e_go, e_cj = s.expr_int()
    c1 = s.int_lit()
    c2 = s.int_lit()
    a_go, a_cj = s.body(n=1)
    b_go, b_cj = s.body(n=1)
    d_go, d_cj = s.body(n=1)
    return (
        f"switch {e_go} {{ case {c1}: {a_go}; case {c2}: {b_go}; default: {d_go} }}",
        f"match ({e_cj}) {{ case {c1} => {a_cj}; case {c2} => {b_cj}; "
        f"case _ => {d_cj} }}",
    )


def _gen_package(s: Sampler) -> Tuple[str, str]:
    return f"package {s.ident()}", ""


def _gen_import(s: Sampler) -> Tuple[str, str]:
    pkg = s.rng.choice(["fmt", "os", "strings", "math", "strconv"])
    return f'import "{pkg}"', ""


def _gen_main_decl(s: Sampler) -> Tuple[str, str]:
    b_go, b_cj = s.body(n=s.rng.randint(1, 3))
    return (f"func main() {{ {b_go} }}",
            f"main(): Unit {{ {b_cj} }}")


def _gen_call_stmt(s: Sampler) -> Tuple[str, str]:
    # Generate a bare call statement so the model learns identifiers
    # pass through unchanged when there is no rule to apply.
    g, c = _gen_call(s)
    return g, c


GENERATORS = [
    (_gen_var_typed, 8),
    (_gen_short_decl, 8),
    (_gen_const, 3),
    (_gen_assign, 8),
    (_gen_incr, 4),
    (_gen_println, 10),
    (_gen_print, 3),
    (_gen_printf_simple, 6),
    (_gen_if, 6),
    (_gen_if_else, 5),
    (_gen_if_elif_else, 3),
    (_gen_for_classic, 8),
    (_gen_for_cond, 4),
    (_gen_for_inf, 2),
    (_gen_for_range_underscore, 5),
    (_gen_for_range_iv, 3),
    (_gen_func, 6),
    (_gen_func_multi_ret, 3),
    (_gen_return_tuple, 3),
    (_gen_return, 4),
    (_gen_break, 1),
    (_gen_continue, 1),
    (_gen_len, 3),
    (_gen_append, 4),
    (_gen_slice_decl, 4),
    (_gen_map_decl, 2),
    (_gen_nil, 1),
    (_gen_string_concat, 3),
    (_gen_string_concat_ident, 3),
    (_gen_call_stmt, 6),
    (_gen_method_call, 4),
    (_gen_struct_decl, 4),
    (_gen_interface_decl, 2),
    (_gen_switch_block, 4),
    (_gen_package, 1),
    (_gen_import, 1),
    (_gen_main_decl, 4),
]


def generate_corpus(n_samples: int = 20000, seed: int = 0xC0FFEE
                    ) -> List[Tuple[str, str]]:
    """Generate ``n_samples`` Go ↔ Cangjie chunk pairs."""
    rng = random.Random(seed)
    s = Sampler(rng)
    weights = [w for _, w in GENERATORS]
    gens = [g for g, _ in GENERATORS]
    out: List[Tuple[str, str]] = []
    while len(out) < n_samples:
        g = rng.choices(gens, weights=weights, k=1)[0]
        try:
            pair = g(s)
        except Exception:
            continue
        go, cj = pair
        go = go.strip()
        cj = cj.strip()
        if not go:
            continue
        out.append((go, cj))
    return out
