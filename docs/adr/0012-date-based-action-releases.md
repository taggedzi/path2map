# ADR-0012: Cut date-based releases from a manual workflow

## Status
Accepted

## Context
Releases used `MAJOR.MINOR.PATCH` and started when a maintainer pushed a
`vX.Y.Z` tag. Version bumps, changelog edits, packaging checks, and publishing
were split across local steps and that tag-triggered workflow.

## Decision
Number releases by UTC date: `YYYY.MM.DD`. A later release on the same date
uses `YYYY.MM.DD.N` with `N` starting at 1. Tag them `vYYYY.MM.DD`. Dots keep
the number valid as a Python package version.

Publish only by running the `Release` workflow (`workflow_dispatch`) from the
Actions tab. The workflow assigns the version, updates the changelog and
version files, runs the same quality checks as CI, builds the sdist and wheel,
pushes the version commit to the selected branch, and creates the GitHub
Release with those artifacts attached.

Keep publishing on GitHub Releases only (ADR-0005). A pushed tag does not
start a release.

## Consequences
Maintainers start a release from Actions. The selected branch must accept
pushes from `github-actions[bot]`. Release numbers no longer encode breaking
changes; the changelog records those. A failed run that has not created the
tag can be started again for the same version. A run that already created the
tag allocates the next same-day number.
