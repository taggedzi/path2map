# path2map Implementation TODO (Prompt-Driven)

This file turns `SPECS.md` into a step-by-step execution plan with copy/paste prompts for Codex.

## Better Way (Recommended)
Instead of one large build, use **small vertical slices** with strict acceptance gates:
1. Implement one slice.
2. Add/adjust tests for that slice.
3. Run `black`, `ruff`, `mypy`, `pytest`.
4. Commit only that slice.

This reduces regressions and keeps behavior aligned with `SPECS.md` + ADR constraints.

## Global Rules For Every Step
- Follow `SPECS.md` as source of truth.
- Respect precedence pipeline exactly: defaults -> `.p2mignore` -> `--ignore` -> `--filter` -> render.
- No runtime dependencies unless explicitly approved.
- Use `.venv` for Python commands:
  - `source .venv/bin/activate`
- Python compatibility: 3.10+
- No filesystem mutation features.
- No file-content reads for scanning.
- No implicit metadata/stat cost unless metadata is requested.
- Keep output deterministic.

## Definition of Done For Each Step
- Targeted tests added/updated and passing.
- Existing tests still pass.
- `python -m black .`
- `python -m ruff check .`
- `python -m mypy src`
- `python -m pytest --cov=path2map --cov-report=term-missing`

## Prompt Template
Use this structure for each step:

```text
Implement TODO Step <N> from TODO.md only.
Scope strictly to that step.
Follow AGENTS.md, ADRs, and SPECS.md.
Use .venv. Run black, ruff, mypy, pytest at the end.
If blocked by ambiguity that affects compatibility/UX/defaults, stop and ask.
Then provide:
1) what changed,
2) tests added/updated,
3) command results summary,
4) exact commit message suggestion.
```

---

## Step 0: Baseline Guardrails and Repo Hygiene
**Goal**: Ensure clean starting point and test/tooling baseline.

**Prompt**
```text
Implement TODO Step 0 from TODO.md only.
- Verify worktree status and report if dirty.
- Ensure `.gitignore` excludes caches/artifacts (e.g., `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.coverage`).
- Verify current scaffold still passes smoke test.
- Do not add product functionality yet.
```

**Acceptance**
- Worktree sanity confirmed.
- Tooling/test baseline is green.

---

## Step 1: CLI Argument Surface (Parsing Only)
**Goal**: Define full CLI options from spec, no business logic yet.

**Prompt**
```text
Implement TODO Step 1 from TODO.md only.
Add full argparse flag surface in `src/path2map/cli.py` matching `SPECS.md`:
- directory/input, output, stdout
- max-depth
- follow-symlinks and/or symlinks mode handling per spec
- ignore/filter
- folders-only, sort, comments, emojis
- color, theme
- details, time-format, size-format, details-style
- type, version, help
Do not implement traversal/render behavior yet.
Add parser-focused unit tests for defaults and flag parsing.
```

**Acceptance**
- Parsing succeeds for all documented flags.
- No traversal/output logic added yet.

---

## Step 2: Core Data Model
**Goal**: Create canonical tree/node model used by all renderers.

**Prompt**
```text
Implement TODO Step 2 from TODO.md only.
Create `src/path2map/model.py` with typed structures for nodes and tree metadata.
Include fields required by all outputs: path, name, type, depth, ext, children, optional size/mtime, and symlink markers.
Keep model minimal and deterministic.
Add focused model tests.
```

**Acceptance**
- Single canonical model exists and is tested.

---

## Step 3: Traversal Engine (No Ignore/Filter Yet)
**Goal**: Deterministic filesystem enumeration with depth and symlink handling.

**Prompt**
```text
Implement TODO Step 3 from TODO.md only.
Create `src/path2map/traversal.py` for directory enumeration:
- root from `--directory`
- deterministic ordering hooks
- max-depth semantics including 0
- symlink behavior (default show-not-follow)
- optional follow with cycle safety
No ignore/filter logic yet.
Add traversal unit tests using tempfile/pathlib.
```

