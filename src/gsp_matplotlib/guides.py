"""Matplotlib realization of semantic GSP guide objects."""

from __future__ import annotations

from typing import Any, Literal

import matplotlib.axes

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisGuideStyle,
    AxisSide,
    PanelTextGuide,
    PanelTextRole,
    View2D,
    logical_px_to_points,
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
            kwargs: dict[str, Any] = {}
            if guide.style.title_font_size_px is not None:
                kwargs["fontsize"] = _px_to_points(axes, guide.style.title_font_size_px)
            if guide.style.guide_margin_px is not None:
                kwargs["pad"] = _px_to_points(axes, guide.style.guide_margin_px)
            axes.set_title(guide.text, **kwargs)


def _render_x_guide(axes: matplotlib.axes.Axes, view: View2D, guide: AxisGuide | None) -> None:
    if guide is None:
        return
    if guide.side != AxisSide.BOTTOM:
        raise ValueError("Matplotlib reference slice only supports bottom x guides")
    axes.set_xlim(view.x_range)
    axes.xaxis.set_visible(guide.visible)
    axes.spines["bottom"].set_visible(guide.visible and guide.spine_visible)
    label_kwargs = _axis_label_kwargs(axes, guide.style)
    axes.set_xlabel(guide.label_text or "", **label_kwargs)
    _apply_tick_style(axes, "x", guide.style)
    if guide.visible:
        ticks = resolve_ticks(guide.tick_spec, view.x_range)
        axes.set_xticks(ticks.values)
        axes.set_xticklabels(ticks.labels)
    else:
        axes.set_xticks(())
        axes.set_xticklabels(())
    axes.grid(guide.grid_visible, axis="x", **_grid_kwargs(axes, guide.style))


def _render_y_guide(axes: matplotlib.axes.Axes, view: View2D, guide: AxisGuide | None) -> None:
    if guide is None:
        return
    if guide.side != AxisSide.LEFT:
        raise ValueError("Matplotlib reference slice only supports left y guides")
    axes.set_ylim(view.y_range)
    axes.yaxis.set_visible(guide.visible)
    axes.spines["left"].set_visible(guide.visible and guide.spine_visible)
    label_kwargs = _axis_label_kwargs(axes, guide.style)
    axes.set_ylabel(guide.label_text or "", **label_kwargs)
    _apply_tick_style(axes, "y", guide.style)
    if guide.visible:
        ticks = resolve_ticks(guide.tick_spec, view.y_range)
        axes.set_yticks(ticks.values)
        axes.set_yticklabels(ticks.labels)
    else:
        axes.set_yticks(())
        axes.set_yticklabels(())
    axes.grid(guide.grid_visible, axis="y", **_grid_kwargs(axes, guide.style))


def _axis_label_kwargs(
    axes: matplotlib.axes.Axes, style: AxisGuideStyle
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if style.axis_label_font_size_px is not None:
        kwargs["fontsize"] = _px_to_points(axes, style.axis_label_font_size_px)
    if style.axis_label_padding_px is not None:
        kwargs["labelpad"] = _px_to_points(axes, style.axis_label_padding_px)
    return kwargs


def _apply_tick_style(
    axes: matplotlib.axes.Axes, axis: Literal["x", "y"], style: AxisGuideStyle
) -> None:
    kwargs: dict[str, Any] = {}
    if style.tick_length_px is not None:
        kwargs["length"] = _px_to_points(axes, style.tick_length_px)
    if style.tick_width_px is not None:
        kwargs["width"] = _px_to_points(axes, style.tick_width_px)
    if style.tick_label_padding_px is not None:
        kwargs["pad"] = _px_to_points(axes, style.tick_label_padding_px)
    if style.tick_label_font_size_px is not None:
        kwargs["labelsize"] = _px_to_points(axes, style.tick_label_font_size_px)
    if kwargs:
        axes.tick_params(axis=axis, **kwargs)


def _grid_kwargs(
    axes: matplotlib.axes.Axes, style: AxisGuideStyle
) -> dict[str, Any]:
    if style.grid_width_px is None:
        return {}
    return {"linewidth": _px_to_points(axes, style.grid_width_px)}


def _px_to_points(axes: matplotlib.axes.Axes, logical_px: float) -> float:
    return logical_px_to_points(logical_px, float(axes.figure.dpi))
