"""Tests for the first Matplotlib/reference query proof."""

import numpy as np

import pytest

from gsp.protocol import (
    CoordinateSpace,
    ImageOrigin,
    ImageVisual,
    PointVisual,
    QueryContributionKind,
    QueryHit,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    TEXT_QUERY_PAYLOAD_KIND,
    TextVisual,
    VisualFamily,
)
from gsp_matplotlib.protocol_query import (
    QueryVisualEntry,
    failed_query_result,
    query_visuals,
    unsupported_query_result,
)


def test_query_returns_frontmost_point_over_image():
    """A point above an image wins with frontmost hit policy."""
    image = ImageVisual(
        id="visual:image",
        image=np.array(
            [
                [[10, 20, 30, 255], [40, 50, 60, 255]],
                [[70, 80, 90, 255], [100, 110, 120, 255]],
            ],
            dtype=np.uint8,
        ),
        extent=(-1.0, 1.0, -1.0, 1.0),
        origin=ImageOrigin.UPPER,
    )
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.25, 0.25]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([0.25], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(id="query:point", panel_id="panel:main", coordinate=(0.25, 0.25)),
        [QueryVisualEntry(image, z_order=0), QueryVisualEntry(points, z_order=1)],
    )

    assert result.status == QueryStatus.HIT
    assert result.hits == (
        QueryHit(
            contribution_kind=QueryContributionKind.DATA,
            visual_id="visual:points",
            visual_family=VisualFamily.POINT,
            item_id=0,
            visual_coordinate=(0.25, 0.25),
            data_coordinate=(0.25, 0.25),
            displayed_rgba=(1.0, 0.0, 0.0, 1.0),
        ),
    )
    assert result.visual_family == VisualFamily.POINT
    assert result.visual_id == "visual:points"
    assert result.item_id == 0
    assert result.displayed_rgba == (1.0, 0.0, 0.0, 1.0)


