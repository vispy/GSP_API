"""Minimal JSON fixture adapter for the current conformance slice."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any, TypeAlias, cast

import numpy as np

from gsp.protocol import (
    GUIDE_QUERY_PAYLOAD_KIND,
    QueryResult,
    QueryStatus,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    TILED_IMAGE_QUERY_PAYLOAD_KIND,
    TiledImageQueryPayload,
    VisualFamily,
)

from .array_chunks import validate_base64_array_chunk
from .baseline import image_visual_fixture, point_visual_fixture
from .debug_report import conformance_debug_report
from .replay import InProcessReplayResult, replay_conformance_fixtures


JsonFixture: TypeAlias = dict[str, Any]

MINIMAL_JSON_FIXTURE_NAME = "minimal_v0_1.json"


def load_minimal_json_fixture() -> JsonFixture:
    """Load the committed minimal `gsp.conformance.fixture@0.1` JSON fixture."""
    text = resources.files(__package__).joinpath(MINIMAL_JSON_FIXTURE_NAME).read_text(encoding="utf-8")
    return cast(JsonFixture, json.loads(text))


def validate_minimal_json_fixture(fixture: JsonFixture | None = None) -> JsonFixture:
    """Validate the committed minimal fixture enough for the M043 semantic replay adapter."""
    loaded = load_minimal_json_fixture() if fixture is None else fixture
    if loaded.get("schema_kind") != "gsp.conformance.fixture":
        raise ValueError("fixture schema_kind must be gsp.conformance.fixture")
    if loaded.get("schema_version") != "0.1.0":
        raise ValueError("fixture schema_version must be 0.1.0")
    if conformance_debug_report().get("schema_authority") is not False:
        raise ValueError("debug-json report must remain non-authoritative")

    _validate_array_resources(loaded)
    _validate_backend_expectations(loaded)
    _validate_query_expectations(loaded, replay_conformance_fixtures())
    return loaded


def replay_minimal_json_fixture(fixture: JsonFixture | None = None) -> InProcessReplayResult:
    """Validate the JSON fixture and replay it through the Matplotlib reference adapter."""
    validate_minimal_json_fixture(fixture)
    return replay_conformance_fixtures()


def _validate_array_resources(fixture: JsonFixture) -> None:
    arrays = _required_child_mapping(fixture, "resources").get("arrays")
    if not isinstance(arrays, list):
        raise ValueError("fixture resources.arrays must be a list")
    chunks = {validate_base64_array_chunk(_required_mapping(item, "array")).resource_id: item for item in arrays}
    expected = {
        "res.point.positions": _contiguous_bytes(point_visual_fixture().positions),
        "res.point.colors": _contiguous_bytes(point_visual_fixture().colors),
        "res.point.sizes": _contiguous_bytes(point_visual_fixture().sizes),
        "res.image.rgba8": _contiguous_bytes(image_visual_fixture().image),
    }
    if set(chunks) != set(expected):
        raise ValueError("fixture array resources do not match the current semantic slice")
    for resource_id, expected_bytes in expected.items():
        chunk = validate_base64_array_chunk(_required_mapping(chunks[resource_id], "array"))
        if chunk.decoded_bytes != expected_bytes:
            raise ValueError(f"fixture array bytes do not match baseline resource {resource_id!r}")


def _validate_backend_expectations(fixture: JsonFixture) -> None:
    expectations = _required_child_mapping(fixture, "backend_expectations")
    matplotlib = _required_child_mapping(expectations, "matplotlib")
    datoviz = _required_child_mapping(expectations, "datoviz")
    if matplotlib.get("expectation") != "pass":
        raise ValueError("minimal fixture requires Matplotlib pass expectation")
    if datoviz.get("expectation") != "skip" or not datoviz.get("reason_code"):
        raise ValueError("minimal fixture requires Datoviz skip expectation with reason_code")


def _validate_query_expectations(fixture: JsonFixture, replay: InProcessReplayResult) -> None:
    queries = fixture.get("queries")
    if not isinstance(queries, list):
        raise ValueError("fixture queries must be a list")
    expected_by_id = {_required_string(_required_mapping(query, "query"), "query_id"): _required_mapping(query, "query") for query in queries}
    if set(expected_by_id) != {"query:point-over-image", "query:guide-tick", "query:guide-miss", "query:tiled-fixture"}:
        raise ValueError("fixture queries do not match the current semantic slice")

    _assert_query_result(expected_by_id["query:point-over-image"], replay.point_query)
    _assert_query_result(expected_by_id["query:guide-tick"], replay.guide_query)
    _assert_query_result(expected_by_id["query:guide-miss"], replay.guide_miss)
    _assert_query_result(expected_by_id["query:tiled-fixture"], replay.tiled_query)


def _assert_query_result(query: dict[str, Any], result: QueryResult) -> None:
    expected = _required_child_mapping(query, "expected_result")
    if expected.get("status") != result.status.value:
        raise ValueError(f"query {result.request_id!r} status does not match replay")
    if expected.get("hit") != result.hit:
        raise ValueError(f"query {result.request_id!r} hit flag does not match replay")
    if expected.get("request_id") != result.request_id:
        raise ValueError(f"query {result.request_id!r} request_id does not match replay")

    if result.status == QueryStatus.HIT:
        _assert_hit_query_result(expected, result)


def _assert_hit_query_result(expected: dict[str, Any], result: QueryResult) -> None:
    visual_family = result.visual_family.value if isinstance(result.visual_family, VisualFamily) else result.visual_family
    if expected.get("visual_family", visual_family) != visual_family:
        raise ValueError(f"query {result.request_id!r} visual_family does not match replay")
    if expected.get("visual_id", result.visual_id) != result.visual_id:
        raise ValueError(f"query {result.request_id!r} visual_id does not match replay")
    if expected.get("item_id", result.item_id) != result.item_id:
        raise ValueError(f"query {result.request_id!r} item_id does not match replay")

    payloads = expected.get("extension_payloads", [])
    if not isinstance(payloads, list):
        raise ValueError("extension_payloads must be a list")
    if result.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND:
        _assert_payload_kind(payloads, GUIDE_QUERY_PAYLOAD_KIND)
    if result.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND:
        _assert_payload_kind(payloads, TILED_IMAGE_QUERY_PAYLOAD_KIND)
        if not isinstance(result.extension_payload, TiledImageQueryPayload):
            raise ValueError("tiled query replay payload type is invalid")
        value = _required_child_mapping(cast(dict[str, Any], payloads[0]), "value")
        if value.get("source_id") != result.extension_payload.source_id:
            raise ValueError("tiled query source_id does not match replay")


def _assert_payload_kind(payloads: list[Any], payload_kind: str) -> None:
    if not payloads:
        raise ValueError(f"expected extension payload {payload_kind}")
    payload = _required_mapping(payloads[0], "extension_payload")
    if payload.get("payload_kind") != payload_kind:
        raise ValueError(f"expected extension payload {payload_kind}")


def _contiguous_bytes(value: object) -> bytes:
    return np.ascontiguousarray(value).tobytes(order="C")


def _required_child_mapping(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    return _required_mapping(value.get(field_name), field_name)


def _required_mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return cast(dict[str, Any], value)


def _required_string(value: dict[str, Any], field_name: str) -> str:
    field = value.get(field_name)
    if not isinstance(field, str) or not field:
        raise ValueError(f"{field_name} must be a non-empty string")
    return field
