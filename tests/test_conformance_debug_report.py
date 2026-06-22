"""Tests for debug JSON conformance report generation."""

import json

from fixtures.conformance import conformance_debug_report


def test_conformance_debug_report_is_json_safe_and_non_authoritative():
    report = conformance_debug_report()

    encoded = json.dumps(report, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["report_kind"] == "gsp.conformance.debug-json"
    assert decoded["schema_authority"] is False
    assert decoded["array_transport"] == "omitted"


def test_conformance_debug_report_contains_backend_outcomes_and_semantic_queries():
    report = conformance_debug_report()
    backends = {entry["backend_id"]: entry for entry in report["backends"]}

    assert set(backends) == {"matplotlib", "datoviz"}
    assert backends["matplotlib"]["status"] == "pass"
    assert backends["datoviz"]["status"] == "skip"

    replay = backends["matplotlib"]["replay"]
    assert replay["server_name"] == "gsp-v0.1-reference"
    assert replay["queries"]["point"]["status"] == "hit"
    assert replay["queries"]["point"]["visual_id"] == "visual:point-fixture"
    assert replay["queries"]["guide"]["extension_payload"]["text_value"] == "half"
    assert replay["queries"]["guide_miss"]["status"] == "miss"
    assert replay["queries"]["tiled"]["extension_payload"]["source_id"] == "source:tiled-fixture"
    assert replay["tiled_mosaic"]["source_rect"] == [0, 0, 2, 2]
