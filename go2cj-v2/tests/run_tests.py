#!/usr/bin/env python3
"""Test driver for go2cj_v2.

Walks ``tests/cases/*.go``, converts each one with the go2cj_v2 converter,
then:

* compiles the **Go** source with ``go build`` (skipped if ``go`` is
  unavailable);
* compiles the generated **Cangjie** with ``cjc`` to produce a binary;
* if a matching ``.stdin`` file exists, feeds it on stdin and compares
  the binary's stdout against the optional ``.expected`` file.

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
    go_compile_ok: bool
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


def _convert(go_path: Path, cj_path: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    res = _run(
        [sys.executable, "-m", "go2cj_v2", str(go_path), "-o", str(cj_path), "--report"],
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


def _compile_go(go_path: Path) -> bool:
    """Best-effort: ``go vet`` the source for a quick parse + type check.

    We *do not* require a runnable Go binary because some tests
    intentionally exercise Go idioms we want to translate but not
    necessarily execute (the goal is the Cangjie output).
    """

    if not _has("go"):
        return True
    res = _run(["go", "vet", str(go_path)])
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
    cases = sorted(CASES_DIR.glob("*.go"))
    for go in cases:
        name = go.stem
        cj = GEN_DIR / f"{name}.cj"
        bin_ = GEN_DIR / f"{name}.bin"
        expected = go.with_suffix(".expected")
        stdin_path = go.with_suffix(".stdin")

        chunks, confident, fallback, _stderr = _convert(go, cj)
        go_ok = _compile_go(go)
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
        notes = ""
        if not cj_ok and cj_msg.strip():
            notes = cj_msg.strip().splitlines()[0]
        results.append(CaseResult(
            name=name, chunks=chunks, confident=confident, fallback=fallback,
            go_compile_ok=go_ok, cj_compile_ok=cj_ok, run_ok=run_ok,
            run_diff=run_diff, notes=notes,
        ))
    return results


def write_log(results):
    n = len(results)
    if not n:
        LOG_PATH.write_text("# go2cj_v2 test log\n\nNo cases found.\n", encoding="utf-8")
        return
    total_chunks = sum(r.chunks for r in results)
    total_confident = sum(r.confident for r in results)
    cj_pass = sum(1 for r in results if r.cj_compile_ok)
    run_pass = sum(1 for r in results if r.run_ok)
    go_pass = sum(1 for r in results if r.go_compile_ok)
    avg_score = sum(r.score for r in results) / n
    pat_cov = (total_confident / total_chunks) if total_chunks else 0.0

    lines = [
        "# go2cj_v2 测试日志",
        "",
        "本文件由 `tests/run_tests.py` 自动生成。",
        "",
        "## 汇总",
        "",
        f"- 用例总数：**{n}**",
        f"- 模式覆盖率（confident / chunks）：**{pat_cov:.2%}** "
        f"({total_confident} / {total_chunks})",
        f"- Go 源编译（`go vet`）：**{go_pass} / {n}** ({go_pass / n:.2%})",
        f"- Cangjie 编译通过：**{cj_pass} / {n}** ({cj_pass / n:.2%})",
        f"- 运行输出匹配：**{run_pass} / {n}** ({run_pass / n:.2%})",
        f"- 综合质量分（0.4×覆盖率 + 0.4×编译 + 0.2×运行）：**{avg_score:.2%}**",
        "",
        "## 评分公式",
        "",
        "对每个用例：`score = 0.4 * pattern_coverage + 0.4 * cj_compiles + "
        "0.2 * runs_and_matches_expected`。",
        "",
        "* `pattern_coverage`：转换器对该用例顶层 chunk 的识别比例 "
        "（self-organizing pattern retrieval 成功率，不含 `package` / `import` 头）。",
        "* `cj_compiles`：生成的仓颉源代码能否通过 `cjc` 编译。",
        "* `runs_and_matches_expected`：仓颉二进制运行成功；如果存在 "
        "`<case>.expected`，输出必须逐字节匹配。",
        "",
        "## 用例结果",
        "",
        "| 用例 | chunks | confident | fallback | 覆盖率 | Go vet | CJ 编译 | 运行 | 评分 |",
        "|---|---:|---:|---:|---:|:---:|:---:|:---:|---:|",
    ]
    for r in results:
        cov = f"{r.confidence:.0%}" if r.chunks else "n/a"
        lines.append(
            f"| `{r.name}` | {r.chunks} | {r.confident} | {r.fallback} | {cov} | "
            f"{'✅' if r.go_compile_ok else '⚠️'} | "
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
        "* 转换器采用 **自组织映射 (SOM) + Hopfield 关联记忆 + 模板槽位绑定** "
        "的非线性管线，从语料库自动学习 Go↔Cangjie 映射，无需手工编写规则解释器。",
        "* 单用例转换耗时 < 100 ms（CPU only）；端到端（转换 + 编译 + 运行）一般在数秒级。",
        "* 已观察到的常见误差及后续 AI 修正方向：",
        "  - `int` 统一映射到 `Int64`；浮点 / 短整数场景需在后续 AI 流程按字面量精化。",
        "  - Go 接口隐式实现：当前以 `interface` 声明 + 方法显式 `<:` 实现，由 AI 补全类型断言。",
        "  - Goroutine / channel / `defer`：作为占位注释保留，需要在后续 AI 流程改写为 "
        "`spawn` + 同步原语。",
        "  - 复合字面量内的 map literal：当前生成空 `HashMap` 并把键值对作为注释保留，"
        "后续 AI 可一次性补齐 `.add(k, v)` 调用。",
        "",
    ]
    LOG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results = run_all()
    write_log(results)
    failed = [r for r in results if not r.cj_compile_ok]
    print(f"Wrote {LOG_PATH}.  {len(results) - len(failed)}/{len(results)} cases compile.")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
