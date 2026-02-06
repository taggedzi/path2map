"""Tests for output routing and filename generation."""

from __future__ import annotations

from datetime import datetime
import io
from pathlib import Path

from path2map.output import OutputOptions, resolve_output_path, route_output


def test_route_output_defaults_to_stdout_when_no_output_path() -> None:
    """Without --output, rendered text goes to stdout."""
    stream = io.StringIO()

    written = route_output(
        "hello",
        options=OutputOptions(output_type="text", output_path=None, stdout=False),
        stream=stream,
    )

    assert written == []
    assert stream.getvalue() == "hello\n"


def test_route_output_writes_explicit_file_without_stdout(tmp_path: Path) -> None:
    """When --output is a file and --stdout is false, write only file."""
    stream = io.StringIO()
    out_file = tmp_path / "result.json"

    written = route_output(
        '{"a":1}',
        options=OutputOptions(
            output_type="json", output_path=str(out_file), stdout=False
        ),
        stream=stream,
    )

    assert written == [out_file]
    assert out_file.read_text(encoding="utf-8") == '{"a":1}'
    assert stream.getvalue() == ""


def test_route_output_directory_generates_timestamped_filename(tmp_path: Path) -> None:
    """Directory output target gets auto-generated timestamped filename."""
    stamp = datetime(2026, 2, 6, 15, 4, 5)

    written = route_output(
        "x",
        options=OutputOptions(
            output_type="csv", output_path=str(tmp_path), stdout=False
        ),
        now_fn=lambda: stamp,
    )

    expected = tmp_path / "path2map_2026-02-06_150405.csv"
    assert written == [expected]
    assert expected.read_text(encoding="utf-8") == "x"


def test_route_output_can_write_and_stdout(tmp_path: Path) -> None:
    """--stdout with --output routes to both destinations."""
    stream = io.StringIO()
    out_file = tmp_path / "tree.txt"

    written = route_output(
        "tree",
        options=OutputOptions(
            output_type="text", output_path=str(out_file), stdout=True
        ),
        stream=stream,
    )

    assert written == [out_file]
    assert out_file.read_text(encoding="utf-8") == "tree"
    assert stream.getvalue() == "tree\n"


def test_resolve_output_path_uses_explicit_file_path() -> None:
    """Non-directory output path remains unchanged."""
    target = Path("/tmp/path2map_custom.md")
    resolved = resolve_output_path(
        output_path=target,
        output_type="md",
        now=datetime(2026, 2, 6, 12, 0, 0),
    )

    assert resolved == target
