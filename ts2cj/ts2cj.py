#!/usr/bin/env python3
"""ts2cj — TypeScript → Cangjie converter (single-file).

Usage:
    python3 ts2cj.py input.ts -o output.cj
    python3 ts2cj.py input.ts                 # write next to input as input.cj
    cat input.ts | python3 ts2cj.py -         # read from stdin

Implementation: rule-engine / expert-system style. See readme.md for details.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engine import Transformer


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="TypeScript → Cangjie converter")
    p.add_argument("input", help="path to .ts file, or '-' for stdin")
    p.add_argument("-o", "--output", help="output .cj file (default: <input>.cj)")
    p.add_argument("--report", action="store_true",
                   help="also print quality / confidence report to stderr")
    args = p.parse_args(argv)

    if args.input == "-":
        src = sys.stdin.read()
        out_path = Path(args.output) if args.output else None
    else:
        in_path = Path(args.input)
        src = in_path.read_text(encoding="utf-8")
        out_path = Path(args.output) if args.output else in_path.with_suffix(".cj")

    t = Transformer()
    res = t.convert(src)

    if out_path is None:
        sys.stdout.write(res.source)
    else:
        out_path.write_text(res.source, encoding="utf-8")

    if args.report:
        sys.stderr.write(
            f"[ts2cj] fires={res.rule_fires} notes={len(res.notes)} "
            f"quality~{res.quality:.2f}\n"
        )
        for note in res.notes:
            sys.stderr.write(f"  note: {note}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
