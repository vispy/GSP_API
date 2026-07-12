"""Build and validate the GSP 0.2 specification source and requirement registries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Iterable, cast


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "spec" / "requirements"
SOURCE_INVENTORY = REGISTRY_DIR / "source_inventory.json"
REQUIREMENTS = REGISTRY_DIR / "requirements.json"
REGISTRIES = REGISTRY_DIR / "registries.json"
SOURCE_DISPOSITIONS = REGISTRY_DIR / "source_dispositions.json"
REQUIREMENT_ID = re.compile(
    r"^GSP-(CORE|LIFE|SCENE|DATA|VIS|VIEW|CAP|QUERY|XPORT|EXT|PROD)-\d{3}$"
)
REQUIREMENT_REF = re.compile(
    r"GSP-(CORE|LIFE|SCENE|DATA|VIS|VIEW|CAP|QUERY|XPORT|EXT|PROD)-\d{3}"
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


def build_requirement_registry() -> dict[str, object]:
    """Extract stable labeled requirements from the GSP 0.2 target chapters."""
    rows: list[dict[str, object]] = []
    for path in _markdown_files(ROOT / "spec" / "current"):
        relative = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            matches = list(REQUIREMENT_REF.finditer(line.replace("`", "")))
            for match in matches:
                requirement_id = match.group(0)
                statement = _requirement_statement(line, requirement_id)
                rows.append(
                    {
                        "id": requirement_id,
                        "domain": requirement_id.split("-")[1].lower(),
                        "statement": statement,
                        "status": "accepted",
                        "source": _legacy_source_for(requirement_id),
                        "destination": relative,
                        "tests": _tests_for(requirement_id),
                        "notes": "Domain-level executable evidence; backend-specific limits are recorded in profiles/.",
                    }
                )
    return {
        "schema": "gsp.requirements@0.2",
        "requirements": sorted(rows, key=lambda row: str(row["id"])),
    }


def build_source_dispositions() -> dict[str, object]:
    """Assign every detailed specification source one explicit consolidation disposition."""
    inventory = build_source_inventory()
    rows: list[dict[str, str]] = []
    sources = cast(list[dict[str, str]], inventory["sources"])
    for source in sources:
        if source["classification"] != "detailed-normative-source":
            continue
        path = source["path"]
        if "backend" in path or "datoviz_v04_api_boundary" in path:
            disposition = "move-to-backend-profile"
            destination = "spec/current/backend-profiles.md"
        elif "conformance" in path or "visual_qa" in path:
            disposition = "move-to-conformance"
            destination = "spec/requirements/requirements.json"
        elif "vispy2" in path:
            disposition = "move-to-producer-profile"
            destination = "spec/current/scene.md"
        else:
            disposition = "migrated-to-normative-chapter"
            destination = source["destination"]
        notes = "Detailed source retained for provenance; GSP 0.2 target text and registry control future changes."
        if "mesh_materials_s038" in path:
            notes = "Bounded unlit/flat-Lambert/Texture2D contracts migrated; general material graphs remain outside GSP 0.2."
        elif "mesh_face_culling_alpha" in path:
            notes = "Projected-NDC culling migrated; strict non-opaque 3D compositing remains outside GSP 0.2."
        elif "data_sources" in path:
            notes = "Bounded preconfigured/tiled/HTTP-array rules migrated; general remote-data support is not claimed."
        rows.append(
            {
                "source": path,
                "disposition": disposition,
                "destination": destination,
                "notes": notes,
            }
        )
    return {
        "schema": "gsp.source-dispositions@0.2",
        "dispositions": sorted(rows, key=lambda row: row["source"]),
    }


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
    expected_requirements = build_requirement_registry()
    if payload != expected_requirements:
        errors.append("requirements.json is stale; run tools/spec_traceability.py --write")
    expected_dispositions = build_source_dispositions()
    if not SOURCE_DISPOSITIONS.exists():
        errors.append("source_dispositions.json is missing")
    else:
        dispositions = json.loads(SOURCE_DISPOSITIONS.read_text(encoding="utf-8"))
        if dispositions != expected_dispositions:
            errors.append("source_dispositions.json is stale; run tools/spec_traceability.py --write")
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


def _requirement_statement(line: str, requirement_id: str) -> str:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    for index, cell in enumerate(cells):
        if requirement_id in cell and index + 1 < len(cells):
            statement = cells[index + 1]
            if statement:
                return statement
    plain = line.replace("`", "")
    suffix = plain.split(requirement_id, 1)[1].lstrip(" :—-")
    return suffix.strip() or f"Normative requirement {requirement_id}."


def _legacy_source_for(requirement_id: str) -> str:
    domain = requirement_id.split("-")[1]
    return {
        "CORE": "PROJECT_CHARTER.md",
        "LIFE": "spec/protocol.md",
        "SCENE": "spec/visual_families_v1.md",
        "DATA": "spec/resources.md",
        "VIS": "spec/visual_cross_cutting_rules.md",
        "VIEW": "spec/transforms.md",
        "CAP": "spec/capabilities.md",
        "QUERY": "spec/query.md",
        "XPORT": "spec/transports.md",
        "EXT": "spec/extensions.md",
        "PROD": "spec/vispy2/api.md",
    }[domain]


def _tests_for(requirement_id: str) -> list[str]:
    """Return maintained executable evidence for a normative requirement domain."""
    domain = requirement_id.split("-")[1]
    return {
        "CORE": ["tests/test_protocol_spine.py", "tests/test_import_surface.py"],
        "LIFE": ["tests/test_protocol_spine.py"],
        "SCENE": ["tests/test_protocol_spine.py", "tests/test_vispy2_protocol_mvp.py"],
        "DATA": ["tests/test_buffer.py", "tests/test_conformance_array_chunks.py"],
        "VIS": ["tests/test_matplotlib_protocol_slice.py", "tests/test_mesh_visual_protocol.py"],
        "VIEW": ["tests/test_transform_protocol.py", "tests/test_view3d_protocol.py"],
        "CAP": ["tests/test_axis_provider_capabilities.py", "tests/test_datoviz_v04_protocol_renderer.py"],
        "QUERY": ["tests/test_matplotlib_protocol_query.py", "tests/test_matplotlib_scoped_query.py"],
        "XPORT": ["tests/test_protocol_spine.py", "tests/test_conformance_json_fixture.py"],
        "EXT": ["tests/test_extension_data_sources.py", "tests/test_s020_security_validation.py"],
        "PROD": ["tests/test_vispy2_protocol_mvp.py", "tests/test_vispy2_s051_acceptance.py"],
    }[domain]


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
        REQUIREMENTS.write_text(
            json.dumps(build_requirement_registry(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        SOURCE_DISPOSITIONS.write_text(
            json.dumps(build_source_dispositions(), indent=2, sort_keys=True) + "\n",
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
