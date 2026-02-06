"""Tests for include filtering and ancestor retention."""

from __future__ import annotations

from pathlib import Path

from path2map.filtering import FilterConfig, filter_entries_with_ancestors
from path2map.ignore import IgnoreConfig, PathEntry, filter_ignored_entries


def test_filter_pass_through_when_no_filters() -> None:
    """Without `--filter`, entries pass through unchanged."""
    entries = [
        PathEntry(path="src", is_dir=True),
        PathEntry(path="src/main.py", is_dir=False),
    ]

    kept = filter_entries_with_ancestors(entries, config=FilterConfig(filters=[]))

    assert kept == entries


def test_multiple_filters_use_or_semantics() -> None:
    """Any matching filter regex should include a path."""
    entries = [
        PathEntry(path="src/main.py", is_dir=False),
        PathEntry(path="docs/readme.md", is_dir=False),
        PathEntry(path="assets/logo.png", is_dir=False),
    ]

    kept = filter_entries_with_ancestors(
        entries,
        config=FilterConfig(filters=[r"\.py$", r"^docs/"]),
    )

    assert [entry.path for entry in kept] == ["src/main.py", "docs/readme.md"]


def test_ancestors_of_matching_descendants_are_retained() -> None:
    """Matching descendants keep parent directories for context."""
    entries = [
        PathEntry(path="src", is_dir=True),
        PathEntry(path="src/pkg", is_dir=True),
        PathEntry(path="src/pkg/main.py", is_dir=False),
        PathEntry(path="docs", is_dir=True),
        PathEntry(path="docs/readme.md", is_dir=False),
    ]

    kept = filter_entries_with_ancestors(
        entries,
        config=FilterConfig(filters=[r"main\.py$"]),
    )

    assert [entry.path for entry in kept] == [
        "src",
        "src/pkg",
        "src/pkg/main.py",
    ]


def test_filter_runs_after_ignore_stage(tmp_path: Path) -> None:
    """Ignore exclusions are not reintroduced by later filter stage."""
    entries = [
        PathEntry(path="build", is_dir=True),
        PathEntry(path="build/main.py", is_dir=False),
        PathEntry(path="src", is_dir=True),
        PathEntry(path="src/main.py", is_dir=False),
    ]

    after_ignore = filter_ignored_entries(
        entries,
        scan_root=tmp_path,
        config=IgnoreConfig(use_default_ignores=True),
    )

    after_filter = filter_entries_with_ancestors(
        after_ignore,
        config=FilterConfig(filters=[r"\.py$"]),
    )

    assert [entry.path for entry in after_ignore] == ["src", "src/main.py"]
    assert [entry.path for entry in after_filter] == ["src", "src/main.py"]


def test_non_matching_filter_returns_empty_set() -> None:
    """No regex matches should result in no included entries."""
    entries = [
        PathEntry(path="src", is_dir=True),
        PathEntry(path="src/main.py", is_dir=False),
    ]

    kept = filter_entries_with_ancestors(
        entries,
        config=FilterConfig(filters=[r"^docs/"]),
    )

    assert kept == []
