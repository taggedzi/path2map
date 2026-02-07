# path2map

`path2map` inspects a directory tree and exports deterministic maps in text and structured formats.

## Why make path2map

There are other tools out there that make a tree based folder map, but I wanted one that would allow a .gitignore type file that it observed to block files and folders in a project. So for example I often work with python programming and I often end up with a lot of hidden folders like .mypy_cache, .ruff_chache, .pytest_cache, etc. And I want to be able to see the entire project with out all the **extra stuff** and allow me to consistently filter, sort, and collect data on a project. It has many usages outside of this so I am trying to make it very basic and very utilitarian.

My usecase I put a `.p2mignore` file in the root of your project and exclude the tree parts you don't want included just like a `.gitignore` file. And none of those will show up in your tree.  

## Here are some of the features this provides

* output in many different formats like stdout, TEXT, MARKDOWN, JSON, CVS, and even HTML.
* It handles symlinks and allows depth control to prevent infinite recursion.
* Regex exclusion applied after defaults and .p2mignore rules.
* You can include regex filters.
* A simple sort feature
* Emoji (folder/file icon) support.
* Color output.
* File detail collection like file size and time

## Simple Example

```text
(.venv) tagger@path2map:~/path2map/docs/samples/input/project$ path2map --directory .
project
├── assets
│   └── images
│       └── logo.svg
├── src
│   ├── main.py
│   └── utils.py
├── .p2mignore
├── config.toml
└── README.md
```

## Sample Screen Shots

Help output preview:

![CLI help screenshot](/docs/assets/screenshots/path2map-help.jpg)

Sample text tree preview:

![Sample tree screenshot](/docs/assets/screenshots/path2map-default.jpg)

## Project Policies

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Versioning Policy](docs/versioning.md)
- [Release Dry Run Checklist](docs/release-dry-run.md)
- [CLI Argument Reference](docs/cli-arguments.md)
- [Sample Catalog](docs/samples/README.md)

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
