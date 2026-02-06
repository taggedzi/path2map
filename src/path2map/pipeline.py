"""Canonical traversal -> ignore -> filter -> tree orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, cast

from path2map.filtering import FilterConfig, filter_entries_with_ancestors
from path2map.ignore import IgnoreConfig, PathEntry, filter_ignored_entries
from path2map.model import TreeModel
from path2map.traversal import TraversalOptions, enumerate_entries, tree_from_entries


@dataclass(frozen=True)
class PipelineOptions:
    """Options for the canonical logical-tree pipeline."""

    directory: str = "."
    max_depth: int | None = None
    follow_symlinks: bool = False
    symlinks: str | None = None
    use_default_ignores: bool = True
    p2mignore_enabled: bool = True
    p2mignore_path: str | None = None
    cli_ignore: str | None = None
    filters: list[str] = field(default_factory=list)


def build_logical_tree(options: PipelineOptions) -> TreeModel:
    """Run the canonical pipeline and return the logical tree."""
    symlink_mode = _resolve_symlink_mode(options.follow_symlinks, options.symlinks)
    scan_root, entries, max_depth = enumerate_entries(
        options.directory,
        options=TraversalOptions(
            max_depth=options.max_depth, symlink_mode=symlink_mode
        ),
    )

    path_entries = [
        PathEntry(path=entry.path, is_dir=entry.is_dir) for entry in entries
    ]

    ignore_config = IgnoreConfig(
        use_default_ignores=options.use_default_ignores,
        p2mignore_enabled=options.p2mignore_enabled,
        p2mignore_path=Path(options.p2mignore_path) if options.p2mignore_path else None,
        cli_ignore=options.cli_ignore,
    )
    after_ignore = filter_ignored_entries(
        path_entries,
        scan_root=scan_root,
        config=ignore_config,
    )

    after_filter = filter_entries_with_ancestors(
        after_ignore,
        config=FilterConfig(filters=options.filters),
    )

    kept_paths = {entry.path for entry in after_filter}
    filtered_entries = [entry for entry in entries if entry.path in kept_paths]

    return tree_from_entries(
        scan_root=scan_root,
        entries=filtered_entries,
        max_depth=max_depth,
    )


def _resolve_symlink_mode(
    follow_symlinks: bool,
    symlinks: str | None,
) -> Literal["skip", "show", "follow"]:
    if symlinks is not None:
        if symlinks not in {"skip", "show", "follow"}:
            raise ValueError("symlinks must be one of: skip, show, follow")
        return cast(Literal["skip", "show", "follow"], symlinks)
    return "follow" if follow_symlinks else "show"
