"""Canonical tree data model used by traversal and renderers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Literal

NodeType = Literal["directory", "file"]


@dataclass(slots=True)
class TreeNode:
    """A node in the logical filesystem tree."""

    path: str
    name: str
    type: NodeType
    depth: int
    ext: str = ""
    children: list["TreeNode"] = field(default_factory=list)
    size: int | None = None
    mtime: datetime | None = None
    is_symlink: bool = False
    symlink_target: str | None = None
    symlink_cycle: bool = False

    def __post_init__(self) -> None:
        """Validate invariants for node shape and metadata usage."""
        if self.depth < 0:
            raise ValueError("depth must be >= 0")

        if self.type == "file" and self.children:
            raise ValueError("file nodes cannot contain children")

    @classmethod
    def directory(
        cls,
        *,
        path: str,
        name: str,
        depth: int,
        children: list["TreeNode"] | None = None,
        is_symlink: bool = False,
        symlink_target: str | None = None,
        symlink_cycle: bool = False,
    ) -> "TreeNode":
        """Create a directory node."""
        return cls(
            path=path,
            name=name,
            type="directory",
            depth=depth,
            ext="",
            children=list(children or []),
            is_symlink=is_symlink,
            symlink_target=symlink_target,
            symlink_cycle=symlink_cycle,
        )

    @classmethod
    def file(
        cls,
        *,
        path: str,
        name: str,
        depth: int,
        ext: str = "",
        size: int | None = None,
        mtime: datetime | None = None,
        is_symlink: bool = False,
        symlink_target: str | None = None,
        symlink_cycle: bool = False,
    ) -> "TreeNode":
        """Create a file node."""
        return cls(
            path=path,
            name=name,
            type="file",
            depth=depth,
            ext=ext,
            size=size,
            mtime=mtime,
            is_symlink=is_symlink,
            symlink_target=symlink_target,
            symlink_cycle=symlink_cycle,
        )


@dataclass(slots=True)
class TreeModel:
    """Container for a full logical tree and scan-level metadata."""

    root: TreeNode
    scan_root: str
    max_depth: int | None = None

    def iter_preorder(self) -> Iterator[TreeNode]:
        """Yield nodes in deterministic preorder based on child order."""
        stack: list[TreeNode] = [self.root]
        while stack:
            current = stack.pop()
            yield current
            stack.extend(reversed(current.children))
