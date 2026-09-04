"""Command-line front end: reads color values one per line, from files or stdin."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Iterator

from .convert import hex_to_rgb, oklab_to_rgb, rgb_to_hex, rgb_to_oklab


def read_lines(paths: list[str]) -> Iterator[str]:
    """Yield non-empty, non-comment lines from the given files, or from stdin
    if no paths were given. A path of "-" also means stdin, so it can be
    mixed with real files in the same invocation."""
    if not paths:
        sources: Iterable = [sys.stdin]
    else:
        sources = []
        for path in paths:
            sources.append(sys.stdin if path == "-" else open(path, encoding="utf-8"))

    for source in sources:
        try:
            for raw in source:
                line = raw.strip()
                if line:
                    yield line
        finally:
            if source is not sys.stdin:
                source.close()


def parse_oklab(text: str) -> tuple[float, float, float]:
    text = text.strip()
    if text.lower().startswith("oklab(") and text.endswith(")"):
        text = text[len("oklab("):-1]
    parts = text.replace(",", " ").split()
    if len(parts) != 3:
        raise ValueError(f"expected 3 numbers for OKLab, got: {text!r}")
    L, a, b = (float(p) for p in parts)
    return L, a, b


def format_oklab(L: float, a: float, b: float) -> str:
    return f"oklab({L:.4f} {a:.4f} {b:.4f})"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oklabconv",
        description="Convert colors between sRGB hex and OKLab, one value per line.",
    )
    parser.add_argument(
        "--to",
        choices=("oklab", "srgb"),
        required=True,
        help="target format; input is assumed to be the other one",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="input files, one color per line (default: read from stdin)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    for line in read_lines(args.files):
        try:
            if args.to == "oklab":
                r, g, b = hex_to_rgb(line)
                print(format_oklab(*rgb_to_oklab(r, g, b)))
            else:
                L, a, b = parse_oklab(line)
                print(rgb_to_hex(*oklab_to_rgb(L, a, b)))
        except ValueError as exc:
            print(f"oklabconv: skipping {line!r}: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
