"""Build and validate the GSP 0.2 specification source and requirement registries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "spec" / "requirements"
SOURCE_INVENTORY = REGISTRY_DIR / "source_inventory.json"
REQUIREMENTS = REGISTRY_DIR / "requirements.json"
REQUIREMENT_ID = re.compile(
    r"^GSP-(CORE|LIFE|SCENE|DATA|VIS|VIEW|CAP|QUERY|XPORT|EXT|PROD)-\d{3}$"
)


def build_source_inventory() -> dict[str, object]:
    """Return a deterministic classification of semantic and rationale sources."""
    rows: list[dict[str, str]] = []
    for path in _markdown_files(ROOT / "spec"):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("spec/requirements/"):
            continue
        if relative.startswith("spec/current/"):
            classification = "consolidation-draft"
            disposition = "target"
            destination = relative
        else:
            classification = "detailed-normative-source"
            disposition = "migration-required"
            destination = _destination_for(relative)
        rows.append(
            {
                "path": relative,
                "classification": classification,
                "disposition": disposition,
                "destination": destination,
            }
        )
    for directory, classification in (
        (ROOT / "adr", "accepted-rationale"),
        (ROOT / ".agent" / "decisions", "accepted-decision-record"),
    ):
        for path in _markdown_files(directory):
            rows.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "classification": classification,
                    "disposition": "preserve-and-link",
                    "destination": path.relative_to(ROOT).as_posix(),
                }
            )
    return {"schema": "gsp.source-inventory@0.2", "sources": sorted(rows, key=lambda row: row["path"])}


def validate() -> list[str]:
    """Return registry validation errors without mutating the repository."""
    errors: list[str] = []
    expected = build_source_inventory()
    if not SOURCE_INVENTORY.exists():
        errors.append("source_inventory.json is missing")
    else:
        actual = json.loads(SOURCE_INVENTORY.read_text(encoding="utf-8"))
        if actual != expected:
            errors.append("source_inventory.json is stale; run tools/spec_traceability.py --write")

    payload = json.loads(REQUIREMENTS.read_text(encoding="utf-8"))
    if payload.get("schema") != "gsp.requirements@0.2":
        errors.append("requirements.json has an unsupported schema")
    seen: set[str] = set()
    for index, requirement in enumerate(payload.get("requirements", [])):
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str) or not REQUIREMENT_ID.fullmatch(requirement_id):
            errors.append(f"requirements[{index}] has an invalid id")
            continue
        if requirement_id in seen:
            errors.append(f"duplicate requirement id {requirement_id}")
        seen.add(requirement_id)
        for path_field in ("source", "destination"):
            value = requirement.get(path_field)
            if not isinstance(value, str) or not value:
                errors.append(f"{requirement_id} has an invalid {path_field}")
            elif not (ROOT / value.split("#", 1)[0]).exists():
                errors.append(f"{requirement_id} references missing {path_field} {value}")
        tests = requirement.get("tests")
        if not isinstance(tests, list):
            errors.append(f"{requirement_id} tests must be a list")
        else:
            for test in tests:
                if not isinstance(test, str) or not (ROOT / test.split("::", 1)[0]).exists():
                    errors.append(f"{requirement_id} references missing test {test!r}")
    return errors


def _markdown_files(directory: Path) -> Iterable[Path]:
    if not directory.exists():
        return ()
    return sorted(path for path in directory.rglob("*.md") if path.is_file())


def _destination_for(relative: str) -> str:
    if relative.startswith("spec/visuals/") or "visual" in relative or "color_mapping" in relative:
        return "spec/current/visuals.md"
    if any(token in relative for token in ("view3d", "transform", "navigation", "layout", "canvas_size")):
        return "spec/current/views-layout.md"
    if "quer" in relative:
        return "spec/current/queries.md"
    if any(token in relative for token in ("resource", "data_source")):
        return "spec/current/resources.md"
    if any(token in relative for token in ("capabil", "backend")):
        return "spec/current/capabilities.md"
    if any(token in relative for token in ("transport", "extension")):
        return "spec/current/transports-extensions.md"
    if "vispy2" in relative:
        return "spec/current/scene.md"
    if "protocol" in relative or "conformance" in relative:
        return "spec/current/protocol.md"
    return "spec/current/index.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        SOURCE_INVENTORY.write_text(
            json.dumps(build_source_inventory(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    errors = validate()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("GSP specification traceability: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