**Acceptance**
- Depth + symlink behavior validated.
- No infinite recursion on cycles.

---

## Step 4: Ignore Pipeline (Defaults + .p2mignore + CLI Ignore)
**Goal**: Implement exclusion stages 2–4 exactly.

**Prompt**
```text
Implement TODO Step 4 from TODO.md only.
Create `src/path2map/ignore.py` implementing:
1) built-in default ignores (toggleable),
2) `.p2mignore` parsing (single root file),
3) CLI `--ignore` regex hard exclusion.
Ensure stage precedence matches spec.
Add tests for precedence, negation behavior in `.p2mignore`, and full-relative-path regex behavior.
```

**Acceptance**
- Default ignores and `.p2mignore` behavior deterministic.
- CLI `--ignore` is hard exclusion.

---

## Step 5: Include Filter + Ancestor Retention
**Goal**: Implement stage 5 and stage 6 tree retention behavior.

**Prompt**
```text
Implement TODO Step 5 from TODO.md only.
Create `src/path2map/filtering.py`:
- apply `--filter` regex include-only logic after ignore stages,
- support multiple filters with OR logic,
- retain ancestors of matched descendants.
Add tests proving filter order and ancestor preservation.
```

**Acceptance**
- Filter runs after ignore stages.
- Ancestor context always preserved for matches.

---

## Step 6: Tree Builder Integration
**Goal**: Integrate traversal + ignore + filter into one canonical pipeline.

**Prompt**
```text
Implement TODO Step 6 from TODO.md only.
Wire pipeline in one orchestration path used by CLI:
Enumerate -> defaults -> .p2mignore -> --ignore -> --filter -> logical tree.
Ensure all later renderers consume this same tree.
Add integration tests for full precedence table.
```

**Acceptance**
- Single pipeline path used consistently.

---

## Step 7: Text Renderer (Default Output)
**Goal**: Implement default human-readable text tree.

**Prompt**
```text
Implement TODO Step 7 from TODO.md only.
Create `src/path2map/render/text.py` and wire `--type text` default.
Support folders-only, sorting (folders first), comments, emojis.
Respect details toggles without forcing stat when details are off.
Add renderer tests with fixed expected output snapshots/strings.
```

**Acceptance**
- Deterministic text output.
- Feature flags affect rendering only (not selection semantics).

---

## Step 8: Markdown Renderer
**Goal**: Add markdown output.

**Prompt**
```text
Implement TODO Step 8 from TODO.md only.
Add `src/path2map/render/markdown.py` for `--type md`.
Wrap tree in fenced code block and keep structure equivalent to text renderer.
Add tests confirming markdown wrapper + consistent core tree content.
```

**Acceptance**
- MD output consistent with text tree semantics.

---

## Step 9: JSON and CSV Renderers
**Goal**: Add machine-consumable formats from same tree.

**Prompt**
```text
Implement TODO Step 9 from TODO.md only.
Add `src/path2map/render/json.py` and `src/path2map/render/csv.py`.
JSON: hierarchical tree, include metadata fields only when requested.
CSV: flat rows with columns path,name,type,ext,depth,size,mtime.
No schema drift from spec.
Add tests for schema and determinism.
```

**Acceptance**
- JSON/CSV generated from canonical tree.
- Stable field presence/order and deterministic rows.

---

## Step 10: HTML Renderer
**Goal**: Add shareable HTML output.

**Prompt**
```text
Implement TODO Step 10 from TODO.md only.
Add `src/path2map/render/html.py` with minimal CSS and optional JS for collapsible tree.
Keep semantics identical to other renderers.
Add tests for structure sanity and deterministic generation.
```

**Acceptance**
- HTML renderer exists and is deterministic.

---

## Step 11: Color + Details Formatting
**Goal**: Add optional color and metadata formatting behavior.

