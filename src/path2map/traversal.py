"""Filesystem traversal for building the logical tree model."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, Iterable, Literal

from path2map.model import TreeModel, TreeNode

SymlinkMode = Literal["skip", "show", "follow"]
SortKey = Callable[[os.DirEntry[str]], tuple[int, str, str]]


@dataclass(frozen=True)
class TraversalOptions:
    """Options controlling traversal behavior."""

    max_depth: int | None = None
    symlink_mode: SymlinkMode = "show"
    sort_key: SortKey | None = None


@dataclass(frozen=True)
class TraversedEntry:
    """A single enumerated filesystem entry."""

    path: str
    name: str
    is_dir: bool
    depth: int
    ext: str = ""
    is_symlink: bool = False
    symlink_target: str | None = None
    symlink_cycle: bool = False


def build_tree(
    directory: str | Path,
    *,
    options: TraversalOptions | None = None,
) -> TreeModel:
    """Traverse a directory and return a canonical logical tree."""
    scan_root, entries, max_depth = enumerate_entries(directory, options=options)
    return tree_from_entries(scan_root=scan_root, entries=entries, max_depth=max_depth)


def enumerate_entries(
    directory: str | Path,
    *,
    options: TraversalOptions | None = None,
) -> tuple[Path, list[TraversedEntry], int | None]:
    """Enumerate filesystem entries without applying ignore/filter stages."""
    opts = options or TraversalOptions()
    scan_root = Path(directory).resolve()

    if opts.max_depth is not None and opts.max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    if opts.max_depth == 0:
        return scan_root, [], opts.max_depth

    visited: set[tuple[int, int] | str] = {_directory_identity(scan_root)}
    entries: list[TraversedEntry] = []
    _walk_directory(
        scan_root=scan_root,
        current_dir=scan_root,
        depth=1,
        options=opts,
        visited=visited,
        out=entries,
    )
    return scan_root, entries, opts.max_depth


def tree_from_entries(
    *,
    scan_root: Path,
    entries: list[TraversedEntry],
    max_depth: int | None,
) -> TreeModel:
    """Construct a logical tree model from enumerated entries."""
    root = TreeNode.directory(path=".", name=scan_root.name, depth=0)
    nodes_by_path: dict[str, TreeNode] = {".": root}

    for entry in entries:
        node: TreeNode
        if entry.is_dir:
            node = TreeNode.directory(
                path=entry.path,
                name=entry.name,
                depth=entry.depth,
                is_symlink=entry.is_symlink,
                symlink_target=entry.symlink_target,
                symlink_cycle=entry.symlink_cycle,
            )
        else:
            node = TreeNode.file(
                path=entry.path,
                name=entry.name,
                depth=entry.depth,
                ext=entry.ext,
                is_symlink=entry.is_symlink,
                symlink_target=entry.symlink_target,
                symlink_cycle=entry.symlink_cycle,
            )

        parent_path = entry.path.rpartition("/")[0] or "."
        parent = nodes_by_path.get(parent_path)
        if parent is None:
            continue

        parent.children.append(node)
        nodes_by_path[entry.path] = node

    return TreeModel(root=root, scan_root=str(scan_root), max_depth=max_depth)


def _walk_directory(
    *,
    scan_root: Path,
    current_dir: Path,
    depth: int,
    options: TraversalOptions,
    visited: set[tuple[int, int] | str],
    out: list[TraversedEntry],
) -> None:
    if options.max_depth is not None and depth > options.max_depth:
        return

    for entry in _iter_entries(current_dir, options.sort_key):
        is_symlink = entry.is_symlink()
        path = Path(entry.path)
        rel_path = path.relative_to(scan_root).as_posix()

        if is_symlink and options.symlink_mode == "skip":
            continue

        is_dir = entry.is_dir(follow_symlinks=False) or (
            is_symlink and entry.is_dir(follow_symlinks=True)
        )

        if is_dir:
            symlink_target = _symlink_target(path) if is_symlink else None
            symlink_cycle = False

            should_traverse = not (is_symlink and options.symlink_mode != "follow")
            if options.max_depth is not None and depth >= options.max_depth:
                should_traverse = False

            if should_traverse:
                traversal_path = path.resolve() if is_symlink else path
                identity = _directory_identity(traversal_path)
                if identity in visited:
                    symlink_cycle = is_symlink
                    should_traverse = False
                else:
                    visited.add(identity)

            out.append(
                TraversedEntry(
                    path=rel_path,
                    name=entry.name,
                    is_dir=True,
                    depth=depth,
                    is_symlink=is_symlink,
                    symlink_target=symlink_target,
                    symlink_cycle=symlink_cycle,
                )
            )

            if should_traverse:
                _walk_directory(
                    scan_root=scan_root,
                    current_dir=traversal_path,
                    depth=depth + 1,
                    options=options,
                    visited=visited,
                    out=out,
                )
                visited.remove(identity)
            continue

        out.append(
            TraversedEntry(
                path=rel_path,
                name=entry.name,
                is_dir=False,
                depth=depth,
                ext=path.suffix,
                is_symlink=is_symlink,
                symlink_target=_symlink_target(path) if is_symlink else None,
            )
        )


def _iter_entries(
    directory: Path, sort_key: SortKey | None
) -> Iterable[os.DirEntry[str]]:
    with os.scandir(directory) as scanner:
        entries = list(scanner)

    if sort_key is None:
        entries.sort(key=_default_sort_key)
    else:
        entries.sort(key=sort_key)

    return entries


def _default_sort_key(entry: os.DirEntry[str]) -> tuple[int, str, str]:
    # Directory-first deterministic ordering, then case-insensitive name.
    is_dir = entry.is_dir(follow_symlinks=False) or (
        entry.is_symlink() and entry.is_dir(follow_symlinks=True)
    )
    return (0 if is_dir else 1, entry.name.casefold(), entry.name)


def _directory_identity(path: Path) -> tuple[int, int] | str:
    stat_result = path.stat()
    if stat_result.st_ino and stat_result.st_dev:
        return (stat_result.st_dev, stat_result.st_ino)
    return str(path)


def _symlink_target(path: Path) -> str | None:
    try:
        return os.readlink(path)
    except OSError:
        return None
