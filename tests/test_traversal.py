"""Unit tests for traversal behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from path2map.traversal import TraversalOptions, build_tree


def _all_paths(root) -> list[str]:
    paths: list[str] = []

    def _walk(node) -> None:
        paths.append(node.path)
        for child in node.children:
            _walk(child)

    _walk(root)
    return paths


def test_max_depth_zero_returns_only_root(tmp_path: Path, monkeypatch) -> None:
    """max_depth=0 keeps only the scan root node."""
    (tmp_path / "child.txt").write_text("x", encoding="utf-8")

    def unexpected(*args, **kwargs):
        raise AssertionError("Depth zero must not enumerate or collect metadata")

    monkeypatch.setattr("path2map.traversal.os.scandir", unexpected)
    monkeypatch.setattr("path2map.traversal._entry_size", unexpected)
    monkeypatch.setattr("path2map.traversal._entry_mtime", unexpected)

    model = build_tree(tmp_path, options=TraversalOptions(max_depth=0))

    assert model.root.path == "."
    assert model.root.depth == 0
    assert model.root.children == []


@pytest.mark.parametrize("max_depth", [0, 1, None])
@pytest.mark.parametrize("kind", ["missing", "file"])
def test_invalid_scan_root(tmp_path: Path, max_depth, kind) -> None:
    """Invalid roots retain useful filesystem exceptions at every depth."""
    root = tmp_path / kind
    if kind == "file":
        root.touch()
    error = FileNotFoundError if kind == "missing" else NotADirectoryError
    with pytest.raises(error):
        build_tree(root, options=TraversalOptions(max_depth=max_depth))


@pytest.mark.parametrize("max_depth", [0, 1, None])
@pytest.mark.parametrize("mode", ["show", "skip", "follow"])
def test_directory_symlink_scan_root(
    tmp_path: Path, followed_directory_link, max_depth, mode
) -> None:
    """A root link resolves to its directory regardless of descendant link mode."""
    target = tmp_path / "target"
    target.mkdir()
    (target / "child.txt").touch()
    link = tmp_path / "link"
    followed_directory_link(link, target)
    model = build_tree(
        link, options=TraversalOptions(max_depth=max_depth, symlink_mode=mode)
    )
    assert model.scan_root == str(target.resolve())
    assert _all_paths(model.root) == (["."] if max_depth == 0 else [".", "child.txt"])


def test_default_symlink_mode_shows_but_does_not_follow(
    tmp_path: Path, directory_symlink
) -> None:
    """Default mode shows symlinked directories as leaf nodes."""
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    (target_dir / "inside.txt").write_text("x", encoding="utf-8")
    directory_symlink(tmp_path / "link_to_target", target_dir)

    model = build_tree(tmp_path)

    node_names = [child.name for child in model.root.children]
    assert node_names == ["link_to_target", "target"]

    link_node = model.root.children[0]
    assert link_node.type == "directory"
    assert link_node.is_symlink is True
    assert link_node.children == []


def test_follow_symlinks_cycle_safe(tmp_path: Path, directory_symlink) -> None:
    """Following symlinks marks cycle nodes and terminates traversal."""
    real_dir = tmp_path / "dir"
    real_dir.mkdir()
    loop_link = real_dir / "loop"
    directory_symlink(loop_link, real_dir)

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


@pytest.mark.parametrize("external", [False, True])
def test_follow_preserves_each_alias_tree(
    tmp_path: Path, followed_directory_link, external: bool
) -> None:
    """Internal/external targets retain separate alias children and cycle markers."""
    root = tmp_path / "root"
    root.mkdir()
    target = (tmp_path if external else root) / "real"
    (target / "nested").mkdir(parents=True)
    (target / "nested" / "inside.txt").write_text("x", encoding="utf-8")
    followed_directory_link(target / "loop", target)
    for alias in ("alias", "second"):
        followed_directory_link(root / alias, target)

    model = build_tree(root, options=TraversalOptions(symlink_mode="follow"))
    prefixes = ["alias"] + ([] if external else ["real"]) + ["second"]
    expected = ["."]
    for prefix in prefixes:
        expected.extend(
            [
                prefix,
                f"{prefix}/loop",
                f"{prefix}/nested",
                f"{prefix}/nested/inside.txt",
            ]
        )
    assert _all_paths(model.root) == expected
    for node in model.root.children:
        loop, nested = node.children
        assert loop.symlink_cycle is True
        assert loop.children == []
        assert nested.depth == 2
        assert nested.children[0].depth == 3


@pytest.mark.parametrize("mode", ["follow", "show", "skip"])
@pytest.mark.parametrize("max_depth", [0, 1, 2, 3, None])
def test_alias_depth_and_modes(
    tmp_path: Path, followed_directory_link, mode, max_depth
) -> None:
    """Depth limits count logical components; show/skip never enter targets."""
    root = tmp_path / "root"
    root.mkdir()
    target = tmp_path / "external"
    (target / "nested").mkdir(parents=True)
    (target / "nested" / "file.txt").write_text("x", encoding="utf-8")
    followed_directory_link(root / "alias", target)
    model = build_tree(
        root, options=TraversalOptions(symlink_mode=mode, max_depth=max_depth)
    )
    expected = ["."]
    if mode != "skip" and max_depth != 0:
        expected.append("alias")
        if mode == "follow" and (max_depth is None or max_depth >= 2):
            expected.append("alias/nested")
            if max_depth is None or max_depth >= 3:
                expected.append("alias/nested/file.txt")
    assert _all_paths(model.root) == expected
