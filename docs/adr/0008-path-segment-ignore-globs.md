# ADR-0008: Match ignore globs by path segment

## Status
Accepted

## Context

SPECS.md promises gitignore-style globs. Whole-path `fnmatch` lets ordinary
wildcards cross directory boundaries, while literal prefix checks miss wildcard
directory rules. These errors affect every export through the shared pipeline.

## Decision

Match each path component with stdlib `fnmatch`. Patterns with a leading slash
or an interior slash match from the scan root; other patterns match names at
any depth. A whole `**` component consumes zero or more components, except that
trailing `/**` requires contents below the preceding directory.

Evaluate matches against directory ancestors as well as the entry itself.
A trailing slash requires a directory, so an exact regular-file match does not
qualify. Track reachable component positions iteratively to avoid recursive
backtracking and recursion depth limits.

Preserve ordered negation, existing case handling, and the hard-exclusion
precedence in ADR-0001. This correction changes glob selection, not traversal
or export schemas. It adds no dependency, consistent with ADR-0003.

## Consequences

The documented segment, anchoring, and directory rules work consistently across
all formats. Users relying on the old accidental matches may see changed trees.
This is a focused matcher correction; it does not expand ignore-file parsing
to implement every Git escape or whitespace rule.
