"""Tests for CSV renderer behavior."""

from __future__ import annotations

from datetime import datetime

from path2map.model import TreeModel, TreeNode
from path2map.render.csv import CsvRenderOptions, render_csv


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
                size=42,
                mtime=datetime(2026, 1, 2, 3, 4),
            ),
        ],
    )
    return TreeModel(root=root, scan_root="/tmp/project")


def test_render_csv_schema_and_default_metadata_blanks() -> None:
    """CSV output uses stable columns and blank metadata by default."""
    rendered = render_csv(_fixture_model())

    assert rendered.splitlines() == [
        "path,name,type,ext,depth,size,mtime",
        ".,project,directory,,0,,",
        "src,src,directory,,1,,",
        "src/main.py,main.py,file,.py,2,,",
    ]


def test_render_csv_includes_requested_metadata() -> None:
    """CSV includes size/mtime values when details requests them."""
    rendered = render_csv(
        _fixture_model(),
        options=CsvRenderOptions(details="size,mtime", time_format="%Y-%m-%d"),
    )

    assert rendered.splitlines()[-1] == "src/main.py,main.py,file,.py,2,42,2026-01-02"


def test_render_csv_is_deterministic() -> None:
    """Rendering twice yields byte-for-byte identical CSV."""
    model = _fixture_model()

    first = render_csv(model, options=CsvRenderOptions(details="size"))
    second = render_csv(model, options=CsvRenderOptions(details="size"))

    assert first == second
