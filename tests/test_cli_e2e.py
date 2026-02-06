"""End-to-end CLI tests for canonical behavior."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from path2map import cli


def _run_cli_capture(capsys, argv: list[str]) -> tuple[int, str]:
    exit_code = cli.main(argv)
    output = capsys.readouterr().out
    return exit_code, output


def test_cli_precedence_chain_e2e(tmp_path: Path, capsys) -> None:
    """defaults -> .p2mignore -> --ignore -> --filter is preserved end-to-end."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "keep.py").write_text("x", encoding="utf-8")
    (tmp_path / "src" / "drop.py").write_text("x", encoding="utf-8")

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "tool.py").write_text("x", encoding="utf-8")

    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "out.py").write_text("x", encoding="utf-8")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x", encoding="utf-8")

    (tmp_path / ".p2mignore").write_text(
        "src/*.py\n!src/keep.py\n!build/out.py\n",
        encoding="utf-8",
    )

    code, text = _run_cli_capture(
        capsys,
        [
            "--directory",
            str(tmp_path),
            "-i",
            r"^src/keep\.py$",
            "-F",
            r"\.py$",
            "-t",
            "text",
        ],
    )

    assert code == 0
    assert "tool.py" in text
    assert "keep.py" not in text
    assert "drop.py" not in text
    assert "out.py" not in text
    assert "config" not in text


def test_cli_max_depth_zero_e2e(tmp_path: Path, capsys) -> None:
    """max-depth=0 returns only root node in rendered output."""
    (tmp_path / "child.txt").write_text("x", encoding="utf-8")

    code, text = _run_cli_capture(
        capsys,
        ["--directory", str(tmp_path), "-D", "0", "-t", "text"],
    )

    assert code == 0
    lines = text.strip().splitlines()
    assert lines == [tmp_path.name]


def test_cli_follow_symlinks_cycle_safe_e2e(tmp_path: Path, capsys) -> None:
    """Following symlinks avoids infinite recursion in cycle cases."""
    real_dir = tmp_path / "dir"
    real_dir.mkdir()
    (real_dir / "loop").symlink_to(real_dir, target_is_directory=True)

    code, text = _run_cli_capture(
        capsys,
        ["--directory", str(tmp_path), "--follow-symlinks", "-t", "text"],
    )

    assert code == 0
    assert text.count("loop") == 1


def test_cli_outputs_are_deterministic_across_formats(tmp_path: Path, capsys) -> None:
    """Repeated CLI runs over same tree produce identical output per format."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x", encoding="utf-8")
    (tmp_path / "README.md").write_text("x", encoding="utf-8")

    for output_type in ("text", "md", "json", "csv", "html"):
        code_a, out_a = _run_cli_capture(
            capsys,
            ["--directory", str(tmp_path), "-t", output_type],
        )
        code_b, out_b = _run_cli_capture(
            capsys,
            ["--directory", str(tmp_path), "-t", output_type],
        )

        assert code_a == 0
        assert code_b == 0
        assert out_a == out_b


def test_cli_metadata_opt_in_no_stat_when_disabled(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """No metadata stat helper is used when details=none."""
    (tmp_path / "file.txt").write_text("hello", encoding="utf-8")

    def _unexpected(*_args, **_kwargs):
        raise AssertionError("metadata helper should not be called")

    monkeypatch.setattr("path2map.traversal._entry_size", _unexpected)
    monkeypatch.setattr("path2map.traversal._entry_mtime", _unexpected)

    code, _ = _run_cli_capture(capsys, ["--directory", str(tmp_path), "-t", "text"])

    assert code == 0


def test_cli_metadata_opt_in_collects_when_enabled(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Metadata details mode enables size/mtime rendering."""
    (tmp_path / "file.txt").write_text("hello", encoding="utf-8")

    monkeypatch.setattr("path2map.traversal._entry_size", lambda _entry: 5)
    monkeypatch.setattr(
        "path2map.traversal._entry_mtime",
        lambda _entry: datetime(2026, 1, 2, 3, 4),
    )

    code, text = _run_cli_capture(
        capsys,
        [
            "--directory",
            str(tmp_path),
            "-t",
            "text",
            "--details",
            "size,mtime",
            "--time-format",
            "%Y-%m-%d",
        ],
    )

    assert code == 0
    assert "file.txt (5 B, 2026-01-02)" in text
