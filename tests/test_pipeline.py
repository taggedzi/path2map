"""Integration tests for the canonical pipeline precedence."""

from __future__ import annotations

from pathlib import Path

from path2map.pipeline import PipelineOptions, build_logical_tree


def _paths_in_preorder(model) -> list[str]:
    return [node.path for node in model.iter_preorder()]


def test_pipeline_applies_precedence_chain(tmp_path: Path) -> None:
    """defaults -> .p2mignore -> --ignore -> --filter precedence is respected."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "keep.py").write_text("x", encoding="utf-8")
    (tmp_path / "src" / "drop.py").write_text("x", encoding="utf-8")

    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "readme.md").write_text("x", encoding="utf-8")

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "tool.py").write_text("x", encoding="utf-8")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x", encoding="utf-8")

    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "out.py").write_text("x", encoding="utf-8")

    (tmp_path / ".p2mignore").write_text(
        "src/*.py\n!src/keep.py\n!build/out.py\n",
        encoding="utf-8",
    )

    model = build_logical_tree(
        PipelineOptions(
            directory=str(tmp_path),
            cli_ignore=r"^src/keep\.py$",
            filters=[r"\.py$"],
        )
    )

    assert _paths_in_preorder(model) == [".", "tools", "tools/tool.py"]


def test_pipeline_filter_retains_ancestors(tmp_path: Path) -> None:
    """Filter matches keep ancestor directories in final logical tree."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "sub").mkdir(parents=True, exist_ok=True)
    (tmp_path / "pkg" / "sub" / "main.py").write_text("x", encoding="utf-8")
    (tmp_path / "pkg" / "sub" / "data.txt").write_text("x", encoding="utf-8")

    model = build_logical_tree(
        PipelineOptions(
            directory=str(tmp_path),
            filters=[r"main\.py$"],
        )
    )

    assert _paths_in_preorder(model) == [".", "pkg", "pkg/sub", "pkg/sub/main.py"]


def test_pipeline_supports_symlinks_option_over_follow_flag(tmp_path: Path) -> None:
    """Explicit --symlinks mode overrides --follow-symlinks compatibility flag."""
    real = tmp_path / "real"
    real.mkdir()
    (real / "inside.py").write_text("x", encoding="utf-8")
    (tmp_path / "link").symlink_to(real, target_is_directory=True)

    model = build_logical_tree(
        PipelineOptions(
            directory=str(tmp_path),
            follow_symlinks=True,
            symlinks="show",
            filters=[r"inside\.py$"],
        )
    )

    # symlinks="show" prevents traversal through link even if follow flag is true.
    assert _paths_in_preorder(model) == [".", "real", "real/inside.py"]
