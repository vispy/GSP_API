"""Resolved layout snapshot extraction for Matplotlib reference figures."""

from __future__ import annotations

from collections.abc import Iterable
from typing import cast

import matplotlib.axes
import matplotlib.backend_bases
import matplotlib.figure
import matplotlib.transforms
import numpy as np

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    LayoutDiagnostic,
    LayoutDiagnosticStatus,
    LayoutLayer,
    LogicalPixelRect,
    PixelOrigin,
    RenderTarget,
    ResolvedGuideBox,
    ResolvedLayoutSnapshot,
    View2D,
)
from gsp.protocol.guides import PanelTextGuide, PanelTextRole


def resolve_matplotlib_layout_snapshot(
    figure: matplotlib.figure.Figure,
    axes: matplotlib.axes.Axes,
    *,
    snapshot_id: str,
    view: View2D | None = None,
    axis_guides: Iterable[AxisGuide] = (),
    panel_text_guides: Iterable[PanelTextGuide] = (),
    device_scale: float = 1.0,
) -> ResolvedLayoutSnapshot:
    """Resolve a GSP layout snapshot from a drawn Matplotlib reference axes."""
    figure.canvas.draw()
    renderer = cast(
        matplotlib.backend_bases.RendererBase,
        getattr(figure.canvas, "get_renderer")(),
    )
    width = float(figure.bbox.width)
    height = float(figure.bbox.height)
    render_target = RenderTarget(
        logical_width_px=width,
        logical_height_px=height,
        device_scale=device_scale,
        dpi=float(figure.dpi),
        pixel_origin=PixelOrigin.TOP_LEFT,
        query_coordinate_space="panel",
    )
    panel_rect = LogicalPixelRect(0.0, 0.0, width, height)
    plot_rect = _rect_from_bbox(axes.get_window_extent(renderer), height)
    axis_guides_tuple = tuple(axis_guides)
    panel_text_guides_tuple = tuple(panel_text_guides)
    axis_label_boxes = _axis_label_boxes(axes, axis_guides_tuple, height, renderer)
    tick_label_boxes = _tick_label_boxes(axes, axis_guides_tuple, height, renderer)
    title_boxes = _title_boxes(axes, panel_text_guides_tuple, height, renderer)
    guide_boxes = axis_label_boxes + tick_label_boxes + title_boxes
    return ResolvedLayoutSnapshot(
        snapshot_id=snapshot_id,
        render_target=render_target,
        panel_rect_px=panel_rect,
        plot_rect_px=plot_rect,
        view_id=view.id if view is not None else None,
        data_to_screen_transform=_data_to_top_left_transform(axes, height),
        guide_boxes=guide_boxes,
        tick_label_boxes=tick_label_boxes,
        axis_label_boxes=axis_label_boxes,
        title_boxes=title_boxes,
        grid_clip_rect_px=plot_rect,
        z_layers=_layout_layers(axis_guides_tuple, panel_text_guides_tuple),
        diagnostics=(
            LayoutDiagnostic(
                code="matplotlib_native_layout_resolved",
                status=LayoutDiagnosticStatus.RESOLVED,
                message="Snapshot extracted from Matplotlib native artist layout after draw.",
            ),
        ),
    )


def _axis_label_boxes(
    axes: matplotlib.axes.Axes,
    guides: tuple[AxisGuide, ...],
    figure_height: float,
    renderer: matplotlib.backend_bases.RendererBase,
) -> tuple[ResolvedGuideBox, ...]:
    boxes: list[ResolvedGuideBox] = []
    for guide in guides:
        artist = axes.xaxis.label if guide.dimension == AxisDimension.X else axes.yaxis.label
        if not artist.get_visible() or not artist.get_text():
            continue
        boxes.append(
            ResolvedGuideBox(
                guide_id=guide.id,
                kind="axis_label",
                rect_px=_rect_from_bbox(artist.get_window_extent(renderer), figure_height),
                role=f"{guide.dimension.value}_axis_label",
                layer="guides",
            )
        )
    return tuple(boxes)


def _tick_label_boxes(
    axes: matplotlib.axes.Axes,
    guides: tuple[AxisGuide, ...],
    figure_height: float,
    renderer: matplotlib.backend_bases.RendererBase,
) -> tuple[ResolvedGuideBox, ...]:
    boxes: list[ResolvedGuideBox] = []
    for guide in guides:
        artists = (
            axes.get_xticklabels()
            if guide.dimension == AxisDimension.X
            else axes.get_yticklabels()
        )
        for artist in artists:
            if not artist.get_visible() or not artist.get_text():
                continue
            boxes.append(
                ResolvedGuideBox(
                    guide_id=guide.id,
                    kind="tick_label",
                    rect_px=_rect_from_bbox(artist.get_window_extent(renderer), figure_height),
                    role=f"{guide.dimension.value}_tick_label",
                    layer="guides",
                )
            )
    return tuple(boxes)


def _title_boxes(
    axes: matplotlib.axes.Axes,
    guides: tuple[PanelTextGuide, ...],
    figure_height: float,
    renderer: matplotlib.backend_bases.RendererBase,
) -> tuple[ResolvedGuideBox, ...]:
    boxes: list[ResolvedGuideBox] = []
    title_guides = tuple(guide for guide in guides if guide.role == PanelTextRole.TITLE)
    if not title_guides:
        return ()
    title_artist = axes.title
    if not title_artist.get_visible() or not title_artist.get_text():
        return ()
    for guide in title_guides:
        boxes.append(
            ResolvedGuideBox(
                guide_id=guide.id,
                kind="title",
                rect_px=_rect_from_bbox(title_artist.get_window_extent(renderer), figure_height),
                role=guide.role.value,
                layer="guides",
            )
        )
    return tuple(boxes)


def _layout_layers(
    axis_guides: tuple[AxisGuide, ...], panel_text_guides: tuple[PanelTextGuide, ...]
) -> tuple[LayoutLayer, ...]:
    layers = [LayoutLayer(object_id=guide.id, layer="guides", z_order=0.0) for guide in axis_guides]
    layers.extend(
        LayoutLayer(object_id=guide.id, layer="guides", z_order=1.0)
        for guide in panel_text_guides
    )
    return tuple(layers)


def _data_to_top_left_transform(
    axes: matplotlib.axes.Axes, figure_height: float
) -> tuple[float, ...]:
    matrix = axes.transData.get_affine().get_matrix()
    flip = np.array(
        [[1.0, 0.0, 0.0], [0.0, -1.0, figure_height], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    top_left = flip @ matrix
    return tuple(float(value) for value in top_left.reshape(-1))


def _rect_from_bbox(
    bbox: matplotlib.transforms.BboxBase, figure_height: float
) -> LogicalPixelRect:
    return LogicalPixelRect(
        x=float(bbox.x0),
        y=float(figure_height - bbox.y1),
        width=float(bbox.width),
        height=float(bbox.height),
    )
