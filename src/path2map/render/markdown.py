"""Markdown renderer for tree output."""

from __future__ import annotations

from path2map.model import TreeModel
from path2map.render.text import TextRenderOptions, render_text


def render_markdown(
    model: TreeModel,
    *,
    options: TextRenderOptions | None = None,
) -> str:
    """Render logical tree as fenced markdown text block."""
    content = render_text(model, options=options)
    return f"```text\n{content}\n```"
