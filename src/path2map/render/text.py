"""Text renderer for logical tree output."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
import sys

from path2map.model import TreeModel, TreeNode

_ANSI_RESET = "\x1b[0m"
_ANSI_DIRECTORY = "\x1b[1;34m"
_ANSI_CODE = "\x1b[32m"
_ANSI_CONFIG = "\x1b[36m"
_ANSI_DOCS = "\x1b[33m"
_ANSI_MEDIA = "\x1b[35m"
_ANSI_ARCHIVE = "\x1b[31m"
_ANSI_EXEC = "\x1b[92m"

_CODE_EXTS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".kt",
    ".scala",
    ".sh",
    ".ps1",
}
_CONFIG_EXTS = {
    ".ini",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".xml",
    ".cfg",
    ".conf",
    ".env",
}
_DOC_EXTS = {".md", ".rst", ".txt", ".adoc", ".pdf"}
_MEDIA_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".mp3",
    ".wav",
    ".flac",
    ".mp4",
    ".mov",
    ".mkv",
}
_ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"}
_EXEC_EXTS = {".exe", ".msi", ".bat", ".cmd", ".com", ".bin", ".appimage"}


@dataclass(frozen=True)
class TextRenderOptions:
    """Options controlling text rendering output."""

    folders_only: bool = False
    sort: bool = False
    comments: bool = False
    emojis: bool = False
    color: str = "auto"
    details: str = "none"
    time_format: str = "%Y-%m-%d %H:%M"
    size_format: str = "binary"
    details_style: str = "inline"


def render_text(model: TreeModel, *, options: TextRenderOptions | None = None) -> str:
    """Render a logical tree model to deterministic plain-text output."""
    opts = options or TextRenderOptions()
    use_color = _use_color(opts.color)

    lines: list[_RenderLine] = []
    _append_node_lines(
        lines,
        model.root,
        prefix="",
        is_last=True,
        is_root=True,
        options=opts,
        use_color=use_color,
    )

    if opts.details_style == "columns":
        return _render_columns(lines)

    return "\n".join(line.inline_text for line in lines)


def _append_node_lines(
    lines: list[_RenderLine],
    node: TreeNode,
    *,
    prefix: str,
    is_last: bool,
    is_root: bool,
    options: TextRenderOptions,
    use_color: bool,
) -> None:
    branch = "" if is_root else ("└── " if is_last else "├── ")
    label = _format_label(node, is_root=is_root, options=options, use_color=use_color)
    details_columns = _detail_columns(node, options=options)

    inline = f"{prefix}{branch}{label}"
    if options.details_style == "inline":
        detail_items = [item for item in details_columns if item]
        if detail_items:
            inline = f"{inline} ({', '.join(detail_items)})"

    lines.append(
        _RenderLine(
            inline_text=inline,
            column_label=f"{prefix}{branch}{label}",
            size_text=details_columns[0],
            mtime_text=details_columns[1],
        )
    )

    next_prefix = "" if is_root else f"{prefix}{'    ' if is_last else '│   '}"
    children = _visible_children(node, options=options)
    for index, child in enumerate(children):
        _append_node_lines(
            lines,
            child,
            prefix=next_prefix,
            is_last=index == len(children) - 1,
            is_root=False,
            options=options,
            use_color=use_color,
        )


def _render_columns(lines: list[_RenderLine]) -> str:
    label_width = max((_display_width(line.column_label) for line in lines), default=0)
    rendered: list[str] = []
    for line in lines:
        parts = [_pad_display(line.column_label, label_width)]
        if line.size_text:
            parts.append(line.size_text)
        if line.mtime_text:
            parts.append(line.mtime_text)
        rendered.append("  ".join(parts).rstrip())
    return "\n".join(rendered)


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


def _format_label(
    node: TreeNode,
    *,
    is_root: bool,
    options: TextRenderOptions,
    use_color: bool,
) -> str:
    label = node.name

    if options.emojis:
        if node.type == "directory":
            label = f"📁 {label}"
        elif node.type == "file":
            label = f"📄 {label}"

    if (
        options.comments
        and not options.folders_only
        and node.type == "directory"
        and not node.children
        and not is_root
    ):
        label = f"{label} [Empty folder]"

    if not use_color:
        return label

    color = _node_color(node)
    if color:
        return f"{color}{label}{_ANSI_RESET}"
    return label


def _detail_columns(node: TreeNode, *, options: TextRenderOptions) -> tuple[str, str]:
    if options.details == "none":
        return "", ""

    size_text = ""
    mtime_text = ""

    if options.details in {"size", "size,mtime"} and node.size is not None:
        size_text = _format_size(node.size, options.size_format)

    if options.details in {"mtime", "size,mtime"} and node.mtime is not None:
        mtime_text = _format_mtime(node.mtime, options.time_format)

    return size_text, mtime_text


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


def _use_color(mode: str) -> bool:
    if mode == "always":
        return True
    if mode == "never":
        return False
    return sys.stdout.isatty()


def _node_color(node: TreeNode) -> str | None:
    if node.type == "directory":
        return _ANSI_DIRECTORY

    ext = node.ext.casefold()
    if ext in _CODE_EXTS:
        return _ANSI_CODE
    if ext in _CONFIG_EXTS:
        return _ANSI_CONFIG
    if ext in _DOC_EXTS:
        return _ANSI_DOCS
    if ext in _MEDIA_EXTS:
        return _ANSI_MEDIA
    if ext in _ARCHIVE_EXTS:
        return _ANSI_ARCHIVE
    if ext in _EXEC_EXTS:
        return _ANSI_EXEC
    return None


@dataclass(frozen=True)
class _RenderLine:
    inline_text: str
    column_label: str
    size_text: str
    mtime_text: str


def _display_width(value: str) -> int:
    return len(_strip_ansi(value))


def _pad_display(value: str, width: int) -> str:
    padding = width - _display_width(value)
    return value + (" " * max(padding, 0))


def _strip_ansi(value: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", value)
