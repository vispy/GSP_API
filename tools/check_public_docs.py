"""Reject stale public terminology and inconsistent GSP 0.2 version surfaces."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = ROOT / "mkdocs_source"
EXCLUDED_PUBLIC_PREFIXES = (
    "development-history/",
    "philosophy/",
)
EXCLUDED_PUBLIC_PATHS = {
    "about.md",
    "protocol.md",
    "conformance.md",
    "gallery.md",
    "review-examples.md",
    "s023_visual_qa.md",
    "api/gsp.md",
    "api/gsp_datoviz.md",
    "api/gsp_extra.md",
    "api/gsp_matplotlib.md",
    "api/gsp_network.md",
    "api/gsp_pydantic.md",
    "api/vispy_2.md",
}
FORBIDDEN = {
    "removed producer import": re.compile(r"\bimport\s+vispy2\b|\bfrom\s+vispy2\b"),
    "legacy environment selection": re.compile(r"GSP_RENDERER="),
    "stale public version": re.compile(r"\b0\.1\.0\b"),
}


def validate() -> list[str]:
    """Return public documentation consistency errors."""
    errors: list[str] = []
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = pyproject["project"]["version"]
    if version != "0.2.0":
        errors.append(f"pyproject project.version is {version!r}, expected '0.2.0'")
    producer_init = (ROOT / "src/gsp_vispy2/__init__.py").read_text(encoding="utf-8")
    if '__version__ = "0.2.0"' not in producer_init:
        errors.append("gsp_vispy2.__version__ does not match project version 0.2.0")
    protocol_init = (ROOT / "src/gsp/protocol/__init__.py").read_text(encoding="utf-8")
    if 'PROTOCOL_VERSION = "0.2"' not in protocol_init:
        errors.append("gsp.protocol.PROTOCOL_VERSION is not 0.2")
    if (ROOT / "src/vispy2").exists():
        errors.append("removed src/vispy2 compatibility package has returned")

    public_files = [ROOT / "README.md"]
    public_files.extend(
        path
        for path in sorted(PUBLIC_ROOT.rglob("*.md"))
        if path.relative_to(PUBLIC_ROOT).as_posix() not in EXCLUDED_PUBLIC_PATHS
        and not path.relative_to(PUBLIC_ROOT).as_posix().startswith(EXCLUDED_PUBLIC_PREFIXES)
    )
    for path in public_files:
        text = path.read_text(encoding="utf-8")
        if path == ROOT / "README.md":
            text = text.split("## Legacy code", maxsplit=1)[0]
        relative = path.relative_to(ROOT).as_posix()
        for description, pattern in FORBIDDEN.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{relative}:{line}: {description}: {match.group(0)!r}")
    tutorial = (PUBLIC_ROOT / "getting-started/first-scene.md").read_text(encoding="utf-8")
    if '--8<-- "examples/docs/first_scene.py"' not in tutorial:
        errors.append("first-scene tutorial is not synchronized with its executable source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    errors = validate()
    for error in errors:
        print(error)
    if not errors:
        print("GSP public documentation consistency: OK")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
