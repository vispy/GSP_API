"""Tests for the minimal authoritative JSON conformance fixture."""

import json

from fixtures.conformance import (
    conformance_debug_report,
    load_minimal_json_fixture,
    replay_minimal_json_fixture,
    validate_base64_array_chunk,
    validate_minimal_json_fixture,
)
from gsp.protocol import QueryStatus, TILED_IMAGE_QUERY_PAYLOAD_KIND, VisualFamily


def test_minimal_json_fixture_is_json_safe_and_authoritative():
    fixture = load_minimal_json_fixture()

    encoded = json.dumps(fixture, sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["schema_kind"] == "gsp.conformance.fixture"
    assert decoded["schema_version"] == "0.1.0"
    assert conformance_debug_report()["schema_authority"] is False


def test_minimal_json_fixture_arrays_are_typed_base64_chunks():
    fixture = validate_minimal_json_fixture()
    arrays = fixture["resources"]["arrays"]

    chunks = {entry["resource_id"]: validate_base64_array_chunk(entry) for entry in arrays}

    assert set(chunks) == {"res.point.positions", "res.point.colors", "res.point.sizes", "res.image.rgba8"}
    assert chunks["res.point.positions"].dtype == "float32"
    assert chunks["res.point.colors"].dtype == "uint8"
    assert chunks["res.image.rgba8"].shape == (2, 2, 4)


def test_minimal_json_fixture_keeps_guides_semantic_not_buffers():
    fixture = validate_minimal_json_fixture()
    guides = {guide["guide_id"]: guide for guide in fixture["scene"]["guides"]}

    assert guides["guide:x-fixture"]["ticks"] == [0.0, 0.5, 1.0]
    assert guides["guide:x-fixture"]["labels"] == ["zero", "half", "one"]
    assert guides["guide:y-fixture"]["target_count"] == 4


def test_minimal_json_fixture_replays_through_matplotlib_reference_adapter():
    replay = replay_minimal_json_fixture()

    assert replay.point_query.status == QueryStatus.HIT
    assert replay.point_query.visual_family == VisualFamily.POINT
    assert replay.guide_query.status == QueryStatus.HIT
    assert replay.guide_miss.status == QueryStatus.MISS
    assert replay.tiled_query.status == QueryStatus.HIT
    assert replay.tiled_query.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
    assert replay.tiled_mosaic_source_rect == (0, 0, 2, 2)
