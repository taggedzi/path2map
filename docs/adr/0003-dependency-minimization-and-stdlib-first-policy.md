# ADR-0003: Dependency minimization and stdlib-first policy

## Status
Accepted

## Context
path2map is intended to be a small, reliable, long-lived utility that operates
on local filesystems and is frequently used in constrained or security-sensitive
environments.

Every third-party dependency introduces:
- additional attack surface
- licensing considerations
- supply-chain risk
- maintenance and compatibility overhead

Many core features of path2map (filesystem traversal, regex matching, ignore
rules, formatting, and serialization) are well supported by Python’s standard
library.

To preserve security, portability, and ease of maintenance, dependency usage
must be intentional rather than opportunistic.

## Decision
path2map follows a **stdlib-first dependency policy**.

- The Python standard library is preferred for all functionality where it is
  reasonably sufficient.
- New third-party dependencies are not added by default.
- Any proposed dependency must be explicitly reviewed and approved before use.

Approval requires documenting:
- the dependency’s license
- why the standard library is insufficient
- expected maintenance and security impact
- the scope of usage within the project

This policy applies to both runtime and development dependencies.

## Alternatives considered

### Freely adding dependencies for convenience
Rejected.
Convenience alone does not justify increased risk and maintenance burden.

### Vendoring third-party code
Rejected.
Vendored code still carries maintenance and security obligations while reducing
visibility into updates and vulnerabilities.

### Allowing dependencies only for development tooling
Partially accepted.
Development dependencies (linting, formatting, testing) are allowed but must be
kept minimal and well-maintained.

## Consequences

### Positive
- Smaller attack surface
- Fewer licensing concerns
- Easier auditing and long-term maintenance
- Improved portability across environments

### Tradeoffs
- Some features may require more custom implementation
- Development effort may be slightly higher for certain capabilities
- Some popular convenience libraries may be intentionally excluded

## Notes
This policy does not prohibit future dependency usage.

If a dependency provides clear, material benefit that cannot be reasonably
achieved with the standard library, it may be introduced with explicit approval
and documentation.

This ADR is intended to prevent
