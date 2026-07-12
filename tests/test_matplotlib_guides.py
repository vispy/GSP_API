"""Tests for Matplotlib realization of semantic guide objects."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import numpy as np

import pytest
import gsp_vispy2 as vp
from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisGuideStyle,
    AxisSide,
    LogicalPixelRect,
    PanelTextGuide,
    PanelTextGuideStyle,
    PanelTextRole,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryStatus,
    RenderTarget,
    ResolvedGuideBox,
    ResolvedLayoutSnapshot,
    TickSpec,
    TickSpecKind,
    View2D,
    logical_px_to_points,
)
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides
from gsp_matplotlib.layout import resolve_matplotlib_layout_snapshot
from gsp_matplotlib.layout_query import query_resolved_layout_guides


def test_render_axis_guides_uses_explicit_gsp_ticks_and_labels():
    fig, ax = plt.subplots()
    view = View2D(id="view:main", panel_id="panel:main", x_range=(0.0, 1.0), y_range=(-1.0, 1.0))
    guides = (
        AxisGuide(
            id="guide:x",
            view_id=view.id,
            dimension=AxisDimension.X,
            side=AxisSide.BOTTOM,
            label_text="time",
            tick_spec=TickSpec(
                kind=TickSpecKind.EXPLICIT,
                explicit_values=(0.0, 0.5, 1.0),
                explicit_labels=("zero", "half", "one"),
                target_count=None,
            ),
        ),
        AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, label_text="value"),
    )

    try:
        render_axis_guides(ax, view, guides)

        assert list(ax.get_xticks()) == [0.0, 0.5, 1.0]
        assert [label.get_text() for label in ax.get_xticklabels()] == ["zero", "half", "one"]
        assert ax.get_xlabel() == "time"
        assert ax.get_ylabel() == "value"
    finally:
        plt.close(fig)


def test_render_axis_guides_uses_auto_linear_nice_ticks_not_native_locator():
    fig, ax = plt.subplots()
    view = View2D(id="view:main", panel_id="panel:main", x_range=(-1.0, 1.0), y_range=(0.0, 5000.0))

    try:
        render_axis_guides(
            ax,
            view,
            (
                AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM),
                AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, tick_spec=TickSpec(target_count=5)),
            ),
        )

        assert list(ax.get_xticks()) == [-1.0, -0.5, 0.0, 0.5, 1.0]
        assert [label.get_text() for label in ax.get_yticklabels()] == ["0", "1e+03", "2e+03", "3e+03", "4e+03", "5e+03"]
    finally:
        plt.close(fig)


def test_render_axis_guides_accepts_reversed_view2d_limits():
    fig, ax = plt.subplots()
    view = View2D(id="view:main", panel_id="panel:main", x_range=(1.0, -1.0), y_range=(5.0, -5.0))

    try:
        render_axis_guides(
            ax,
            view,
            (
                AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM),
                AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT),
            ),
        )

        assert ax.get_xlim() == (1.0, -1.0)
        assert ax.get_ylim() == (5.0, -5.0)
        assert list(ax.get_xticks()) == [-1.0, -0.5, 0.0, 0.5, 1.0]
        assert list(ax.get_yticks()) == [-4.0, -2.0, 0.0, 2.0, 4.0]
    finally:
        plt.close(fig)


def test_render_axis_guides_preserves_explicit_ticks_under_reversed_view2d_limits():
    fig, ax = plt.subplots()
    view = View2D(id="view:main", panel_id="panel:main", x_range=(1.0, -1.0), y_range=(-1.0, 1.0))
    guide = AxisGuide(
        id="guide:x",
        view_id=view.id,
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        tick_spec=TickSpec(
            kind=TickSpecKind.EXPLICIT,
            explicit_values=(1.0, 0.0, -1.0),
            explicit_labels=("right", "center", "left"),
            target_count=None,
        ),
    )

    try:
        render_axis_guides(ax, view, (guide,))

        assert ax.get_xlim() == (1.0, -1.0)
        assert list(ax.get_xticks()) == [1.0, 0.0, -1.0]
        assert [label.get_text() for label in ax.get_xticklabels()] == ["right", "center", "left"]
    finally:
        plt.close(fig)


def test_render_panel_text_guide_sets_title():
    fig, ax = plt.subplots()

    try:
        render_panel_text_guides(ax, (PanelTextGuide(id="guide:title", panel_id="panel:main", role=PanelTextRole.TITLE, text="Demo"),))

        assert ax.get_title() == "Demo"
    finally:
        plt.close(fig)


def test_render_guides_maps_logical_pixel_style_to_matplotlib_points():
    fig, ax = plt.subplots(dpi=100)
    view = View2D(id="view:main", panel_id="panel:main")
    guide = AxisGuide(
        id="guide:x",
        view_id=view.id,
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        label_text="time",
        grid_visible=True,
        style=AxisGuideStyle(
            axis_label_font_size_px=16.0,
            tick_label_font_size_px=12.0,
            tick_length_px=6.0,
            tick_width_px=2.0,
            axis_label_padding_px=8.0,
            tick_label_padding_px=4.0,
            grid_width_px=1.5,
        ),
    )
    title = PanelTextGuide(
        id="guide:title",
        panel_id="panel:main",
        role=PanelTextRole.TITLE,
        text="Styled",
        style=PanelTextGuideStyle(title_font_size_px=20.0, guide_margin_px=10.0),
    )

    try:
        render_axis_guides(ax, view, (guide,))
        render_panel_text_guides(ax, (title,))
        fig.canvas.draw()

        assert ax.xaxis.label.get_fontsize() == pytest.approx(logical_px_to_points(16.0, 100.0))
        assert ax.title.get_fontsize() == pytest.approx(logical_px_to_points(20.0, 100.0))
        assert ax.xaxis.labelpad == pytest.approx(logical_px_to_points(8.0, 100.0))
        first_tick = ax.xaxis.majorTicks[0]
        assert first_tick.tick1line.get_markersize() == pytest.approx(logical_px_to_points(6.0, 100.0))
        assert first_tick.tick1line.get_markeredgewidth() == pytest.approx(logical_px_to_points(2.0, 100.0))
        assert ax.get_xticklabels()[0].get_fontsize() == pytest.approx(logical_px_to_points(12.0, 100.0))
        assert ax.get_xgridlines()[0].get_linewidth() == pytest.approx(logical_px_to_points(1.5, 100.0))
    finally:
        plt.close(fig)


def test_grid_visibility_follows_axis_guides():
    fig, ax = plt.subplots()
    view = View2D(id="view:main", panel_id="panel:main")

    try:
        render_axis_guides(
            ax,
            view,
            (
                AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, grid_visible=True),
                AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, grid_visible=False),
            ),
        )

        assert any(line.get_visible() for line in ax.get_xgridlines())
        assert not any(line.get_visible() for line in ax.get_ygridlines())
    finally:
        plt.close(fig)


def test_grid_visibility_follows_axis_guides_with_reversed_limits():
    fig, ax = plt.subplots()
    view = View2D(id="view:main", panel_id="panel:main", x_range=(1.0, -1.0), y_range=(1.0, -1.0))

    try:
        render_axis_guides(
            ax,
            view,
            (
                AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, grid_visible=True),
                AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, grid_visible=True),
            ),
        )

        assert ax.get_xlim() == (1.0, -1.0)
        assert ax.get_ylim() == (1.0, -1.0)
        assert any(line.get_visible() for line in ax.get_xgridlines())
        assert any(line.get_visible() for line in ax.get_ygridlines())
    finally:
        plt.close(fig)


def test_vispy2_matplotlib_render_realizes_default_guides_without_mutating_visuals():
    fig, ax = vp.subplots()
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    point = ax.scatter(np.array([[0.0, 0.0]], dtype=np.float32), id="visual:points")

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert fig.visuals() == (point,)
        assert len(fig.axis_guides()) == 2
        assert list(mpl_axes.get_xticks()) == [-1.0, -0.5, 0.0, 0.5, 1.0]
    finally:
        plt.close(mpl_fig)


def test_resolve_matplotlib_layout_snapshot_exposes_native_guide_geometry():
    fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=100)
    view = View2D(id="view:main", panel_id="panel:main", x_range=(0.0, 1.0), y_range=(-1.0, 1.0))
    axis_guides = (
        AxisGuide(
            id="guide:x",
            view_id=view.id,
            dimension=AxisDimension.X,
            side=AxisSide.BOTTOM,
            label_text="time",
            tick_spec=TickSpec(
                kind=TickSpecKind.EXPLICIT,
                explicit_values=(0.0, 0.5, 1.0),
                explicit_labels=("zero", "half", "one"),
                target_count=None,
            ),
            grid_visible=True,
        ),
        AxisGuide(
            id="guide:y",
            view_id=view.id,
            dimension=AxisDimension.Y,
            side=AxisSide.LEFT,
            label_text="value",
            grid_visible=True,
        ),
    )
    title = PanelTextGuide(
        id="guide:title",
        panel_id="panel:main",
        role=PanelTextRole.TITLE,
        text="Resolved layout",
    )

    try:
        render_axis_guides(ax, view, axis_guides)
        render_panel_text_guides(ax, (title,))
        fig.tight_layout()

        snapshot = resolve_matplotlib_layout_snapshot(
            fig,
            ax,
            snapshot_id="layout:matplotlib",
            view=view,
            axis_guides=axis_guides,
            panel_text_guides=(title,),
        )

        assert snapshot.render_target.logical_width_px == 640
        assert snapshot.render_target.logical_height_px == 480
        assert snapshot.view_id == "view:main"
        assert snapshot.plot_rect_px.width > 0
        assert snapshot.plot_rect_px.height > 0
        assert snapshot.grid_clip_rect_px == snapshot.plot_rect_px
        assert [box.kind for box in snapshot.title_boxes] == ["title"]
        assert snapshot.title_boxes[0].rect_px.y < snapshot.plot_rect_px.y
        assert any(box.role == "x_axis_label" for box in snapshot.axis_label_boxes)
        assert any(box.role == "y_axis_label" for box in snapshot.axis_label_boxes)
        assert any(box.role == "x_tick_label" for box in snapshot.tick_label_boxes)
        assert any(box.role == "y_tick_label" for box in snapshot.tick_label_boxes)
        assert len(snapshot.data_to_screen_transform) == 9
    finally:
        plt.close(fig)


def test_resolve_matplotlib_layout_snapshot_records_device_scale_metadata():
    fig, ax = plt.subplots(figsize=(3.2, 2.4), dpi=100)
    try:
        snapshot = resolve_matplotlib_layout_snapshot(
            fig,
            ax,
            snapshot_id="layout:hidpi",
            device_scale=2.0,
        )

        assert snapshot.render_target.logical_width_px == 320
        assert snapshot.render_target.logical_height_px == 240
        assert snapshot.render_target.device_scale == 2.0
        assert snapshot.render_target.framebuffer_width_px == 640
        assert snapshot.render_target.framebuffer_height_px == 480
    finally:
        plt.close(fig)


def test_query_resolved_matplotlib_layout_guides_hits_title_box():
    fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=100)
    view = View2D(id="view:main", panel_id="panel:main")
    axis_guides = (
        AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, label_text="x"),
        AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, label_text="y"),
    )
    title = PanelTextGuide(
        id="guide:title",
        panel_id="panel:main",
        role=PanelTextRole.TITLE,
        text="Queryable title",
    )

    try:
        render_axis_guides(ax, view, axis_guides)
        render_panel_text_guides(ax, (title,))
        fig.tight_layout()
        snapshot = resolve_matplotlib_layout_snapshot(
            fig,
            ax,
            snapshot_id="layout:matplotlib",
            view=view,
            axis_guides=axis_guides,
            panel_text_guides=(title,),
        )
        title_rect = snapshot.title_boxes[0].rect_px
        result = query_resolved_layout_guides(
            QueryRequest(
                id="query:title",
                panel_id="panel:main",
                coordinate=(
                    title_rect.x + title_rect.width / 2.0,
                    title_rect.y + title_rect.height / 2.0,
                ),
                coordinate_space=QueryCoordinateSpace.PANEL,
                layout_snapshot_id=snapshot.snapshot_id,
            ),
            snapshot,
        )

        assert result.status == QueryStatus.HIT
        assert result.visual_id == "guide:title"
        assert result.layout_snapshot_id == "layout:matplotlib"
        assert result.extension_payload.guide_id == "guide:title"
        assert result.extension_payload.role == "title"
    finally:
        plt.close(fig)


def test_query_resolved_matplotlib_layout_guides_returns_all_overlapping_boxes():
    synthetic = ResolvedLayoutSnapshot(
        snapshot_id="layout:synthetic",
        render_target=RenderTarget(logical_width_px=100, logical_height_px=100),
        panel_rect_px=LogicalPixelRect(0, 0, 100, 100),
        plot_rect_px=LogicalPixelRect(10, 10, 80, 80),
        title_boxes=(
            ResolvedGuideBox(guide_id="guide:title", kind="title", role="title", rect_px=LogicalPixelRect(20, 5, 60, 20)),
        ),
        axis_label_boxes=(
            ResolvedGuideBox(guide_id="guide:x", kind="axis_label", role="x_axis_label", rect_px=LogicalPixelRect(20, 15, 60, 20)),
        ),
    )
    result = query_resolved_layout_guides(
        QueryRequest(
            id="query:all-guides",
            panel_id="panel:main",
            coordinate=(50, 18),
            coordinate_space=QueryCoordinateSpace.PANEL,
            hit_policy=QueryHitPolicy.ALL,
        ),
        synthetic,
    )

    assert result.status == QueryStatus.HIT
    assert [hit.visual_id for hit in result.hits] == ["guide:title", "guide:x"]
