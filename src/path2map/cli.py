"""Minimal CLI stub for path2map."""

from __future__ import annotations

import argparse
from typing import Sequence

from path2map import __version__


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(prog="path2map", description="path2map CLI")
    parser.add_argument("--directory", default=".")
    parser.add_argument("-o", "--output")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("-D", "--max-depth", type=int)
    parser.add_argument("--follow-symlinks", action="store_true")
    parser.add_argument("--symlinks", choices=("skip", "show", "follow"))
    parser.add_argument("-i", "--ignore")
    parser.add_argument("-F", "--filter", action="append", default=[])
    parser.add_argument("-f", "--folders-only", action="store_true")
    parser.add_argument("-s", "--sort", action="store_true")
    parser.add_argument("-c", "--comments", action="store_true")
    parser.add_argument("--emojis", action="store_true")
    parser.add_argument("--color", choices=("auto", "always", "never"), default="auto")
    parser.add_argument("--theme")
    parser.add_argument(
        "--details",
        choices=("none", "size", "mtime", "size,mtime"),
        default="none",
    )
    parser.add_argument("--time-format", default="%Y-%m-%d %H:%M")
    parser.add_argument(
        "--size-format", choices=("binary", "decimal"), default="binary"
    )
    parser.add_argument(
        "--details-style", choices=("inline", "columns"), default="inline"
    )
    parser.add_argument(
        "-t", "--type", choices=("text", "md", "json", "csv", "html"), default="text"
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
