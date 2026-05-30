#!/usr/bin/env python3
"""kotlin2cj 端到端测试驱动。

流程：
  1. `cargo build --release` 构建翻译器；
  2. 遍历 ``tests/cases/*.kt``，用 kotlin2cj 翻译为仓颉代码；
  3. 用 ``cjc`` 编译生成可执行文件；
  4. 运行并把标准输出与同名 ``*.expected`` 比对。

结果汇总写入 ``tests/log.md``。

用法::

    source /path/to/cangjie/envsetup.sh
    python3 tests/run_tests.py
"""

from __future__ import annotations

import dataclasses
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES_DIR = HERE / "cases"
GEN_DIR = HERE / "generated"
LOG_PATH = HERE / "log.md"
BIN = ROOT / "target" / "release" / "kotlin2cj"


@dataclasses.dataclass
class CaseResult:
    name: str
    translate_ok: bool
    compile_ok: bool
    run_ok: bool
    note: str = ""


def build_translator() -> bool:
    print("[build] cargo build --release ...")
    r = subprocess.run(
        ["cargo", "build", "--release"], cwd=ROOT, capture_output=True, text=True
    )
    if r.returncode != 0:
        print(r.stderr)
        return False
    return True


def have_cjc() -> bool:
    from shutil import which

    return which("cjc") is not None


def run_case(kt: Path) -> CaseResult:
    name = kt.stem
    GEN_DIR.mkdir(exist_ok=True)
    cj = GEN_DIR / f"{name}.cj"
    binp = GEN_DIR / name

    # 1) 翻译
    r = subprocess.run(
        [str(BIN), str(kt), "-o", str(cj)], capture_output=True, text=True
    )
    if r.returncode != 0:
        return CaseResult(name, False, False, False, r.stderr.strip()[:200])

    if not have_cjc():
        return CaseResult(name, True, False, False, "cjc 不可用，跳过编译")

    # 2) 编译
    r = subprocess.run(
        ["cjc", str(cj), "-o", str(binp)], capture_output=True, text=True
    )
    if r.returncode != 0:
        first = r.stderr.strip().splitlines()
        return CaseResult(name, True, False, False, first[0] if first else "编译失败")

    # 3) 运行 + 比对
    stdin_path = kt.with_suffix(".stdin")
    stdin_data = stdin_path.read_text() if stdin_path.exists() else None
    r = subprocess.run([str(binp)], input=stdin_data, capture_output=True, text=True)
    expected_path = kt.with_suffix(".expected")
    if not expected_path.exists():
        return CaseResult(name, True, True, True, "无 expected，仅验证编译")
    expected = expected_path.read_text()
    if r.stdout == expected:
        return CaseResult(name, True, True, True)
    return CaseResult(
        name, True, True, False,
        f"输出不符: got={r.stdout!r} want={expected!r}"[:200],
    )


def tick(b: bool) -> str:
    return "✅" if b else "❌"


def main() -> int:
    if not build_translator():
        print("翻译器构建失败")
        return 1

    cases = sorted(CASES_DIR.glob("*.kt"))
    results = [run_case(c) for c in cases]

    n = len(results)
    t_ok = sum(r.translate_ok for r in results)
    c_ok = sum(r.compile_ok for r in results)
    r_ok = sum(r.run_ok for r in results)

    lines = ["# kotlin2cj 测试日志", ""]
    lines.append(f"- 用例总数: {n}")
    lines.append(f"- 翻译成功: {t_ok}/{n}")
    lines.append(f"- 仓颉编译通过: {c_ok}/{n}")
    lines.append(f"- 运行输出匹配: {r_ok}/{n}")
    lines.append("")
    lines.append("| 用例 | 翻译 | 编译 | 运行 | 备注 |")
    lines.append("|------|------|------|------|------|")
    for r in results:
        lines.append(
            f"| {r.name} | {tick(r.translate_ok)} | {tick(r.compile_ok)} | "
            f"{tick(r.run_ok)} | {r.note} |"
        )
    LOG_PATH.write_text("\n".join(lines) + "\n")

    print("\n".join(lines[:6]))
    for r in results:
        if not (r.compile_ok and r.run_ok):
            print(f"  FAIL {r.name}: {r.note}")
    return 0 if r_ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
