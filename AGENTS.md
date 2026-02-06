# AGENTS.md

This file is the operational guide for AI coding agents (Codex, Cursor agents, etc.) working in this repository.

**path2map** is a directory-structure inspection and export tool that generates **human-readable** and **machine-consumable** representations of filesystem trees, with consistent traversal → ignore → filter → tree-build → render semantics across all output formats.

If anything in this file conflicts with `SPECS.md`, **`SPECS.md` is the source of truth**.

---

## Python environment

This project uses a Python virtual environment located at `.venv/`.

Rules:
- The `.venv/` directory is created and managed by the user.
- Agents must not create, modify, delete, or replace virtual environments.
- All Python commands (tests, linting, formatting, execution) must be run
  using the `.venv/` environment.
- If the environment is not active or unavailable, agents must stop and ask
  for guidance rather than guessing.

## 0) Decision hierarchy (important)

When guidance conflicts, follow this order:

1. `SPECS.md` (authoritative behavior and intent)
2. User-facing docs (`README.md`, `docs/`)
3. Code + tests (actual behavior)
4. `AGENTS.md` (workflow and guardrails)

`AGENTS.md` exists to help agents succeed — not to override the product.

---

## 0.5) Architectural Decision Records (ADRs)

This project uses **Architectural Decision Records (ADRs)** to document
important design and architectural decisions.

ADRs exist to capture **why** decisions were made — not to document how
the code works.

### Rules for ADRs

- ADRs live in `docs/adr/`
- ADRs are short, focused, and written in plain language
- Not every change needs an ADR

### When an ADR is required

Create or update an ADR when a change:

- affects traversal, ignore, or filtering behavior
- impacts CLI UX, defaults, or output compatibility
- introduces or rejects a dependency
- changes determinism, performance posture, or safety boundaries
- enforces or relaxes a long-term constraint

### How agents should use ADRs

- Read relevant ADRs before proposing changes
- Do not silently violate an accepted ADR
- If an ADR no longer fits, propose a **new ADR** rather than bypassing it

---

## 1) Project overview

* **Name:** path2map
* **Primary language:** Python
* **Minimum runtime:** Python 3.10+
* **Developer environment:** Python 3.12+ (Windows-friendly)
* **Packaging:** pip
* **Containers:** none
* **Primary interface:** CLI

---

## 2) Agent mission

Agents should:

* Implement features exactly as specified in `SPECS.md`.
* Preserve traversal semantics and precedence across **all** output formats.
* Favor correctness, determinism, and clarity over cleverness.
* Write tests for core behavior early and expand coverage over time.

Agents must:

* Ask for clarification when ambiguity is **high-impact**.
* Keep changes scoped to the task.
* Avoid “improving” UX, defaults, or architecture unless requested.

---

## 3) Non-negotiable constraints

### Dependencies

* **Do not add new dependencies** without prior discussion and approval.
* Any proposed dependency must include:

  * license
  * why stdlib is insufficient
  * security / maintenance considerations
* Prefer the standard library wherever reasonable.

### Tests

* **No network calls in tests** (direct or indirect).
* Tests must be deterministic and self-contained.

### Logging & sensitive data

* Logging must follow OS conventions (console and/or log files).
* Logging must be configurable (level, size, rotation).
* Logs are intended to be **copy-pasteable diagnostics for users**.
* Never log:

  * environment variable values
  * credentials, tokens, cookies
  * file contents
  * full command lines that may contain secrets
* Paths and filenames are generally acceptable.

---

## 4) Canonical traversal model (must not drift)

All outputs must follow this pipeline, in order:

1. Enumerate filesystem entries from `--directory`
2. Apply built-in default ignores (unless disabled)
3. Apply `.p2mignore` rules (if enabled)
4. Apply CLI `--ignore` regex exclusions
5. Apply CLI `--filter` regex (include-only spotlight)
6. Build a logical tree (retain ancestors of matching nodes)
7. Render to selected output format

Precedence order is stable and intentional:
**defaults → `.p2mignore` → `--ignore` → `--filter` → render**

---

## 5) Determinism & ordering

* Output should be **deterministic by default**.
* File and directory ordering should be explicit and stable.
* Platform differences (Windows vs POSIX) must be handled intentionally.
* Any nondeterminism must be:

  * documented, or
  * behind an explicit flag.

---

## 6) Definition of done

A task is “done” when:

* The objective is implemented and functional.
* Documentation is updated if user-visible behavior changed.
* `ruff`, `black`, and `mypy` pass.
* All unit tests pass.
* Coverage **does not regress**.

### Coverage policy

* Target: **≥87% overall**
* Priority is **meaningful behavior coverage**, not line padding.
* Early scaffolding may fall short temporarily if:

  * core modules are tested (ignore, filter, tree build)
  * a follow-up task is noted to raise coverage

---

## 7) Expected repository structure

The repo currently contains only `SPECS.md`. Default to this layout unless approved otherwise:

* `src/path2map/` — core library
* `src/path2map/cli.py` — CLI entrypoint
* `src/path2map/traversal.py` — directory walking, depth, symlinks
* `src/path2map/ignore.py` — default ignores + `.p2mignore` + regex ignore
* `src/path2map/filtering.py` — regex filter logic + ancestor retention
* `src/path2map/model.py` — tree/node data structures
* `src/path2map/render/` — format renderers (text/md/json/csv/html)
* `tests/` — unit tests mirroring module layout
* `docs/` — user documentation (if needed)
* `pyproject.toml` — tooling config

If deviation from this layout is needed, propose it first.

---

## 8) Canonical commands

Once tooling exists, standardize on:

### Setup

```bash
py -3.12 -m venv .venv
. .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### Format

```bash
python -m black .
```

### Lint

```bash
python -m ruff check .
```

### Type-check

```bash
python -m mypy src
```

### Tests + coverage

```bash
python -m pytest
python -m pytest --cov=path2map --cov-report=term-missing
```

### Run

```bash
python -m path2map --help
```

---

## 9) CLI & output stability rules

* Do **not** rename CLI flags, change defaults, or alter output structure without approval.
* JSON/CSV schema changes are compatibility changes and must be documented.
* Text/Markdown output changes should preserve structure unless explicitly requested.

---

## 10) Documentation & API standards

* Docstrings are **required** for any externally callable interface:

  * CLI entrypoints
  * public functions/classes
* Type hints are expected throughout core logic.
* Docs must be updated when behavior, flags, formats, or defaults change.

---

## 11) Testing priorities

Focus tests on:

* ignore/filter precedence
* depth limiting (`--max-depth`, including `0`)
* symlink behavior (show vs follow, cycle safety)
* deterministic output across formats
* metadata opt-in behavior (no `stat()` unless requested)

Use stdlib helpers (`tempfile`, `pathlib`) for filesystem tests.

---

## 12) Performance posture

* Avoid premature optimization.
* Do not `stat()` files unless metadata is requested.
* Never read file contents.
* Prefer streaming or incremental rendering for large trees where practical.

---

## 13) Agent communication expectations

For each task or PR, include:

* what changed and why
* how to run tests
* examples (before/after) if output changed
* known limitations or follow-ups

---

## 14) When to ask the human

Ask for clarification when:

* behavior affects UX, defaults, or compatibility
* adding dependencies
* platform differences are unclear
* security/logging boundaries may be crossed

If ambiguity is **low-impact**, choose the simplest reasonable behavior and **document it**.

---

## 15) Reference

* `SPECS.md` — authoritative specification
