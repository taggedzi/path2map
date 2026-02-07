#!/usr/bin/env bash
set -euo pipefail

# Run from repository root with .venv active.
if [[ ! -f "pyproject.toml" ]]; then
  echo "Run this script from the repository root."
  exit 1
fi

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "Activate .venv first: source .venv/bin/activate"
  exit 1
fi

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
echo "Packaging validation complete."
