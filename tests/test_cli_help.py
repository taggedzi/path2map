"""Help text tests for CLI documentation quality."""

from __future__ import annotations

import re

from path2map.cli import build_parser


def test_help_includes_examples_and_argument_descriptions() -> None:
    """Help output includes examples and primary argument guidance."""
    help_text = build_parser().format_help()

    assert "Examples:" in help_text
    assert "--directory" in help_text
    assert "--output" in help_text
    assert "--details-style" in help_text
    assert "Reserved for future renderer themes" in help_text


def test_help_shows_defaults_for_configurable_options() -> None:
    """Help output displays defaults for options users commonly tune."""
    help_text = build_parser().format_help()

    assert "(default: .)" in help_text
    assert "(default: auto)" in help_text
    assert re.search(r"\(default:\s*binary\)", help_text) is not None
    assert "(default: text)" in help_text
