"""Unit tests for the canonical tree model."""

from __future__ import annotations

from datetime import datetime

import pytest

from path2map.model import TreeModel, TreeNode


def test_file_node_supports_optional_metadata() -> None:
    """File nodes keep optional size and mtime metadata."""
    modified = datetime(2026, 1, 2, 3, 4)

    node = TreeNode.file(
        path="src/path2map/cli.py",
        name="cli.py",
        depth=2,
        ext=".py",
        size=123,
        mtime=modified,
    )

    assert node.path == "src/path2map/cli.py"
    assert node.name == "cli.py"
    assert node.type == "file"
    assert node.depth == 2
    assert node.ext == ".py"
    assert node.children == []
    assert node.size == 123
    assert node.mtime == modified
    assert node.is_symlink is False
    assert node.symlink_target is None
    assert node.symlink_cycle is False


def test_directory_node_supports_symlink_markers() -> None:
    """Directory nodes carry symlink marker fields when needed."""
    node = TreeNode.directory(
        path="vendor",
        name="vendor",
        depth=1,
        is_symlink=True,
        symlink_target="/mnt/data/vendor",
        symlink_cycle=True,
    )

    assert node.type == "directory"
    assert node.ext == ""
    assert node.is_symlink is True
    assert node.symlink_target == "/mnt/data/vendor"
    assert node.symlink_cycle is True


def test_file_node_cannot_have_children() -> None:
    """Invariant: file nodes are always leaves in the tree."""
    child = TreeNode.file(path="a.txt", name="a.txt", depth=1)

    with pytest.raises(ValueError, match="file nodes cannot contain children"):
        TreeNode(
            path="root.txt",
            name="root.txt",
            type="file",
            depth=0,
            children=[child],
        )


def test_depth_must_be_non_negative() -> None:
    """Invariant: depth cannot be negative."""
    with pytest.raises(ValueError, match="depth must be >= 0"):
        TreeNode.directory(path="src", name="src", depth=-1)


def test_tree_model_preorder_is_deterministic() -> None:
    """Preorder iteration preserves explicit child ordering."""
    leaf_a = TreeNode.file(path="root/a.py", name="a.py", depth=1, ext=".py")
    leaf_b = TreeNode.file(path="root/b.py", name="b.py", depth=1, ext=".py")
    root = TreeNode.directory(
        path="root", name="root", depth=0, children=[leaf_a, leaf_b]
    )

    model = TreeModel(root=root, scan_root="root")

    assert [node.path for node in model.iter_preorder()] == [
        "root",
        "root/a.py",
        "root/b.py",
    ]
