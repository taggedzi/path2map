# ADR-0009: Select directories before rendering

## Status

Accepted

## Context

Directory-only selection lived in the text and HTML renderers, so JSON and CSV
still emitted files. ADR-0001 requires all formats to consume the same selection.

## Decision

Apply `folders_only` in the shared pipeline after regex filtering retains
ancestors and before constructing the tree. Keep only directory entries and
always retain the root. A file match can therefore retain its ancestor directories
without emitting the file. Ignore precedence and deterministic order are unchanged.

Keep existing text/HTML renderer options for direct library callers and for
disabling comments. The CLI's finalized tree already contains only directories.

## Consequences

All CLI formats share directory-only selection, including empty directories.
JSON keys and CSV columns remain compatible. Unflagged output is unchanged.
This implements ADR-0001's shared selection rule without moving format-specific
presentation into the pipeline or adding dependencies.
