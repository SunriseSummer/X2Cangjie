"""Command-line entry point: ``python -m ts2cj input.ts -o output.cj``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import convert_source


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ts2cj",
        description="Convert a TypeScript source file to Cangjie source.",
    )
    parser.add_argument("input", help="TypeScript source file (.ts)")
    parser.add_argument("-o", "--output", help="Output Cangjie file (.cj). Default: stdout.")
    parser.add_argument("--no-main", action="store_true",
                        help="Do not wrap free statements in a main() function.")
    parser.add_argument("--report", action="store_true",
                        help="Print a conversion summary to stderr.")
    args = parser.parse_args(argv)

    src = Path(args.input).read_text(encoding="utf-8")
    result = convert_source(src, wrap_main=not args.no_main)

    if args.output:
        Path(args.output).write_text(result.source, encoding="utf-8")
    else:
        sys.stdout.write(result.source)

    if args.report:
        sys.stderr.write(
            f"[ts2cj] chunks={result.chunks} "
            f"confident={result.confident_chunks} "
            f"fallback={result.fallback_chunks} "
            f"confidence={result.confidence:.2%}\n"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
