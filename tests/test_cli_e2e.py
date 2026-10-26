"""End-to-end CLI tests for canonical behavior."""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

import pytest

from path2map import cli


class _NodeLabels(HTMLParser):
    """Extract node labels without including document styles or titles."""

    def __init__(self):
        super().__init__()
        self.labels = []
        self.in_node = False

    def handle_starttag(self, tag, attrs):
        self.in_node = dict(attrs).get("class") == "node"

    def handle_endtag(self, tag):
        self.in_node = False

    def handle_data(self, data):
        if self.in_node:
            self.labels.append(data)


def _exported_names(output, output_type):
    if output_type == "json":

        def names(node):
            return [node["name"]] + [
                name for child in node["children"] for name in names(child)
            ]

        return names(json.loads(output))
    if output_type == "csv":
        return [row["name"] for row in csv.DictReader(io.StringIO(output))]
    if output_type == "html":
        parser = _NodeLabels()
        parser.feed(output)
        labels = parser.labels
    else:
        labels = [line for line in output.splitlines() if not line.startswith("```")]
    return [
        re.sub(r"\s+(?:\(.*|\[Empty folder\]).*$", "", label.lstrip(" │├└─📁📄"))
        for label in labels
    ]


@pytest.mark.parametrize("output_type", ["text", "md", "json", "csv", "html"])
@pytest.mark.parametrize("folders_only", [False, True])
@pytest.mark.parametrize(
    "presentation", [[], ["--comments", "--emojis", "--details", "size,mtime"]]
)
def test_cli_folders_only_selected_nodes(
    tmp_path: Path, capsys, output_type, folders_only, presentation
) -> None:
    """All formats select identical nodes, including nested and empty directories."""
    (tmp_path / "branch" / "nested").mkdir(parents=True)
    (tmp_path / "empty").mkdir()
    (tmp_path / "root.txt").touch()
    (tmp_path / "branch" / "nested" / "leaf.py").touch()
    argv = [
        "--directory",
        str(tmp_path),
        "-t",
        output_type,
        "--color",
        "never",
        *presentation,
    ]
    if folders_only:
        argv.append("--folders-only")
    code, output = _run_cli_capture(capsys, argv)
    assert code == 0
    expected = [tmp_path.name, "branch", "nested", "empty"]
    if not folders_only:
        expected.insert(3, "leaf.py")
        expected.append("root.txt")
    assert _exported_names(output, output_type) == expected
    expected_paths = [".", "branch", "branch/nested", "empty"]
    if not folders_only:
        expected_paths.insert(3, "branch/nested/leaf.py")
        expected_paths.append("root.txt")
    if output_type == "json":

        def flatten(node):
            return [node] + [
                item for child in node["children"] for item in flatten(child)
            ]

        nodes = flatten(json.loads(output))
        keys = {"path", "name", "type", "ext", "depth", "children"}
        if presentation:
            keys.update({"size", "mtime"})
        assert all(set(node) == keys for node in nodes)
    elif output_type == "csv":
        reader = csv.DictReader(io.StringIO(output))
        assert reader.fieldnames == [
            "path",
            "name",
            "type",
            "ext",
            "depth",
            "size",
            "mtime",
        ]
        nodes = list(reader)
    if output_type in {"json", "csv"}:
        assert [node["path"] for node in nodes] == expected_paths
        assert [int(node["depth"]) for node in nodes] == [
            0 if path == "." else path.count("/") + 1 for path in expected_paths
        ]
    if folders_only:
        assert "Empty folder" not in output


def _run_cli_capture(capsys, argv: list[str]) -> tuple[int, str]:
    exit_code = cli.main(argv)
    output = capsys.readouterr().out
    return exit_code, output


@pytest.mark.parametrize("output_type", ["text", "md", "json", "csv", "html"])
def test_cli_ignore_globs_across_exports(tmp_path: Path, capsys, output_type) -> None:
    """Every export uses the same corrected glob selection."""
    for relative_path in (
        "src/cache/hidden-directory.txt",
        "a/cache/hidden-nested.txt",
        "src/hidden-direct.py",
        "src/nested/visible-nested.py",
        "secret.txt",
        "a/secret.txt",
        "cache",
    ):
        path = tmp_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    (tmp_path / ".p2mignore").write_text(
        "src/cache/\n**/cache/\n/cache/\nsrc/*.py\n**/secret.txt\n",
        encoding="utf-8",
    )

    code, output = _run_cli_capture(
        capsys, ["--directory", str(tmp_path), "-t", output_type]
    )

    assert code == 0
    assert "visible-nested.py" in output
    assert "cache" in output  # Root regular file survives directory-only rules.
    for excluded in (
        "hidden-directory",
        "hidden-nested",
        "hidden-direct",
        "secret.txt",
    ):
        assert excluded not in output


