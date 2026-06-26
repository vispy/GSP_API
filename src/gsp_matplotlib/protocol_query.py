"""Reference panel-query proof for protocol visuals."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import sqrt
from typing import Iterable

import numpy as np

from gsp.protocol.color import ColorScale, ScalarColorSlot
from gsp.protocol.query import (
    MESH_QUERY_PAYLOAD_KIND,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    TEXT_QUERY_PAYLOAD_KIND,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    MeshQueryPayload,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryStatus,
    ScalarColorQueryPayload,
    TransformQueryPayload,
    VisualFamily,
)
from gsp.protocol import AffineTransform2DResource, CoordinateSpace, InverseStatus, View2D
from gsp.protocol.visuals import (
    ImageOrigin,
    ImageVisual,
    MarkerVisual,
    MeshColorMode,
    MeshVisual,
    PointVisual,
    TextVisual,
)
from gsp_matplotlib.color_mapping import map_scalar_value, resolve_color_scale
from gsp_matplotlib.transforms import (
    binding_inline_digest,
    binding_transform_ids,
    declared_to_panel_ndc,
    inverse_transform_coordinate,
    transformed_positions,
)


@dataclass(frozen=True, slots=True)
class QueryVisualEntry:
    """Visual plus z-order for reference query evaluation."""

    visual: PointVisual | ImageVisual | TextVisual | MeshVisual | MarkerVisual
    z_order: int = 0


def query_visuals(
    request: QueryRequest,
    entries: Iterable[QueryVisualEntry],
    *,
    panel_bounds: tuple[float, float, float, float] | None = None,
    color_scales: Mapping[str, ColorScale] | None = None,
    view: View2D | None = None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None = None,
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
            hit = _query_point_visual(
                request,
                visual,
                color_scales=color_scales,
                view=view,
                transform_resources=transform_resources,
            )
        elif isinstance(visual, MarkerVisual):
            hit = _query_marker_visual(
                request,
                visual,
                color_scales=color_scales,
                view=view,
                transform_resources=transform_resources,
            )
        elif isinstance(visual, ImageVisual):
            hit = _query_image_visual(request, visual, color_scales=color_scales)
        elif isinstance(visual, TextVisual):
            hit = _query_text_visual(
                request, visual, view=view, transform_resources=transform_resources
            )
        elif isinstance(visual, MeshVisual):
            hit = _query_mesh_visual(
                request, visual, view=view, transform_resources=transform_resources
            )
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
    if request.hit_policy == QueryHitPolicy.ALL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            hits=tuple(hit.hits[0] for hit in hits),
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


def _contains(
    bounds: tuple[float, float, float, float], coordinate: tuple[float, float]
) -> bool:
    left, right, bottom, top = bounds
    x, y = coordinate
    x_min, x_max = sorted((left, right))
    y_min, y_max = sorted((bottom, top))
    return x_min <= x <= x_max and y_min <= y <= y_max


def _query_point_visual(
    request: QueryRequest,
    visual: PointVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None,
    view: View2D | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> QueryResult | None:
    source_positions = visual.positions[:, :2]
    positions = transformed_positions(
        visual.positions, visual.transform, transform_resources
    )
    sizes = (
        visual.sizes
        if isinstance(visual.sizes, np.ndarray)
        else np.full(positions.shape[0], visual.sizes)
    )
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
    source = source_positions[best_index]
    rgba, payload = _point_color_query_payload(
        visual, best_index, color_scales=color_scales
    )
    extension_kind, extension_payload = _transform_or_existing_payload(
        visual,
        request,
        (float(point[0]), float(point[1])),
        (float(source[0]), float(source[1])),
        view,
        existing_kind=SCALAR_COLOR_QUERY_PAYLOAD_KIND if payload else None,
        existing_payload=payload,
    )
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
        displayed_rgba=rgba,
        value=_point_query_value(visual, best_index),
        extension_payload_kind=extension_kind,
        extension_payload=extension_payload,
    )


def _query_image_visual(
    request: QueryRequest,
    visual: ImageVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None,
) -> QueryResult | None:
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
    rgba, payload = _image_color_query_payload(
        visual, value, row, col, color_scales=color_scales
    )

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
        extension_payload_kind=SCALAR_COLOR_QUERY_PAYLOAD_KIND if payload else None,
        extension_payload=payload,
    )


def _query_marker_visual(
    request: QueryRequest,
    visual: MarkerVisual,
    *,
    color_scales: Mapping[str, ColorScale] | None,
    view: View2D | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> QueryResult | None:
    source_positions = visual.positions[:, :2]
    positions = transformed_positions(
        visual.positions, visual.transform, transform_resources
    )
    sizes = (
        visual.sizes
        if isinstance(visual.sizes, np.ndarray)
        else np.full(positions.shape[0], visual.sizes)
    )
    query = np.array(request.coordinate, dtype=np.float64)

    best_index: int | None = None
    best_distance = float("inf")
    for index, (position, size) in enumerate(zip(positions, sizes, strict=True)):
        radius = sqrt(float(size) / np.pi)
        distance = float(np.linalg.norm(query - position.astype(np.float64)))
        if distance <= radius and distance < best_distance:
            best_index = index
            best_distance = distance

    if best_index is None:
        return None

    marker = positions[best_index]
    source = source_positions[best_index]
    rgba, payload = _marker_color_query_payload(
        visual, best_index, color_scales=color_scales
    )
    extension_kind, extension_payload = _transform_or_existing_payload(
        visual,
        request,
        (float(marker[0]), float(marker[1])),
        (float(source[0]), float(source[1])),
        view,
        existing_kind=SCALAR_COLOR_QUERY_PAYLOAD_KIND if payload else None,
        existing_payload=payload,
    )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=visual.id,
        visual_family="marker",
        item_id=best_index,
        visual_coordinate=(float(marker[0]), float(marker[1])),
        data_coordinate=(float(marker[0]), float(marker[1])),
        displayed_rgba=rgba,
        value=_marker_query_value(visual, best_index),
        extension_payload_kind=extension_kind,
        extension_payload=extension_payload,
    )


def _query_text_visual(
    request: QueryRequest,
    visual: TextVisual,
    *,
    view: View2D | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> QueryResult | None:
    source_positions = visual.positions[:, :2]
    positions = transformed_positions(
        visual.positions, visual.transform, transform_resources
    )
    sizes = visual.font_size_values()
    colors = _rgba01(visual.rgba_values())
    query = np.array(request.coordinate, dtype=np.float64)

    best_index: int | None = None
    best_distance = float("inf")
    for index, (position, size) in enumerate(zip(positions, sizes, strict=True)):
        # Conservative item-level CPU proxy: hit the label anchor neighborhood only.
        # Glyph-level geometry and exact backend text metrics remain deferred.
        radius = max(float(size) * 0.5, 1.0)
        distance = float(np.linalg.norm(query - position.astype(np.float64)))
        if distance <= radius and distance < best_distance:
            best_index = index
            best_distance = distance

    if best_index is None:
        return None

    position = positions[best_index]
    source = source_positions[best_index]
    text = visual.texts[best_index]
    extension_kind, extension_payload = _transform_or_existing_payload(
        visual,
        request,
        (float(position[0]), float(position[1])),
        (float(source[0]), float(source[1])),
        view,
        existing_kind=TEXT_QUERY_PAYLOAD_KIND,
        existing_payload={
            "kind": "text",
            "visual_id": visual.id,
            "item_index": best_index,
            "text": text,
            "position": (float(position[0]), float(position[1])),
            "coordinate_space": visual.coordinate_space.value,
        },
    )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=visual.id,
        visual_family=VisualFamily.TEXT,
        item_id=best_index,
        visual_coordinate=(float(position[0]), float(position[1])),
        data_coordinate=(float(position[0]), float(position[1])),
        displayed_rgba=(
            float(colors[best_index][0]),
            float(colors[best_index][1]),
            float(colors[best_index][2]),
            float(colors[best_index][3]),
        ),
        value=text,
        extension_payload_kind=extension_kind,
        extension_payload=extension_payload,
    )


def _query_mesh_visual(
    request: QueryRequest,
    visual: MeshVisual,
    *,
    view: View2D | None,
    transform_resources: Mapping[str, AffineTransform2DResource] | None,
) -> QueryResult | None:
    if visual.positions.shape[1] != 2:
        return None
    color_mode = visual.resolved_color_mode()
    if color_mode is MeshColorMode.VERTEX:
        return None

    query = np.array(request.coordinate, dtype=np.float64)
    positions = transformed_positions(
        visual.positions, visual.transform, transform_resources
    )
    best_face_index: int | None = None
    best_order = float("-inf")
    for face_index, vertex_indices in enumerate(visual.faces):
        triangle = positions[vertex_indices]
        if _point_in_triangle(query, triangle):
            order = float(visual.order)
            if order >= best_order:
                best_face_index = face_index
                best_order = order

    if best_face_index is None:
        return None

    vertex_indices_tuple = tuple(int(index) for index in visual.faces[best_face_index])
    rgba = _mesh_face_rgba(visual, best_face_index)
    payload = MeshQueryPayload(
        visual_id=visual.id,
        hit_kind="face",
        face_index=best_face_index,
        vertex_indices=vertex_indices_tuple,
        panel_xy=request.coordinate,
        coordinate_space=visual.coordinate_space.value,
        displayed_rgba=rgba,
    )
    declared_coord = request.coordinate
    extension_kind, extension_payload = _transform_or_existing_payload(
        visual,
        request,
        declared_coord,
        inverse_transform_coordinate(
            declared_coord, visual.transform, transform_resources
        ),
        view,
        existing_kind=MESH_QUERY_PAYLOAD_KIND,
        existing_payload=payload,
    )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=visual.id,
        visual_family=VisualFamily.MESH,
        item_id=best_face_index,
        visual_coordinate=request.coordinate,
        data_coordinate=request.coordinate,
        displayed_rgba=rgba,
        value={
            "hit_kind": "face",
            "face_index": best_face_index,
            "vertex_indices": vertex_indices_tuple,
        },
        extension_payload_kind=extension_kind,
        extension_payload=extension_payload,
    )


def _transform_or_existing_payload(
    visual: PointVisual | MarkerVisual | TextVisual | MeshVisual,
    request: QueryRequest,
    declared_coord: tuple[float, float],
    source_coord: tuple[float, float],
    view: View2D | None,
    *,
    existing_kind: str | None,
    existing_payload: object | None,
) -> tuple[str | None, object | None]:
    if visual.transform is None and view is None:
        return existing_kind, existing_payload
    data_coord = (
        declared_coord if visual.coordinate_space is CoordinateSpace.DATA else None
    )
    payload = TransformQueryPayload(
        visual_id=visual.id,
        panel_xy=request.coordinate,
        panel_ndc=declared_to_panel_ndc(declared_coord, visual.coordinate_space, view),
        declared_coordinate_space=visual.coordinate_space.value,
        declared_space_coord=declared_coord,
        source_coord=source_coord,
        data_coord=data_coord,
        transform_ids=binding_transform_ids(visual.transform),
        inline_transform_digest=binding_inline_digest(visual.transform),
        view_id=view.id if view is not None else None,
        inverse_status=InverseStatus.EXACT,
    )
    return TRANSFORM_QUERY_PAYLOAD_KIND, payload


def _point_in_triangle(point: np.ndarray, triangle: np.ndarray) -> bool:
    a, b, c = triangle
    v0 = c - a
    v1 = b - a
    v2 = point - a
    dot00 = float(np.dot(v0, v0))
    dot01 = float(np.dot(v0, v1))
    dot02 = float(np.dot(v0, v2))
    dot11 = float(np.dot(v1, v1))
    dot12 = float(np.dot(v1, v2))
    denominator = dot00 * dot11 - dot01 * dot01
    if denominator == 0.0:
        return False
    inv_denominator = 1.0 / denominator
    u = (dot11 * dot02 - dot01 * dot12) * inv_denominator
    v = (dot00 * dot12 - dot01 * dot02) * inv_denominator
    epsilon = 1e-12
    return u >= -epsilon and v >= -epsilon and (u + v) <= 1.0 + epsilon


def _mesh_face_rgba(
    visual: MeshVisual, face_index: int
) -> tuple[float, float, float, float]:
    color_mode = visual.resolved_color_mode()
    colors = _rgba01(visual.color)
    if color_mode is MeshColorMode.UNIFORM:
        color = colors.reshape(1, 4)[0]
    elif color_mode is MeshColorMode.FACE:
        color = colors[face_index]
    else:
        raise ValueError("vertex mesh colors are not supported by face query")
    return (float(color[0]), float(color[1]), float(color[2]), float(color[3]))


def _point_color_query_payload(
    visual: PointVisual,
    item_index: int,
    *,
    color_scales: Mapping[str, ColorScale] | None,
) -> tuple[tuple[float, float, float, float], ScalarColorQueryPayload | None]:
    if visual.color_encoding is None:
        if visual.colors is None:
            raise ValueError("PointVisual requires colors or color_encoding")
        color = _rgba01(visual.colors)[item_index]
        return (
            float(color[0]),
            float(color[1]),
            float(color[2]),
            float(color[3]),
        ), None

    encoding = visual.color_encoding
    scale = resolve_color_scale(color_scales, encoding.color_scale_id)
    mapped = map_scalar_value(
        float(encoding.values[item_index]), scale, alpha=encoding.alpha
    )
    return mapped.displayed_rgba, ScalarColorQueryPayload(
        visual_id=visual.id,
        item_kind="point",
        item_id=item_index,
        color_slot=ScalarColorSlot.COLOR,
        color_scale_id=scale.id,
        colormap_id=scale.colormap.id.value,
        source_value=mapped.source_value,
        normalized_value_raw=mapped.normalized_value_raw,
        normalized_value_clipped=mapped.normalized_value_clipped,
        range_class=mapped.range_class,
        lut_index=mapped.lut_index,
        displayed_rgba=mapped.displayed_rgba,
    )


def _marker_color_query_payload(
    visual: MarkerVisual,
    item_index: int,
    *,
    color_scales: Mapping[str, ColorScale] | None,
) -> tuple[tuple[float, float, float, float], ScalarColorQueryPayload | None]:
    if visual.fill_color_encoding is None:
        if visual.fill_colors is None:
            raise ValueError("MarkerVisual requires fill_colors or fill_color_encoding")
        color = _rgba01(visual.fill_colors)[item_index]
        return (
            float(color[0]),
            float(color[1]),
            float(color[2]),
            float(color[3]),
        ), None

    encoding = visual.fill_color_encoding
    scale = resolve_color_scale(color_scales, encoding.color_scale_id)
    mapped = map_scalar_value(
        float(encoding.values[item_index]), scale, alpha=encoding.alpha
    )
    return mapped.displayed_rgba, ScalarColorQueryPayload(
        visual_id=visual.id,
        item_kind="marker",
        item_id=item_index,
        color_slot=ScalarColorSlot.FILL,
        color_scale_id=scale.id,
        colormap_id=scale.colormap.id.value,
        source_value=mapped.source_value,
        normalized_value_raw=mapped.normalized_value_raw,
        normalized_value_clipped=mapped.normalized_value_clipped,
        range_class=mapped.range_class,
        lut_index=mapped.lut_index,
        displayed_rgba=mapped.displayed_rgba,
    )


def _image_color_query_payload(
    visual: ImageVisual,
    value: np.ndarray | np.generic,
    row: int,
    col: int,
    *,
    color_scales: Mapping[str, ColorScale] | None,
) -> tuple[tuple[float, float, float, float], ScalarColorQueryPayload | None]:
    if visual.color_scale_id is None:
        return _image_value_to_rgba(value), None

    scale = resolve_color_scale(color_scales, visual.color_scale_id)
    mapped = map_scalar_value(float(np.asarray(value).item()), scale)
    return mapped.displayed_rgba, ScalarColorQueryPayload(
        visual_id=visual.id,
        item_kind="texel",
        texel=(row, col),
        color_slot=ScalarColorSlot.IMAGE,
        color_scale_id=scale.id,
        colormap_id=scale.colormap.id.value,
        source_value=mapped.source_value,
        normalized_value_raw=mapped.normalized_value_raw,
        normalized_value_clipped=mapped.normalized_value_clipped,
        range_class=mapped.range_class,
        lut_index=mapped.lut_index,
        displayed_rgba=mapped.displayed_rgba,
    )


def _point_query_value(visual: PointVisual, item_index: int) -> object | None:
    if visual.color_encoding is None:
        return None
    return float(visual.color_encoding.values[item_index])


def _marker_query_value(visual: MarkerVisual, item_index: int) -> object | None:
    if visual.fill_color_encoding is None:
        return None
    return float(visual.fill_color_encoding.values[item_index])


def _rgba01(colors: np.ndarray) -> np.ndarray:
    if colors.dtype == np.dtype(np.uint8):
        return colors.astype(np.float64) / 255.0
    return colors.astype(np.float64)


def _image_value_to_rgba(
    value: np.ndarray | np.generic,
) -> tuple[float, float, float, float]:
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
