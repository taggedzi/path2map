# path2map

`path2map` inspects a directory tree and exports deterministic maps in text and structured formats.

## Quick Start

```bash
source .venv/bin/activate
python -m path2map --help
```

## Common Usage

Scan current directory (text):

```bash
python -m path2map --directory .
```

Limit depth:

```bash
python -m path2map --directory . --max-depth 1
```

Apply include filter and ignore regex:

```bash
python -m path2map --directory . --filter "\\.py$" --ignore "^build/"
```

Export formats:

```bash
python -m path2map --directory . --type md
python -m path2map --directory . --type json
python -m path2map --directory . --type csv
python -m path2map --directory . --type html
```

Output routing:

```bash
# stdout only (default)
python -m path2map --directory . --type text

# write file
python -m path2map --directory . --type json --output tree.json

# write to directory with timestamped filename
python -m path2map --directory . --type csv --output ./exports

# both stdout and file
python -m path2map --directory . --type md --output tree.md --stdout
```

Details and styling:

```bash
python -m path2map --directory . --details size,mtime --time-format "%Y-%m-%d %H:%M"
python -m path2map --directory . --details size --size-format decimal --details-style columns
python -m path2map --directory . --color always --emojis
```

Symlink behavior:

```bash
python -m path2map --directory . --follow-symlinks
python -m path2map --directory . --symlinks show
python -m path2map --directory . --symlinks follow
```
