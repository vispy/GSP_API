"""Checks for the GSP 0.2 public documentation boundary."""

from tools.check_public_docs import validate


def test_public_documentation_uses_the_current_version_and_api() -> None:
    """Current pages cannot regress to removed 0.1 user instructions."""
    assert validate() == []
