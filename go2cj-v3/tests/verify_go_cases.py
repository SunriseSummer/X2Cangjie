#!/usr/bin/env python3
"""Verify every ``tests/cases/<name>.go`` compiles and (if a matching
``.expected`` file exists) runs to produce that exact stdout.

This validates that the Go test inputs themselves are correct — i.e.
that the ``.expected`` files describe what real ``go run`` actually
emits, not just what we *think* it should emit.  Run this whenever
you add a new test case::

    python3 tests/verify_go_cases.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = HERE / "cases"


def run_go(go: Path) -> tuple[bool, str, str]:
    try:
        p = subprocess.run(
            ["go", "run", str(go)],
            capture_output=True, text=True, timeout=30,
        )
        return p.returncode == 0, p.stdout, p.stderr
    except Exception as e:
        return False, "", str(e)


def main() -> int:
    fails: list[str] = []
    for go in sorted(CASES.glob("*.go")):
        name = go.stem
        ok, out, err = run_go(go)
        expected = go.with_suffix(".expected")
        if not ok:
            print(f"FAIL {name}: go failed: {err.splitlines()[0] if err else '?'}")
            fails.append(name)
            continue
        if expected.exists():
            want = expected.read_text()
            if out != want:
                print(f"FAIL {name}: stdout mismatch\n  want: {want!r}\n  got:  {out!r}")
                fails.append(name)
                continue
        print(f"PASS {name}")
    print(f"\n{sum(1 for _ in CASES.glob('*.go')) - len(fails)}/"
          f"{sum(1 for _ in CASES.glob('*.go'))} go cases OK")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
