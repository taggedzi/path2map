# ADR-0010: Resolve automatic color per output destination

## Status

Accepted

## Context

The CLI reused one rendering for stdout and file exports. With a terminal
attached, automatic ANSI colors leaked into text and Markdown files, contrary
to SPECS.md section 6.

## Decision

For text and Markdown exports, render files with color disabled when the policy
is `auto`. When `--stdout` is also requested, retain the TTY-aware stdout
rendering. Output routing accepts optional separate stdout content; callers
that provide a single rendering keep their existing behavior.

Preserve `always` and `never` for both destinations. Color remains a rendering
concern; traversal and tree selection are unchanged.

## Consequences

Interactive exports are plain by default, including timestamped directory
exports. Combined automatic output can require two renderings of the same tree,
without repeating traversal or metadata collection. No dependencies or output
schemas change.
