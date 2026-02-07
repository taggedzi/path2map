# Release Candidate Dry Run (2026-02-07)

This checklist captures the Step 20 dry run outcome before public announcement.

## 1) Local quality checks

- Black: pass
  - `python -m black .`
- Ruff: pass
  - `python -m ruff check .`
- Mypy: pass
  - `python -m mypy src`
- Pytest + coverage: pass
  - `python -m pytest --cov=path2map --cov-report=term-missing`
  - Result: `62 passed`, `94%` coverage

## 2) CI status on branch

- Not verifiable from local-only dry run context.
- Required before release: confirm `CI` workflow is green on target branch.

## 3) Package build/install smoke test

- Status: fail (blocked by environment dependency resolution)
- Attempted:
  - `python -m build --sdist --no-isolation`
  - `python -m build --wheel --no-isolation`
- Failure:
  - Missing dependencies in active `.venv`:
    - `setuptools>=68`
    - `wheel`
  - Network-restricted environment prevented installing missing packages.

## 4) Docs/manual sanity pass

- README policy links: pass (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/versioning.md`)
- Top-level governance docs present: pass

## 5) Changelog/version/tag plan

- `CHANGELOG.md`: has `v0.1.0` entry (dated `2026-02-06`)
- `pyproject.toml` version: `0.1.0`
- `src/path2map/__init__.py` version: `0.1.0`
- Tag plan: `v0.1.0` when release blockers are cleared

## Go/No-Go Decision

- Decision: **NO-GO**
- Blocking item:
  - Packaging smoke test is not passing in current environment due missing build dependencies (`setuptools>=68`, `wheel`).

## Exit Criteria To Flip To GO

1. Ensure `.venv` has required build dependencies (`setuptools>=68`, `wheel`).
2. Re-run `bash scripts/package_check.sh` and confirm successful `sdist` + `wheel` build and wheel install smoke test.
3. Confirm GitHub `CI` workflow is green on the release branch/tag source commit.
