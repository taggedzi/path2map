"""Unit tests for traversal behavior."""

from __future__ import annotations

from pathlib import Path

from path2map.traversal import TraversalOptions, build_tree


def _all_paths(root) -> list[str]:
    paths: list[str] = []

    def _walk(node) -> None:
        paths.append(node.path)
        for child in node.children:
            _walk(child)

    _walk(root)
    return paths


def test_max_depth_zero_returns_only_root(tmp_path: Path) -> None:
    """max_depth=0 keeps only the scan root node."""
    (tmp_path / "child.txt").write_text("x", encoding="utf-8")

    model = build_tree(tmp_path, options=TraversalOptions(max_depth=0))

    assert model.root.path == "."
    assert model.root.depth == 0
    assert model.root.children == []


def test_default_symlink_mode_shows_but_does_not_follow(tmp_path: Path) -> None:
    """Default mode shows symlinked directories as leaf nodes."""
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "inside.txt").write_text("x", encoding="utf-8")
    (tmp_path / "link_to_target").symlink_to(target_dir, target_is_directory=True)

    model = build_tree(tmp_path)

    node_names = [child.name for child in model.root.children]
    assert node_names == ["link_to_target", "target"]

    link_node = model.root.children[0]
    assert link_node.type == "directory"
    assert link_node.is_symlink is True
    assert link_node.children == []


def test_follow_symlinks_cycle_safe(tmp_path: Path) -> None:
    """Following symlinks marks cycle nodes and terminates traversal."""
    real_dir = tmp_path / "dir"
    real_dir.mkdir()
    loop_link = real_dir / "loop"
    loop_link.symlink_to(real_dir, target_is_directory=True)

    model = build_tree(tmp_path, options=TraversalOptions(symlink_mode="follow"))

    dir_node = next(child for child in model.root.children if child.name == "dir")
    loop_node = next(child for child in dir_node.children if child.name == "loop")

    assert loop_node.is_symlink is True
    assert loop_node.symlink_cycle is True
    assert loop_node.children == []


def test_default_order_is_directory_first_then_name(tmp_path: Path) -> None:
    """Traversal ordering is deterministic by default."""
    (tmp_path / "zeta.txt").write_text("x", encoding="utf-8")
    (tmp_path / "alpha.txt").write_text("x", encoding="utf-8")
    (tmp_path / "bbb").mkdir()
    (tmp_path / "aaa").mkdir()

    model = build_tree(tmp_path)

    assert [child.name for child in model.root.children] == [
        "aaa",
        "bbb",
        "alpha.txt",
        "zeta.txt",
    ]


def test_custom_sort_key_hook_is_supported(tmp_path: Path) -> None:
    """Traversal supports a custom sorting hook for entries."""
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "b.txt").write_text("x", encoding="utf-8")

    options = TraversalOptions(sort_key=lambda entry: (0, "", -ord(entry.name[0])))
    model = build_tree(tmp_path, options=options)

    assert [child.name for child in model.root.children] == ["b.txt", "a.txt"]


def test_relative_paths_and_depth_are_tracked(tmp_path: Path) -> None:
    """Nodes use scan-root relative paths and correct depth values."""
    folder = tmp_path / "src"
    folder.mkdir()
    nested = folder / "main.py"
    nested.write_text("print('x')", encoding="utf-8")

    model = build_tree(tmp_path)

    paths = _all_paths(model.root)
    assert "." in paths
    assert "src" in paths
    assert "src/main.py" in paths

    src_node = next(child for child in model.root.children if child.name == "src")
    file_node = next(child for child in src_node.children if child.name == "main.py")
    assert src_node.depth == 1
    assert file_node.depth == 2
