"""Tests for ignore-stage precedence and matching behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from path2map.ignore import (
    IgnoreConfig,
    PathEntry,
    filter_ignored_entries,
    matches_any_ignore_pattern,
)


@pytest.mark.parametrize(
    "pattern,path,is_dir,expected",
    [
        ("src/*/", "src/cache", True, True),
        ("**/cache/", "a/cache", True, True),
        ("/cache/", "cache", False, False),
        ("src/*.py", "src/nested/main.py", False, False),
        ("**/secret.txt", "secret.txt", False, True),
        ("src/*/", "src/cache/item.txt", False, True),
        ("src/*/", "src/cache", False, False),
        ("src/*/", "other/src/cache", True, False),
        ("**/cache/", "cache", True, True),
        ("**/cache/", "a/b/cache/item", False, True),
        ("**/cache/", "a/cache", False, False),
        ("/cache/", "cache/item", False, True),
        ("/cache/", "a/cache", True, False),
        ("cache/", "a/cache", True, True),
        ("src/*.py", "src/main.py", False, True),
        ("src/*.py", "other/src/main.py", False, False),
        ("src/*.py", "src/pkg.py/child", False, True),
        ("**/secret.txt", "a/b/secret.txt", False, True),
        ("a/**/b", "a/b", False, True),
        ("a/**/b", "a/x/y/b", False, True),
        ("a/**/b", "other/a/b", False, False),
        ("a/**", "a", True, False),
        ("a/**", "a/x/y", False, True),
        ("src/?.[ch]", "src/a.c", False, True),
        ("src/?.[ch]", "src/ab.c", False, False),
        ("src/?.[ch]", "src/x/a.c", False, False),
        ("src/**x/file", "src/a/bx/file", False, False),
        ("/secret.txt", "nested/secret.txt", False, False),
        ("*.pyc", "nested/a.pyc", False, True),
        ("/", "anything", True, False),
    ],
)
def test_ignore_glob_path_segments(pattern, path, is_dir, expected) -> None:
    """Globs respect segment boundaries, anchoring, and directory types."""
    assert (
        matches_any_ignore_pattern(rel_path=path, is_dir=is_dir, patterns=[pattern])
        is expected
    )


def test_default_ignores_exclude_matching_paths() -> None:
    """Default ignore patterns exclude expected directories and descendants."""
    entries = [
        PathEntry(path="src/main.py", is_dir=False),
        PathEntry(path=".git", is_dir=True),
        PathEntry(path=".git/config", is_dir=False),
        PathEntry(path="build", is_dir=True),
        PathEntry(path="build/output.txt", is_dir=False),
    ]

    kept = filter_ignored_entries(entries, scan_root=Path("."), config=IgnoreConfig())

    assert [entry.path for entry in kept] == ["src/main.py"]


def test_default_ignores_can_be_disabled() -> None:
    """Default ignores are optional and can be turned off."""
    entries = [
        PathEntry(path=".git", is_dir=True),
        PathEntry(path="src/app.py", is_dir=False),
    ]

    kept = filter_ignored_entries(
        entries,
        scan_root=Path("."),
        config=IgnoreConfig(use_default_ignores=False),
    )

    assert [entry.path for entry in kept] == [".git", "src/app.py"]


def test_p2mignore_negation_restores_path(tmp_path: Path) -> None:
    """Later negation in `.p2mignore` can re-include prior p2mignore matches."""
    (tmp_path / ".p2mignore").write_text("*.pyc\n!important.pyc\n", encoding="utf-8")
    entries = [
        PathEntry(path="a.pyc", is_dir=False),
        PathEntry(path="important.pyc", is_dir=False),
        PathEntry(path="keep.py", is_dir=False),
    ]

    kept = filter_ignored_entries(entries, scan_root=tmp_path, config=IgnoreConfig())

    assert [entry.path for entry in kept] == ["important.pyc", "keep.py"]


def test_default_ignores_apply_before_p2mignore(tmp_path: Path) -> None:
    """Defaults are stage-2 exclusions and are not overridden by `.p2mignore`."""
    (tmp_path / ".p2mignore").write_text("!.git/config\n", encoding="utf-8")
    entries = [
        PathEntry(path=".git", is_dir=True),
        PathEntry(path=".git/config", is_dir=False),
        PathEntry(path="src/main.py", is_dir=False),
    ]

    kept = filter_ignored_entries(entries, scan_root=tmp_path, config=IgnoreConfig())

    assert [entry.path for entry in kept] == ["src/main.py"]


def test_cli_ignore_is_hard_exclusion_after_p2mignore(tmp_path: Path) -> None:
    """CLI regex ignore excludes even paths re-included by `.p2mignore`."""
    (tmp_path / ".p2mignore").write_text("*.py\n!src/keep.py\n", encoding="utf-8")
    entries = [
        PathEntry(path="src/keep.py", is_dir=False),
        PathEntry(path="src/other.py", is_dir=False),
    ]

    kept = filter_ignored_entries(
        entries,
        scan_root=tmp_path,
        config=IgnoreConfig(cli_ignore=r"^src/keep\.py$"),
    )

    assert kept == []


def test_cli_ignore_regex_applies_to_full_relative_path(tmp_path: Path) -> None:
    """CLI regex matching is done against full relative path text."""
    entries = [
        PathEntry(path="src/tool.py", is_dir=False),
        PathEntry(path="tool.py", is_dir=False),
        PathEntry(path="src/tool.txt", is_dir=False),
    ]

    kept = filter_ignored_entries(
        entries,
        scan_root=tmp_path,
        config=IgnoreConfig(cli_ignore=r"^src/.*\.py$"),
    )

    assert [entry.path for entry in kept] == ["tool.py", "src/tool.txt"]


def test_cli_ignore_supports_comma_separated_patterns(tmp_path: Path) -> None:
    """Comma-separated CLI regex patterns are treated as multiple exclusions."""
    entries = [
        PathEntry(path="docs/readme.md", is_dir=False),
        PathEntry(path="src/main.py", is_dir=False),
        PathEntry(path="src/main.txt", is_dir=False),
    ]

    kept = filter_ignored_entries(
        entries,
        scan_root=tmp_path,
        config=IgnoreConfig(cli_ignore=r"\.md$,^src/.*\.py$"),
    )

    assert [entry.path for entry in kept] == ["src/main.txt"]
