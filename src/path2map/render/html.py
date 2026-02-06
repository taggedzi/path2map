"""HTML renderer for logical tree output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import html

from path2map.model import TreeModel, TreeNode


@dataclass(frozen=True)
class HtmlRenderOptions:
    """Options controlling HTML rendering output."""

    folders_only: bool = False
    sort: bool = False
    comments: bool = False
    emojis: bool = False
    details: str = "none"
    time_format: str = "%Y-%m-%d %H:%M"
    size_format: str = "binary"


def render_html(model: TreeModel, *, options: HtmlRenderOptions | None = None) -> str:
    """Render logical tree as a deterministic HTML document."""
    opts = options or HtmlRenderOptions()
    body = _render_node_list([model.root], options=opts, is_root=True)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>path2map</title>",
            "  <style>",
            "    body { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 1rem; }",
            "    ul.tree { list-style: none; padding-left: 1rem; }",
            "    ul.tree ul { list-style: none; padding-left: 1.25rem; }",
            "    .node { white-space: pre; }",
            "    details > summary { cursor: pointer; }",
            "  </style>",
            "</head>",
            "<body>",
            body,
            "</body>",
            "</html>",
        ]
    )


def _render_node_list(
    nodes: list[TreeNode],
    *,
    options: HtmlRenderOptions,
    is_root: bool,
) -> str:
    lines: list[str] = ['<ul class="tree">' if is_root else "<ul>"]
    for node in nodes:
        children = _visible_children(node, options=options)
        label = html.escape(_format_label(node, is_root=is_root, options=options))

        if children:
            lines.append("  <li>")
            lines.append(f'    <details open><summary class="node">{label}</summary>')
            lines.append(
                _indent(_render_node_list(children, options=options, is_root=False), 6)
            )
            lines.append("    </details>")
            lines.append("  </li>")
        else:
            lines.append(f'  <li><span class="node">{label}</span></li>')

    lines.append("</ul>")
    return "\n".join(lines)


def _indent(text: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" for line in text.splitlines())


def _visible_children(node: TreeNode, *, options: HtmlRenderOptions) -> list[TreeNode]:
    children = node.children
    if options.folders_only:
        children = [child for child in children if child.type == "directory"]

    if options.sort:
        children = sorted(
            children,
            key=lambda child: (
                0 if child.type == "directory" else 1,
                child.name.casefold(),
                child.name,
            ),
        )

    return children


def _format_label(node: TreeNode, *, is_root: bool, options: HtmlRenderOptions) -> str:
    label = node.name if is_root else node.name

    if options.emojis:
        if node.type == "directory":
            label = f"📁 {label}"
        elif node.type == "file":
            label = f"📄 {label}"

    details_text = _format_details(node, options=options)
    if details_text:
        label = f"{label} ({details_text})"

    if (
        options.comments
        and not options.folders_only
        and node.type == "directory"
        and not node.children
        and not is_root
    ):
        label = f"{label} [Empty folder]"

    return label


def _format_details(node: TreeNode, *, options: HtmlRenderOptions) -> str:
    if options.details == "none":
        return ""

    values: list[str] = []
    if options.details in {"size", "size,mtime"} and node.size is not None:
        values.append(_format_size(node.size, options.size_format))

    if options.details in {"mtime", "size,mtime"} and node.mtime is not None:
        values.append(_format_mtime(node.mtime, options.time_format))

    return ", ".join(values)


def _format_mtime(value: datetime, time_format: str) -> str:
    return value.strftime(time_format)


def _format_size(value: int, size_format: str) -> str:
    base = 1024 if size_format == "binary" else 1000
    units = (
        ("B", "KiB", "MiB", "GiB", "TiB")
        if base == 1024
        else ("B", "KB", "MB", "GB", "TB")
    )
    size = float(value)
    for unit in units:
        if size < base or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= base
    return f"{int(value)} B"
