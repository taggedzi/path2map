"""Regex include filtering with ancestor retention."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Pattern

from path2map.ignore import PathEntry, normalize_relative_path


@dataclass(frozen=True)
class FilterConfig:
    """Configuration for include-only filter behavior."""

    filters: list[str] = field(default_factory=list)


def compile_filter_patterns(filter_values: list[str]) -> list[Pattern[str]]:
    """Compile all non-empty include filter regex values."""
    return [re.compile(value) for value in filter_values if value.strip()]


def filter_entries_with_ancestors(
    entries: list[PathEntry],
    *,
    config: FilterConfig | None = None,
) -> list[PathEntry]:
    """Apply include-only regex filtering and retain ancestors of matches.

    This function is intended to run after ignore stages have already excluded
    entries from consideration.
    """
    cfg = config or FilterConfig()
    patterns = compile_filter_patterns(cfg.filters)
    if not patterns:
        return list(entries)

    normalized = [
        _NormalizedEntry(entry=entry, path=normalize_relative_path(entry.path))
        for entry in entries
    ]
    matched_paths = {
        item.path
        for item in normalized
        if any(pattern.search(item.path) for pattern in patterns)
    }
    if not matched_paths:
        return []

    kept: list[PathEntry] = []
    for item in normalized:
        if item.path in matched_paths:
            kept.append(item.entry)
            continue

        if item.entry.is_dir and any(
            _is_ancestor(item.path, matched) for matched in matched_paths
        ):
            kept.append(item.entry)

    return kept


@dataclass(frozen=True)
class _NormalizedEntry:
    entry: PathEntry
    path: str


def _is_ancestor(path: str, descendant: str) -> bool:
    if path == ".":
        return descendant != "."
    return descendant.startswith(f"{path}/")
