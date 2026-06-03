#!/usr/bin/env python3
"""Verify that every ``trainset/programs/<name>.go`` and
``trainset/programs/<name>.cj`` both compile, run, and produce the
**same stdout**.

Runs ``go run`` for the Go side and ``cjc + execute`` for the Cangjie
side, requiring ``go`` and ``cjc`` to be available on ``PATH`` (source
``/tmp/cangjie/envsetup.sh`` first).

Exits with a non-zero status if any pair fails.  Prints a per-pair
verdict and a final summary.

Usage::

    python3 trainset/verify_programs.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROGRAMS = HERE / "programs"


def run_go(go_path: Path) -> tuple[bool, str, str]:
    try:
        p = subprocess.run(
            ["go", "run", str(go_path)],
            capture_output=True, text=True, timeout=60,
        )
        return p.returncode == 0, p.stdout, p.stderr
    except Exception as e:
        return False, "", f"exec error: {e}"


def run_cj(cj_path: Path) -> tuple[bool, str, str]:
    try:
        with tempfile.TemporaryDirectory() as td:
            bin_path = Path(td) / "a.out"
            cp = subprocess.run(
                ["cjc", str(cj_path), "-o", str(bin_path)],
                capture_output=True, text=True, timeout=60,
            )
            if cp.returncode != 0 or not bin_path.exists():
                return False, "", cp.stderr or cp.stdout
            rp = subprocess.run(
                [str(bin_path)],
                capture_output=True, text=True, timeout=30,
            )
            return rp.returncode == 0, rp.stdout, rp.stderr
    except Exception as e:
        return False, "", f"exec error: {e}"


def main() -> int:
    pairs = sorted({p.stem for p in PROGRAMS.glob("*.go")}
                   & {p.stem for p in PROGRAMS.glob("*.cj")})
    fails: list[str] = []
    for name in pairs:
        go_path = PROGRAMS / f"{name}.go"
        cj_path = PROGRAMS / f"{name}.cj"
        ok_go, go_out, go_err = run_go(go_path)
        ok_cj, cj_out, cj_err = run_cj(cj_path)
        if not ok_go:
            print(f"FAIL {name}: go failed:\n{go_err}")
            fails.append(name)
            continue
        if not ok_cj:
            print(f"FAIL {name}: cj failed:\n{cj_err}")
            fails.append(name)
            continue
        if go_out != cj_out:
            print(
                f"FAIL {name}: output differs\n"
                f"  go: {go_out!r}\n  cj: {cj_out!r}"
            )
            fails.append(name)
            continue
        print(f"PASS {name}")
    print(f"\n{len(pairs) - len(fails)}/{len(pairs)} program pairs OK")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
