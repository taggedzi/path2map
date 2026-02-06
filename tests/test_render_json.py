"""Tests for JSON renderer behavior."""

from __future__ import annotations

from datetime import datetime
import json

from path2map.model import TreeModel, TreeNode
from path2map.render.json import JsonRenderOptions, render_json


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
                size=123,
                mtime=datetime(2026, 1, 2, 3, 4),
            ),
        ],
    )
    return TreeModel(root=root, scan_root="/tmp/project")


def test_render_json_default_schema_without_metadata_fields() -> None:
    """Default JSON output omits size/mtime fields."""
    payload = json.loads(render_json(_fixture_model()))

    assert set(payload.keys()) == {"path", "name", "type", "ext", "depth", "children"}
    child_keys = set(payload["children"][1].keys())
    assert "size" not in child_keys
    assert "mtime" not in child_keys


def test_render_json_includes_metadata_fields_when_enabled() -> None:
    """Metadata keys appear when details mode requests them."""
    payload = json.loads(
        render_json(
            _fixture_model(),
            options=JsonRenderOptions(details="size,mtime", time_format="%Y-%m-%d"),
        )
    )

    file_node = payload["children"][1]
    assert file_node["size"] == 123
    assert file_node["mtime"] == "2026-01-02"


def test_render_json_is_deterministic() -> None:
    """Rendering the same model repeatedly produces identical output."""
    model = _fixture_model()

    first = render_json(model, options=JsonRenderOptions(details="size,mtime"))
    second = render_json(model, options=JsonRenderOptions(details="size,mtime"))

    assert first == second
