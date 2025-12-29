# path2map — Unified Feature & CLI Specification

> **Purpose**
> `path2map` is a directory-structure inspection and export tool. Its goal is to generate *human-readable* and *machine-consumable* representations of a filesystem tree, with strong filtering, ignoring, formatting, and export capabilities — without assuming a developer-only audience.

This document consolidates all agreed-upon design ideas and serves as a **single authoritative reference** for future implementation.

---

## 1. Core Philosophy

* **Readable by default** — clean tree output with minimal noise
* **Opt-in power** — advanced features enabled only when requested
* **Predictable rules** — consistent precedence for ignore, filter, and output
* **Non-developer friendly** — formats usable outside programming workflows
* **Scriptable** — stable CLI, machine-readable formats, deterministic output

---

## 2. Directory Traversal Model

Traversal always follows this pipeline:

1. Enumerate filesystem entries from `--directory`
2. Apply **built-in default ignores**
3. Apply `.p2mignore` rules (if enabled)
4. Apply CLI `--ignore` regex exclusions
5. Apply CLI `--filter` regex (include-only spotlight)
6. Build a logical tree (retain ancestors of matching nodes)
7. Render to selected output format

This ensures **all output formats match each other**.

### 2.1 Depth Limiting

```
-D, --max-depth [n]
```

* Limits traversal depth relative to the scan root.
* `0` means: only the root directory (no children).
* `1` means: root + immediate children.
* Default: unlimited.

Depth limiting is applied during enumeration/building to avoid unnecessary work.

### 2.2 Symbolic Links & Cycle Safety

Symlinks (and similar reparse points) can create cycles that lead to infinite recursion.

Default behavior:

* **Do not follow** symlinked directories.
* Still display the symlink entry as a leaf (optionally annotated).

Options:

```
--follow-symlinks
```

* If enabled, symlinked directories may be traversed.
* The implementation must be cycle-safe:

  * Maintain a visited set using a stable identity (e.g., device+inode where available, otherwise resolved/real path).
  * If a cycle is detected, stop traversal for that branch and optionally add a comment such as `Symlink cycle`.

```
--symlinks [skip|show|follow]
```

* Future-safe consolidated form (optional). If used, supersedes `--follow-symlinks`.

  * `skip`: omit symlinks entirely
  * `show`: display symlinks but do not traverse (recommended default)
  * `follow`: traverse with cycle detection

---

## 3. Ignore System

### 3.1 Built-in Default Ignores

Applied automatically unless disabled:

```
.git/
.venv/
__pycache__/
.mypy_cache/
.pytest_cache/
node_modules/
dist/
build/
```

---

### 3.2 `.p2mignore`

A project-level ignore file modeled after `.gitignore`.

**Location**

* Default: `<scan-root>/.p2mignore`
* Can be overridden via CLI

**Format rules**

* One pattern per line
* Blank lines ignored
* `#` comments supported
* Gitignore-style glob patterns
* Negation supported with `!`

**Example**

```
# Version control
.git/

# Python
__pycache__/
*.pyc

# Allow one file back in
!important.pyc
```

---

### 3.3 CLI Ignore (Regex)

```
-i, --ignore [regex]
```

* Comma-separated regex list
* Applies to full relative path
* Hard exclusion (cannot be overridden)

---

## 4. Regex Filter (Include Spotlight)

```
-F, --filter [regex]
```

* Only paths matching the regex are included
* Ancestor folders are preserved for context
* Applied *after* ignores

**Examples**

```
-F "\.py$"
-F "^src/"
-F "tui"
```

Multiple `--filter` flags may be allowed (OR logic).

---

## 5. Tree Rendering Options

### 5.1 Folder / File Controls

```
-f, --folders-only
```

* Omit files entirely
* Disables file-only features (comments, extensions, etc.)

```
-s, --sort
```

* Alphabetical sorting
* Folders listed before files

```
-c, --comments
```

* Adds contextual comments (e.g., `Empty folder`)
* Disabled when `--folders-only` is active

```
--emojis
```

* Adds visual icons

  * 📁 Folder
  * 📄 File

---

## 6. Color Output

```
--color [auto|always|never]
```

* `auto` (default): color only if stdout is a TTY
* `always`: force color
* `never`: disable color entirely

```
--theme [name]
```

* Optional theme selector (future-safe)

### Coloring Rules

* Folders: distinct color or bold
* Files: normal
* Extension-based coloring groups:

  * Code
  * Config
  * Docs
  * Media (image/audio/video)
  * Archives
  * Executables

**Exported files default to no color**, unless `--color always`.

---

## 7. File Details (Opt-In Metadata)

```
--details [none|size|mtime|size,mtime]
```

* `size`: human-readable file size
* `mtime`: last modified local timestamp

```
--time-format [strftime]
--size-format [binary|decimal]
```

Defaults:

* Time: `%Y-%m-%d %H:%M`
* Size: binary (KiB/MiB)

### Display Styles

```
--details-style [inline|columns]
```

**Inline**

```
file.py (3.2 KiB, 2025-12-29 13:04)
```

**Columns**

```
file.py     3.2 KiB   2025-12-29 13:04
```

Folders typically omit size or display `—`.

---

## 8. Output & Export

### 8.1 Output Target

```
-o, --output [path]
--stdout
```

* If output path is a directory, filename is auto-generated
* Timestamped filenames:

  * `path2map_YYYY-MM-DD_HHMMSS.ext`

---

### 8.2 Output Formats

```
-t, --type [text|md|json|csv|html]
```

#### text

* Default human-readable tree

#### md

* Tree wrapped in fenced Markdown block

#### json

* Structured hierarchical representation
* Includes metadata fields when enabled

#### csv

* Flat row-based list
* Columns: path, name, type, ext, depth, size, mtime

#### html

* Shareable, collapsible tree
* Minimal CSS, optional JS

---

## 9. CLI Meta Options

```
-V, --version
-h, --help
```

---

## 10. Precedence Summary

| Stage           | Purpose                  |
| --------------- | ------------------------ |
| Default ignores | Hard exclusions          |
| .p2mignore      | Project-level rules      |
| --ignore        | User-enforced exclusions |
| --filter        | Include-only spotlight   |
| Output format   | Rendering only           |

---

## 11. Non-Goals (Intentional Constraints)

* No filesystem mutation
* No recursive `.p2mignore` hierarchy (single root file)
* No implicit size/stat cost unless requested
* No dynamic plugin system (initially)

---

## 12. Implementation Notes (Non-Binding)

* Tree-building first, rendering second
* Consider `pathspec` for ignore matching
* Rich or ANSI output acceptable
* All formats should originate from the same tree model

---

## 13. Project Status

This document represents a **complete, coherent v1 feature set**.
Nothing here is provisional or speculative.

Future additions should preserve:

* CLI stability
* Default simplicity
* Predictable precedence

---

*End of specification.*
