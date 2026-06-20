"""Conformance tests for the accepted GSP v0.1 vertical slice."""

import pytest

from fixtures.conformance import capability_snapshot_fixture, point_over_image_scene
from fixtures.conformance.baseline import position_buffer_resource_fixture
from gsp.protocol import AdaptationOutcome, QueryResult, QueryStatus, VisualFamily
from gsp_matplotlib.protocol_query import query_visuals
from gsp_matplotlib.protocol_renderer import render_image_visual, render_point_visual


def test_conformance_capability_snapshot_locks_v01_surface():
    """The baseline advertises only the current v0.1 surface."""
    caps = capability_snapshot_fixture()

    assert caps.protocol_versions == ("0.1",)
    assert [transport.value for transport in caps.transports] == ["inproc"]
    assert caps.visual_families == ("point", "image")
    assert caps.query_modes == ("panel-query", "point-item", "image-texel")
    assert caps.deterministic is True
    assert caps.adapt_visual("point").outcome == AdaptationOutcome.ACCEPT
    assert caps.adapt_visual("mesh").outcome == AdaptationOutcome.REJECT


def test_conformance_fixtures_use_direct_memory_not_serialization():
    """The local fixture path uses memoryview/NumPy data directly."""
    resource = position_buffer_resource_fixture()

    assert resource.data is not None
    assert resource.data.nbytes == resource.byte_length
    assert resource.external_source is None
    assert resource.contiguous is True


def test_conformance_point_over_image_query_frontmost_result():
    """The canonical point-over-image scene returns the frontmost point."""
    scene = point_over_image_scene()

    result = query_visuals(scene.query, scene.entries)

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.POINT
    assert result.visual_id == scene.point.id
    assert result.item_id == 0
    assert result.displayed_rgba == (1.0, 0.0, 0.0, 1.0)


def test_conformance_matplotlib_reference_artists():
    """Matplotlib reference rendering must preserve fixture IDs and assumptions."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scene = point_over_image_scene()
    fig, ax = plt.subplots()
    try:
        image_artist = render_image_visual(ax, scene.image)
        point_artist = render_point_visual(ax, scene.point)

        assert image_artist.get_gid() == scene.image.id
        assert point_artist.get_gid() == scene.point.id
        assert image_artist.get_interpolation() == "nearest"
        assert image_artist.origin == "upper"
        assert list(image_artist.get_extent()) == [-1.0, 1.0, -1.0, 1.0]
        assert len(point_artist.get_offsets()) == 2
    finally:
        plt.close(fig)


def test_query_result_status_invariants_are_locked():
    """Query status invariants distinguish hit and all non-hit statuses."""
    QueryResult(
        request_id="query:outside",
        status=QueryStatus.OUTSIDE_PANEL,
        hit=False,
        panel_coordinate=(10.0, 10.0),
    )

    with pytest.raises(ValueError, match="hit results"):
        QueryResult(
            request_id="query:bad-hit",
            status=QueryStatus.HIT,
            hit=False,
            panel_coordinate=(0.0, 0.0),
        )

    with pytest.raises(ValueError, match="unsupported"):
        QueryResult(
            request_id="query:unsupported",
            status=QueryStatus.UNSUPPORTED,
            hit=False,
            panel_coordinate=(0.0, 0.0),
        )

    for status in (QueryStatus.STALE, QueryStatus.DROPPED, QueryStatus.FAILED):
        with pytest.raises(ValueError, match=status.value):
            QueryResult(
                request_id=f"query:{status.value}",
                status=status,
                hit=False,
                panel_coordinate=(0.0, 0.0),
            )

    with pytest.raises(ValueError, match="non-hit query results"):
        QueryResult(
            request_id="query:bad-miss",
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=(0.0, 0.0),
            visual_id="visual:points",
        )
