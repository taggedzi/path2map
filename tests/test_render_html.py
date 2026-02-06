"""Tests for HTML renderer behavior."""

from __future__ import annotations

from datetime import datetime

from path2map.model import TreeModel, TreeNode
from path2map.render.html import HtmlRenderOptions, render_html


def _fixture_model() -> TreeModel:
    root = TreeNode.directory(
        path=".",
        name="project",
        depth=0,
        children=[
            TreeNode.directory(path="src", name="src", depth=1),
            TreeNode.file(
                path="src/main.py",
                name="main.py",
                depth=2,
                ext=".py",
                size=10,
                mtime=datetime(2026, 1, 2, 3, 4),
            ),
        ],
    )
    return TreeModel(root=root, scan_root="/tmp/project")


def test_render_html_document_structure() -> None:
    """HTML output includes basic document structure and tree container."""
    rendered = render_html(_fixture_model())

    assert rendered.startswith("<!doctype html>")
    assert '<html lang="en">' in rendered
    assert "<body>" in rendered
    assert '<ul class="tree">' in rendered
    assert "project" in rendered


def test_render_html_deterministic_output() -> None:
    """Rendering the same model repeatedly yields identical HTML."""
    model = _fixture_model()

    first = render_html(model, options=HtmlRenderOptions(sort=True, comments=True))
    second = render_html(model, options=HtmlRenderOptions(sort=True, comments=True))

    assert first == second


def test_render_html_supports_details_and_escaping() -> None:
    """Metadata text and HTML escaping are correctly represented."""
    model = _fixture_model()
    model.root.children[0].name = "<src>"

    rendered = render_html(
        model,
        options=HtmlRenderOptions(details="size,mtime", time_format="%Y-%m-%d"),
    )

    assert "&lt;src&gt;" in rendered
    assert "main.py (10 B, 2026-01-02)" in rendered
