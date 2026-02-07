"""Minimal CLI stub for path2map."""

from __future__ import annotations

import argparse
from typing import Sequence

from path2map import __version__
from path2map.output import OutputOptions, route_output
from path2map.pipeline import PipelineOptions, build_logical_tree
from path2map.render.csv import CsvRenderOptions, render_csv
from path2map.render.html import HtmlRenderOptions, render_html
from path2map.render.json import JsonRenderOptions, render_json
from path2map.render.markdown import render_markdown
from path2map.render.text import TextRenderOptions, render_text

_HELP_EPILOG = """Examples:
  path2map --directory .
  path2map --directory . --max-depth 2 --sort
  path2map --directory . --filter "\\.py$" --ignore "^build/"
  path2map --directory . --type json --output tree.json
  path2map --directory . --type md --output tree.md --stdout
"""


class _HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    """Formatter that preserves epilog layout and shows argument defaults."""


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="path2map",
        description=(
            "Inspect a directory tree and render deterministic maps in text and "
            "structured formats."
        ),
        epilog=_HELP_EPILOG,
        formatter_class=_HelpFormatter,
    )
    parser.add_argument(
        "--directory",
        default=".",
        help="Root directory to scan.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output file path or output directory. If a directory is provided, "
            "a timestamped filename is generated."
        ),
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print rendered output to stdout when writing to --output.",
    )
    parser.add_argument(
        "-D",
        "--max-depth",
        type=int,
        help="Maximum traversal depth from --directory (0 means only the root).",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links during traversal (legacy convenience flag).",
    )
    parser.add_argument(
        "--symlinks",
        choices=("skip", "show", "follow"),
        help="Symlink behavior: skip links, show links, or follow links.",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        help="Regex exclusion applied after defaults and .p2mignore rules.",
    )
    parser.add_argument(
        "-F",
        "--filter",
        action="append",
        default=[],
        help="Regex include filter (repeatable; OR logic). Ancestors are retained.",
    )
    parser.add_argument(
        "-f",
        "--folders-only",
        action="store_true",
        help="Render directories only.",
    )
    parser.add_argument(
        "-s",
        "--sort",
        action="store_true",
        help="Sort each directory (directories first, then files, case-insensitive).",
    )
    parser.add_argument(
        "-c",
        "--comments",
        action="store_true",
        help='Add contextual labels such as "[Empty folder]" for empty directories.',
    )
    parser.add_argument(
        "--emojis",
        action="store_true",
        help="Prefix labels with emojis where supported by the output type.",
    )
    parser.add_argument(
        "--color",
        choices=("auto", "always", "never"),
        default="auto",
        help=(
            "Color policy for text/markdown output. "
            "auto=TTY-aware, always=force ANSI, never=disable."
        ),
    )
    parser.add_argument(
        "--theme",
        help="Reserved for future renderer themes (currently no effect).",
    )
    parser.add_argument(
        "--details",
        choices=("none", "size", "mtime", "size,mtime"),
        default="none",
        help="Metadata details to include in output.",
    )
    parser.add_argument(
        "--time-format",
        default="%Y-%m-%d %H:%M",
        help="strftime format used when mtime details are rendered.",
    )
    parser.add_argument(
        "--size-format",
        choices=("binary", "decimal"),
        default="binary",
        help="Size units for rendered size details.",
    )
    parser.add_argument(
        "--details-style",
        choices=("inline", "columns"),
        default="inline",
        help="Render metadata details inline or in aligned columns.",
    )
    parser.add_argument(
        "-t",
        "--type",
        choices=("text", "md", "json", "csv", "html"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    model = build_logical_tree(
        PipelineOptions(
            directory=args.directory,
            max_depth=args.max_depth,
            follow_symlinks=args.follow_symlinks,
            symlinks=args.symlinks,
            cli_ignore=args.ignore,
            filters=args.filter,
            details=args.details,
        )
    )

    text_options = TextRenderOptions(
        folders_only=args.folders_only,
        sort=args.sort,
        comments=args.comments,
        emojis=args.emojis,
        color=args.color,
        details=args.details,
        time_format=args.time_format,
        size_format=args.size_format,
        details_style=args.details_style,
    )

    rendered = ""
    if args.type == "text":
        rendered = render_text(model, options=text_options)
    elif args.type == "md":
        rendered = render_markdown(
            model,
            options=text_options,
        )
    elif args.type == "json":
        rendered = render_json(
            model,
            options=JsonRenderOptions(
                details=args.details, time_format=args.time_format
            ),
        )
    elif args.type == "csv":
        rendered = render_csv(
            model,
            options=CsvRenderOptions(
                details=args.details, time_format=args.time_format
            ),
        )
    elif args.type == "html":
        rendered = render_html(
            model,
            options=HtmlRenderOptions(
                folders_only=args.folders_only,
                sort=args.sort,
                comments=args.comments,
                emojis=args.emojis,
                details=args.details,
                time_format=args.time_format,
                size_format=args.size_format,
            ),
        )

    route_output(
        rendered,
        options=OutputOptions(
            output_type=args.type,
            output_path=args.output,
            stdout=args.stdout,
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
