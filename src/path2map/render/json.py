"""JSON renderer for logical tree output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json

from path2map.model import TreeModel, TreeNode


@dataclass(frozen=True)
class JsonRenderOptions:
    """Options controlling JSON metadata emission."""

    details: str = "none"
    time_format: str = "%Y-%m-%d %H:%M"


def render_json(model: TreeModel, *, options: JsonRenderOptions | None = None) -> str:
    """Render the tree model to deterministic JSON text."""
    opts = options or JsonRenderOptions()
    payload = _node_to_dict(model.root, options=opts)
    return json.dumps(payload, indent=2, sort_keys=False)


def _node_to_dict(node: TreeNode, *, options: JsonRenderOptions) -> dict[str, object]:
    data: dict[str, object] = {
        "path": node.path,
        "name": node.name,
        "type": node.type,
        "ext": node.ext,
        "depth": node.depth,
        "children": [_node_to_dict(child, options=options) for child in node.children],
    }

    include_size = options.details in {"size", "size,mtime"}
    include_mtime = options.details in {"mtime", "size,mtime"}

    if include_size:
        data["size"] = node.size

    if include_mtime:
        data["mtime"] = _format_mtime(node.mtime, options.time_format)

    return data


def _format_mtime(value: datetime | None, time_format: str) -> str | None:
    if value is None:
        return None
    return value.strftime(time_format)
