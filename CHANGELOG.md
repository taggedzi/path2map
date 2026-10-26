# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Keep text and Markdown file exports free of ANSI color under `--color auto`,
  while combined `--stdout` output remains TTY-aware. Explicit `always` and
  `never` policies still apply to both destinations (#6).
- Honor `--folders-only` in JSON and CSV as well as text, Markdown, and HTML
  by selecting directories in the shared pipeline (#5). Schemas are unchanged.
- Correct `.p2mignore` glob segment boundaries, root anchoring, directory-only
  rules and descendant matching, and zero-directory `**` matching across all
  export formats (#4). Rule ordering and hard-exclusion precedence are preserved.
- Preserve alias-relative paths and depths when following directory symlinks,
  including external targets and multiple aliases. Ignore and filter rules now
  match those logical paths, while cycle detection remains branch-local (#3).

## [v0.1.0] - 2026-02-06

### Added
- Initial release of `path2map` as a CLI and Python package.
- Canonical traversal pipeline with precedence:
  defaults -> `.p2mignore` -> `--ignore` -> `--filter` -> render.
- Multi-format renderers: text, markdown, JSON, CSV, and HTML.
- Deterministic ordering and cross-platform traversal behavior.
- Core test suite for traversal, ignore/filter precedence, renderers, and CLI.
