"""Tests for Matplotlib reference scoped query routing."""

import numpy as np

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    PointVisual,
    QueryContributionKind,
    QueryHitPolicy,
    QueryRequest,
    QueryScope,
    QueryStatus,
    TickSpec,
    TickSpecKind,
    View2D,
)
from gsp_matplotlib.guide_query import QueryGuideEntry
from gsp_matplotlib.protocol_query import QueryVisualEntry
from gsp_matplotlib.scoped_query import query_scoped_scene


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
