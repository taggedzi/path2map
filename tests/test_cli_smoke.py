"""Smoke tests for the minimal CLI stub."""

from __future__ import annotations

import pytest

from path2map import cli


def test_cli_smoke() -> None:
    """CLI imports and exits successfully for help output."""
    assert cli.main([]) == 0

    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--help"])

    assert exc_info.value.code == 0
