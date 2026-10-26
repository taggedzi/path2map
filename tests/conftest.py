"""Shared fixtures for filesystem capabilities."""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def directory_symlink() -> Callable[[Path, Path], None]:
    """Create a directory symlink, skipping when Windows denies the privilege."""

    def create(link: Path, target: Path) -> None:
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            if getattr(exc, "winerror", None) == 1314:
                pytest.skip(
                    "Windows symlink creation privilege unavailable (WinError 1314)"
                )
            raise

    return create
