# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.0] - 2026-02-06

### Added
- Initial release of `path2map` as a CLI and Python package.
- Canonical traversal pipeline with precedence:
  defaults -> `.p2mignore` -> `--ignore` -> `--filter` -> render.
- Multi-format renderers: text, markdown, JSON, CSV, and HTML.
- Deterministic ordering and cross-platform traversal behavior.
- Core test suite for traversal, ignore/filter precedence, renderers, and CLI.
