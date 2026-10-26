# ADR-0005: Publish releases through GitHub only

## Status
Accepted

## Context
The release workflow included optional PyPI publishing, but publishing was not
configured. Its job-level secret condition also prevented workflow validation.
The maintainer requested removal of the PyPI publishing system.

## Decision
Publish release artifacts through GitHub Releases only. Remove the PyPI job and
its variable, secret, and environment setup instructions. Keep building and
validating the source distribution and wheel for GitHub release downloads.

## Consequences
Release automation no longer requires PyPI credentials or configuration.
Publishing to a package index would require a separate future decision.
