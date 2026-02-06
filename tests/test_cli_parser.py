"""Parser tests for CLI argument surface."""

from __future__ import annotations

from path2map.cli import build_parser


def test_parser_defaults() -> None:
    """Parser exposes stable defaults for the CLI surface."""
    parser = build_parser()
    args = parser.parse_args([])

    assert args.directory == "."
    assert args.output is None
    assert args.stdout is False
    assert args.max_depth is None
    assert args.follow_symlinks is False
    assert args.symlinks is None
    assert args.ignore is None
    assert args.filter == []
    assert args.folders_only is False
    assert args.sort is False
    assert args.comments is False
    assert args.emojis is False
    assert args.color == "auto"
    assert args.theme is None
    assert args.details == "none"
    assert args.time_format == "%Y-%m-%d %H:%M"
    assert args.size_format == "binary"
    assert args.details_style == "inline"
    assert args.type == "text"


def test_parser_accepts_full_flag_set() -> None:
    """Parser accepts all currently defined public flags."""
    parser = build_parser()
    args = parser.parse_args(
        [
            "--directory",
            "project",
            "-o",
            "out.txt",
            "--stdout",
            "-D",
            "2",
            "--follow-symlinks",
            "--symlinks",
            "follow",
            "-i",
            "^build/",
            "-F",
            "\\.py$",
            "-F",
            "^src/",
            "-f",
            "-s",
            "-c",
            "--emojis",
            "--color",
            "always",
            "--theme",
            "default",
            "--details",
            "size,mtime",
            "--time-format",
            "%Y",
            "--size-format",
            "decimal",
            "--details-style",
            "columns",
            "-t",
            "json",
        ]
    )

    assert args.directory == "project"
    assert args.output == "out.txt"
    assert args.stdout is True
    assert args.max_depth == 2
    assert args.follow_symlinks is True
    assert args.symlinks == "follow"
    assert args.ignore == "^build/"
    assert args.filter == ["\\.py$", "^src/"]
    assert args.folders_only is True
    assert args.sort is True
    assert args.comments is True
    assert args.emojis is True
    assert args.color == "always"
    assert args.theme == "default"
    assert args.details == "size,mtime"
    assert args.time_format == "%Y"
    assert args.size_format == "decimal"
    assert args.details_style == "columns"
    assert args.type == "json"
