# ADR-0004: Logging posture and redaction guarantees

## Status
Accepted

## Context
path2map is intended to be a reliable CLI utility used in a wide range of
environments, including personal machines, shared systems, and potentially
security-sensitive contexts.

Logs are primarily intended to help users:
- diagnose failures or unexpected behavior
- provide actionable information when reporting issues to developers
- understand what the tool attempted to do and where it failed

However, logging can easily become a liability if it exposes sensitive data,
environment details, or implementation internals that users did not intend
to disclose.

A clear logging posture is required to balance usefulness, safety, and trust.

## Decision
path2map adopts a **safe-by-default logging posture** with explicit redaction
guarantees.

### Logging goals
- Provide clear, actionable diagnostic information
- Support copy-paste sharing of logs for troubleshooting
- Avoid overwhelming users with unnecessary detail by default

### Logging guarantees
path2map logging must:

- Never log:
  - environment variable values
  - credentials, tokens, keys, cookies, or secrets
  - file contents
  - user-provided input that may contain secrets unless explicitly sanitized
- Avoid logging full command lines when they may include sensitive data
- Prefer structured, contextual messages over raw data dumps

Paths and filenames are generally acceptable, but should be logged at an
appropriate level and with care.

### Configuration
Logging must be:
- configurable by level (e.g. INFO, DEBUG)
- configurable by output (console and/or file)
- configurable with size limits and rotation

Sensitive logging (e.g. verbose debugging) must be opt-in and clearly labeled.

## Alternatives considered

### Verbose logging by default
Rejected.
This increases the risk of accidental data exposure and reduces signal quality.

### Minimal or silent logging
Rejected.
Users need meaningful diagnostics when things go wrong.

### Redaction handled informally or case-by-case
Rejected.
Redaction must be intentional and systematic to be reliable.

## Consequences

### Positive
- Users can safely share logs without fear of leaking secrets
- Reduced security and privacy risk
- Clear expectations for contributors and agents
- Improved trust in the tool

### Tradeoffs
- Additional care required when adding new log statements
- Some debugging scenarios may require explicit opt-in verbosity

## Notes
Logging behavior is part of the public contract of the tool.

Any feature that introduces new logging behavior or touches user-provided
inputs must respect this ADR or explicitly propose a change via a new ADR.
