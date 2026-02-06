"""Ignore-rule handling for traversal stage filtering."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
import re
from typing import Pattern

DEFAULT_IGNORE_PATTERNS: tuple[str, ...] = (
    ".git/",
    ".venv/",
    "__pycache__/",
    ".mypy_cache/",
    ".pytest_cache/",
    "node_modules/",
    "dist/",
    "build/",
)


@dataclass(frozen=True)
class PathEntry:
    """A traversal entry candidate represented by relative path."""

    path: str
    is_dir: bool


@dataclass(frozen=True)
class IgnoreRule:
    """A `.p2mignore` rule."""

    pattern: str
    is_negation: bool = False


@dataclass(frozen=True)
class IgnoreConfig:
    """Configuration for ignore stage filtering."""

    use_default_ignores: bool = True
    p2mignore_enabled: bool = True
    p2mignore_path: Path | None = None
    cli_ignore: str | None = None


def filter_ignored_entries(
    entries: list[PathEntry],
    *,
    scan_root: Path,
    config: IgnoreConfig | None = None,
) -> list[PathEntry]:
    """Filter candidate entries using defaults, `.p2mignore`, and CLI regex."""
    cfg = config or IgnoreConfig()

    p2m_rules = (
        load_p2mignore_rules(scan_root=scan_root, p2mignore_path=cfg.p2mignore_path)
        if cfg.p2mignore_enabled
        else []
    )
    cli_patterns = compile_cli_ignore_patterns(cfg.cli_ignore)

    filtered: list[PathEntry] = []
    for entry in entries:
        if should_ignore_entry(
            entry,
            use_default_ignores=cfg.use_default_ignores,
            p2mignore_rules=p2m_rules,
            cli_ignore_patterns=cli_patterns,
        ):
            continue
        filtered.append(entry)

    return filtered


def should_ignore_entry(
    entry: PathEntry,
    *,
    use_default_ignores: bool,
    p2mignore_rules: list[IgnoreRule],
    cli_ignore_patterns: list[Pattern[str]],
) -> bool:
    """Return whether an entry should be excluded by ignore stages 2-4."""
    rel_path = normalize_relative_path(entry.path)

    if use_default_ignores and matches_any_ignore_pattern(
        rel_path=rel_path,
        is_dir=entry.is_dir,
        patterns=DEFAULT_IGNORE_PATTERNS,
    ):
        return True

    if _matches_p2mignore(
        rel_path=rel_path, is_dir=entry.is_dir, rules=p2mignore_rules
    ):
        return True

    if any(regex.search(rel_path) for regex in cli_ignore_patterns):
        return True

    return False


def compile_cli_ignore_patterns(ignore_value: str | None) -> list[Pattern[str]]:
    """Compile comma-separated CLI ignore regex patterns."""
    if ignore_value is None:
        return []
    parts = [part.strip() for part in ignore_value.split(",")]
    return [re.compile(part) for part in parts if part]


def load_p2mignore_rules(
    *,
    scan_root: Path,
    p2mignore_path: Path | None = None,
) -> list[IgnoreRule]:
    """Load `.p2mignore` rules from scan root (or provided override path)."""
    ignore_file = p2mignore_path or (scan_root / ".p2mignore")
    if not ignore_file.exists():
        return []

    rules: list[IgnoreRule] = []
    for raw_line in ignore_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            pattern = line[1:].strip()
            if pattern:
                rules.append(IgnoreRule(pattern=pattern, is_negation=True))
            continue
        rules.append(IgnoreRule(pattern=line))

    return rules


def matches_any_ignore_pattern(
    *,
    rel_path: str,
    is_dir: bool,
    patterns: tuple[str, ...] | list[str],
) -> bool:
    """Return True if any glob pattern matches a relative path."""
    return any(
        _matches_glob_pattern(rel_path=rel_path, is_dir=is_dir, pattern=p)
        for p in patterns
    )


def _matches_p2mignore(
    *,
    rel_path: str,
    is_dir: bool,
    rules: list[IgnoreRule],
) -> bool:
    ignored = False
    for rule in rules:
        if not _matches_glob_pattern(
            rel_path=rel_path, is_dir=is_dir, pattern=rule.pattern
        ):
            continue
        ignored = not rule.is_negation
    return ignored


def _matches_glob_pattern(*, rel_path: str, is_dir: bool, pattern: str) -> bool:
    normalized_path = normalize_relative_path(rel_path)

    anchored = pattern.startswith("/")
    cleaned = pattern.lstrip("/")
    dir_only = cleaned.endswith("/")
    cleaned = cleaned.rstrip("/")
    if not cleaned:
        return False

    segments = normalized_path.split("/")

    if dir_only:
        if "/" in cleaned or anchored:
            return normalized_path == cleaned or normalized_path.startswith(
                f"{cleaned}/"
            )

        for index, segment in enumerate(segments):
            if not fnmatch(segment, cleaned):
                continue
            if index < len(segments) - 1 or is_dir:
                return True
        return False

    if "/" in cleaned or anchored:
        return fnmatch(normalized_path, cleaned)

    return any(fnmatch(segment, cleaned) for segment in segments)


def normalize_relative_path(path: str) -> str:
    """Normalize incoming path text to POSIX-style relative form."""
    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/") if normalized != "." else "."
