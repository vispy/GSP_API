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
from gsp.protocol.extensions import TILED_IMAGE_EXTENSION_CAPABILITY
from gsp.protocol.visuals import ImageInterpolation
from gsp_matplotlib.protocol_renderer import render_image_visual


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
    visual = ImageVisual(
        id=visual_id,
        image=mosaic.data,
        extent=extent,
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
    left, right, bottom, top = extent
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

    rect_x, rect_y, rect_w, rect_h = source_rect
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
    rgba01 = tuple(channel / 255.0 for channel in rgba8)
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
        extension_payload_kind=f"{TILED_IMAGE_EXTENSION_CAPABILITY}.query",
        extension_payload=payload,
    )
