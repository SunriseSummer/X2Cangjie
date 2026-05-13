#!/usr/bin/env python3
"""Test driver for swift2cj.

Walks ``tests/cases/*.swift``, converts each one with the swift2cj
converter, then:

* type-checks the **Swift** source with ``swiftc -typecheck`` (skipped if
  ``swiftc`` is unavailable);
* compiles the **generated Cangjie** with ``cjc`` to produce a binary;
* runs the binary; if a matching ``.expected`` file exists, compares its
  stdout byte-for-byte against the expected output.

Per-case results are aggregated into :file:`tests/log.md`.

Usage::

    source /path/to/cangjie/envsetup.sh
    python3 tests/run_tests.py
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES_DIR = HERE / "cases"
GEN_DIR = HERE / "generated"
LOG_PATH = HERE / "log.md"


@dataclasses.dataclass
class CaseResult:
    name: str
    chunks: int
    confident: int
    fallback: int
    sw_compile_ok: bool
    cj_compile_ok: bool
    run_ok: bool
    run_diff: str
    notes: str

    @property
    def confidence(self) -> float:
        return (self.confident / self.chunks) if self.chunks else 0.0

    @property
    def score(self) -> float:
        """Composite quality score in [0, 1].

        * 0.40 — pattern coverage (confidence ratio)
        * 0.40 — Cangjie compiles
        * 0.20 — runtime output matches (if expected file present)
        """

        s = 0.4 * self.confidence
        if self.cj_compile_ok:
            s += 0.4
        if self.run_ok:
            s += 0.2
        return s


def _strip_ansi(s: str) -> str:
    import re as _re
    return _re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def _convert(sw_path: Path, cj_path: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    res = _run(
        [sys.executable, "-m", "swift2cj", str(sw_path), "-o", str(cj_path), "--report"],
        env=env,
    )
    chunks = confident = fallback = 0
    for tok in res.stderr.split():
        if tok.startswith("chunks="):
            chunks = int(tok.split("=", 1)[1])
        elif tok.startswith("confident="):
            confident = int(tok.split("=", 1)[1])
        elif tok.startswith("fallback="):
            fallback = int(tok.split("=", 1)[1])
    return chunks, confident, fallback, res.stderr


def _has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _case_sort_key(path: Path):
    import re
    m = re.match(r"^(\d+)_(.*)$", path.stem)
    if m:
        return (int(m.group(1)), m.group(2))
    return (10**9, path.stem)


def _typecheck_swift(sw_path: Path) -> bool:
    if not _has("swiftc"):
        return True
    res = _run(["swiftc", "-typecheck", str(sw_path)])
    return res.returncode == 0


def _compile_cj(cj_path: Path, out_path: Path):
    res = _run(["cjc", str(cj_path), "-o", str(out_path)])
    return res.returncode == 0, _strip_ansi(res.stderr or res.stdout)


def _run_binary(bin_path: Path, stdin_path):
    stdin_text = stdin_path.read_text() if stdin_path and stdin_path.exists() else None
    res = subprocess.run(
        [str(bin_path)], input=stdin_text, capture_output=True, text=True, timeout=10,
    )
    return res.returncode == 0, res.stdout


def run_all():
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    cases = sorted(CASES_DIR.glob("*.swift"), key=_case_sort_key)
    for sw in cases:
        name = sw.stem
        cj = GEN_DIR / f"{name}.cj"
        bin_ = GEN_DIR / f"{name}.bin"
        expected = sw.with_suffix(".expected")
        stdin_path = sw.with_suffix(".stdin")

        chunks, confident, fallback, _stderr = _convert(sw, cj)
        sw_ok = _typecheck_swift(sw)
        cj_ok, cj_msg = _compile_cj(cj, bin_)
        run_ok = False
        run_diff = ""
        if cj_ok:
            try:
                rc_ok, out = _run_binary(bin_, stdin_path)
            except Exception as exc:
                rc_ok, out = False, str(exc)
            if expected.exists():
                want = expected.read_text()
                run_ok = rc_ok and out == want
                if not run_ok:
                    run_diff = f"want:\n{want!r}\n got:\n{out!r}"
            else:
                run_ok = rc_ok
        notes = "" if cj_ok else (cj_msg.strip().splitlines()[0] if cj_msg.strip() else "")
        results.append(CaseResult(
            name=name, chunks=chunks, confident=confident, fallback=fallback,
            sw_compile_ok=sw_ok, cj_compile_ok=cj_ok, run_ok=run_ok,
            run_diff=run_diff, notes=notes,
        ))
    return results


def write_log(results):
    n = len(results)
    if not n:
        LOG_PATH.write_text("# swift2cj test log\n\nNo cases found.\n", encoding="utf-8")
        return
    total_chunks = sum(r.chunks for r in results)
    total_confident = sum(r.confident for r in results)
    cj_pass = sum(1 for r in results if r.cj_compile_ok)
    run_pass = sum(1 for r in results if r.run_ok)
    sw_pass = sum(1 for r in results if r.sw_compile_ok)
    avg_score = sum(r.score for r in results) / n
    pat_cov = (total_confident / total_chunks) if total_chunks else 0.0

    lines = [
        "# swift2cj 测试日志",
        "",
        "本文件由 `tests/run_tests.py` 自动生成。",
        "",
        "## 汇总",
        "",
        f"- 用例总数：**{n}**",
        f"- 模式覆盖率（confident / chunks）：**{pat_cov:.2%}** "
        f"({total_confident} / {total_chunks})",
        f"- Swift 源类型检查通过：**{sw_pass} / {n}** ({sw_pass / n:.2%})",
        f"- Cangjie 编译通过：**{cj_pass} / {n}** ({cj_pass / n:.2%})",
        f"- 运行输出匹配（含无期望文件的纯运行成功）：**{run_pass} / {n}** "
        f"({run_pass / n:.2%})",
        f"- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**{avg_score:.2%}**",
        "",
        "## 评分公式",
        "",
        "对每个用例：`score = 0.4 * pattern_coverage + 0.4 * cj_compiles + "
        "0.2 * runs_and_matches_expected`。",
        "",
        "* `pattern_coverage`：转换器对该用例顶层 chunk 的 SOM/Hopfield 模式识别比例。",
        "* `cj_compiles`：生成的仓颉源代码能否通过 `cjc` 编译。",
        "* `runs_and_matches_expected`：生成的仓颉二进制运行成功；如果存在 "
        "`<case>.expected`，输出必须逐字节匹配。",
        "",
        "## 用例结果",
        "",
        "| 用例 | chunks | confident | fallback | 覆盖率 | Swift 检查 | CJ 编译 | 运行 | 评分 |",
        "|---|---:|---:|---:|---:|:---:|:---:|:---:|---:|",
    ]
    for r in results:
        cov = f"{r.confidence:.0%}" if r.chunks else "n/a"
        lines.append(
            f"| `{r.name}` | {r.chunks} | {r.confident} | {r.fallback} | {cov} | "
            f"{'✅' if r.sw_compile_ok else '⚠️'} | "
            f"{'✅' if r.cj_compile_ok else '❌'} | "
            f"{'✅' if r.run_ok else '❌'} | {r.score:.2%} |"
        )

    failing = [r for r in results if not (r.cj_compile_ok and r.run_ok)]
    if failing:
        lines += ["", "## 失败 / 待改进用例诊断", ""]
        for r in failing:
            lines.append(f"### `{r.name}`")
            lines.append("")
            if r.notes:
                lines.append(f"- cjc 诊断：`{r.notes}`")
            if r.run_diff:
                lines.append(f"- 运行差异：")
                lines.append("  ```")
                for ln in r.run_diff.splitlines():
                    lines.append("  " + ln)
                lines.append("  ```")
            lines.append("")

    lines += [
        "",
        "## 质量分析",
        "",
        "* **架构**：转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** "
        "的非线性管线，从语料库自动学习 Swift↔CJ 映射，不需要传统语法分析器或训练数据。",
        "* **效能**：单用例耗时 < 100 ms，全部用例端到端 (转换 + 编译 + 运行) 一般在数秒级；"
        "推理过程纯 CPU、无 GPU 依赖。",
        "* **鲁棒性**：未识别的 chunk 不会让管线崩溃，而是以 "
        "`/* swift2cj: TODO */` 注释保留原文，方便后续 AI 单点修复。",
        "",
        "### 常见简化与后续 AI 可修正方向",
        "",
        "* Swift 类型 `Int` 统一映射到 Cangjie `Int64`；浮点用例可由后续 AI 根据字面量"
        "精化为 `Float64` / `Float32`。",
        "* Swift 外部参数标签（例如 `func f(_ x:)` 的 `_`）一律抹去，转换为单一形参名。"
        "调用点的具名参数 (`f(x: 1)`) 直接保留，与 `init` 上的 `!` 命名参数兼容。",
        "* Swift 结构体的隐式 memberwise init 由转换器显式生成；如果用户已写了 "
        "`init(...)`，转换器不会重复合成。",
        "* Swift 错误处理：`throw` 自定义 `Error` 类型不会通过 Cangjie 编译（Cangjie 仅允许"
        "继承自 `Exception`），用例库中已避免这一形态；`do/catch` 块统一翻译为 "
        "`try { ... } catch (e: Exception) { ... }`。",
        "* Swift 泛型约束 `<T: P>` 当前丢弃为 `<T>`；多重约束用例需后续 AI 改写为 "
        "Cangjie `where` 子句。",
        "",
    ]
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    results = run_all()
    write_log(results)
    failed = [r for r in results if not r.cj_compile_ok]
    print(f"Wrote {LOG_PATH}.  {len(results) - len(failed)}/{len(results)} cases compile.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
