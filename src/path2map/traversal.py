"""Filesystem traversal for building the logical tree model."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
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


def build_tree(
    directory: str | Path,
    *,
    options: TraversalOptions | None = None,
) -> TreeModel:
    """Traverse a directory and return a canonical logical tree."""
    opts = options or TraversalOptions()
    scan_root = Path(directory).resolve()

    if opts.max_depth is not None and opts.max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    root = TreeNode.directory(path=".", name=scan_root.name, depth=0)

    visited: set[tuple[int, int] | str] = set()
    visited.add(_directory_identity(scan_root))

    if opts.max_depth == 0:
        return TreeModel(root=root, scan_root=str(scan_root), max_depth=opts.max_depth)

    root.children = _walk_directory(
        scan_root=scan_root,
        current_dir=scan_root,
        depth=1,
        options=opts,
        visited=visited,
    )

    return TreeModel(root=root, scan_root=str(scan_root), max_depth=opts.max_depth)


def _walk_directory(
    *,
    scan_root: Path,
    current_dir: Path,
    depth: int,
    options: TraversalOptions,
    visited: set[tuple[int, int] | str],
) -> list[TreeNode]:
    if options.max_depth is not None and depth > options.max_depth:
        return []

    children: list[TreeNode] = []
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
            node = TreeNode.directory(
                path=rel_path,
                name=entry.name,
                depth=depth,
                is_symlink=is_symlink,
                symlink_target=_symlink_target(path) if is_symlink else None,
            )
            children.append(node)

            if options.max_depth is not None and depth >= options.max_depth:
                continue

            if is_symlink and options.symlink_mode != "follow":
                continue

            traversal_path = path.resolve() if is_symlink else path
            identity = _directory_identity(traversal_path)
            if identity in visited:
                node.symlink_cycle = is_symlink
                continue

            visited.add(identity)
            node.children = _walk_directory(
                scan_root=scan_root,
                current_dir=traversal_path,
                depth=depth + 1,
                options=options,
                visited=visited,
            )
            visited.remove(identity)
            continue

        node = TreeNode.file(
            path=rel_path,
            name=entry.name,
            depth=depth,
            ext=path.suffix,
            is_symlink=is_symlink,
            symlink_target=_symlink_target(path) if is_symlink else None,
        )
        children.append(node)

    return children


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