def test_query_returns_image_texel_and_value():
    """Image query reports texel coordinates, displayed RGBA, and source value."""
    image = ImageVisual(
        id="visual:image",
        image=np.array(
            [
                [[10, 20, 30, 255], [40, 50, 60, 255]],
                [[70, 80, 90, 255], [100, 110, 120, 255]],
            ],
            dtype=np.uint8,
        ),
        extent=(-1.0, 1.0, -1.0, 1.0),
        origin=ImageOrigin.UPPER,
    )

    result = query_visuals(
        QueryRequest(id="query:image", panel_id="panel:main", coordinate=(0.75, 0.75)),
        [QueryVisualEntry(image)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.IMAGE
    assert result.texel == (0, 1)
    assert result.value == (40, 50, 60, 255)
    assert result.displayed_rgba == (40 / 255.0, 50 / 255.0, 60 / 255.0, 1.0)


def test_query_returns_text_item_payload_without_glyph_fields():
    """TextVisual query is item-level and reports public visual/item identity."""
    text = TextVisual(
        id="visual:text",
        texts=("first", "second"),
        positions=np.array([[0.0, 0.0], [10.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        rgba=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
        font_size_px=np.array([4.0, 4.0], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(id="query:text", panel_id="panel:main", coordinate=(10.5, 0.0)),
        [QueryVisualEntry(text)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.TEXT
    assert result.visual_id == "visual:text"
    assert result.item_id == 1
    assert result.value == "second"
    assert result.extension_payload_kind == TEXT_QUERY_PAYLOAD_KIND
    assert result.extension_payload == {
        "kind": "text",
        "visual_id": "visual:text",
        "item_index": 1,
        "text": "second",
        "position": (10.0, 0.0),
        "coordinate_space": "data",
    }
    assert "glyph" not in result.extension_payload
    assert result.displayed_rgba == (0.0, 0.0, 1.0, 128 / 255.0)


def test_query_returns_frontmost_text_over_point():
    """Text participates in item-level frontmost/all ordering."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([4.0], dtype=np.float32),
    )
    text = TextVisual(
        id="visual:text",
        texts=("label",),
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        font_size_px=4.0,
    )

    result = query_visuals(
        QueryRequest(
            id="query:front-text", panel_id="panel:main", coordinate=(0.0, 0.0)
        ),
        [QueryVisualEntry(points, z_order=0), QueryVisualEntry(text, z_order=2)],
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.TEXT
    assert result.item_id == 0


def test_query_text_misses_outside_anchor_neighborhood():
    text = TextVisual(
        id="visual:text",
        texts=("label",),
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
        font_size_px=2.0,
    )

    result = query_visuals(
        QueryRequest(
            id="query:text-miss", panel_id="panel:main", coordinate=(20.0, 0.0)
        ),
        [QueryVisualEntry(text)],
    )

    assert result.status == QueryStatus.MISS


def test_query_request_defaults_to_data_scope():
    request = QueryRequest(
        id="query:default-scope", panel_id="panel:main", coordinate=(0.0, 0.0)
    )

    assert request.scope == QueryScope.DATA
    assert request.requested_extension_payload_kinds == ()


def test_query_result_with_hits_mirrors_first_hit_to_compatibility_fields():
    hit = QueryHit(
        contribution_kind=QueryContributionKind.DATA,
        visual_id="visual:points",
        visual_family=VisualFamily.POINT,
        item_id=2,
        visual_coordinate=(0.1, 0.2),
        data_coordinate=(0.1, 0.2),
        displayed_rgba=(0.0, 1.0, 0.0, 1.0),
    )

    result = QueryResult(
        request_id="query:hit-list",
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=(0.1, 0.2),
        hits=(hit,),
    )

    assert result.visual_id == "visual:points"
    assert result.visual_family == VisualFamily.POINT
    assert result.item_id == 2
    assert result.displayed_rgba == (0.0, 1.0, 0.0, 1.0)


def test_query_result_can_represent_all_hits_front_to_back():
    back = QueryHit(
        contribution_kind=QueryContributionKind.DATA,
        visual_id="visual:image",
        visual_family=VisualFamily.IMAGE,
    )
    front = QueryHit(
        contribution_kind=QueryContributionKind.DATA,
        visual_id="visual:points",
        visual_family=VisualFamily.POINT,
    )

    result = QueryResult(
        request_id="query:all",
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=(0.0, 0.0),
        hits=(front, back),
    )

    assert result.hits == (front, back)
    assert result.visual_id == "visual:points"
    assert result.visual_family == VisualFamily.POINT


def test_non_hit_query_results_reject_hit_payload_fields():
    with pytest.raises(ValueError, match="non-hit query results"):
        QueryResult(
            request_id="query:bad-miss",
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=(0.0, 0.0),
            hits=(
                QueryHit(
                    contribution_kind=QueryContributionKind.DATA,
                    visual_id="visual:points",
                ),
            ),
        )


def test_query_returns_miss_when_no_visual_contains_coordinate():
    """Miss is distinct from unsupported capability."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([0.01], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(id="query:miss", panel_id="panel:main", coordinate=(10.0, 10.0)),
        [QueryVisualEntry(points)],
    )

    assert result.status == QueryStatus.MISS
    assert not result.hit
    assert result.visual_id is None


def test_query_returns_outside_panel_before_testing_visuals():
    """Panel bounds produce outside-panel rather than miss."""
    points = PointVisual(
        id="visual:points",
        positions=np.array([[10.0, 10.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([100.0], dtype=np.float32),
    )

    result = query_visuals(
        QueryRequest(
            id="query:outside", panel_id="panel:main", coordinate=(10.0, 10.0)
        ),
        [QueryVisualEntry(points)],
        panel_bounds=(-1.0, 1.0, -1.0, 1.0),
    )

    assert result.status == QueryStatus.OUTSIDE_PANEL
    assert not result.hit
    assert result.visual_id is None


def test_query_helper_results_use_diagnostics_for_terminal_failures():
    """Unsupported and failed are distinct non-hit terminal statuses."""
    request = QueryRequest(
        id="query:unsupported", panel_id="panel:main", coordinate=(0.0, 0.0)
    )

    unsupported = unsupported_query_result(
        request, "backend does not advertise point-item queries"
    )
    failed = failed_query_result(request, "readback buffer allocation failed")

    assert unsupported.status == QueryStatus.UNSUPPORTED
    assert unsupported.diagnostic == "backend does not advertise point-item queries"
    assert failed.status == QueryStatus.FAILED
    assert failed.diagnostic == "readback buffer allocation failed"
