"""CSV renderer for logical tree output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import csv
import io

from path2map.model import TreeModel, TreeNode


@dataclass(frozen=True)
class CsvRenderOptions:
    """Options controlling CSV metadata emission."""

    details: str = "none"
    time_format: str = "%Y-%m-%d %H:%M"


def render_csv(model: TreeModel, *, options: CsvRenderOptions | None = None) -> str:
    """Render the tree model into deterministic CSV rows."""
    opts = options or CsvRenderOptions()

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["path", "name", "type", "ext", "depth", "size", "mtime"])

    for node in model.iter_preorder():
        writer.writerow(
            [
                node.path,
                node.name,
                node.type,
                node.ext,
                str(node.depth),
                _render_size(node, options=opts),
                _render_mtime(node, options=opts),
            ]
        )

    return output.getvalue().rstrip("\n")


def _render_size(node: TreeNode, *, options: CsvRenderOptions) -> str:
    if options.details not in {"size", "size,mtime"}:
        return ""
    if node.size is None:
        return ""
    return str(node.size)


def _render_mtime(node: TreeNode, *, options: CsvRenderOptions) -> str:
    if options.details not in {"mtime", "size,mtime"}:
        return ""
    if node.mtime is None:
        return ""
    return _format_mtime(node.mtime, options.time_format)


def _format_mtime(value: datetime, time_format: str) -> str:
    return value.strftime(time_format)
