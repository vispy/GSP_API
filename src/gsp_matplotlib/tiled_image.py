"""Matplotlib reference proof for local tiled image sources."""

from __future__ import annotations

import matplotlib.axes
import matplotlib.image
import numpy as np

from gsp.protocol import (
    FakeTiledImageProvider,
    ImageOrigin,
    ImageVisual,
    QueryRequest,
    QueryResult,
    QueryStatus,
    TiledImageQueryPayload,
    TiledImageSource,
    ViewportTileRequest,
    VisualFamily,
)
from gsp.protocol.extensions import TILED_IMAGE_QUERY_PAYLOAD_KIND
from gsp.protocol.visuals import ImageInterpolation
from gsp_matplotlib.protocol_renderer import render_image_visual
from gsp_matplotlib.protocol_query import unsupported_query_result


def render_tiled_image_source(
    axes: matplotlib.axes.Axes,
    source: TiledImageSource,
    provider: FakeTiledImageProvider,
    *,
    source_rect: tuple[int, int, int, int],
    extent: tuple[float, float, float, float],
    level: int = 0,
    visual_id: str = "visual:tiled-image",
) -> matplotlib.image.AxesImage:
    """Materialize a viewport mosaic and render it as a reference image."""
    mosaic = provider.get_viewport_mosaic(
        ViewportTileRequest(source_id=source.id, level=level, source_rect=source_rect)
    )
    rendered_extent = _clipped_extent(source_rect, mosaic.source_rect, extent, source.origin)
    visual = ImageVisual(
        id=visual_id,
        image=mosaic.data,
        extent=rendered_extent,
        origin=ImageOrigin(source.origin),
        interpolation=ImageInterpolation.NEAREST,
    )
    return render_image_visual(axes, visual)


def query_tiled_image_source(
    request: QueryRequest,
    source: TiledImageSource,
    provider: FakeTiledImageProvider,
    *,
    source_rect: tuple[int, int, int, int],
    extent: tuple[float, float, float, float],
    level: int = 0,
    visual_id: str = "visual:tiled-image",
) -> QueryResult:
    """Answer a reference query against a materialized tiled-image source."""
    if not set(request.requested_extension_payload_kinds).issubset({TILED_IMAGE_QUERY_PAYLOAD_KIND}):
        return unsupported_query_result(request, "tiled-image query cannot satisfy requested extension payloads")

    try:
        mosaic = provider.get_viewport_mosaic(
            ViewportTileRequest(source_id=source.id, level=level, source_rect=source_rect)
        )
    except ValueError as exc:
        if "does not intersect source bounds" not in str(exc):
            raise
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
        )

    clipped_source_rect = mosaic.source_rect
    rendered_extent = _clipped_extent(source_rect, clipped_source_rect, extent, source.origin)
    left, right, bottom, top = rendered_extent
    x, y = request.coordinate
    x_min, x_max = sorted((left, right))
    y_min, y_max = sorted((bottom, top))
    if not (x_min <= x <= x_max and y_min <= y <= y_max):
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
        )

    rect_x, rect_y, rect_w, rect_h = clipped_source_rect
    u = 0.0 if right == left else (x - left) / (right - left)
    v_extent = 0.0 if top == bottom else (y - bottom) / (top - bottom)
    v = 1.0 - v_extent if source.origin == "upper" else v_extent
    local_x = int(np.clip(np.floor(u * rect_w), 0, rect_w - 1))
    local_y = int(np.clip(np.floor(v * rect_h), 0, rect_h - 1))
    source_x = rect_x + local_x
    source_y = rect_y + local_y
    tile_h, tile_w = source.tile_shape
    tile_x = source_x // tile_w
    tile_y = source_y // tile_h
    texel_x = source_x % tile_w
    texel_y = source_y % tile_h
    rgba8 = provider.pixel_value(level, source_x, source_y)
    rgba01 = (rgba8[0] / 255.0, rgba8[1] / 255.0, rgba8[2] / 255.0, rgba8[3] / 255.0)
    payload = TiledImageQueryPayload(
        source_id=source.id,
        level=level,
        tile_x=tile_x,
        tile_y=tile_y,
        texel_x=texel_x,
        texel_y=texel_y,
        source_x=source_x,
        source_y=source_y,
        uv=(float(u), float(v)),
        value=rgba8,
    )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=visual_id,
        visual_family=VisualFamily.IMAGE,
        texel=(source_y, source_x),
        visual_coordinate=(float(u), float(v)),
        data_coordinate=(float(x), float(y)),
        displayed_rgba=rgba01,
        value=rgba8,
        extension_payload_kind=TILED_IMAGE_QUERY_PAYLOAD_KIND,
        extension_payload=payload,
    )


def _clipped_extent(
    requested_source_rect: tuple[int, int, int, int],
    clipped_source_rect: tuple[int, int, int, int],
    extent: tuple[float, float, float, float],
    origin: str,
) -> tuple[float, float, float, float]:
    rect_x, rect_y, rect_w, rect_h = requested_source_rect
    clipped_x, clipped_y, clipped_w, clipped_h = clipped_source_rect
    left, right, bottom, top = extent

    x0 = (clipped_x - rect_x) / rect_w
    x1 = (clipped_x + clipped_w - rect_x) / rect_w
    rendered_left = left + x0 * (right - left)
    rendered_right = left + x1 * (right - left)

    y0 = (clipped_y - rect_y) / rect_h
    y1 = (clipped_y + clipped_h - rect_y) / rect_h
    if origin == "upper":
        rendered_top = top - y0 * (top - bottom)
        rendered_bottom = top - y1 * (top - bottom)
    else:
        rendered_bottom = bottom + y0 * (top - bottom)
        rendered_top = bottom + y1 * (top - bottom)

    return (float(rendered_left), float(rendered_right), float(rendered_bottom), float(rendered_top))
