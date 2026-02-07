# Versioning and Compatibility Policy

`path2map` follows Semantic Versioning (`MAJOR.MINOR.PATCH`).

## SemVer Interpretation

- `PATCH`: bug fixes and internal improvements that do not change public behavior.
- `MINOR`: backward-compatible feature additions.
- `MAJOR`: backward-incompatible changes.

## What Counts as Breaking

Treat these as breaking changes and require a `MAJOR` bump:

- Renaming/removing CLI flags or changing their meaning.
- Changing default behavior that alters output selection or structure.
- Changing JSON or CSV schema (field names, required fields, structure).
- Reordering or changing output semantics in ways that break automation.

## Release Checklist

Before tagging a release:

1. Ensure CI is green on `main`.
2. Update `CHANGELOG.md` with release notes.
3. Confirm `pyproject.toml` and `src/path2map/__init__.py` version match.
4. Run local package validation:
   - `source .venv/bin/activate`
   - `bash scripts/package_check.sh`
5. Create and push a tag (`vX.Y.Z`) to trigger release automation.
