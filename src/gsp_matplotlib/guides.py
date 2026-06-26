"""Matplotlib realization of semantic GSP guide objects."""

from __future__ import annotations

import matplotlib.axes

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    PanelTextGuide,
    PanelTextRole,
    View2D,
    resolve_ticks,
)


def render_axis_guides(axes: matplotlib.axes.Axes, view: View2D, guides: tuple[AxisGuide, ...]) -> None:
    """Realize semantic axis guides through Matplotlib native axis artists."""
    x_guides = tuple(guide for guide in guides if guide.dimension == AxisDimension.X)
    y_guides = tuple(guide for guide in guides if guide.dimension == AxisDimension.Y)
    _render_x_guide(axes, view, x_guides[0] if x_guides else None)
    _render_y_guide(axes, view, y_guides[0] if y_guides else None)


def render_panel_text_guides(axes: matplotlib.axes.Axes, text_guides: tuple[PanelTextGuide, ...]) -> None:
    """Realize semantic panel text guides through Matplotlib native artists."""
    for guide in text_guides:
        if guide.role == PanelTextRole.TITLE:
            axes.set_title(guide.text)


def _render_x_guide(axes: matplotlib.axes.Axes, view: View2D, guide: AxisGuide | None) -> None:
    if guide is None:
        return
    if guide.side != AxisSide.BOTTOM:
        raise ValueError("Matplotlib reference slice only supports bottom x guides")
    axes.set_xlim(view.x_range)
    axes.xaxis.set_visible(guide.visible)
    axes.spines["bottom"].set_visible(guide.visible and guide.spine_visible)
    axes.set_xlabel(guide.label_text or "")
    if guide.visible:
        ticks = resolve_ticks(guide.tick_spec, view.x_range)
        axes.set_xticks(ticks.values)
        axes.set_xticklabels(ticks.labels)
    else:
        axes.set_xticks(())
        axes.set_xticklabels(())
    axes.grid(guide.grid_visible, axis="x")


def _render_y_guide(axes: matplotlib.axes.Axes, view: View2D, guide: AxisGuide | None) -> None:
    if guide is None:
        return
    if guide.side != AxisSide.LEFT:
        raise ValueError("Matplotlib reference slice only supports left y guides")
    axes.set_ylim(view.y_range)
    axes.yaxis.set_visible(guide.visible)
    axes.spines["left"].set_visible(guide.visible and guide.spine_visible)
    axes.set_ylabel(guide.label_text or "")
    if guide.visible:
        ticks = resolve_ticks(guide.tick_spec, view.y_range)
        axes.set_yticks(ticks.values)
        axes.set_yticklabels(ticks.labels)
    else:
        axes.set_yticks(())
        axes.set_yticklabels(())
    axes.grid(guide.grid_visible, axis="y")
