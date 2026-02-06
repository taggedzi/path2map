# ADR-0001: Core traversal and ignore precedence model

## Status
Accepted

## Context
path2map is designed to produce consistent, deterministic representations of
filesystem directory trees for both human and machine consumption.

Early design discussions identified a high risk of ambiguity and drift if
ignore rules, filters, and traversal behavior were allowed to vary by output
format or implementation detail.

Users must be able to reason about:
- *why* a file appears or does not appear
- *which* ignore rule excluded it
- *how* filters interact with traversal depth and hierarchy

To achieve this, traversal behavior must be explicit, ordered, and shared
across all output formats.

## Decision
path2map uses a **single, canonical traversal pipeline** that is applied
identically for all output formats:

1. Enumerate filesystem entries from the root directory
2. Apply built-in default ignores (unless explicitly disabled)
3. Apply `.p2mignore` rules (if enabled)
4. Apply CLI `--ignore` regex exclusions
5. Apply CLI `--filter` regex inclusion (spotlight behavior)
6. Build a logical tree that preserves ancestors of matching nodes
7. Render the resulting tree into the requested output format

This precedence order is fixed and intentional.

Traversal, ignore evaluation, filtering, and tree construction must be
completed **before** any rendering logic is applied.

Renderers must operate only on the finalized tree model and must not perform
additional filtering or traversal.

## Alternatives considered

### Output-specific traversal logic
Rejected.
This leads to inconsistent behavior between formats and makes reasoning
about output difficult or impossible.

### Filter-first traversal
Rejected.
Filtering before ignore evaluation complicates precedence rules and produces
counterintuitive results when combined with depth limits and ignore files.

### Renderer-driven filtering
Rejected.
Renderers must be pure consumers of the tree model to guarantee consistency
and testability.

## Consequences

### Positive
- Predictable and explainable output
- Consistent behavior across all formats
- Clear testing boundaries
- Reduced long-term maintenance complexity

### Tradeoffs
- Slightly more upfront architectural discipline
- Some features (e.g. renderer-specific shortcuts) are intentionally disallowed

## Notes
This ADR is foundational. Any future feature that affects traversal, ignore
logic, filtering, or tree construction must preserve this model or explicitly
supersede this ADR with a new one.
