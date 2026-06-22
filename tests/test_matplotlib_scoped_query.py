"""Tests for Matplotlib reference scoped query routing."""

import numpy as np

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    FakeTiledImageProvider,
    PointVisual,
    QueryContributionKind,
    QueryHitPolicy,
    QueryRequest,
    QueryScope,
    QueryStatus,
    TILED_IMAGE_QUERY_PAYLOAD_KIND,
    TiledImageQueryPayload,
    TiledImageSource,
    TickSpec,
    TickSpecKind,
    View2D,
)
from gsp_matplotlib.guide_query import QueryGuideEntry
from gsp_matplotlib.protocol_query import QueryVisualEntry
from gsp_matplotlib.scoped_query import QueryExtensionEntry, query_scoped_scene
from gsp_matplotlib.tiled_image import query_tiled_image_source


def _point() -> PointVisual:
    return PointVisual(
        id="visual:points",
        positions=np.array([[0.5, -1.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([0.25], dtype=np.float32),
    )


def _view() -> View2D:
    return View2D(id="view:main", panel_id="panel:main", x_range=(0.0, 1.0), y_range=(-1.0, 1.0))


def _x_guide() -> AxisGuide:
    return AxisGuide(
        id="guide:x",
        view_id="view:main",
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        tick_spec=TickSpec(
            kind=TickSpecKind.EXPLICIT,
            explicit_values=(0.0, 0.5, 1.0),
            explicit_labels=("zero", "half", "one"),
            target_count=None,
        ),
    )


def _tiled_source() -> TiledImageSource:
    return TiledImageSource(
        id="source:tiles",
        shape=(8, 8, 4),
        tile_shape=(4, 4),
        extent=(-1.0, 1.0, -1.0, 1.0),
    )


def _tiled_entry(*, z_order: int = 0) -> QueryExtensionEntry:
    source = _tiled_source()
    provider = FakeTiledImageProvider(source)
    return QueryExtensionEntry(
        lambda request: query_tiled_image_source(
            request,
            source,
            provider,
            source_rect=(2, 2, 4, 4),
            extent=(-1.0, 1.0, -1.0, 1.0),
            visual_id="visual:tiled-image",
        ),
        extension_payload_kinds=(TILED_IMAGE_QUERY_PAYLOAD_KIND,),
        z_order=z_order,
    )


def test_scoped_query_data_ignores_overlapping_guides():
    result = query_scoped_scene(
        QueryRequest(id="query:data", panel_id="panel:main", coordinate=(0.5, -1.0), scope=QueryScope.DATA),
        visual_entries=(QueryVisualEntry(_point(), z_order=0),),
        view=_view(),
        guide_entries=(QueryGuideEntry(_x_guide(), z_order=1),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "visual:points"
    assert result.hits[0].contribution_kind == QueryContributionKind.DATA


def test_scoped_query_guides_ignores_overlapping_data():
    result = query_scoped_scene(
        QueryRequest(id="query:guides", panel_id="panel:main", coordinate=(0.5, -1.0), scope=QueryScope.GUIDES),
        visual_entries=(QueryVisualEntry(_point(), z_order=2),),
        view=_view(),
        guide_entries=(QueryGuideEntry(_x_guide(), z_order=0),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "guide:x"
    assert result.hits[0].contribution_kind == QueryContributionKind.GUIDE
    assert result.extension_payload.tick_value == 0.5


def test_scoped_query_all_rendered_returns_frontmost_by_reference_z_order():
    result = query_scoped_scene(
        QueryRequest(id="query:all-rendered", panel_id="panel:main", coordinate=(0.5, -1.0), scope=QueryScope.ALL_RENDERED),
        visual_entries=(QueryVisualEntry(_point(), z_order=0),),
        view=_view(),
        guide_entries=(QueryGuideEntry(_x_guide(), z_order=1),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "guide:x"
    assert result.hits == result.hits[:1]
    assert result.hits[0].contribution_kind == QueryContributionKind.GUIDE


def test_scoped_query_all_rendered_all_returns_hits_front_to_back():
    result = query_scoped_scene(
        QueryRequest(
            id="query:all-rendered-all",
            panel_id="panel:main",
            coordinate=(0.5, -1.0),
            scope=QueryScope.ALL_RENDERED,
            hit_policy=QueryHitPolicy.ALL,
        ),
        visual_entries=(QueryVisualEntry(_point(), z_order=0),),
        view=_view(),
        guide_entries=(QueryGuideEntry(_x_guide(), z_order=1),),
    )

    assert result.status == QueryStatus.HIT
    assert [hit.visual_id for hit in result.hits] == ["guide:x", "visual:points"]
    assert [hit.contribution_kind for hit in result.hits] == [QueryContributionKind.GUIDE, QueryContributionKind.DATA]


def test_scoped_query_all_rendered_with_guides_requires_view():
    result = query_scoped_scene(
        QueryRequest(id="query:unsupported", panel_id="panel:main", coordinate=(0.5, -1.0), scope=QueryScope.ALL_RENDERED),
        visual_entries=(QueryVisualEntry(_point(), z_order=0),),
        view=None,
        guide_entries=(QueryGuideEntry(_x_guide(), z_order=1),),
    )

    assert result.status == QueryStatus.UNSUPPORTED
    assert "View2D" in result.diagnostic


def test_scoped_query_data_returns_tiled_extension_payload():
    result = query_scoped_scene(
        QueryRequest(
            id="query:tiled",
            panel_id="panel:main",
            coordinate=(0.25, 0.25),
            scope=QueryScope.DATA,
            requested_extension_payload_kinds=(TILED_IMAGE_QUERY_PAYLOAD_KIND,),
        ),
        extension_entries=(_tiled_entry(),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "visual:tiled-image"
    assert result.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, TiledImageQueryPayload)
    assert result.hits[0].contribution_kind == QueryContributionKind.DATA
    assert result.extension_payload.source_id == "source:tiles"
    assert result.extension_payload.tile_x == 1
    assert result.extension_payload.texel_x == 0


def test_scoped_query_all_rendered_sorts_extension_hits_with_data_hits():
    result = query_scoped_scene(
        QueryRequest(
            id="query:all-rendered-extension",
            panel_id="panel:main",
            coordinate=(0.5, -1.0),
            scope=QueryScope.ALL_RENDERED,
            hit_policy=QueryHitPolicy.ALL,
        ),
        visual_entries=(QueryVisualEntry(_point(), z_order=0),),
        extension_entries=(_tiled_entry(z_order=2),),
    )

    assert result.status == QueryStatus.HIT
    assert [hit.visual_id for hit in result.hits] == ["visual:tiled-image", "visual:points"]
    assert result.hits[0].extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
    assert result.hits[1].extension_payload_kind is None


def test_scoped_query_all_rendered_extension_payload_request_filters_ineligible_guides():
    result = query_scoped_scene(
        QueryRequest(
            id="query:all-rendered-extension-request",
            panel_id="panel:main",
            coordinate=(0.5, -1.0),
            scope=QueryScope.ALL_RENDERED,
            requested_extension_payload_kinds=(TILED_IMAGE_QUERY_PAYLOAD_KIND,),
        ),
        extension_entries=(_tiled_entry(z_order=0),),
        view=_view(),
        guide_entries=(QueryGuideEntry(_x_guide(), z_order=2),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "visual:tiled-image"
    assert result.extension_payload_kind == TILED_IMAGE_QUERY_PAYLOAD_KIND
    assert [hit.visual_id for hit in result.hits] == ["visual:tiled-image"]


def test_scoped_query_data_rejects_unsupported_extension_payload_kind():
    result = query_scoped_scene(
        QueryRequest(
            id="query:bad-extension",
            panel_id="panel:main",
            coordinate=(0.25, 0.25),
            scope=QueryScope.DATA,
            requested_extension_payload_kinds=("gsp.other@0.1.query",),
        ),
        extension_entries=(_tiled_entry(),),
    )

    assert result.status == QueryStatus.UNSUPPORTED
    assert "extension payload" in result.diagnostic
