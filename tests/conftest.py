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


@pytest.fixture(params=["native", "simulated"])
def followed_directory_link(request, directory_symlink, monkeypatch):
    """Exercise real links and a privilege-independent scandir/resolve simulation."""
    if request.param == "native":
        return directory_symlink

    from path2map import traversal

    targets: dict[Path, Path] = {}
    original_iter = traversal._iter_entries
    original_resolve = Path.resolve
    original_readlink = traversal.os.readlink

    class LinkEntry:
        def __init__(self, entry):
            self.entry = entry

        def __getattr__(self, name):
            return getattr(self.entry, name)

        def is_symlink(self):
            return True

        def is_dir(self, *, follow_symlinks=True):
            return follow_symlinks

    def iter_entries(directory, sort_key):
        for entry in original_iter(directory, sort_key):
            yield LinkEntry(entry) if Path(entry.path) in targets else entry

    def resolve(path, *args, **kwargs):
        return original_resolve(targets.get(path, path), *args, **kwargs)

    def readlink(path, *args, **kwargs):
        if Path(path) in targets:
            return str(targets[Path(path)])
        return original_readlink(path, *args, **kwargs)

    def create(link: Path, target: Path) -> None:
        link.mkdir()
        targets[link] = target

    monkeypatch.setattr(traversal, "_iter_entries", iter_entries)
    monkeypatch.setattr(Path, "resolve", resolve)
    monkeypatch.setattr(traversal.os, "readlink", readlink)
    return create
