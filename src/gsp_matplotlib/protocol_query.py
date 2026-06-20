"""Reference panel-query proof for protocol visuals."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterable

import numpy as np

from gsp.protocol.query import QueryRequest, QueryResult, QueryStatus, VisualFamily
from gsp.protocol.visuals import ImageOrigin, ImageVisual, PointVisual


@dataclass(frozen=True, slots=True)
class QueryVisualEntry:
    """Visual plus z-order for reference query evaluation."""

    visual: PointVisual | ImageVisual
    z_order: int = 0


def query_visuals(
    request: QueryRequest,
    entries: Iterable[QueryVisualEntry],
    *,
    panel_bounds: tuple[float, float, float, float] | None = None,
) -> QueryResult:
    """Answer a panel query against formal visual models.

    This reference implementation evaluates simple data/NDC coordinates directly.
    It is deliberately CPU-side and deterministic; Datoviz should later provide a
    GPU-authoritative implementation with the same result schema.
    """
    if panel_bounds is not None and not _contains(panel_bounds, request.coordinate):
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.OUTSIDE_PANEL,
            hit=False,
            panel_coordinate=request.coordinate,
        )

    hits: list[QueryResult] = []
    for entry in sorted(entries, key=lambda item: item.z_order, reverse=True):
        visual = entry.visual
        if isinstance(visual, PointVisual):
            hit = _query_point_visual(request, visual)
        elif isinstance(visual, ImageVisual):
            hit = _query_image_visual(request, visual)
        else:
            hit = None
        if hit is not None:
            hits.append(hit)

    if not hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
        )
    return hits[0]


def unsupported_query_result(request: QueryRequest, diagnostic: str) -> QueryResult:
    """Return a standard unsupported query result for capability-gated callers."""
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.UNSUPPORTED,
        hit=False,
        panel_coordinate=request.coordinate,
        diagnostic=diagnostic,
    )


def failed_query_result(request: QueryRequest, diagnostic: str) -> QueryResult:
    """Return a standard backend/readback failure query result."""
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.FAILED,
        hit=False,
        panel_coordinate=request.coordinate,
        diagnostic=diagnostic,
    )


def _contains(bounds: tuple[float, float, float, float], coordinate: tuple[float, float]) -> bool:
    left, right, bottom, top = bounds
    x, y = coordinate
    x_min, x_max = sorted((left, right))
    y_min, y_max = sorted((bottom, top))
    return x_min <= x <= x_max and y_min <= y <= y_max


def _query_point_visual(request: QueryRequest, visual: PointVisual) -> QueryResult | None:
    positions = visual.positions[:, :2]
    sizes = visual.sizes if isinstance(visual.sizes, np.ndarray) else np.full(positions.shape[0], visual.sizes)
    colors = _rgba01(visual.colors)
    query = np.array(request.coordinate, dtype=np.float64)

    best_index: int | None = None
    best_distance = float("inf")
    for index, (position, size) in enumerate(zip(positions, sizes)):
        radius = sqrt(float(size) / np.pi)
        distance = float(np.linalg.norm(query - position.astype(np.float64)))
        if distance <= radius and distance < best_distance:
            best_index = index
            best_distance = distance

    if best_index is None:
        return None

    point = positions[best_index]
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=visual.id,
        visual_family=VisualFamily.POINT,
        item_id=best_index,
        visual_coordinate=(float(point[0]), float(point[1])),
        data_coordinate=(float(point[0]), float(point[1])),
        displayed_rgba=tuple(float(x) for x in colors[best_index]),
    )


def _query_image_visual(request: QueryRequest, visual: ImageVisual) -> QueryResult | None:
    left, right, bottom, top = visual.extent
    x, y = request.coordinate
    x_min, x_max = sorted((left, right))
    y_min, y_max = sorted((bottom, top))
    if not (x_min <= x <= x_max and y_min <= y <= y_max):
        return None

    height = visual.image.shape[0]
    width = visual.image.shape[1]
    if width <= 0 or height <= 0:
        return None

    u = 0.0 if right == left else (x - left) / (right - left)
    v_extent = 0.0 if top == bottom else (y - bottom) / (top - bottom)
    v = 1.0 - v_extent if visual.origin == ImageOrigin.UPPER else v_extent

    col = int(np.clip(np.floor(u * width), 0, width - 1))
    row = int(np.clip(np.floor(v * height), 0, height - 1))
    value = visual.image[row, col]
    rgba = _image_value_to_rgba(value)

    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=visual.id,
        visual_family=VisualFamily.IMAGE,
        texel=(row, col),
        visual_coordinate=(float(u), float(v)),
        data_coordinate=(float(x), float(y)),
        displayed_rgba=rgba,
        value=_python_value(value),
    )


def _rgba01(colors: np.ndarray) -> np.ndarray:
    if colors.dtype == np.dtype(np.uint8):
        return colors.astype(np.float64) / 255.0
    return colors.astype(np.float64)


def _image_value_to_rgba(value: np.ndarray | np.generic) -> tuple[float, float, float, float]:
    array = np.asarray(value)
    scale = 255.0 if array.dtype == np.dtype(np.uint8) else 1.0
    flat = array.astype(np.float64).reshape(-1) / scale
    if flat.size == 1:
        channel = float(flat[0])
        return (channel, channel, channel, 1.0)
    if flat.size == 3:
        return (float(flat[0]), float(flat[1]), float(flat[2]), 1.0)
    return (float(flat[0]), float(flat[1]), float(flat[2]), float(flat[3]))


def _python_value(value: np.ndarray | np.generic) -> object:
    array = np.asarray(value)
    if array.ndim == 0:
        return array.item()
    return tuple(array.tolist())
