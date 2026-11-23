"""Tests for date-based release numbering."""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_version.py"
_SPEC = importlib.util.spec_from_file_location("release_version", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
release_version = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(release_version)

TODAY = date(2026, 11, 23)


def test_next_calver_ignores_older_schemes() -> None:
    """SemVer tags do not consume the date version."""
    version = release_version.next_calver(["v0.1.0", "v1.2.3"], TODAY)

    assert version == "2026.11.23"


def test_next_calver_increments_on_the_same_utc_date() -> None:
    """A later release on the same date uses the next suffix."""
    tags = ["v2026.11.23", "v2026.11.22", "v2026.11.23.1"]

    assert release_version.next_calver(tags, TODAY) == "2026.11.23.2"


def test_next_calver_starts_over_on_a_new_date() -> None:
    """The previous day's suffix does not carry forward."""
    version = release_version.next_calver(["v2026.11.22.4"], TODAY)

    assert version == "2026.11.23"


def test_next_calver_skips_invalid_calendar_tags() -> None:
    """Tags that are not real dates stay out of the sequence."""
    version = release_version.next_calver(["v2026.02.31", "v2026.11.23.0"], TODAY)

    assert version == "2026.11.23"


def test_stamp_pyproject_replaces_only_the_project_version() -> None:
    """Tool target-version settings stay in place."""
    text = '[project]\nversion = "0.1.0"\n\n[tool.black]\ntarget-version = ["py310"]\n'

    stamped = release_version.stamp_pyproject(text, "2026.11.23")

    assert stamped == (
        '[project]\nversion = "2026.11.23"\n\n[tool.black]\ntarget-version = ["py310"]\n'
    )


def test_stamp_pyproject_rejects_an_ambiguous_file() -> None:
    """Zero or several version assignments fail closed."""
    with pytest.raises(ValueError, match="expected one pyproject"):
        release_version.stamp_pyproject('[project]\nname = "path2map"\n', "2026.11.23")


def test_stamp_init_replaces_the_package_version() -> None:
    """The installed package version tracks the release number."""
    text = '__all__ = ["__version__"]\n\n__version__ = "0.1.0"\n'

    assert release_version.stamp_init(text, "2026.11.23.1") == (
        '__all__ = ["__version__"]\n\n__version__ = "2026.11.23.1"\n'
    )


def test_promote_changelog_moves_unreleased_notes() -> None:
    """Unreleased notes become the dated section and the heading resets."""
    text = (
        "# Changelog\n\n"
        "## [Unreleased]\n\n"
        "### Fixed\n"
        "- One\n\n"
        "## [v0.1.0] - 2026-02-06\n"
    )

    promoted = release_version.promote_changelog(text, "2026.11.23", TODAY)

    assert promoted == (
        "# Changelog\n\n"
        "## [Unreleased]\n\n"
        "## [v2026.11.23] - 2026-11-23\n\n"
        "### Fixed\n"
        "- One\n\n"
        "## [v0.1.0] - 2026-02-06\n"
    )
    assert release_version.promote_changelog(promoted, "2026.11.23", TODAY) == promoted


def test_promote_changelog_records_an_empty_unreleased_section() -> None:
    """A release with no notes still gets a changelog heading."""
    text = "# Changelog\n\n## [Unreleased]\n\n## [v0.1.0] - 2026-02-06\n"

    promoted = release_version.promote_changelog(text, "2026.11.23", TODAY)

    assert "No notable changes recorded." in promoted
    assert promoted.index("## [Unreleased]") < promoted.index("## [v2026.11.23]")
    assert promoted.index("## [v2026.11.23]") < promoted.index("## [v0.1.0]")


def test_promote_changelog_requires_the_unreleased_heading() -> None:
    """A changelog without the expected section is not rewritten."""
    with pytest.raises(ValueError, match="Unreleased"):
        release_version.promote_changelog("# Changelog\n", "2026.11.23", TODAY)


def test_prepare_release_stamps_the_repository_copy(tmp_path: Path) -> None:
    """Preparing a release writes the same version into every release file."""
    package = tmp_path / "src" / "path2map"
    package.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion = "0.1.0"\n', encoding="utf-8"
    )
    (package / "__init__.py").write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "## [Unreleased]\n\n### Changed\n- Date releases\n\n## [v0.1.0] - 2026-02-06\n",
        encoding="utf-8",
    )

    version = release_version.prepare_release(tmp_path, ["v0.1.0"], TODAY)

    assert version == "2026.11.23"
    assert 'version = "2026.11.23"' in (tmp_path / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert '__version__ = "2026.11.23"' in (package / "__init__.py").read_text(
        encoding="utf-8"
    )
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [v2026.11.23] - 2026-11-23" in changelog
    assert "Date releases" in changelog.split("## [v0.1.0]")[0]


def test_apply_release_rejects_a_version_for_a_different_day(tmp_path: Path) -> None:
    """The package version and the changelog date stay on the same day."""
    with pytest.raises(ValueError, match="not a date version"):
        release_version.apply_release(tmp_path, "2026.11.22", TODAY)


def test_cli_prepare_prints_the_version(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The workflow command prints only the chosen version."""
    package = tmp_path / "src" / "path2map"
    package.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nversion = "0.1.0"\n', encoding="utf-8"
    )
    (package / "__init__.py").write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "## [Unreleased]\n\n## [v0.1.0] - 2026-02-06\n", encoding="utf-8"
    )
    tags = tmp_path / "tags.txt"
    tags.write_text("v2026.11.23\n", encoding="utf-8")

    code = release_version.main(
        [
            "prepare",
            "--tags-file",
            str(tags),
            "--root",
            str(tmp_path),
            "--date",
            "2026-11-23",
        ]
    )

    assert code == 0
    assert capsys.readouterr().out == "2026.11.23.1\n"
    assert '__version__ = "2026.11.23.1"' in (package / "__init__.py").read_text(
        encoding="utf-8"
    )


def test_cli_rejects_a_bad_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A bad override date fails before any file is changed."""
    tags = tmp_path / "tags.txt"
    tags.write_text("", encoding="utf-8")

    code = release_version.main(
        ["next", "--tags-file", str(tags), "--date", "2026-13-40"]
    )

    assert code == 2
    assert "YYYY-MM-DD" in capsys.readouterr().err
