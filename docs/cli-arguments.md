# CLI Argument Reference

Use `python -m path2map --help` for the canonical command summary.

## Core Arguments

| Argument | Description | Default |
|---|---|---|
| `--directory` | Root directory to scan. | `.` |
| `-o, --output` | Output file path or output directory. If a directory is used, path2map generates a timestamped filename. | not set |
| `--stdout` | Also write output to stdout when `--output` is set. | `False` |
| `-t, --type` | Output format: `text`, `md`, `json`, `csv`, `html`. | `text` |
| `-V, --version` | Print version and exit. | n/a |

## Traversal and Selection

| Argument | Description | Default |
|---|---|---|
| `-D, --max-depth` | Maximum depth from root (`0` means only the root node). | not set |
| `--follow-symlinks` | Follow symlinks during traversal (legacy convenience flag). | `False` |
| `--symlinks` | Symlink mode: `skip`, `show`, `follow`. | not set |
| `-i, --ignore` | Regex exclusion applied after defaults and `.p2mignore`. | not set |
| `-F, --filter` | Include-only regex filter (repeatable; OR logic). Ancestors of matches are retained. | empty list |
| `-f, --folders-only` | Render directories only. | `False` |
| `-s, --sort` | Sort nodes per directory (folders first, then files, case-insensitive). | `False` |

## Presentation

| Argument | Description | Default |
|---|---|---|
| `-c, --comments` | Adds contextual labels like `[Empty folder]` on empty directories. | `False` |
| `--emojis` | Prefix node labels with emoji markers where applicable. | `False` |
| `--color` | Color mode for text/markdown: `auto`, `always`, `never`. | `auto` |
| `--theme` | Reserved for future theming support (currently no effect). | not set |

## Metadata Details

| Argument | Description | Default |
|---|---|---|
| `--details` | Metadata fields: `none`, `size`, `mtime`, `size,mtime`. | `none` |
| `--time-format` | `strftime` format for `mtime` output. | `%Y-%m-%d %H:%M` |
| `--size-format` | File size units: `binary` (`KiB`) or `decimal` (`KB`). | `binary` |
| `--details-style` | Detail layout in text/markdown: `inline` or `columns`. | `inline` |

## Examples

```bash
# Basic text tree
python -m path2map --directory .

# Depth-limited, sorted output
python -m path2map --directory . --max-depth 2 --sort

# Include only Python files, while excluding build artifacts
python -m path2map --directory . --filter "\\.py$" --ignore "^build/"

# Export JSON to a file
python -m path2map --directory . --type json --output tree.json

# Export markdown and also print to stdout
python -m path2map --directory . --type md --output tree.md --stdout

# Render file sizes and timestamps with column formatting
python -m path2map --directory . --details size,mtime --details-style columns
```