def test_cli_precedence_chain_e2e(tmp_path: Path, capsys) -> None:
    """defaults -> .p2mignore -> --ignore -> --filter is preserved end-to-end."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "keep.py").write_text("x", encoding="utf-8")
    (tmp_path / "src" / "drop.py").write_text("x", encoding="utf-8")

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "tool.py").write_text("x", encoding="utf-8")

    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "out.py").write_text("x", encoding="utf-8")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x", encoding="utf-8")

    (tmp_path / ".p2mignore").write_text(
        "src/*.py\n!src/keep.py\n!build/out.py\n",
        encoding="utf-8",
    )

    code, text = _run_cli_capture(
        capsys,
        [
            "--directory",
            str(tmp_path),
            "-i",
            r"^src/keep\.py$",
            "-F",
            r"\.py$",
            "-t",
            "text",
        ],
    )

    assert code == 0
    assert "tool.py" in text
    assert "keep.py" not in text
    assert "drop.py" not in text
    assert "out.py" not in text
    assert "config" not in text


def test_cli_max_depth_zero_e2e(tmp_path: Path, capsys) -> None:
    """max-depth=0 returns only root node in rendered output."""
    (tmp_path / "child.txt").write_text("x", encoding="utf-8")

    code, text = _run_cli_capture(
        capsys,
        ["--directory", str(tmp_path), "-D", "0", "-t", "text"],
    )

    assert code == 0
    lines = text.strip().splitlines()
    assert lines == [tmp_path.name]


def test_cli_follow_symlinks_cycle_safe_e2e(
    tmp_path: Path, capsys, directory_symlink
) -> None:
    """Following symlinks avoids infinite recursion in cycle cases."""
    real_dir = tmp_path / "dir"
    real_dir.mkdir()
    directory_symlink(real_dir / "loop", real_dir)

    code, text = _run_cli_capture(
        capsys,
        ["--directory", str(tmp_path), "--follow-symlinks", "-t", "text"],
    )

    assert code == 0
    assert text.count("loop") == 1


def test_cli_outputs_are_deterministic_across_formats(tmp_path: Path, capsys) -> None:
    """Repeated CLI runs over same tree produce identical output per format."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x", encoding="utf-8")
    (tmp_path / "README.md").write_text("x", encoding="utf-8")

    for output_type in ("text", "md", "json", "csv", "html"):
        code_a, out_a = _run_cli_capture(
            capsys,
            ["--directory", str(tmp_path), "-t", output_type],
        )
        code_b, out_b = _run_cli_capture(
            capsys,
            ["--directory", str(tmp_path), "-t", output_type],
        )

        assert code_a == 0
        assert code_b == 0
        assert out_a == out_b


def test_cli_metadata_opt_in_no_stat_when_disabled(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """No metadata stat helper is used when details=none."""
    (tmp_path / "file.txt").write_text("hello", encoding="utf-8")

    def _unexpected(*_args, **_kwargs):
        raise AssertionError("metadata helper should not be called")

    monkeypatch.setattr("path2map.traversal._entry_size", _unexpected)
    monkeypatch.setattr("path2map.traversal._entry_mtime", _unexpected)

    code, _ = _run_cli_capture(capsys, ["--directory", str(tmp_path), "-t", "text"])

    assert code == 0


def test_cli_metadata_opt_in_collects_when_enabled(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Metadata details mode enables size/mtime rendering."""
    (tmp_path / "file.txt").write_text("hello", encoding="utf-8")

    monkeypatch.setattr("path2map.traversal._entry_size", lambda _entry: 5)
    monkeypatch.setattr(
        "path2map.traversal._entry_mtime",
        lambda _entry: datetime(2026, 1, 2, 3, 4),
    )

    code, text = _run_cli_capture(
        capsys,
        [
            "--directory",
            str(tmp_path),
            "-t",
            "text",
            "--details",
            "size,mtime",
            "--time-format",
            "%Y-%m-%d",
        ],
    )

    assert code == 0
    assert "file.txt (5 B, 2026-01-02)" in text


@pytest.mark.parametrize("external", [False, True])
@pytest.mark.parametrize(
    "follow_args", [["--follow-symlinks"], ["--symlinks", "follow"]]
)
def test_cli_follow_alias_paths_and_rules(
    tmp_path: Path, capsys, followed_directory_link, external, follow_args
) -> None:
    """CLI filtering and each ignore stage use alias paths, preserving ancestors."""
    root = tmp_path / "root"
    root.mkdir()
    target = (tmp_path if external else root) / "real"
    (target / "nested").mkdir(parents=True)
    for name in ("keep.py", "project.py", "cli.py"):
        (target / "nested" / name).write_text("x", encoding="utf-8")
    (target / "build").mkdir()
    (target / "build" / "out.py").write_text("x", encoding="utf-8")
    followed_directory_link(root / "alias", target)
    followed_directory_link(root / "second", target)
    (root / ".p2mignore").write_text("alias/nested/project.py\n", encoding="utf-8")

    code, output = _run_cli_capture(
        capsys,
        [
            "--directory",
            str(root),
            *follow_args,
            "-t",
            "json",
            "-F",
            "^alias/",
            "-i",
            r"^alias/nested/cli\.py$",
        ],
    )
    assert code == 0
    tree = json.loads(output)

    def paths(node):
        return [(node["path"], node["depth"])] + [
            item for child in node["children"] for item in paths(child)
        ]

    assert paths(tree) == [
        (".", 0),
        ("alias", 1),
        ("alias/nested", 2),
        ("alias/nested/keep.py", 3),
    ]
