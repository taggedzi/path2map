"""Tests for details formatting, color policy, and metadata opt-in."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

from path2map.cli import main
from path2map.model import TreeModel, TreeNode
from path2map.render.text import TextRenderOptions, render_text
from path2map.traversal import TraversalOptions, enumerate_entries


def _fixture_model(size: int = 1536) -> TreeModel:
    root = TreeNode.directory(
        path=".",
        name="project",
        depth=0,
        children=[
            TreeNode.file(
                path="main.py",
                name="main.py",
                depth=1,
                ext=".py",
                size=size,
                mtime=datetime(2026, 1, 2, 3, 4),
            )
        ],
    )
    return TreeModel(root=root, scan_root="/tmp/project")


def test_text_details_size_format_binary_and_decimal() -> None:
    """size-format changes unit base for human-readable output."""
    model = _fixture_model(size=1536)

    binary_text = render_text(
        model,
        options=TextRenderOptions(details="size", size_format="binary"),
    )
    decimal_text = render_text(
        model,
        options=TextRenderOptions(details="size", size_format="decimal"),
    )

    assert "1.5 KiB" in binary_text
    assert "1.5 KB" in decimal_text


def test_text_details_style_columns_outputs_column_layout() -> None:
    """details-style=columns appends columns instead of inline tuple."""
    model = _fixture_model(size=12)

    text = render_text(
        model,
        options=TextRenderOptions(
            details="size,mtime",
            details_style="columns",
            time_format="%Y-%m-%d",
        ),
    )

    lines = text.splitlines()
    assert "(" not in lines[1]
    assert "12 B" in lines[1]
    assert "2026-01-02" in lines[1]


def test_text_color_always_adds_ansi() -> None:
    """color=always applies ANSI styles regardless of TTY state."""
    text = render_text(_fixture_model(), options=TextRenderOptions(color="always"))

    assert "\x1b[" in text


def test_text_color_never_disables_ansi() -> None:
    """color=never prevents ANSI styles from appearing."""
    text = render_text(_fixture_model(), options=TextRenderOptions(color="never"))

    assert "\x1b[" not in text


@pytest.mark.parametrize("output_type", ["text", "md"])
@pytest.mark.parametrize("is_tty", [False, True])
@pytest.mark.parametrize("color", ["auto", "always", "never"])
@pytest.mark.parametrize("destination", ["stdout", "file", "both", "directory"])
def test_cli_color_per_destination(
    tmp_path: Path,
    monkeypatch,
    capsys,
    output_type: str,
    is_tty: bool,
    color: str,
    destination: str,
) -> None:
    """File color is explicit while automatic stdout color follows its TTY."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "main.py").touch()
    monkeypatch.setattr(sys.stdout, "isatty", lambda: is_tty)
    argv = ["--directory", str(root), "--type", output_type]
    # Omitting --color exercises the default auto policy.
    if color != "auto":
        argv += ["--color", color]
    output = tmp_path / f"tree.{output_type}"
    if destination == "directory":
        output = tmp_path / "exports"
        output.mkdir()
    if destination != "stdout":
        argv += ["--output", str(output)]
    if destination == "both":
        argv += ["--stdout"]

    assert main(argv) == 0
    stdout = capsys.readouterr().out
    if destination in ("stdout", "both"):
        assert ("\x1b[" in stdout) == (
            color == "always" or (color == "auto" and is_tty)
        )
        assert "main.py" in stdout
    else:
        assert stdout == ""
    if destination != "stdout":
        if destination == "directory":
            files = list(output.iterdir())
            assert len(files) == 1
            output = files[0]
        exported = output.read_text(encoding="utf-8")
        assert ("\x1b[" in exported) == (color == "always")
        assert "main.py" in exported
        if output_type == "md":
            assert exported.startswith("```text\n")
            assert exported.endswith("\n```")


def test_traversal_metadata_not_collected_when_disabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """No metadata helpers are invoked unless collection is enabled."""
    (tmp_path / "file.txt").write_text("hello", encoding="utf-8")

    def _unexpected(*_args, **_kwargs):
        raise AssertionError("metadata helper should not be called")

    monkeypatch.setattr("path2map.traversal._entry_size", _unexpected)
    monkeypatch.setattr("path2map.traversal._entry_mtime", _unexpected)

    _, entries, _ = enumerate_entries(
        tmp_path,
        options=TraversalOptions(collect_metadata=False),
    )

    file_entry = next(entry for entry in entries if entry.path == "file.txt")
    assert file_entry.size is None
    assert file_entry.mtime is None


def test_traversal_metadata_collected_when_enabled(tmp_path: Path) -> None:
    """Metadata fields are filled only when collection is enabled."""
    content = "hello"
    (tmp_path / "file.txt").write_text(content, encoding="utf-8")

    _, entries, _ = enumerate_entries(
        tmp_path,
        options=TraversalOptions(collect_metadata=True),
    )

    file_entry = next(entry for entry in entries if entry.path == "file.txt")
    assert file_entry.size == len(content)
    assert file_entry.mtime is not None
