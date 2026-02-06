"""Text renderer for logical tree output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from path2map.model import TreeModel, TreeNode


@dataclass(frozen=True)
class TextRenderOptions:
    """Options controlling text rendering output."""

    folders_only: bool = False
    sort: bool = False
    comments: bool = False
    emojis: bool = False
    details: str = "none"
    time_format: str = "%Y-%m-%d %H:%M"


def render_text(model: TreeModel, *, options: TextRenderOptions | None = None) -> str:
    """Render a logical tree model to deterministic plain-text output."""
    opts = options or TextRenderOptions()
    lines: list[str] = [_format_label(model.root, is_root=True, options=opts)]
    children = _visible_children(model.root, options=opts)

    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        _append_node_lines(
            lines,
            child,
            prefix="",
            is_last=is_last,
            options=opts,
        )

    return "\n".join(lines)


def _append_node_lines(
    lines: list[str],
    node: TreeNode,
    *,
    prefix: str,
    is_last: bool,
    options: TextRenderOptions,
) -> None:
    branch = "└── " if is_last else "├── "
    lines.append(
        f"{prefix}{branch}{_format_label(node, is_root=False, options=options)}"
    )

    next_prefix = f"{prefix}{'    ' if is_last else '│   '}"
    children = _visible_children(node, options=options)
    for index, child in enumerate(children):
        _append_node_lines(
            lines,
            child,
            prefix=next_prefix,
            is_last=index == len(children) - 1,
            options=options,
        )


def _visible_children(node: TreeNode, *, options: TextRenderOptions) -> list[TreeNode]:
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


def _format_label(node: TreeNode, *, is_root: bool, options: TextRenderOptions) -> str:
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


def _format_details(node: TreeNode, *, options: TextRenderOptions) -> str:
    if options.details == "none":
        return ""

    values: list[str] = []
    if options.details in {"size", "size,mtime"} and node.size is not None:
        values.append(f"{node.size} B")

    if options.details in {"mtime", "size,mtime"} and node.mtime is not None:
        values.append(_format_mtime(node.mtime, options.time_format))

    return ", ".join(values)


def _format_mtime(value: datetime, time_format: str) -> str:
    return value.strftime(time_format)
