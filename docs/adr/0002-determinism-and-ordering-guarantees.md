# ADR-0002: Determinism and ordering guarantees

## Status
Accepted

## Context
path2map is intended to generate directory structure representations that are
useful for both humans and machines. Many intended use cases involve:

- version control diffs
- automation and scripting
- reproducible analysis
- comparison across machines or points in time

Filesystem enumeration order is inherently platform- and filesystem-dependent.
Without explicit guarantees, identical invocations of path2map may produce
different outputs, leading to noisy diffs, brittle automation, and user
confusion.

To maintain trust in the tool’s output, determinism must be an intentional
design property rather than an incidental side effect.

## Decision
path2map guarantees **deterministic output by default**, subject to the
following rules:

- Directory entries are ordered explicitly and consistently.
- Rendering order is derived solely from the constructed tree model.
- Output ordering does not depend on underlying filesystem enumeration order.

Any behavior that may introduce nondeterminism must be:
- documented clearly, and/or
- placed behind an explicit user-controlled option.

Determinism applies across:
- all supported output formats
- repeated runs on the same filesystem state
- supported platforms (Windows, Linux, macOS), within practical limits

## Ordering rules
Unless explicitly overridden or extended by a documented option:

- Directories and files are sorted in a stable, predictable order.
- Ordering logic must be centralized (not duplicated in renderers).
- Case sensitivity handling must be explicit and consistent.
- Renderer implementations must not reorder nodes.

The exact sorting strategy (e.g., lexicographic, case-folded) must be applied
uniformly across the entire tree.

## Alternatives considered

### Rely on filesystem enumeration order
Rejected.
Enumeration order varies across platforms, filesystems, and Python versions,
making output unpredictable and unsuitable for automation or comparison.

### Determinism only for machine-readable formats
Rejected.
Human-readable outputs benefit equally from stability and predictability.

### Per-renderer ordering logic
Rejected.
This increases drift risk and undermines consistency guarantees.

## Consequences

### Positive
- Stable, diff-friendly output
- Predictable automation behavior
- Simplified testing and reasoning
- Clear separation between traversal/model and rendering

### Tradeoffs
- Slight performance cost due to explicit sorting
- Reduced flexibility for renderer-specific ordering optimizations

## Notes
Determinism is a core usability feature, not an implementation detail.

If future features require nondeterministic behavior (e.g. parallel traversal,
streaming optimizations), they must either preserve deterministic output or be
explicitly opt-in and documented.
