# ADR-0011: Validate scan roots before depth limiting

## Status
Accepted

## Context
The depth-zero shortcut could construct a successful directory map for a missing
path or a regular file. Automation needs to distinguish these errors from a valid
root-only scan.

## Decision
Validate the resolved root with a root stat before the depth-zero return at the
shared traversal entry point. Preserve filesystem exceptions for library callers;
the CLI reports missing/non-directory errors on stderr and returns status 1 before
rendering or routing output. Root links resolving to directories remain valid.

## Consequences
Every depth uses the same root validation. Depth zero adds a root stat but never
enumerates descendants or collects file metadata. This root identity check is
separate from opt-in file metadata. Schemas, flags, defaults, and ignore/filter
precedence are unchanged. Validation cannot prevent later filesystem races.
