"""Tests for the first Matplotlib/reference query proof."""

import numpy as np

from gsp.protocol import ImageOrigin, ImageVisual, PointVisual, QueryRequest, QueryStatus, VisualFamily
from gsp_matplotlib.protocol_query import QueryVisualEntry, failed_query_result, query_visuals, unsupported_query_result


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
        QueryRequest(id="query:outside", panel_id="panel:main", coordinate=(10.0, 10.0)),
        [QueryVisualEntry(points)],
        panel_bounds=(-1.0, 1.0, -1.0, 1.0),
    )

    assert result.status == QueryStatus.OUTSIDE_PANEL
    assert not result.hit
    assert result.visual_id is None


def test_query_helper_results_use_diagnostics_for_terminal_failures():
    """Unsupported and failed are distinct non-hit terminal statuses."""
    request = QueryRequest(id="query:unsupported", panel_id="panel:main", coordinate=(0.0, 0.0))

    unsupported = unsupported_query_result(request, "backend does not advertise point-item queries")
    failed = failed_query_result(request, "readback buffer allocation failed")

    assert unsupported.status == QueryStatus.UNSUPPORTED
    assert unsupported.diagnostic == "backend does not advertise point-item queries"
    assert failed.status == QueryStatus.FAILED
    assert failed.diagnostic == "readback buffer allocation failed"
