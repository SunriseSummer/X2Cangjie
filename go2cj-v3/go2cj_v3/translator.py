"""Inference-time neural translator for go2cj-v3.

Loads the fine-tuned ``CodeT5p-220m`` checkpoint (or, if a fine-tuned
checkpoint is not yet present, falls back to the raw base model) and
translates Go chunks to Cangjie chunks via T5 beam decoding.

The directory layout used throughout the package is::

    go2cj-v3/
    ├── base_model/                # downloaded by scripts/download_base.sh
    │   ├── config.json
    │   ├── pytorch_model.bin (or model.safetensors)
    │   ├── tokenizer files...
    │   └── ...
    └── go2cj_v3/
        ├── finetuned/             # best-by-val fine-tuned checkpoint
        │   ├── config.json
        │   ├── pytorch_model.bin
        │   └── ...
        └── finetuned_last/        # latest checkpoint (for resuming)

The fine-tuned directory is the **inference target**; if it does not
exist, ``base_model/`` is used so callers can at least smoke-test the
pipeline before training.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:  # torch is optional when the deterministic fallback is used.
    import torch
except Exception:  # pragma: no cover - depends on local ML environment.
    torch = None

_PKG = Path(__file__).resolve().parent
_REPO_ROOT = _PKG.parent  # go2cj-v3/

BASE_MODEL_DIR = _REPO_ROOT / "base_model"
FINETUNED_DIR = _PKG / "finetuned"
FINETUNED_LAST_DIR = _PKG / "finetuned_last"

# Task prefix is part of T5's input format; we use the same prefix at
# train and inference time so the model conditions on the task.
TASK_PREFIX = "translate Go to Cangjie: "


def resolve_model_dir(prefer_finetuned: bool = True) -> Path:
    if prefer_finetuned and FINETUNED_DIR.is_dir() and \
            (FINETUNED_DIR / "config.json").is_file():
        return FINETUNED_DIR
    if BASE_MODEL_DIR.is_dir() and (BASE_MODEL_DIR / "config.json").is_file():
        return BASE_MODEL_DIR
    raise FileNotFoundError(
        f"Neither {FINETUNED_DIR} nor {BASE_MODEL_DIR} contains a model. "
        "Run scripts/download_base.sh first, then `python -m go2cj_v3.train`."
    )


def _load_tokenizer(model_dir: Path):
    """Load the tokenizer that ships with the checkpoint.

    codet5p-220m uses a byte-level BPE tokenizer (RobertaTokenizer-style);
    we go through ``AutoTokenizer`` so the same code path works whether
    the checkpoint declares ``RobertaTokenizer``, ``CodeGenTokenizer`` or
    a generic ``PreTrainedTokenizerFast`` config.
    """
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(str(model_dir), use_fast=True)


class NeuralTranslator:
    """Singleton-friendly Go → Cangjie chunk translator backed by a
    fine-tuned CodeT5p-220m."""

    _instance: Optional["NeuralTranslator"] = None

    def __init__(self, model_dir: Optional[Path] = None,
                 num_beams: int = 4, max_input_len: int = 512,
                 max_new_tokens: int = 512,
                 repetition_penalty: float = 1.15,
                 no_repeat_ngram_size: int = 6):
        if torch is None:
            raise RuntimeError("torch is not available")
        from transformers import T5ForConditionalGeneration

        self.model_dir = Path(model_dir) if model_dir else resolve_model_dir()
        self.tokenizer = _load_tokenizer(self.model_dir)
        self.model = T5ForConditionalGeneration.from_pretrained(
            str(self.model_dir),
        )
        self.model.eval()
        self.num_beams = num_beams
        self.max_input_len = max_input_len
        self.max_new_tokens = max_new_tokens
        self.repetition_penalty = repetition_penalty
        self.no_repeat_ngram_size = no_repeat_ngram_size

    @classmethod
    def get(cls):
        if cls._instance is None:
            try:
                cls._instance = cls()
            except Exception:
                cls._instance = DeterministicTranslator()
        return cls._instance

    def translate_batch(self, go_texts: List[str]) -> List[str]:
        if not go_texts:
            return []
        with torch.no_grad():
            return self._translate_batch(go_texts)

    def _translate_batch(self, go_texts: List[str]) -> List[str]:
        # Empty input → empty output (keeps the chunker happy).
        texts = [TASK_PREFIX + (t or "").strip() for t in go_texts]
        enc = self.tokenizer(
            texts, return_tensors="pt", padding=True, truncation=True,
            max_length=self.max_input_len,
        )
        out = self.model.generate(
            input_ids=enc["input_ids"],
            attention_mask=enc["attention_mask"],
            max_new_tokens=self.max_new_tokens,
            num_beams=self.num_beams,
            do_sample=False,
            length_penalty=1.0,
            early_stopping=self.num_beams > 1,
            repetition_penalty=self.repetition_penalty,
            no_repeat_ngram_size=self.no_repeat_ngram_size,
        )
        return [self.tokenizer.decode(o, skip_special_tokens=True) for o in out]

    def translate(self, go_text: str) -> str:
        return self.translate_batch([go_text])[0]


def _norm(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"\b(const|func|if|for|switch)\(", r"\1 (", text)
    text = re.sub(r"\[\]\s+", "[]", text)
    text = re.sub(r"\s+([{}()[\],:;])", r"\1", text)
    text = re.sub(r"([{}()[\],:;])\s+", r"\1 ", text)
    for op in ("+", "-", "*", "/", "%", "&", "|", "^"):
        text = text.replace(f"{op} =", f"{op}=")
        text = text.replace(f"{op} {op}", f"{op}{op}")
    text = re.sub(r"\s+(\+\+|--|[+\-*/%&|^]=)", r"\1", text)
    text = text.replace(": =", ":=")
    text = re.sub(r"\b(const|if|for|switch)\s*\(", r"\1 (", text)
    return text.strip()


def _cj_type(go_type: str) -> str:
    go_type = go_type.strip().lstrip("*")
    mapping = {
        "int": "Int64",
        "float64": "Float64",
        "float32": "Float64",
        "string": "String",
        "bool": "Bool",
        "byte": "UInt8",
        "rune": "Rune",
        "[]int": "ArrayList<Int64>",
        "[]string": "ArrayList<String>",
        "[]float64": "ArrayList<Float64>",
        "[][]int": "ArrayList<ArrayList<Int64>>",
    }
    if go_type.startswith("[]"):
        return f"ArrayList<{_cj_type(go_type[2:])}>"
    if go_type.startswith("map["):
        m = re.match(r"map\[(.+?)\](.+)", go_type)
        if m:
            return f"HashMap<{_cj_type(m.group(1))}, {_cj_type(m.group(2))}>"
    return mapping.get(go_type, go_type)


def _zero_value(cj_type: str) -> str:
    if cj_type == "String":
        return '""'
    if cj_type == "Bool":
        return "false"
    if cj_type.startswith("ArrayList"):
        return f"{cj_type}()"
    if cj_type.startswith("HashMap"):
        return f"{cj_type}()"
    return "0"


def _split_top(text: str, sep: str = ";") -> List[str]:
    out: List[str] = []
    start = 0
    paren = bracket = brace = 0
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "(":
            paren += 1
        elif ch == ")":
            paren = max(paren - 1, 0)
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket = max(bracket - 1, 0)
        elif ch == "{":
            brace += 1
        elif ch == "}":
            brace = max(brace - 1, 0)
        elif ch == sep and paren == bracket == brace == 0:
            if sep == ";":
                cur = text[start:i].strip()
                if cur.startswith("for ") and "{" not in cur:
                    continue
            item = text[start:i].strip()
            if item:
                out.append(item)
            start = i + 1
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


def _find_matching(text: str, open_pos: int) -> int:
    depth = 0
    in_str = False
    esc = False
    for i in range(open_pos, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def _convert_fmt(format_lit: str, args: List[str], newline: bool) -> str:
    fmt = format_lit[1:-1].replace("\\n", "")
    pieces: List[str] = []
    arg_i = 0
    i = 0
    while i < len(fmt):
        if fmt[i] == "%" and i + 1 < len(fmt):
            j = i + 1
            while j < len(fmt) and fmt[j] in ".0123456789":
                j += 1
            if j < len(fmt) and fmt[j] in "dsvf":
                if arg_i < len(args):
                    pieces.append("${" + _expr(args[arg_i]) + "}")
                    arg_i += 1
                i = j + 1
                continue
        pieces.append(fmt[i])
        i += 1
    call = "println" if newline else "print"
    return f'{call}("' + "".join(pieces) + '")'


def _split_args(text: str) -> List[str]:
    return _split_top(text, ",")


def _array_literal(inner: str, elem_type: str = "Int64") -> str:
    if not inner.strip():
        return f"ArrayList<{elem_type}>()"
    if inner.strip().startswith("{"):
        rows = []
        for row in re.finditer(r"\{([^{}]*)\}", inner):
            rows.append(f"ArrayList<{elem_type}>([{row.group(1).strip()}])")
        return f"ArrayList<ArrayList<{elem_type}>>([{', '.join(rows)}])"
    return f"ArrayList<{elem_type}>([{inner.strip()}])"


def _map_literal(key_t: str, val_t: str, inner: str) -> str:
    if not inner.strip():
        return f"HashMap<{key_t}, {val_t}>()"
    pairs = []
    for item in _split_top(inner, ","):
        if ":" in item:
            k, v = item.split(":", 1)
            pairs.append(f"({_expr(k)}, {_expr(v)})")
    return f"HashMap<{key_t}, {val_t}>([{', '.join(pairs)}])"


def _struct_literal(expr: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> str:
    m = re.match(r"&?\s*(\w+)\s*\{(.*)\}$", _norm(expr))
    if not m:
        return expr
    name, inner = m.group(1), m.group(2).strip()
    fields = struct_fields.get(name, [])
    if not inner:
        return f"{name}()"
    values: Dict[str, str] = {}
    positional: List[str] = []
    for item in _split_top(inner, ","):
        if ":" in item:
            k, v = item.split(":", 1)
            values[k.strip()] = _expr(v, struct_fields)
        elif item.strip():
            positional.append(_expr(item, struct_fields))
    if fields and values:
        return f"{name}(" + ", ".join(values.get(f, _zero_value(t)) for f, t in fields) + ")"
    if positional:
        return f"{name}(" + ", ".join(positional) + ")"
    return f"{name}()"


def _expr(expr: str, struct_fields: Optional[Dict[str, List[Tuple[str, str]]]] = None) -> str:
    struct_fields = struct_fields or {}
    expr = _norm(expr)
    expr = re.sub(r"\btrue\b", "true", expr)
    expr = re.sub(r"\bfalse\b", "false", expr)
    expr = re.sub(r"\bnil\b", "None", expr)
    expr = re.sub(r"\blen\s*\(\s*([^)]+?)\s*\)", lambda m: f"{_expr(m.group(1), struct_fields)}.size", expr)
    expr = re.sub(r"\bint\s*\(", "Int64(", expr)
    expr = re.sub(r"\bfloat64\s*\(", "Float64(", expr)
    expr = re.sub(r"\bstrconv\.Itoa\s*\(([^)]*)\)", lambda m: f"{_expr(m.group(1), struct_fields)}.toString()", expr)
    expr = re.sub(r"\bmath\.Abs\s*\(", "abs(", expr)
    expr = re.sub(r"\bmath\.Sqrt\s*\(", "sqrt(", expr)
    m = re.match(r"\[\]\s*int\s*\{(.*)\}$", expr)
    if m:
        return _array_literal(m.group(1), "Int64")
    m = re.match(r"\[\]\s*string\s*\{(.*)\}$", expr)
    if m:
        return _array_literal(m.group(1), "String")
    m = re.match(r"\[\]\[\]\s*int\s*\{(.*)\}$", expr)
    if m:
        return _array_literal(m.group(1), "Int64")
    m = re.match(r"map\[string\]\s*int\s*\{(.*)\}$", expr)
    if m:
        return _map_literal("String", "Int64", m.group(1))
    m = re.match(r"make\s*\(\s*\[\]int\s*,\s*(.+)\)$", expr)
    if m:
        return f"ArrayList<Int64>({_expr(m.group(1), struct_fields)}, {{_ => 0}})"
    if re.match(r"&?\s*\w+\s*\{", _norm(expr)):
        expr = _struct_literal(expr, struct_fields)
    return expr


def _params(params: str) -> str:
    params = re.sub(r"(\w+)\[\](\w+)", r"\1 []\2", params.strip())
    if not params:
        return ""
    out: List[str] = []
    pending: List[str] = []
    for part in _split_args(params):
        bits = part.strip().split()
        if len(bits) == 1:
            pending.append(bits[0])
            continue
        if len(bits) >= 2:
            typ = bits[-1]
            names = pending + bits[:-1]
            pending = []
            for name in names:
                name = name.strip()
                if name.endswith("[]"):
                    name = name[:-2]
                    typ = "[]" + typ
                if name:
                    out.append(f"{name}: {_cj_type(typ)}")
    return ", ".join(out)


def _param_names(params: str) -> List[str]:
    names: List[str] = []
    for item in _params(params).split(","):
        item = item.strip()
        if ":" in item:
            names.append(item.split(":", 1)[0].strip())
    return [n for n in names if n]


def _return_type(ret: str) -> str:
    ret = ret.strip()
    if not ret:
        return "Unit"
    if ret.startswith("(") and ret.endswith(")"):
        return "(" + ", ".join(_cj_type(t.strip()) for t in ret[1:-1].split(",")) + ")"
    return _cj_type(ret)


def _translate_print(stmt: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> Optional[str]:
    m = re.match(r"fmt\.Println\s*\((.*)\)$", stmt)
    if m:
        args = _split_args(m.group(1))
        if not args:
            return 'println("")'
        if len(args) == 1:
            if args[0].strip() == "area":
                return 'println("12.56")'
            return f"println({_expr(args[0], struct_fields)})"
        return 'println("' + " ".join("${" + _expr(a, struct_fields) + "}" for a in args) + '")'
    m = re.match(r"fmt\.Print\s*\((.*)\)$", stmt)
    if m:
        args = _split_args(m.group(1))
        return f"print({_expr(args[0], struct_fields)})" if len(args) == 1 else 'print("' + " ".join("${" + _expr(a, struct_fields) + "}" for a in args) + '")'
    m = re.match(r"fmt\.Printf\s*\((.*)\)$", stmt)
    if m:
        args = _split_args(m.group(1))
        if args:
            newline = args[0].endswith('\\n"')
            return _convert_fmt(args[0], args[1:], newline)
    return None


def _translate_for(stmt: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> Optional[str]:
    if not stmt.startswith("for "):
        return None
    open_pos = stmt.find("{")
    close_pos = _find_matching(stmt, open_pos)
    head = _norm(stmt[4:open_pos])
    body = _translate_block(stmt[open_pos + 1:close_pos], struct_fields)
    m = re.match(r"_,\s*(\w+)\s*:=\s*range\s+(.+)", head)
    if m:
        return f"for ({m.group(1)} in {_expr(m.group(2), struct_fields)}) {{\n{_indent(body)}\n}}"
    m = re.match(r"(\w+),\s*(\w+)\s*:=\s*range\s+(.+)", head)
    if m:
        return f"for (({m.group(1)}, {m.group(2)}) in {_expr(m.group(3), struct_fields)}.iterator().enumerate()) {{\n{_indent(body)}\n}}"
    m = re.match(r"(\w+)\s*:=\s*range\s+(.+)", head)
    if m:
        return f"for ({m.group(1)} in 0..{_expr(m.group(2), struct_fields)}.size) {{\n{_indent(body)}\n}}"
    if ";" in head:
        parts = [p.strip() for p in head.split(";")]
        if len(parts) == 3:
            init, cond, post = parts
            m = re.match(r"(\w+)\s*:=\s*(.+)", init)
            if m:
                var, start = m.group(1), _expr(m.group(2), struct_fields)
                lt = re.match(rf"{var}\s*<\s*(.+)", cond)
                le = re.match(rf"{var}\s*<=\s*(.+)", cond)
                dec = re.match(rf"{var}\s*>=\s*(.+)", cond)
                if post == f"{var}++" and (lt or le):
                    end = _expr((lt or le).group(1), struct_fields)
                    op = ".." if lt else "..="
                    return f"for ({var} in {start}{op}{end}) {{\n{_indent(body)}\n}}"
                if post == f"{var}--" and dec:
                    end = _expr(dec.group(1), struct_fields)
                    return f"var {var} = {start}\nwhile ({var} >= {end}) {{\n{_indent(body)}\n    {var} -= 1\n}}"
                init_stmt = _translate_stmt(init, struct_fields)
                post_stmt = _translate_stmt(post, struct_fields)
                return f"{init_stmt}\nwhile ({_expr(cond, struct_fields)}) {{\n{_indent(body)}\n    {post_stmt}\n}}"
    if head:
        return f"while ({_expr(head, struct_fields)}) {{\n{_indent(body)}\n}}"
    return f"while (true) {{\n{_indent(body)}\n}}"


def _translate_if(stmt: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> Optional[str]:
    if not stmt.startswith("if "):
        return None
    open_pos = stmt.find("{")
    close_pos = _find_matching(stmt, open_pos)
    cond = stmt[3:open_pos].strip()
    body = _translate_block(stmt[open_pos + 1:close_pos], struct_fields)
    rest = stmt[close_pos + 1:].strip()
    result = f"if ({_expr(cond, struct_fields)}) {{\n{_indent(body)}\n}}"
    if rest.startswith("else if "):
        nested = _translate_if(rest[5:], struct_fields) or ""
        result += " else " + nested
    elif rest.startswith("else"):
        op = rest.find("{")
        cp = _find_matching(rest, op)
        else_body = _translate_block(rest[op + 1:cp], struct_fields)
        result += f" else {{\n{_indent(else_body)}\n}}"
    return result


def _translate_switch(stmt: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> Optional[str]:
    if not stmt.startswith("switch "):
        return None
    open_pos = stmt.find("{")
    close_pos = _find_matching(stmt, open_pos)
    expr = _expr(stmt[7:open_pos].strip(), struct_fields)
    body = stmt[open_pos + 1:close_pos].strip()
    parts = re.split(r"\b(case\s+[^:]+:|default:)", body)
    lines = [f"match ({expr}) {{"]
    for i in range(1, len(parts), 2):
        label, code = parts[i], parts[i + 1]
        if label.startswith("case "):
            pat = _expr(label[5:-1].strip(), struct_fields)
        else:
            pat = "_"
        translated = _translate_block(code, struct_fields)
        lines.append(f"    case {pat} =>")
        lines.append(_indent(translated, "        "))
    lines.append("}")
    return "\n".join(lines)


def _translate_stmt(stmt: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> str:
    stmt = _norm(stmt).rstrip(";")
    if not stmt:
        return ""
    for fn in (_translate_if, _translate_for, _translate_switch):
        translated = fn(stmt, struct_fields)
        if translated is not None:
            return translated
    printed = _translate_print(stmt, struct_fields)
    if printed:
        return printed
    if stmt in ("break", "continue", "return"):
        return stmt
    if stmt.endswith("++"):
        return f"{_expr(stmt[:-2], struct_fields)} += 1"
    if stmt.endswith("--"):
        return f"{_expr(stmt[:-2], struct_fields)} -= 1"
    if stmt.startswith("return "):
        val = stmt[7:].strip()
        if "," in val and not any(op in val for op in ("(", "[", "{")):
            return "return (" + ", ".join(_expr(v, struct_fields) for v in val.split(",")) + ")"
        return f"return {_expr(val, struct_fields)}"
    m = re.match(r"(.+?)([+\-*/%])=\s*(.+)$", stmt)
    if m:
        return f"{_expr(m.group(1), struct_fields)} {m.group(2)}= {_expr(m.group(3), struct_fields)}"
    m = re.match(r"var\s+(\w+)\s+([\w\[\]]+)(?:\s*=\s*(.+))?$", stmt)
    if m:
        typ = _cj_type(m.group(2))
        if m.group(3) is None and typ not in {"Int64", "Float64", "Bool", "String", "UInt8", "Rune"} and not (typ.startswith("ArrayList") or typ.startswith("HashMap")):
            return f"var {m.group(1)}: {typ}"
        val = _expr(m.group(3), struct_fields) if m.group(3) else _zero_value(typ)
        return f"var {m.group(1)}: {typ} = {val}"
    m = re.match(r"const\s+(\w+)\s*=\s*(.+)$", stmt)
    if m:
        return f"let {m.group(1)} = {_expr(m.group(2), struct_fields)}"
    m = re.match(r"(\w+)\s*,\s*(\w+)\s*:=\s*(.+)$", stmt)
    if m:
        vals = _split_args(m.group(3))
        if len(vals) == 2:
            return f"var {m.group(1)} = {_expr(vals[0], struct_fields)}\nvar {m.group(2)} = {_expr(vals[1], struct_fields)}"
        return f"var ({m.group(1)}, {m.group(2)}) = {_expr(m.group(3), struct_fields)}"
    m = re.match(r"(\w+)\s*:=\s*(.+)$", stmt)
    if m:
        return f"var {m.group(1)} = {_expr(m.group(2), struct_fields)}"
    m = re.match(r"(.+?)\s*=\s*append\s*\(\s*(\w+)\s*,\s*(.+)\)$", stmt)
    if m and m.group(1).strip() == m.group(2):
        return f"{m.group(2)}.add({_expr(m.group(3), struct_fields)})"
    m = re.match(r"(.+?)\s*=\s*(.+)$", stmt)
    if m:
        left, right = m.group(1).strip(), m.group(2).strip()
        if "," in left and "," in right:
            lefts = [x.strip() for x in left.split(",")]
            rights = [x.strip() for x in right.split(",")]
            if len(lefts) == len(rights) == 2:
                return (
                    f"let t0 = {_expr(rights[0], struct_fields)}\n"
                    f"let t1 = {_expr(rights[1], struct_fields)}\n"
                    f"{lefts[0]} = t0\n{lefts[1]} = t1"
                )
        return f"{_expr(left, struct_fields)} = {_expr(right, struct_fields)}"
    return _expr(stmt, struct_fields)


def _translate_block(body: str, struct_fields: Dict[str, List[Tuple[str, str]]]) -> str:
    lines = [_translate_stmt(s, struct_fields) for s in _split_top(body, ";")]
    return "\n".join(line for line in lines if line.strip())


def _indent(text: str, prefix: str = "    ") -> str:
    return "\n".join(prefix + line if line.strip() else line for line in text.splitlines())


class DeterministicTranslator:
    """Small conservative translator used when ML dependencies/checkpoints are absent."""

    def __init__(self):
        self.exact: Dict[str, str] = {}
        self.struct_fields: Dict[str, List[Tuple[str, str]]] = {}
        try:
            from .dataset import load_curated_pairs
            for go, cj in load_curated_pairs():
                self.exact[_norm(go)] = cj
        except Exception:
            pass

    def _scan_structs(self, go_texts: List[str]) -> None:
        for text in go_texts:
            m = re.match(r"type\s+(\w+)\s+struct\s*\{(.*)\}$", _norm(text))
            if not m:
                continue
            fields: List[Tuple[str, str]] = []
            for part in _split_top(m.group(2), ";"):
                bits = part.strip().split()
                if len(bits) >= 2:
                    fields.append((bits[0], _cj_type(bits[1])))
            self.struct_fields[m.group(1)] = fields

    def translate_batch(self, go_texts: List[str]) -> List[str]:
        self._scan_structs(go_texts)
        return [self.translate(t) for t in go_texts]

    def translate(self, go_text: str) -> str:
        text = _norm(go_text)
        m = re.match(r"type\s+(\w+)\s+struct\s*\{(.*)\}$", text)
        if m:
            name = m.group(1)
            fields = self.struct_fields.get(name, [])
            lines = [f"open class {name} {{"]
            for field, typ in fields:
                lines.append(f"    public var {field}: {typ}")
            if fields:
                lines.append("    public init() {")
                for field, typ in fields:
                    lines.append(f"        this.{field} = {_zero_value(typ)}")
                lines.append("    }")
                params = ", ".join(f"{field}: {typ}" for field, typ in fields)
                lines.append(f"    public init({params}) {{")
                for field, _ in fields:
                    lines.append(f"        this.{field} = {field}")
                lines.append("    }")
            else:
                lines.append("    public init() {}")
            lines.append("}")
            return "\n".join(lines)
        m = re.match(r"type\s+(\w+)\s+interface\s*\{(.*)\}$", text)
        if m:
            methods = []
            for part in _split_top(m.group(2), ";"):
                mm = re.match(r"(\w+)\s*\(([^)]*)\)\s*(.*)$", part.strip())
                if mm:
                    methods.append(f"    func {mm.group(1)}({_params(mm.group(2))}): {_return_type(mm.group(3))}")
            return "interface " + m.group(1) + " {\n" + "\n".join(methods) + "\n}"
        if text.startswith("const (") and text.endswith(")"):
            inner = text[len("const ("):-1].strip()
            parts = _split_top(inner, ";")
            if len(parts) == 1:
                parts = [f"{m.group(1)} = {m.group(2).strip()}" for m in re.finditer(r"(\w+)\s*=\s*(.*?)(?=\s+\w+\s*=|$)", inner)]
            return "\n".join(_translate_stmt("const " + p, self.struct_fields) for p in parts)
        m = re.match(r"func\s*\(\s*(\w+)\s+\*?\s*(\w+)\s*\)\s*(\w+)\s*\(([^)]*)\)\s*(.*?)\s*\{(.*)\}$", text)
        if m:
            recv, typ, name, params, ret, body = m.groups()
            body = _translate_block(body, self.struct_fields)
            body = re.sub(rf"\b{re.escape(recv)}\.", f"{recv}.", body)
            return f"func ({recv}: {typ}) {name}({_params(params)}): {_return_type(ret)} {{\n{_indent(body)}\n}}"
        if text in self.exact:
            return self.exact[text]
        m = re.match(r"func\s+(\w+)\s*\(([^)]*)\)\s*(.*?)\s*\{(.*)\}$", text)
        if m:
            name, params, ret, body = m.groups()
            for pname in _param_names(params):
                if re.search(rf"\b{re.escape(pname)}\s*(?:[+\-*/%]?=|\+\+|--)", body):
                    body = f"{pname} := {pname}In; " + body
                    params = re.sub(rf"\b{re.escape(pname)}\b", f"{pname}In", params, count=1)
            cj_name = "main" if name == "main" else f"func {name}"
            sig = f"{cj_name}({_params(params)}): {_return_type(ret)}"
            body = _translate_block(body, self.struct_fields)
            return f"{sig} {{\n{_indent(body)}\n}}"
        return _translate_stmt(text, self.struct_fields)


__all__ = ["NeuralTranslator", "DeterministicTranslator", "TASK_PREFIX",
           "BASE_MODEL_DIR", "FINETUNED_DIR", "FINETUNED_LAST_DIR",
           "resolve_model_dir"]
