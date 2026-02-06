"""Tests for text renderer behavior."""

from __future__ import annotations

from datetime import datetime

from path2map.model import TreeModel, TreeNode
from path2map.render.text import TextRenderOptions, render_text


def _fixture_model() -> TreeModel:
    docs = TreeNode.directory(path="docs", name="docs", depth=1, children=[])
    src = TreeNode.directory(
        path="src",
        name="src",
        depth=1,
        children=[
            TreeNode.file(
                path="src/main.py",
                name="main.py",
                depth=2,
                ext=".py",
                size=12,
                mtime=datetime(2026, 1, 2, 3, 4),
            ),
            TreeNode.file(
                path="src/readme.md",
                name="readme.md",
                depth=2,
                ext=".md",
            ),
        ],
    )
    root = TreeNode.directory(
        path=".",
        name="project",
        depth=0,
        children=[
            TreeNode.file(path="z.txt", name="z.txt", depth=1, ext=".txt"),
            docs,
            src,
        ],
    )
    return TreeModel(root=root, scan_root="/tmp/project")


def test_render_text_default_tree_structure() -> None:
    """Renderer emits deterministic tree lines from model order."""
    text = render_text(_fixture_model())

    assert text == "\n".join(
        [
            "project",
            "├── z.txt",
            "├── docs",
            "└── src",
            "    ├── main.py",
            "    └── readme.md",
        ]
    )


def test_render_text_with_sort_folders_first() -> None:
    """Sort option renders folders before files alphabetically."""
    text = render_text(_fixture_model(), options=TextRenderOptions(sort=True))

    assert text == "\n".join(
        [
            "project",
            "├── docs",
            "├── src",
            "│   ├── main.py",
            "│   └── readme.md",
            "└── z.txt",
        ]
    )


def test_render_text_folders_only_hides_files() -> None:
    """folders-only omits file nodes from output."""
    text = render_text(_fixture_model(), options=TextRenderOptions(folders_only=True))

    assert text == "\n".join(
        [
            "project",
            "├── docs",
            "└── src",
        ]
    )


def test_render_text_comments_mark_empty_directories() -> None:
    """comments option marks empty directory nodes."""
    text = render_text(_fixture_model(), options=TextRenderOptions(comments=True))

    assert "docs [Empty folder]" in text


def test_render_text_emojis_and_details() -> None:
    """Renderer supports emojis and metadata details without stat calls."""
    text = render_text(
        _fixture_model(),
        options=TextRenderOptions(
            emojis=True,
            details="size,mtime",
            time_format="%Y-%m-%d",
        ),
    )

    assert "📁 project" in text
    assert "📄 main.py (12 B, 2026-01-02)" in text
    # readme has no metadata populated, so detail suffix is omitted.
    assert "📄 readme.md" in text
    assert "readme.md (" not in text
