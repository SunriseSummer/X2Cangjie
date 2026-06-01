#!/usr/bin/env python3
"""kotlin2cj 项目级端到端测试驱动。

流程：
  1. 遍历 ``tests/cases/proj_*`` 目录，用 kotlin2cj 进行项目级转换；
  2. 用 ``cjpm build`` 编译生成的 cjpm 项目；
  3. 用 ``cjpm run`` 运行并与 ``expected_output`` 比对。

结果汇总写入 ``tests/project_log.md``。

用法::

    source /path/to/cangjie/envsetup.sh
    python3 tests/run_project_tests.py
"""

from __future__ import annotations

import dataclasses
import subprocess
import sys
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES_DIR = HERE / "cases"
CANGJIE_DIR = HERE / "cangjie"
LOG_PATH = HERE / "project_log.md"
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


def have_cjpm() -> bool:
    from shutil import which
    return which("cjpm") is not None


def run_project_case(proj_dir: Path) -> CaseResult:
    name = proj_dir.name
    CANGJIE_DIR.mkdir(exist_ok=True)
    out_dir = CANGJIE_DIR / name

    # Clean previous output
    if out_dir.exists():
        shutil.rmtree(out_dir)

    # 1) Translate project
    r = subprocess.run(
        [str(BIN), str(proj_dir), "-o", str(out_dir)],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return CaseResult(name, False, False, False, r.stderr.strip()[:200])

    if not have_cjpm():
        return CaseResult(name, True, False, False, "cjpm 不可用，跳过编译")

    # 2) Build with cjpm
    r = subprocess.run(
        ["cjpm", "build"],
        cwd=str(out_dir), capture_output=True, text=True
    )
    if r.returncode != 0:
        first = r.stderr.strip().splitlines()
        return CaseResult(name, True, False, False,
                          (first[0] if first else "编译失败")[:200])

    # 3) Run with cjpm run, capture output
    r = subprocess.run(
        ["cjpm", "run"],
        cwd=str(out_dir), capture_output=True, text=True
    )

    # 4) Compare output
    expected_path = proj_dir / "expected_output"
    if not expected_path.exists():
        return CaseResult(name, True, True, True, "无 expected，仅验证编译")

    expected = expected_path.read_text().rstrip() + "\n"
    actual = r.stdout
    # cjpm run 会在末尾追加 "cjpm run finished" 行，需要剥离
    lines = actual.rstrip().split("\n")
    if lines and lines[-1].strip() == "cjpm run finished":
        lines = lines[:-1]
    # 去除尾部空行
    while lines and lines[-1].strip() == "":
        lines = lines[:-1]
    actual = "\n".join(lines) + "\n" if lines else ""

    if actual == expected:
        return CaseResult(name, True, True, True)

    return CaseResult(
        name, True, True, False,
        f"输出不符:\n  got={actual!r}\n  want={expected!r}"[:300],
    )


def tick(b: bool) -> str:
    return "✅" if b else "❌"


def main() -> int:
    if not build_translator():
        print("翻译器构建失败")
        return 1

    # Find project test cases (directories starting with proj_)
    proj_dirs = sorted([
        d for d in CASES_DIR.iterdir()
        if d.is_dir() and d.name.startswith("proj_")
    ])

    if not proj_dirs:
        print("未找到项目级测试用例（tests/cases/proj_*）")
        return 0

    results = [run_project_case(d) for d in proj_dirs]

    n = len(results)
    t_ok = sum(r.translate_ok for r in results)
    c_ok = sum(r.compile_ok for r in results)
    r_ok = sum(r.run_ok for r in results)

    lines = ["# kotlin2cj 项目级测试日志", ""]
    lines.append(f"- 项目用例总数: {n}")
    lines.append(f"- 翻译成功: {t_ok}/{n}")
    lines.append(f"- cjpm 编译通过: {c_ok}/{n}")
    lines.append(f"- 运行输出匹配: {r_ok}/{n}")
    lines.append("")
    lines.append("| 项目 | 翻译 | 编译 | 运行 | 备注 |")
    lines.append("|------|------|------|------|------|")
    for r in results:
        lines.append(
            f"| {r.name} | {tick(r.translate_ok)} | {tick(r.compile_ok)} | "
            f"{tick(r.run_ok)} | {r.note} |"
        )
    LOG_PATH.write_text("\n".join(lines) + "\n")

    print("\n".join(lines[:7]))
    for r in results:
        if not (r.compile_ok and r.run_ok):
            print(f"  FAIL {r.name}: {r.note}")
    return 0 if r_ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