**Prompt**
```text
Implement TODO Step 11 from TODO.md only.
Implement color policy: auto|always|never (TTY-aware for auto).
Apply extension group coloring per spec where relevant.
Implement details formatting:
- details: none|size|mtime|size,mtime
- time format
- size format binary|decimal
- details-style inline|columns
Ensure no metadata stat calls unless details requested.
Add tests for formatting and stat opt-in behavior.
```

**Acceptance**
- Color rules and metadata formatting behave as specified.
- No implicit metadata cost.

---

## Step 12: Output Routing and File Export
**Goal**: Implement stdout/file writing behavior.

**Prompt**
```text
Implement TODO Step 12 from TODO.md only.
Implement `--stdout`, `--output`, and output-path directory handling with timestamped filenames:
`path2map_YYYY-MM-DD_HHMMSS.ext`
Map extension by `--type`.
Add tests for routing decisions and filename generation.
```

**Acceptance**
- Correct routing and deterministic filename format.

---

## Step 13: Final CLI Integration + End-to-End Tests + Docs Sync
**Goal**: Ship cohesive v1 behavior.

**Prompt**
```text
Implement TODO Step 13 from TODO.md only.
Finalize CLI execution flow in `src/path2map/cli.py`:
- parse args
- run canonical pipeline
- render selected format
- route output
Add end-to-end tests covering:
- precedence chain
- max-depth=0
- symlink cycle safety
- deterministic outputs across text/md/json/csv/html
- metadata opt-in
Update README usage examples to match implemented behavior.
Do not add features outside SPECS.
```

**Acceptance**
- End-to-end flows pass.
- Docs align with behavior.
- Coverage is >=87% overall.

---

## Decision Gates (Ask Before Proceeding)
Use a clarification prompt before implementation if any of these remain ambiguous:
1. `Resolved`: expose both `--follow-symlinks` and `--symlinks` in v1.
2. Exact JSON schema details (field naming, root wrapper) before locking tests.
3. Exact CSV row ordering when sorting is disabled (recommended: still deterministic by default).
4. HTML collapsible behavior scope (pure CSS vs minimal JS).

## Suggested Commit Cadence
- One commit per TODO step.
- Commit message style:
  - `step-<N>: <concise behavior>`
  - Example: `step-5: add filter stage with ancestor retention`

---

## Release Readiness Track (GitHub + Packaging)

Use these after core implementation is stable and tests are green.

## Step 14: Public Repo Baseline and Metadata Audit
**Goal**: Ensure repository metadata and top-level docs are complete for public use.

**Prompt**
```text
Implement TODO Step 14 from TODO.md only.
Audit and tighten top-level project docs/metadata:
- README quick start accuracy
- CHANGELOG presence/version alignment
- CONTRIBUTING, CODE_OF_CONDUCT, SECURITY completeness
- LICENSE presence and consistency
- pyproject metadata completeness (description/readme/requires-python/classifiers/urls)
Update only gaps needed for first public release.
```

**Acceptance**
- Top-level docs and package metadata are complete and internally consistent.

---

## Step 15: Packaging Validation (sdist/wheel + install smoke test)
**Goal**: Prove the package can be built and installed cleanly.

**Prompt**
```text
Implement TODO Step 15 from TODO.md only.
Add/verify packaging workflow:
- Build source + wheel artifacts
- Validate package metadata
- Perform a clean install smoke test from built wheel
- Verify CLI entrypoint works after install
Document exact local commands in README or CONTRIBUTING.
Do not publish anything yet.
```

**Acceptance**
- `sdist` and `wheel` build successfully.
- Install smoke test passes from built artifact.

---

## Step 16: CI Automation (Quality Gates)
**Goal**: Add GitHub Actions checks that enforce quality on every PR.

**Prompt**
```text
Implement TODO Step 16 from TODO.md only.
Create CI workflow(s) for pull requests and main branch:
- Python setup
- install with dev dependencies
- black --check
- ruff check
- mypy src
- pytest with coverage output
Fail fast on check failures and keep workflow logs readable.
```

