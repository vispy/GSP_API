"""Tests for bounded reference guide query support."""

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    GUIDE_QUERY_PAYLOAD_KIND,
    GuideQueryPayload,
    QueryRequest,
    QueryStatus,
    TickSpec,
    TickSpecKind,
    View2D,
)
from gsp_matplotlib.guide_query import QueryGuideEntry, query_axis_guides, unsupported_guide_query_result


def test_query_axis_guides_hits_explicit_x_tick():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(0.0, 1.0), y_range=(-1.0, 1.0))
    guide = AxisGuide(
        id="guide:x",
        view_id=view.id,
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        tick_spec=TickSpec(
            kind=TickSpecKind.EXPLICIT,
            explicit_values=(0.0, 0.5, 1.0),
            explicit_labels=("zero", "half", "one"),
            target_count=None,
        ),
    )

    result = query_axis_guides(
        QueryRequest(
            id="query:guide",
            panel_id="panel:main",
            coordinate=(0.5, -1.0),
            layout_snapshot_id="layout:matplotlib",
        ),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.HIT
    assert result.layout_snapshot_id == "layout:matplotlib"
    assert result.visual_id == "guide:x"
    assert result.item_id == 1
    assert result.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND
    assert isinstance(result.extension_payload, GuideQueryPayload)
    assert result.extension_payload.role == "tick"
    assert result.extension_payload.axis_dimension == AxisDimension.X
    assert result.extension_payload.tick_value == 0.5
    assert result.extension_payload.text_value == "half"


def test_query_axis_guides_hits_auto_y_tick():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(-1.0, 1.0), y_range=(-1.0, 1.0))
    guide = AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT)

    result = query_axis_guides(
        QueryRequest(id="query:y-guide", panel_id="panel:main", coordinate=(-1.0, 0.5)),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "guide:y"
    assert result.extension_payload.tick_value == 0.5
    assert result.extension_payload.text_value == "0.5"


def test_query_axis_guides_hits_reversed_auto_x_tick_from_same_view_snapshot():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(1.0, -1.0), y_range=(1.0, -1.0))
    guide = AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM)

    result = query_axis_guides(
        QueryRequest(id="query:reversed-x-guide", panel_id="panel:main", coordinate=(0.5, 1.0)),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "guide:x"
    assert result.item_id == 3
    assert result.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND
    assert result.extension_payload.tick_value == 0.5
    assert result.extension_payload.text_value == "0.5"


def test_query_axis_guides_hits_reversed_explicit_y_tick_from_same_view_snapshot():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(1.0, -1.0), y_range=(1.0, -1.0))
    guide = AxisGuide(
        id="guide:y",
        view_id=view.id,
        dimension=AxisDimension.Y,
        side=AxisSide.LEFT,
        tick_spec=TickSpec(
            kind=TickSpecKind.EXPLICIT,
            explicit_values=(1.0, 0.0, -1.0),
            explicit_labels=("top", "center", "bottom"),
            target_count=None,
        ),
    )

    result = query_axis_guides(
        QueryRequest(id="query:reversed-y-guide", panel_id="panel:main", coordinate=(1.0, -1.0)),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "guide:y"
    assert result.item_id == 2
    assert result.extension_payload.tick_value == -1.0
    assert result.extension_payload.text_value == "bottom"


def test_query_axis_guides_hits_spine_inside_reversed_view_bounds():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(1.0, -1.0), y_range=(1.0, -1.0))
    guide = AxisGuide(
        id="guide:x",
        view_id=view.id,
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        label_text="time",
        tick_spec=TickSpec(kind=TickSpecKind.NONE, target_count=None),
    )

    result = query_axis_guides(
        QueryRequest(id="query:reversed-spine", panel_id="panel:main", coordinate=(0.25, 1.0)),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_id == "guide:x"
    assert result.extension_payload.role == "spine"
    assert result.extension_payload.tick_value is None
    assert result.extension_payload.text_value == "time"


def test_query_axis_guides_miss_when_coordinate_is_not_on_guide():
    view = View2D(id="view:main", panel_id="panel:main")
    guide = AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM)

    result = query_axis_guides(
        QueryRequest(id="query:miss", panel_id="panel:main", coordinate=(0.0, 0.0)),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.MISS
    assert not result.hit


def test_query_axis_guides_ignores_hidden_guides():
    view = View2D(id="view:main", panel_id="panel:main")
    guide = AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, visible=False)

    result = query_axis_guides(
        QueryRequest(id="query:hidden", panel_id="panel:main", coordinate=(0.0, -1.0)),
        view,
        (QueryGuideEntry(guide),),
    )

    assert result.status == QueryStatus.MISS


def test_unsupported_guide_query_result_is_not_miss():
    result = unsupported_guide_query_result(
        QueryRequest(id="query:unsupported", panel_id="panel:main", coordinate=(0.0, 0.0)),
        "datoviz.v04.panel_axis.wip",
    )

    assert result.status == QueryStatus.UNSUPPORTED
    assert not result.hit
    assert "does not support guide queries" in result.diagnostic
