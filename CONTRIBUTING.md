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
