# Contributing

## Development Setup

Use the existing virtual environment in `.venv`:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run Checks Locally

Run these before opening a PR:

```bash
python -m black .
python -m ruff check .
python -m mypy src
python -m pytest
```

Optional explicit coverage run:

```bash
python -m pytest --cov=path2map --cov-report=term-missing
```

## Packaging Validation

Before release, run a full packaging check from the repository root:

```bash
source .venv/bin/activate
bash scripts/package_check.sh
```

Equivalent manual commands:

```bash
source .venv/bin/activate
python -m pip install --upgrade build twine
rm -rf dist build .pkg-smoke-venv src/path2map.egg-info
python -m build
python -m twine check dist/*
python -m venv .pkg-smoke-venv
source .pkg-smoke-venv/bin/activate
python -m pip install --no-deps dist/path2map-*.whl
path2map --help
deactivate
rm -rf .pkg-smoke-venv
```

## Opening a Pull Request

1. Create a focused branch for one change.
2. Keep behavior aligned with `SPECS.md` (source of truth).
3. Add or update tests for behavior changes.
4. Update docs if CLI behavior, outputs, or defaults change.
5. Open a PR with:
   - What changed
   - Why it changed
   - How you validated it (commands + results)
   - Any follow-ups or limitations

## Release Process (Maintainers)

1. Ensure `main` is green in CI and `CHANGELOG.md` + version are updated.
2. Run local packaging validation:
   - `source .venv/bin/activate`
   - `bash scripts/package_check.sh`
3. Create and push a version tag:
   - `git tag v0.1.0`
   - `git push origin v0.1.0`
4. The `Release` workflow will:
   - build `sdist` and `wheel`
   - run `twine check`
   - create a GitHub Release and attach artifacts
5. Optional PyPI publishing:
   - set repository variable `PYPI_PUBLISH=true`
   - set secret `PYPI_API_TOKEN`
   - configure required approvals on the `pypi` environment
