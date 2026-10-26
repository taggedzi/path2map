# ADR-0006: Pin GitHub Actions to full commit SHAs

## Status
Accepted

## Context
Repository Actions policy requires full commit SHAs and permits GitHub-created
actions plus the explicitly allowed `softprops/action-gh-release` action.
Version-tag references prevent CI and release workflows from starting.

## Decision
Pin every external action in CI and release workflows to a verified full commit
SHA. Keep the corresponding major version in a comment for readability.
Resolve pins from the existing major version tags without changing major versions.

## Consequences
Workflow action code stays fixed until its pin is deliberately updated.
Action updates require verifying and replacing the commit SHA.
