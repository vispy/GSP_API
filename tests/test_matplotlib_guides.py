"""Tests for Matplotlib realization of semantic guide objects."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

import numpy as np

import vispy2 as vp
from gsp.protocol import AxisDimension, AxisGuide, AxisSide, PanelTextGuide, PanelTextRole, TickSpec, TickSpecKind, View2D
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides


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


def test_render_panel_text_guide_sets_title():
    fig, ax = plt.subplots()

    try:
        render_panel_text_guides(ax, (PanelTextGuide(id="guide:title", panel_id="panel:main", role=PanelTextRole.TITLE, text="Demo"),))

        assert ax.get_title() == "Demo"
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
