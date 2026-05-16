"""Cross-chunk structural lifting.

The neural translator works on one Go chunk at a time and emits one
Cangjie chunk at a time.  That covers all *local* translation work, but
Go and Cangjie disagree about a few **structural** issues that span
multiple top-level declarations:

* Go structs have no constructor; Cangjie classes do.  Each ``open class``
  needs a synthesized ``public init(...)`` that assigns its fields.
* Go's free-receiver methods (``func (r T) M(...)``) must live *inside*
  the Cangjie class for ``T``.
* Go satisfies interfaces *structurally* (implicit).  Cangjie wants the
  ``<:`` clause on every implementing class plus ``public override`` on
  each interface method.

These transformations need to look at *all* chunks together; they are not
per-chunk translation.  They are kept here, deliberately separate from
the neural translation pipeline.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


# --------------------------------------------------------------------------- #
#  Struct → class with synthesized init                                       #
# --------------------------------------------------------------------------- #

_CLASS_HEAD = re.compile(
    r"^\s*open\s+class\s+(\w+)((?:\s*<:[^{]*)?)\s*\{",
)
_FIELD_LINE = re.compile(
    r"public\s+var\s+(\w+)\s*:\s*([^;\n}]+?)\s*(?=[;\n}])"
)
_HAS_INIT = re.compile(r"\bpublic\s+init\s*\(")


def synthesize_class_inits(decls: List[str]) -> List[str]:
    """Ensure every ``open class`` has a ``public init(...)`` constructor."""

    out: List[str] = []
    for d in decls:
        m = _CLASS_HEAD.match(d)
        if not m or _HAS_INIT.search(d):
            out.append(d)
            continue
        body_start = m.end()
        # Locate the matching closing brace at top level of the class body.
        depth = 1
        i = body_start
        while i < len(d) and depth > 0:
            ch = d[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = d[body_start:i]
        fields: List[Tuple[str, str]] = []
        for fm in _FIELD_LINE.finditer(body):
            fields.append((fm.group(1), fm.group(2).strip()))
        if not fields:
            out.append(d)
            continue
        params = ", ".join(f"{n}: {t}" for n, t in fields)
        assigns = "\n        ".join(f"this.{n} = {n}" for n, _ in fields)
        init = (
            f"\n    public init({params}) {{\n        {assigns}\n    }}\n"
        )
        new = d[:i] + init + d[i:]
        out.append(new)
    return out


# --------------------------------------------------------------------------- #
#  Free-method → class-method promotion                                       #
# --------------------------------------------------------------------------- #

# ``func (r T) Name(arg: U, ...): Ret { ... }`` produced by the model
# becomes ``public func Name(arg: U, ...): Ret { ... }`` inside class T,
# with ``r`` → ``this``.
_METHOD_WITH_RECV = re.compile(
    r"^\s*func\s*\(\s*(\w+)\s*:?\s*([\w<>,\s\[\]]+?)\s*\)\s*"
    r"(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{]+?))?\s*\{",
    re.MULTILINE,
)


def promote_methods(decls: List[str]) -> List[str]:
    """Move ``func (r: T) M(...)`` declarations into ``class T``."""

    classes: Dict[str, int] = {}
    for i, d in enumerate(decls):
        m = _CLASS_HEAD.match(d)
        if m:
            classes[m.group(1)] = i
    if not classes:
        return decls

    moved = set()
    for i, d in enumerate(decls):
        m = _METHOD_WITH_RECV.match(d)
        if not m:
            continue
        recv_name = m.group(1)
        recv_type = m.group(2).strip()
        # The receiver type may be ``T`` or ``*T`` or ``T *`` etc.
        recv_type = recv_type.replace("*", "").strip()
        if recv_type not in classes:
            continue
        mname = m.group(3)
        params = m.group(4).strip()
        ret = (m.group(5) or "Unit").strip()
        body_start = m.end()
        # Find matching close brace.
        depth = 1
        j = body_start
        while j < len(d) and depth > 0:
            ch = d[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        inner = d[body_start:j]
        # Rewrite recv_name → this inside the body.
        if recv_name:
            inner = re.sub(
                r"\b" + re.escape(recv_name) + r"\b", "this", inner
            )
        method = (
            f"\n    public func {mname}({params}): {ret} {{"
            f"{inner}    }}\n"
        )
        # Insert before the final close brace of the class.
        cls_decl = decls[classes[recv_type]]
        last = cls_decl.rfind("}")
        if last == -1:
            continue
        decls[classes[recv_type]] = cls_decl[:last] + method + cls_decl[last:]
        moved.add(i)
    return [d for k, d in enumerate(decls) if k not in moved]


# --------------------------------------------------------------------------- #
#  Implicit interface satisfaction → explicit ``<:``                          #
# --------------------------------------------------------------------------- #

_IFACE_HEAD = re.compile(r"^\s*interface\s+(\w+)\s*\{([\s\S]*?)\n?\}", re.MULTILINE)


def _iface_signatures(body: str) -> List[Tuple[str, str, str]]:
    out = []
    for m in re.finditer(
        r"func\s+(\w+)\s*\(([^)]*)\)\s*:\s*([^\n;}]+)", body,
    ):
        n = m.group(1).strip()
        p = re.sub(r"\s+", " ", m.group(2)).strip()
        r = m.group(3).strip().rstrip(";")
        out.append((n, p, r))
    return out


def _class_method_signatures(body: str) -> List[Tuple[str, str, str]]:
    out = []
    for m in re.finditer(
        r"public\s+(?:override\s+)?func\s+(\w+)\s*\(([^)]*)\)\s*:\s*([^\n;{}]+)",
        body,
    ):
        n = m.group(1).strip()
        p = re.sub(r"\s+", " ", m.group(2)).strip()
        r = m.group(3).strip().rstrip(";")
        out.append((n, p, r))
    return out


def attach_interface_impls(decls: List[str]) -> List[str]:
    full = "\n\n".join(decls)
    interfaces: List[Tuple[str, List[Tuple[str, str, str]]]] = []
    for m in _IFACE_HEAD.finditer(full):
        interfaces.append((m.group(1), _iface_signatures(m.group(2))))
    if not interfaces:
        return decls
    out: List[str] = []
    for d in decls:
        m = _CLASS_HEAD.match(d)
        if not m:
            out.append(d)
            continue
        cname = m.group(1)
        existing_sup = m.group(2) or ""
        body_start = m.end()
        # Find matching close brace.
        depth = 1
        i = body_start
        while i < len(d) and depth > 0:
            ch = d[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = d[body_start:i]
        msigs = set(_class_method_signatures(body))
        implemented = []
        for iname, isigs in interfaces:
            if isigs and all(s in msigs for s in isigs):
                implemented.append(iname)
        if not implemented:
            out.append(d)
            continue
        sup = existing_sup.strip()
        if sup:
            new_head = f"open class {cname} {sup}, {', '.join(implemented)} {{"
        else:
            new_head = f"open class {cname} <: {' & '.join(implemented)} {{"
        new = (
            re.sub(_CLASS_HEAD, new_head, d, count=1)
        )
        # Mark interface methods as ``public override``.
        for iname, isigs in interfaces:
            if iname not in implemented:
                continue
            for n, _, _ in isigs:
                new = re.sub(
                    rf"(\n\s*)public func {re.escape(n)}\b",
                    rf"\1public override func {n}",
                    new,
                )
        out.append(new)
    return out