**Acceptance**
- CI runs automatically for PRs and pushes.
- Lint/type/test gates block regressions.

---

## Step 17: Release Automation (Tag/Publish Preparation)
**Goal**: Define a safe, repeatable release path.

**Prompt**
```text
Implement TODO Step 17 from TODO.md only.
Set up release automation strategy (without forcing an immediate publish):
- tag-driven release workflow
- build artifacts in CI for tags
- optional publish job guarded by secrets/environment approval
- attach artifacts to GitHub Release
Document release steps for maintainers.
```

**Acceptance**
- Maintainer can cut a release from a tag with minimal manual steps.
- Publishing path is explicit and guarded.

---

## Step 18: Versioning and Compatibility Policy
**Goal**: Make version bumps and compatibility expectations explicit.

**Prompt**
```text
Implement TODO Step 18 from TODO.md only.
Document project versioning policy:
- SemVer interpretation for this CLI/package
- what counts as breaking change (CLI flags, JSON/CSV schema, defaults)
- release checklist including CHANGELOG updates
Add short policy section in docs and link from README.
```

**Acceptance**
- Contributors have clear rules for version bumps and compatibility.

---

## Step 19: Issue/PR Templates and GitHub Governance
**Goal**: Improve signal quality and triage consistency on public issues/PRs.

**Prompt**
```text
Implement TODO Step 19 from TODO.md only.
Add GitHub community health templates/config:
- bug report template
- feature request template
- pull request template
- optional issue config for support/usage redirection
Keep templates concise and actionable.
```

**Acceptance**
- New issues/PRs use structured templates with required context.

---

## Step 20: Final Public Release Dry Run
**Goal**: Perform one end-to-end dry run before public announcement.

**Prompt**
```text
Implement TODO Step 20 from TODO.md only.
Run a final release-candidate dry run:
- full local quality checks
- CI green on branch
- package build/install smoke test
- docs link check/manual sanity pass
- verify changelog/version/tag plan
Capture a short go/no-go checklist in docs or release notes draft.
```

**Acceptance**
- One documented dry run is completed with explicit go/no-go outcome.

---

## Step 21: CLI Argument Documentation and Help UX
**Goal**: Provide complete, user-friendly documentation for CLI arguments across help output and docs.

**Prompt**
```text
Implement TODO Step 21 from TODO.md only.
Improve CLI argument documentation in all high-value user touchpoints:
- Expand argparse help text for each flag with clear behavior descriptions
- Add practical examples in `--help` epilog/usage where appropriate
- Ensure defaults and accepted values are visible in help output
- Update README and/or docs with a dedicated CLI arguments reference table
- Include example commands for common workflows and combinations
Keep behavior unchanged; this step is documentation/UX only.
```

**Acceptance**
- `python -m path2map --help` shows clear descriptions for all primary flags.
- Docs include argument descriptions, defaults, and concrete usage examples.
- No CLI behavior or output semantics change.

---

## Step 22: End-to-End Sample Catalog (Docs + Outputs)
**Goal**: Provide a committed sample workspace that demonstrates all core CLI output types and feature combinations.

**Prompt**
```text
Implement TODO Step 22 from TODO.md only.
Create and complete a sample catalog under docs:
- Use `docs/samples/input/` for fixture tree(s)
- Use `docs/samples/output/` for generated example outputs
- Maintain `docs/samples/commands.sh` as the canonical generator script
- Ensure at least one command demonstrates each output type (`text`, `md`, `json`, `csv`, `html`)
- Include examples covering depth, ignore/filter, folders-only, sorting, comments, emojis, details formatting, and symlink flags
Document how to regenerate samples and when to refresh them after behavior changes.
```

**Acceptance**
- `docs/samples/README.md` explains purpose and regeneration workflow.
- `docs/samples/commands.sh` runs successfully in `.venv`.
- Output examples are present and linkable from README/docs.
