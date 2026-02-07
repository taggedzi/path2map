#!/usr/bin/env bash
set -euo pipefail

ROOT="docs/samples/input/project"
OUT="docs/samples/output"

mkdir -p "$OUT"

# 0) CLI help and version reference
python -m path2map --help > "$OUT/help.txt"
python -m path2map --version > "$OUT/version.txt"

# 1) Default text output
python -m path2map --directory "$ROOT" --type text --output "$OUT/tree.text.txt"

# 2) Markdown
python -m path2map --directory "$ROOT" --type md --output "$OUT/tree.md"

# 3) JSON
python -m path2map --directory "$ROOT" --type json --output "$OUT/tree.json"

# 4) CSV
python -m path2map --directory "$ROOT" --type csv --output "$OUT/tree.csv"

# 5) HTML
python -m path2map --directory "$ROOT" --type html --output "$OUT/tree.html"

# 6) Depth, ignore, and filter
python -m path2map --directory "$ROOT" --max-depth 2 --ignore "^build/" --filter "\\.py$" --type text --output "$OUT/tree.filtered.txt"

# 7) Folders-only, sorting, comments, emojis
python -m path2map --directory "$ROOT" --folders-only --sort --comments --emojis --type text --output "$OUT/tree.folders.txt"

# 8) Details formatting
python -m path2map --directory "$ROOT" --details size,mtime --time-format "%Y-%m-%d" --size-format decimal --details-style columns --type text --output "$OUT/tree.details.txt"

# 9) Color policy example (stdout)
python -m path2map --directory "$ROOT" --color always --type text --stdout

# 9b) Theme flag parsing example (reserved/no-op)
python -m path2map --directory "$ROOT" --theme default --type text --output "$OUT/tree.theme.txt"

# 10) Symlink mode examples (if symlinks are present in sample tree)
python -m path2map --directory "$ROOT" --symlinks show --type text --output "$OUT/tree.symlinks-show.txt"
python -m path2map --directory "$ROOT" --symlinks follow --type text --output "$OUT/tree.symlinks-follow.txt"

# 11) Legacy follow-symlinks flag
python -m path2map --directory "$ROOT" --follow-symlinks --type text --output "$OUT/tree.follow-legacy.txt"

echo "Sample outputs written to: $OUT"
