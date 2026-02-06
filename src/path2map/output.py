"""Output routing helpers for stdout and file exports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
from typing import Callable, Literal, TextIO

OutputType = Literal["text", "md", "json", "csv", "html"]

_EXTENSION_BY_TYPE: dict[OutputType, str] = {
    "text": "txt",
    "md": "md",
    "json": "json",
    "csv": "csv",
    "html": "html",
}


@dataclass(frozen=True)
class OutputOptions:
    """Configuration for output routing behavior."""

    output_type: OutputType
    output_path: str | None = None
    stdout: bool = False


def route_output(
    content: str,
    *,
    options: OutputOptions,
    stream: TextIO | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> list[Path]:
    """Route rendered content to stdout and/or file outputs."""
    target_stream = stream or sys.stdout
    now_provider = now_fn or datetime.now

    written_files: list[Path] = []

    if options.stdout or options.output_path is None:
        print(content, file=target_stream)

    if options.output_path is None:
        return written_files

    resolved = resolve_output_path(
        output_path=Path(options.output_path),
        output_type=options.output_type,
        now=now_provider(),
    )
    resolved.write_text(content, encoding="utf-8")
    written_files.append(resolved)

    return written_files


def resolve_output_path(
    *,
    output_path: Path,
    output_type: OutputType,
    now: datetime,
) -> Path:
    """Resolve final output file path, including directory auto-naming."""
    if output_path.exists() and output_path.is_dir():
        return output_path / timestamped_filename(output_type=output_type, now=now)
    return output_path


def timestamped_filename(*, output_type: OutputType, now: datetime) -> str:
    """Create auto-generated timestamp filename for directory output target."""
    stamp = now.strftime("%Y-%m-%d_%H%M%S")
    ext = _EXTENSION_BY_TYPE[output_type]
    return f"path2map_{stamp}.{ext}"
