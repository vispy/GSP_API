"""Tests for the in-process conformance replay harness."""

from fixtures.conformance import replay_conformance_fixtures
from gsp.protocol import (
    GUIDE_QUERY_PAYLOAD_KIND,
    QueryStatus,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    TILED_IMAGE_QUERY_PAYLOAD_KIND,
    TiledImageQueryPayload,
    VisualFamily,
)


def test_in_process_replay_returns_semantic_conformance_results():
    replay = replay_conformance_fixtures()

    assert replay.server_name == "gsp-v0.1-reference"
    assert replay.visual_families == ("point", "image")
    assert replay.extensions == (TILED_IMAGE_EXTENSION_CAPABILITY,)

    assert replay.point_query.status == QueryStatus.HIT
    assert replay.point_query.visual_family == VisualFamily.POINT
    assert replay.point_query.visual_id == "visual:point-fixture"
    assert replay.point_query.item_id == 0

    assert replay.guide_query.status == QueryStatus.HIT
    assert replay.guide_query.visual_id == "guide:x-fixture"
    assert replay.guide_query.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND
    assert replay.guide_miss.status == QueryStatus.MISS

    assert replay.tiled_mosaic_source_rect == (0, 0, 2, 2)
    assert replay.tiled_mosaic_shape == (2, 2, 4)
    assert replay.tiled_query.status == QueryStatus.HIT
    assert replay.tiled_query.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
    assert isinstance(replay.tiled_query.extension_payload, TiledImageQueryPayload)
    assert replay.tiled_query.extension_payload.source_id == "source:tiled-fixture"
    assert replay.tiled_query.extension_payload.value == (0, 0, 0, 255)
