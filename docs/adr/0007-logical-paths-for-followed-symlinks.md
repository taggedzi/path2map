# ADR-0007: Preserve logical paths when following directory symlinks

## Status
Accepted

## Context
Resolving a directory symlink changes the physical directory being scanned.
Deriving descendant paths from that directory loses the alias prefix for internal
targets and fails for targets outside the scan root.

## Decision
Track the logical relative directory separately from the physical scan directory.
Build output paths from logical parent paths and entry names. Use physical paths
for filesystem access and directory identities for branch-local cycle detection.
Each alias retains its own subtree, including when another alias or the real
directory points to the same target. Depth, ignores, and filters use logical paths.

## Consequences
Internal and external directory targets render beneath their aliases across all
formats. Show/skip defaults, ordering, ignore precedence, and output schemas stay
the same. Following a link can still enumerate files outside the scan root, as
explicitly requested by follow mode.
