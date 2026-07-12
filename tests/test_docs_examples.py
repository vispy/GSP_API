"""Executable checks for code presented in the public documentation."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_first_scene_is_the_included_executable_source(tmp_path: Path) -> None:
    """The tutorial includes and executes its checked-in source verbatim."""
    tutorial = (ROOT / "mkdocs_source/getting-started/first-scene.md").read_text(
        encoding="utf-8"
    )
    relative = "examples/docs/first_scene.py"
    assert f'--8<-- "{relative}"' in tutorial
    output = tmp_path / "first-scene.png"
    completed = subprocess.run(
        [sys.executable, str(ROOT / relative), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert output.stat().st_size > 0
    assert str(output) in completed.stdout


def test_readme_uses_only_the_current_producer_import() -> None:
    """The repository landing page cannot regress to the removed import surface."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "import gsp_vispy2 as vp" in readme
    assert "import vispy2" not in readme
