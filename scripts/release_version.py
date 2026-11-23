"""Assign UTC date release numbers and stamp release metadata.

Release numbers are ``YYYY.MM.DD``. Another release on the same UTC date uses
``YYYY.MM.DD.N`` with ``N`` starting at 1. Git tags keep a ``v`` prefix.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from datetime import date, datetime, timezone
from pathlib import Path

_CALVER_RE = re.compile(
    r"^(?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2})" r"(?:\.(?P<seq>[1-9]\d*))?$"
)
_TAG_RE = re.compile(r"^v(?P<version>\d{4}\.\d{2}\.\d{2}(?:\.[1-9]\d*)?)$")
_PYPROJECT_VERSION = re.compile(r'(?m)^version = "[^"]*"$')
_INIT_VERSION = re.compile(r'(?m)^__version__ = "[^"]*"$')


def utc_today() -> date:
    """Return the current date in UTC."""
    return datetime.now(timezone.utc).date()


def parse_calver(value: str) -> tuple[date, int] | None:
    """Parse ``YYYY.MM.DD`` or ``YYYY.MM.DD.N``. Return ``None`` when invalid."""
    match = _CALVER_RE.fullmatch(value.strip())
    if match is None:
        return None
    try:
        day = date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
    except ValueError:
        return None
    seq_text = match.group("seq")
    seq = int(seq_text) if seq_text is not None else 0
    return day, seq


def parse_tag(value: str) -> tuple[date, int] | None:
    """Parse a ``vYYYY.MM.DD`` tag. Return ``None`` for any other tag."""
    match = _TAG_RE.fullmatch(value.strip())
    if match is None:
        return None
    return parse_calver(match.group("version"))


def format_calver(day: date, seq: int) -> str:
    """Format a date version. ``seq`` 0 omits the suffix."""
    if seq < 0:
        raise ValueError(f"release counter must be zero or positive, got {seq}")
    base = f"{day.year:04d}.{day.month:02d}.{day.day:02d}"
    if seq == 0:
        return base
    return f"{base}.{seq}"


def next_calver(tags: Iterable[str], today: date) -> str:
    """Return the next unused date version for ``today``.

    The plain date is used first. Later releases on that date increment the
    suffix so numbers keep increasing.
    """
    highest = -1
    for tag in tags:
        parsed = parse_tag(tag.strip())
        if parsed is None or parsed[0] != today:
            continue
        highest = max(highest, parsed[1])
    return format_calver(today, highest + 1)


def stamp_pyproject(text: str, version: str) -> str:
    """Replace the single ``[project]`` version assignment."""
    matches = list(_PYPROJECT_VERSION.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            f"expected one pyproject version assignment, found {len(matches)}"
        )
    return _PYPROJECT_VERSION.sub(f'version = "{version}"', text, count=1)


def stamp_init(text: str, version: str) -> str:
    """Replace the single package ``__version__`` assignment."""
    matches = list(_INIT_VERSION.finditer(text))
    if len(matches) != 1:
        raise ValueError(f"expected one __version__ assignment, found {len(matches)}")
    return _INIT_VERSION.sub(f'__version__ = "{version}"', text, count=1)


def promote_changelog(text: str, version: str, today: date) -> str:
    """Move ``## [Unreleased]`` notes under a dated version heading.

    A second call for the same heading leaves the changelog unchanged.
    """
    heading = f"## [v{version}] - {today.isoformat()}"
    if re.search(rf"(?m)^{re.escape(heading)}$", text):
        return text
    marker = "## [Unreleased]\n"
    start = text.find(marker)
    if start < 0:
        raise ValueError("CHANGELOG.md is missing an ## [Unreleased] section")
    body_start = start + len(marker)
    next_heading = text.find("\n## ", body_start)
    if next_heading < 0:
        body = text[body_start:]
        rest = ""
    else:
        body = text[body_start : next_heading + 1]
        rest = text[next_heading + 1 :]
    content = body.strip()
    section = f"{content}\n" if content else "No notable changes recorded.\n"
    promoted = f"## [Unreleased]\n\n{heading}\n\n{section}\n"
    return text[:start] + promoted + rest


def apply_release(root: Path, version: str, today: date) -> None:
    """Stamp ``pyproject.toml``, ``__init__.py``, and ``CHANGELOG.md``."""
    parsed = parse_calver(version)
    if parsed is None or parsed[0] != today:
        raise ValueError(f"{version} is not a date version for {today.isoformat()}")
    paths = (
        root / "pyproject.toml",
        root / "src" / "path2map" / "__init__.py",
        root / "CHANGELOG.md",
    )
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise ValueError("missing release files: " + ", ".join(missing))
    pyproject, init_py, changelog = paths
    updated = {
        pyproject: stamp_pyproject(pyproject.read_text(encoding="utf-8"), version),
        init_py: stamp_init(init_py.read_text(encoding="utf-8"), version),
        changelog: promote_changelog(
            changelog.read_text(encoding="utf-8"), version, today
        ),
    }
    for path, text in updated.items():
        path.write_text(text, encoding="utf-8", newline="\n")


def prepare_release(root: Path, tags: Iterable[str], today: date) -> str:
    """Choose the next date version and stamp release metadata."""
    version = next_calver(tags, today)
    apply_release(root, version, today)
    return version


def _parse_day(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"date must be YYYY-MM-DD, got {value}") from exc


def _read_tags(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"tags file not found: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def _command_day(value: str | None) -> date:
    if value is None:
        return utc_today()
    return _parse_day(value)


def main(argv: list[str] | None = None) -> int:
    """Run the release-version command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    next_cmd = subcommands.add_parser("next", help="Print the next date version.")
    next_cmd.add_argument("--tags-file", type=Path, required=True)
    next_cmd.add_argument("--date", help="UTC date YYYY-MM-DD. Defaults to today.")

    apply_cmd = subcommands.add_parser("apply", help="Stamp version files.")
    apply_cmd.add_argument("--version", required=True)
    apply_cmd.add_argument("--date", help="Changelog date YYYY-MM-DD.")
    apply_cmd.add_argument("--root", type=Path, default=Path("."))

    prepare_cmd = subcommands.add_parser(
        "prepare", help="Choose the next version and stamp files."
    )
    prepare_cmd.add_argument("--tags-file", type=Path, required=True)
    prepare_cmd.add_argument("--date", help="UTC date YYYY-MM-DD. Defaults to today.")
    prepare_cmd.add_argument("--root", type=Path, default=Path("."))

    args = parser.parse_args(argv)
    try:
        if args.command == "next":
            version = next_calver(_read_tags(args.tags_file), _command_day(args.date))
            print(version)
        elif args.command == "apply":
            today = (
                _parse_day(args.date)
                if args.date is not None
                else _version_day(args.version)
            )
            apply_release(args.root, args.version, today)
        else:
            version = prepare_release(
                args.root, _read_tags(args.tags_file), _command_day(args.date)
            )
            print(version)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def _version_day(version: str) -> date:
    parsed = parse_calver(version)
    if parsed is None:
        raise ValueError(f"{version} is not a date version")
    return parsed[0]


if __name__ == "__main__":
    raise SystemExit(main())
