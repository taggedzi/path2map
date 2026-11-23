# Versioning and Compatibility Policy

`path2map` release numbers are UTC dates: `YYYY.MM.DD`.

A later release on the same UTC date adds a counter: `YYYY.MM.DD.1`,
`YYYY.MM.DD.2`, and so on. Numbers for a given day keep increasing.

Git tags use a `v` prefix (`v2026.11.23`). The Python package version is the
same number without the prefix. Dots keep the number valid as a Python package
version. The initial release stays `v0.1.0`.

## What to record as breaking

Record these in the changelog for the release that introduces them:

- Renaming or removing CLI flags, or changing their meaning.
- Changing default behavior that alters output selection or structure.
- Changing JSON or CSV schema (field names, required fields, structure).
- Reordering or changing output semantics in ways that break automation.

## Release process

Releases are published from the **Release** workflow in GitHub Actions.

1. Merge the changes you want to ship, including notes under `## [Unreleased]`
   in `CHANGELOG.md`.
2. On GitHub, open **Actions → Release → Run workflow** and choose the branch
   to release. Use `main` for a normal release.
3. The workflow assigns the next date version, moves the unreleased notes into
   that version's changelog section, and sets `pyproject.toml` and
   `src/path2map/__init__.py` to that version.
4. It runs formatting, lint, typecheck, and tests, builds the source
   distribution and wheel, and checks the artifacts with `twine`.
5. It pushes the version commit to the selected branch, tags `vYYYY.MM.DD`,
   and publishes a GitHub Release with the artifacts attached.

The branch must accept pushes from `github-actions[bot]`. Artifacts are
published to GitHub Releases only.

Between releases, the version in the repository is the last released version.
If a run fails before it creates the tag, start it again and it reuses that
version. If the tag already exists, the next run uses the next same-day number.
