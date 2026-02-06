"""Tests for markdown rendering."""

from __future__ import annotations

from path2map.model import TreeModel, TreeNode
from path2map.render.markdown import render_markdown
from path2map.render.text import TextRenderOptions, render_text


def _fixture_model() -> TreeModel:
    root = TreeNode.directory(
        path=".",
        name="project",
        depth=0,
        children=[
            TreeNode.directory(path="src", name="src", depth=1),
            TreeNode.file(path="a.py", name="a.py", depth=1, ext=".py"),
        ],
    )
    return TreeModel(root=root, scan_root="/tmp/project")


def test_markdown_wraps_tree_in_fenced_block() -> None:
    """Markdown output uses a fenced text code block wrapper."""
    result = render_markdown(_fixture_model())

    assert result.startswith("```text\n")
    assert result.endswith("\n```")


def test_markdown_tree_content_matches_text_renderer() -> None:
    """Markdown interior content remains equivalent to text renderer output."""
    model = _fixture_model()
    text = render_text(model, options=TextRenderOptions(sort=True))
    markdown = render_markdown(model, options=TextRenderOptions(sort=True))

    assert markdown == f"```text\n{text}\n```"
