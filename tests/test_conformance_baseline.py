"""Conformance tests for the accepted GSP v0.1 vertical slice."""

import pytest

from fixtures.conformance import capability_snapshot_fixture, guide_scene, point_over_image_scene, tiled_source_scene
from fixtures.conformance.baseline import position_buffer_resource_fixture
from gsp.protocol import (
    GUIDE_QUERY_PAYLOAD_KIND,
    AdaptationOutcome,
    AxisDimension,
    GuideQueryPayload,
    QueryResult,
    QueryStatus,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    TILED_IMAGE_QUERY_PAYLOAD_KIND,
    TileIndex,
    TiledImageQueryPayload,
    VisualFamily,
)
from gsp_matplotlib.guide_query import query_axis_guides, unsupported_guide_query_result
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides
from gsp_matplotlib.protocol_query import query_visuals
from gsp_matplotlib.protocol_renderer import render_image_visual, render_point_visual
from gsp_matplotlib.tiled_image import query_tiled_image_source, render_tiled_image_source


def test_conformance_capability_snapshot_locks_v01_surface():
    """The baseline advertises only the current v0.1 surface."""
    caps = capability_snapshot_fixture()

    assert caps.protocol_versions == ("0.1",)
    assert [transport.value for transport in caps.transports] == ["inproc"]
    assert caps.visual_families == ("point", "image")
    assert caps.query_modes == ("panel-query", "point-item", "image-texel", "guide-query")
    assert caps.supports_extension(TILED_IMAGE_EXTENSION_CAPABILITY)
    assert caps.supports_extension_manifests
    assert caps.supports_virtual_data_sources
    assert caps.supports_tiled_image_sources
    assert caps.supports_synthetic_data_sources
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


def test_conformance_guide_fixture_locks_semantic_intent():
    """The guide fixture captures the accepted S012 axis/title surface."""
    scene = guide_scene()

    assert scene.view.panel_id == "panel:guide-main"
    assert scene.x_axis.label_text == "time"
    assert scene.x_axis.grid_visible is True
    assert scene.x_axis.tick_spec.explicit_values == (0.0, 0.5, 1.0)
    assert scene.x_axis.tick_spec.explicit_labels == ("zero", "half", "one")
    assert scene.y_axis.label_text == "value"
    assert scene.y_axis.tick_spec.target_count == 4
    assert scene.title.text == "Guide fixture"


def test_conformance_matplotlib_reference_guides():
    """Matplotlib guide rendering must preserve deterministic fixture ticks."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scene = guide_scene()
    fig, ax = plt.subplots()
    try:
        render_axis_guides(ax, scene.view, (scene.x_axis, scene.y_axis))
        render_panel_text_guides(ax, (scene.title,))

        assert list(ax.get_xticks()) == [0.0, 0.5, 1.0]
        assert [label.get_text() for label in ax.get_xticklabels()] == ["zero", "half", "one"]
        assert [label.get_text() for label in ax.get_yticklabels()] == [
            "-1.0",
            "-0.5",
            "0",
            "0.5",
            "1.0",
        ]
        assert ax.get_xlabel() == "time"
        assert ax.get_ylabel() == "value"
        assert ax.get_title() == "Guide fixture"
        assert any(line.get_visible() for line in ax.get_xgridlines())
    finally:
        plt.close(fig)


def test_conformance_guide_query_returns_tick_payload():
    """The canonical guide query returns a typed guide payload."""
    scene = guide_scene()

    result = query_axis_guides(scene.tick_query, scene.view, scene.guide_entries)

    assert result.status == QueryStatus.HIT
    assert result.visual_id == scene.x_axis.id
    assert result.item_id == 1
    assert result.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, GuideQueryPayload)
    assert result.extension_payload.guide_id == scene.x_axis.id
    assert result.extension_payload.role == "tick"
    assert result.extension_payload.axis_dimension == AxisDimension.X
    assert result.extension_payload.tick_value == 0.5
    assert result.extension_payload.text_value == "half"


def test_conformance_guide_query_miss_and_unsupported_statuses():
    """Guide misses and unsupported providers remain distinct statuses."""
    scene = guide_scene()

    miss = query_axis_guides(scene.miss_query, scene.view, scene.guide_entries)
    unsupported = unsupported_guide_query_result(scene.tick_query, "datoviz.v04.panel_axis.wip")

    assert miss.status == QueryStatus.MISS
    assert not miss.hit
    assert unsupported.status == QueryStatus.UNSUPPORTED
    assert not unsupported.hit
    assert "does not support guide queries" in unsupported.diagnostic


def test_conformance_tiled_source_fixture_locks_manifest_and_mosaic():
    """The tiled-source fixture is static, local, and deterministic."""
    scene = tiled_source_scene()

    scene.source.validate_manifest_link(scene.manifest)
    mosaic = scene.provider.get_viewport_mosaic(scene.mosaic_request)

    assert scene.manifest.capability == TILED_IMAGE_EXTENSION_CAPABILITY
    assert scene.source.id == "source:tiled-fixture"
    assert scene.source.locality.value == "synthetic"
    assert scene.source.credential_policy.value == "none"
    assert scene.mosaic_request.source_rect == (-2, -2, 4, 4)
    assert mosaic.source_rect == (0, 0, 2, 2)
    assert mosaic.data.shape == (2, 2, 4)
    assert mosaic.tile_indices == (TileIndex(level=0, x=0, y=0),)


def test_conformance_tiled_source_matplotlib_render_and_query():
    """Matplotlib reference tiled-source behavior is fixture-backed for S018 replay."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scene = tiled_source_scene()
    fig, ax = plt.subplots()
    try:
        artist = render_tiled_image_source(
            ax,
            scene.source,
            scene.provider,
            source_rect=scene.mosaic_request.source_rect,
            extent=scene.extent,
            visual_id=scene.visual_id,
        )
        result = query_tiled_image_source(
            scene.query,
            scene.source,
            scene.provider,
            source_rect=scene.mosaic_request.source_rect,
            extent=scene.extent,
            visual_id=scene.visual_id,
        )

        assert artist.get_gid() == scene.visual_id
        assert tuple(artist.get_extent()) == (0.0, 1.0, -1.0, 0.0)
        assert result.status == QueryStatus.HIT
        assert result.visual_id == scene.visual_id
        assert result.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
        assert isinstance(result.extension_payload, TiledImageQueryPayload)
        assert result.extension_payload.source_id == scene.source.id
        assert result.extension_payload.source_x == 0
        assert result.extension_payload.source_y == 0
        assert result.extension_payload.value == (0, 0, 0, 255)
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
