"""Reference panel-query proof for protocol visuals."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from math import sqrt
from typing import Iterable

import numpy as np

from gsp.protocol.color import ColorScale, ScalarColorSlot
from gsp.protocol.query import (
    MESH_QUERY_PAYLOAD_KIND,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    TEXT_QUERY_PAYLOAD_KIND,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    VIEW3D_QUERY_PAYLOAD_KIND,
    VIEW3D_MESH_TRIANGLE_PICK_GEOMETRY_QUERY_KIND,
    VIEW3D_MESH_TRIANGLE_PICK_QUERY_KIND,
    MeshQueryPayload,
    QueryDiagnostic,
    QueryDiagnosticSeverity,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryStatus,
    ScalarColorQueryPayload,
    TransformQueryPayload,
    View3DMeshPickDiagnosticCode,
    View3DMeshTrianglePickGeometryPayload,
    View3DMeshTrianglePickPayload,
    View3DMeshTrianglePickRequest,
    View3DQueryPayload,
    VisualFamily,
)
from gsp.protocol import (
    AffineTransform2DResource,
    CoordinateSpace,
    InverseStatus,
    QueryCoordinateSpace,
    View2D,
    View3D,
    View3DDiagnosticCode,
    View3DProjectionSnapshot,
    Projection3DKind,
    ProjectedFaceClassification,
    classify_projected_triangle,
    face_culling_excludes,
    mesh_pick_barycentric_2d,
    mesh_pick_data_xyz,
    mesh_pick_panel_ndc_z,
    mesh_pick_projected_front_facing,
    project_view3d_data_point,
    projected_triangle_area2,
    unproject_view3d_panel_ndc_point,
)
from gsp.protocol.visuals import (
    DepthMode,
    ImageOrigin,
    ImageVisual,
    MarkerVisual,
    MeshColorMode,
    MeshVisual,
    OpacityPolicy,
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


_MeshPickHit = tuple[
    float,
    str,
    int,
    tuple[float, float, float],
    float,
    tuple[float, float, float],
    bool,
]


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
            layout_snapshot_id=request.layout_snapshot_id,
            view_snapshot_id=request.view_snapshot_id,
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
            result = _with_request_snapshots(hit, request)
            if result.status != QueryStatus.HIT:
                return result
            hits.append(result)

    if not hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=request.layout_snapshot_id,
            view_snapshot_id=request.view_snapshot_id,
        )
    if request.hit_policy == QueryHitPolicy.ALL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            hits=tuple(hit.hits[0] for hit in hits),
            layout_snapshot_id=request.layout_snapshot_id,
            view_snapshot_id=request.view_snapshot_id,
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
        layout_snapshot_id=request.layout_snapshot_id,
        view_snapshot_id=request.view_snapshot_id,
    )


def failed_query_result(request: QueryRequest, diagnostic: str) -> QueryResult:
    """Return a standard backend/readback failure query result."""
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.FAILED,
        hit=False,
        panel_coordinate=request.coordinate,
        diagnostic=diagnostic,
        layout_snapshot_id=request.layout_snapshot_id,
        view_snapshot_id=request.view_snapshot_id,
    )


def query_view3d_ray_context(
    request: QueryRequest,
    view: View3D,
    snapshot: View3DProjectionSnapshot,
    *,
    panel_bounds: tuple[float, float, float, float],
) -> QueryResult:
    """Return a S036 projection-inverse ray context without visual picking."""
    if request.coordinate_space is not QueryCoordinateSpace.PANEL:
        return unsupported_query_result(
            request,
            f"{View3DDiagnosticCode.QUERY_3D_VISUAL_HIT_DEFERRED.value}: "
            "View3D ray readback requires panel coordinates",
        )
    if (
        request.layout_snapshot_id is not None
        and request.layout_snapshot_id != snapshot.layout_snapshot_id
    ) or (
        request.view_snapshot_id is not None
        and request.view_snapshot_id != snapshot.view_projection_snapshot_id
    ):
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.STALE,
            hit=False,
            panel_coordinate=request.coordinate,
            diagnostic=View3DDiagnosticCode.QUERY_3D_SNAPSHOT_MISMATCH.value,
            layout_snapshot_id=snapshot.layout_snapshot_id,
            view_snapshot_id=snapshot.view_projection_snapshot_id,
        )
    panel_ndc = _panel_coordinate_to_ndc(request.coordinate, panel_bounds)
    aspect_ratio = _panel_bounds_aspect_ratio(panel_bounds)
    near = unproject_view3d_panel_ndc_point(
        view, (panel_ndc[0], panel_ndc[1], -1.0), aspect_ratio=aspect_ratio
    )
    far = unproject_view3d_panel_ndc_point(
        view, (panel_ndc[0], panel_ndc[1], 1.0), aspect_ratio=aspect_ratio
    )
    ray_direction = _normalized3(_sub3(far, near))
    payload = View3DQueryPayload(
        view_id=snapshot.view_id,
        view_revision=snapshot.view_revision,
        layout_snapshot_id=snapshot.layout_snapshot_id,
        view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        panel_xy=request.coordinate,
        panel_ndc=panel_ndc,
        near_data_point=near,
        far_data_point=far,
        ray_direction=ray_direction,
    )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_coordinate=panel_ndc,
        data_coordinate=(near[0], near[1]),
        value={
            "kind": "view3d-ray",
            "view_id": snapshot.view_id,
            "view_projection_snapshot_id": snapshot.view_projection_snapshot_id,
        },
        extension_payload_kind=VIEW3D_QUERY_PAYLOAD_KIND,
        extension_payload=payload,
        layout_snapshot_id=snapshot.layout_snapshot_id,
        view_snapshot_id=snapshot.view_projection_snapshot_id,
    )


def query_view3d_mesh_triangle_pick(
    request: View3DMeshTrianglePickRequest,
    entries: Iterable[QueryVisualEntry],
    *,
    view: View3D,
    snapshot: View3DProjectionSnapshot,
    panel_bounds: tuple[float, float, float, float],
    pick_scene_snapshot_id: str | None = None,
    geometry_payload: bool = False,
    include_facing: bool = False,
) -> QueryResult:
    """Return a S044 CPU reference View3D mesh triangle pick result.

    This is a protocol oracle for strict-scope fixtures. It uses public GSP
    scene state only and reports an adapted CPU diagnostic rather than claiming
    that Matplotlib has a native GPU picker.
    """
    actual_pick_scene_snapshot_id = pick_scene_snapshot_id or _view3d_pick_scene_snapshot_id(
        entries,
        snapshot=snapshot,
    )
    invalid = _validate_mesh_pick_request(
        request,
        view=view,
        snapshot=snapshot,
        panel_bounds=panel_bounds,
        pick_scene_snapshot_id=actual_pick_scene_snapshot_id,
        geometry_payload=geometry_payload,
    )
    if invalid is not None:
        return invalid

    panel_ndc = _panel_coordinate_to_ndc(request.panel_xy, panel_bounds)
    best: _MeshPickHit | None = None
    projected_degenerate_seen = False
    for entry in entries:
        visual = entry.visual
        if not isinstance(visual, MeshVisual):
            return _mesh_pick_result(
                request,
                QueryStatus.UNSUPPORTED,
                view=view,
                snapshot=snapshot,
                panel_ndc=panel_ndc,
                pick_scene_snapshot_id=actual_pick_scene_snapshot_id,
                diagnostics=(
                    _pick_diagnostic(
                        View3DMeshPickDiagnosticCode.UNSUPPORTED_SCENE_OCCLUDER,
                        "only MeshVisual entries are accepted in S044 mesh picking",
                    ),
                ),
                geometry_payload=geometry_payload,
            )
        unsupported = _mesh_pick_unsupported_diagnostic(visual)
        if unsupported is not None:
            return _mesh_pick_result(
                request,
                QueryStatus.UNSUPPORTED,
                view=view,
                snapshot=snapshot,
                panel_ndc=panel_ndc,
                pick_scene_snapshot_id=actual_pick_scene_snapshot_id,
                diagnostics=(unsupported,),
                geometry_payload=geometry_payload,
            )
        projected = np.asarray(
            [project_view3d_data_point(view, _float3(row)) for row in visual.positions],
            dtype=np.float64,
        )
        for face_index, vertex_indices in enumerate(visual.faces):
            triangle = projected[vertex_indices]
            area2 = projected_triangle_area2(
                _float3(triangle[0]), _float3(triangle[1]), _float3(triangle[2])
            )
            classification = classify_projected_triangle(area2)
            if classification is ProjectedFaceClassification.DEGENERATE:
                projected_degenerate_seen = True
                continue
            if face_culling_excludes(classification, visual.face_culling):
                continue
            if np.any(triangle[:, 2] < -1.0) or np.any(triangle[:, 2] > 1.0):
                continue
            barycentric = mesh_pick_barycentric_2d(
                panel_ndc,
                _float3(triangle[0]),
                _float3(triangle[1]),
                _float3(triangle[2]),
            )
            if barycentric is None:
                continue
            depth = mesh_pick_panel_ndc_z(
                barycentric,
                _float3(triangle[0]),
                _float3(triangle[1]),
                _float3(triangle[2]),
            )
            if best is not None and abs(depth - best[0]) <= 1.0e-12:
                return _mesh_pick_result(
                    request,
                    QueryStatus.UNSUPPORTED,
                    view=view,
                    snapshot=snapshot,
                    panel_ndc=panel_ndc,
                    pick_scene_snapshot_id=actual_pick_scene_snapshot_id,
                    diagnostics=(
                        _pick_diagnostic(
                            View3DMeshPickDiagnosticCode.AMBIGUOUS_DEPTH_TIE,
                            "equal-depth triangle hits are ambiguous in S044 v1",
                        ),
                    ),
                    geometry_payload=geometry_payload,
                )
            if best is None or depth < best[0]:
                positions = visual.positions[vertex_indices]
                best = (
                    depth,
                    visual.id,
                    int(face_index),
                    barycentric,
                    depth,
                    mesh_pick_data_xyz(
                        barycentric,
                        _float3(positions[0]),
                        _float3(positions[1]),
                        _float3(positions[2]),
                    ),
                    mesh_pick_projected_front_facing(
                        _float3(triangle[0]),
                        _float3(triangle[1]),
                        _float3(triangle[2]),
                    ),
                )

    if best is None:
        diagnostics: tuple[QueryDiagnostic, ...] = (_pick_cpu_reference_diagnostic(),)
        if projected_degenerate_seen:
            diagnostics = diagnostics + (
                _pick_diagnostic(
                    View3DMeshPickDiagnosticCode.UNSUPPORTED_PROJECTED_DEGENERATE,
                    "projected-degenerate triangles do not contribute strict pick hits",
                    severity=QueryDiagnosticSeverity.WARNING,
                ),
            )
        return _mesh_pick_result(
            request,
            QueryStatus.MISS,
            view=view,
            snapshot=snapshot,
            panel_ndc=panel_ndc,
            pick_scene_snapshot_id=actual_pick_scene_snapshot_id,
            diagnostics=diagnostics,
            geometry_payload=geometry_payload,
        )

    _, visual_id, primitive_index, barycentric, panel_ndc_z, data_xyz, front_facing = best
    diagnostics = (_pick_cpu_reference_diagnostic(),)
    if geometry_payload:
        diagnostics = diagnostics + (
            _pick_diagnostic(
                View3DMeshPickDiagnosticCode.ADAPTED_PUBLIC_GEOMETRY_RECONSTRUCTION,
                "Matplotlib reference path reconstructed geometry from public GSP state",
                severity=QueryDiagnosticSeverity.INFO,
            ),
        )
    return _mesh_pick_result(
        request,
        QueryStatus.HIT,
        view=view,
        snapshot=snapshot,
        panel_ndc=panel_ndc,
        pick_scene_snapshot_id=actual_pick_scene_snapshot_id,
        visual_id=visual_id,
        primitive_index=primitive_index,
        diagnostics=diagnostics,
        geometry_payload=geometry_payload,
        hit_barycentric=barycentric,
        hit_panel_ndc_z=panel_ndc_z,
        hit_data_xyz=data_xyz,
        front_facing=front_facing if include_facing else None,
    )


def query_view3d_mesh_triangle_pick_geometry(
    request: View3DMeshTrianglePickRequest,
    entries: Iterable[QueryVisualEntry],
    *,
    view: View3D,
    snapshot: View3DProjectionSnapshot,
    panel_bounds: tuple[float, float, float, float],
    pick_scene_snapshot_id: str | None = None,
    include_facing: bool = False,
) -> QueryResult:
    """Return the S050 geometry payload for the CPU reference pick path."""
    return query_view3d_mesh_triangle_pick(
        request,
        entries,
        view=view,
        snapshot=snapshot,
        panel_bounds=panel_bounds,
        pick_scene_snapshot_id=pick_scene_snapshot_id,
        geometry_payload=True,
        include_facing=include_facing,
    )


def _with_request_snapshots(result: QueryResult, request: QueryRequest) -> QueryResult:
    return replace(
        result,
        layout_snapshot_id=result.layout_snapshot_id or request.layout_snapshot_id,
        view_snapshot_id=result.view_snapshot_id or request.view_snapshot_id,
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
        return unsupported_query_result(
            request,
            f"{View3DDiagnosticCode.QUERY_3D_VISUAL_HIT_DEFERRED.value}: "
            "3D MeshVisual face picking is deferred in S036",
        )
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

    vertex_indices = visual.faces[best_face_index]
    vertex_indices_tuple = (
        int(vertex_indices[0]),
        int(vertex_indices[1]),
        int(vertex_indices[2]),
    )
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


def _triangle_barycentric_2d(
    point: np.ndarray, triangle: np.ndarray
) -> tuple[float, float, float] | None:
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
        return None
    inv_denominator = 1.0 / denominator
    u = (dot11 * dot02 - dot01 * dot12) * inv_denominator
    v = (dot00 * dot12 - dot01 * dot02) * inv_denominator
    w = 1.0 - u - v
    epsilon = 1e-12
    if u < -epsilon or v < -epsilon or w < -epsilon:
        return None
    return (w, v, u)


def _panel_coordinate_to_ndc(
    coordinate: tuple[float, float], bounds: tuple[float, float, float, float]
) -> tuple[float, float]:
    left, right, bottom, top = bounds
    if right == left or top == bottom:
        raise ValueError("panel_bounds must be non-degenerate")
    x, y = coordinate
    return (
        -1.0 + 2.0 * (x - left) / (right - left),
        -1.0 + 2.0 * (y - bottom) / (top - bottom),
    )


def _panel_bounds_aspect_ratio(bounds: tuple[float, float, float, float]) -> float:
    left, right, bottom, top = bounds
    width = abs(right - left)
    height = abs(top - bottom)
    if width == 0.0 or height == 0.0:
        raise ValueError("panel_bounds must be non-degenerate")
    return width / height


def _validate_mesh_pick_request(
    request: View3DMeshTrianglePickRequest,
    *,
    view: View3D,
    snapshot: View3DProjectionSnapshot,
    panel_bounds: tuple[float, float, float, float],
    pick_scene_snapshot_id: str,
    geometry_payload: bool = False,
) -> QueryResult | None:
    if request.view_id != view.id:
        return _mesh_pick_result(
            request,
            QueryStatus.INVALID,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(View3DMeshPickDiagnosticCode.INVALID_VIEW_ID),
            ),
            geometry_payload=geometry_payload,
        )
    if request.panel_id is not None and request.panel_id != view.panel_id:
        return _mesh_pick_result(
            request,
            QueryStatus.INVALID,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(View3DMeshPickDiagnosticCode.INVALID_PANEL_ID),
            ),
            geometry_payload=geometry_payload,
        )
    if snapshot.projection_kind is not Projection3DKind.ORTHOGRAPHIC:
        return _mesh_pick_result(
            request,
            QueryStatus.UNSUPPORTED,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(
                    View3DMeshPickDiagnosticCode.UNSUPPORTED_PROJECTION,
                    "mesh triangle picking geometry is accepted only for orthographic View3D",
                ),
            ),
            geometry_payload=geometry_payload,
        )
    if not _contains(panel_bounds, request.panel_xy):
        return _mesh_pick_result(
            request,
            QueryStatus.INVALID,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(View3DMeshPickDiagnosticCode.INVALID_OUTSIDE_PANEL),
            ),
            geometry_payload=geometry_payload,
        )
    if (
        request.expected_layout_snapshot_id is not None
        and request.expected_layout_snapshot_id != snapshot.layout_snapshot_id
    ):
        return _mesh_pick_result(
            request,
            QueryStatus.STALE,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(View3DMeshPickDiagnosticCode.STALE_LAYOUT_SNAPSHOT),
            ),
            geometry_payload=geometry_payload,
        )
    if (
        request.expected_view_revision is not None
        and request.expected_view_revision != snapshot.view_revision
    ):
        return _mesh_pick_result(
            request,
            QueryStatus.STALE,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(View3DMeshPickDiagnosticCode.STALE_VIEW_REVISION),
            ),
            geometry_payload=geometry_payload,
        )
    if (
        request.expected_view_projection_snapshot_id is not None
        and request.expected_view_projection_snapshot_id
        != snapshot.view_projection_snapshot_id
    ):
        return _mesh_pick_result(
            request,
            QueryStatus.STALE,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(
                    View3DMeshPickDiagnosticCode.STALE_VIEW_PROJECTION_SNAPSHOT
                ),
            ),
            geometry_payload=geometry_payload,
        )
    if (
        request.expected_pick_scene_snapshot_id is not None
        and request.expected_pick_scene_snapshot_id != pick_scene_snapshot_id
    ):
        return _mesh_pick_result(
            request,
            QueryStatus.STALE,
            view=view,
            snapshot=snapshot,
            diagnostics=(
                _pick_diagnostic(View3DMeshPickDiagnosticCode.STALE_PICK_SCENE_SNAPSHOT),
            ),
            geometry_payload=geometry_payload,
        )
    return None


def _mesh_pick_result(
    request: View3DMeshTrianglePickRequest,
    status: QueryStatus,
    *,
    view: View3D,
    snapshot: View3DProjectionSnapshot,
    panel_ndc: tuple[float, float] | None = None,
    pick_scene_snapshot_id: str | None = None,
    visual_id: str | None = None,
    primitive_index: int | None = None,
    diagnostics: tuple[QueryDiagnostic, ...] = (),
    geometry_payload: bool = False,
    hit_barycentric: tuple[float, float, float] | None = None,
    hit_panel_ndc_z: float | None = None,
    hit_data_xyz: tuple[float, float, float] | None = None,
    front_facing: bool | None = None,
) -> QueryResult:
    panel_id = (
        view.panel_id if status in (QueryStatus.HIT, QueryStatus.MISS) else view.panel_id
    )
    layout_snapshot_id = (
        snapshot.layout_snapshot_id
        if status in (QueryStatus.HIT, QueryStatus.MISS)
        else None
    )
    view_revision: int | str | None = (
        snapshot.view_revision if status in (QueryStatus.HIT, QueryStatus.MISS) else None
    )
    view_projection_snapshot_id = (
        snapshot.view_projection_snapshot_id
        if status in (QueryStatus.HIT, QueryStatus.MISS)
        else None
    )
    payload_pick_scene_snapshot_id = (
        pick_scene_snapshot_id
        if status in (QueryStatus.HIT, QueryStatus.MISS)
        else None
    )
    depth_mode = (
        view.depth_mode.value if status in (QueryStatus.HIT, QueryStatus.MISS) else None
    )
    visual_type = "MeshVisual" if visual_id is not None else None
    primitive_kind = "triangle" if visual_id is not None else None
    payload: View3DMeshTrianglePickPayload | View3DMeshTrianglePickGeometryPayload
    if geometry_payload:
        payload = View3DMeshTrianglePickGeometryPayload(
            status=status,
            hit=status is QueryStatus.HIT,
            view_id=view.id,
            panel_id=panel_id,
            panel_xy=request.panel_xy,
            panel_ndc_xy=panel_ndc,
            layout_snapshot_id=layout_snapshot_id,
            view_revision=view_revision,
            view_projection_snapshot_id=view_projection_snapshot_id,
            pick_scene_snapshot_id=payload_pick_scene_snapshot_id,
            depth_mode=depth_mode,
            visual_id=visual_id,
            visual_type=visual_type,
            primitive_kind=primitive_kind,
            primitive_index=primitive_index,
            hit_barycentric=hit_barycentric,
            hit_panel_ndc_z=hit_panel_ndc_z,
            hit_data_xyz=hit_data_xyz,
            front_facing=front_facing,
            diagnostics=diagnostics,
        )
    else:
        payload = View3DMeshTrianglePickPayload(
            status=status,
            hit=status is QueryStatus.HIT,
            view_id=view.id,
            panel_id=panel_id,
            panel_xy=request.panel_xy,
            panel_ndc_xy=panel_ndc,
            layout_snapshot_id=layout_snapshot_id,
            view_revision=view_revision,
            view_projection_snapshot_id=view_projection_snapshot_id,
            pick_scene_snapshot_id=payload_pick_scene_snapshot_id,
            depth_mode=depth_mode,
            visual_id=visual_id,
            visual_type=visual_type,
            primitive_kind=primitive_kind,
            primitive_index=primitive_index,
            diagnostics=diagnostics,
        )
    payload_kind = (
        VIEW3D_MESH_TRIANGLE_PICK_GEOMETRY_QUERY_KIND
        if geometry_payload
        else VIEW3D_MESH_TRIANGLE_PICK_QUERY_KIND
    )
    return QueryResult(
        request_id=(
            f"query:{request.view_id}:mesh-pick-geometry"
            if geometry_payload
            else f"query:{request.view_id}:mesh-pick"
        ),
        status=status,
        hit=status is QueryStatus.HIT,
        panel_coordinate=request.panel_xy,
        visual_id=visual_id,
        visual_family=VisualFamily.MESH if visual_id is not None else None,
        item_id=primitive_index,
        visual_coordinate=panel_ndc if status is QueryStatus.HIT else None,
        extension_payload_kind=payload_kind,
        extension_payload=payload,
        diagnostic=_query_diagnostic_code(diagnostics[0]) if diagnostics else None,
        layout_snapshot_id=payload.layout_snapshot_id,
        view_snapshot_id=payload.view_projection_snapshot_id,
    )


def _mesh_pick_unsupported_diagnostic(visual: MeshVisual) -> QueryDiagnostic | None:
    if visual.positions.shape[1] != 3 or visual.coordinate_space is not CoordinateSpace.DATA:
        return _pick_diagnostic(
            View3DMeshPickDiagnosticCode.UNSUPPORTED_COORDINATE_SPACE,
            "S044 mesh picking accepts only DATA-space 3D MeshVisual positions",
        )
    if visual.transform is not None:
        return _pick_diagnostic(
            View3DMeshPickDiagnosticCode.UNSUPPORTED_NATIVE_STATE_ONLY,
            "S044 mesh picking does not accept transformed 3D meshes",
        )
    if visual.depth_test is DepthMode.DISABLED or visual.depth_write is DepthMode.DISABLED:
        return _pick_diagnostic(
            View3DMeshPickDiagnosticCode.UNSUPPORTED_DEPTH_MODE,
            "S044 mesh picking requires depth-writing opaque_less semantics",
        )
    if visual.opacity_policy is not OpacityPolicy.ORDINARY_ALPHA:
        return _pick_diagnostic(
            View3DMeshPickDiagnosticCode.UNSUPPORTED_TRANSPARENT,
            "S044 mesh picking accepts only ordinary opaque meshes",
        )
    if _mesh_has_nonopaque_alpha(visual):
        return _pick_diagnostic(
            View3DMeshPickDiagnosticCode.UNSUPPORTED_TRANSPARENT,
            "S044 mesh picking accepts only opaque MeshVisual colors",
        )
    return None


def _mesh_has_nonopaque_alpha(visual: MeshVisual) -> bool:
    if visual.color is None:
        return False
    colors = _rgba01(visual.color)
    return bool(np.any(colors[..., 3] < 1.0))


def _pick_diagnostic(
    code: View3DMeshPickDiagnosticCode,
    message: str | None = None,
    *,
    severity: QueryDiagnosticSeverity = QueryDiagnosticSeverity.ERROR,
) -> QueryDiagnostic:
    return QueryDiagnostic(code=code, severity=severity, message=message)


def _pick_cpu_reference_diagnostic() -> QueryDiagnostic:
    return _pick_diagnostic(
        View3DMeshPickDiagnosticCode.ADAPTED_CPU_REFERENCE,
        "Matplotlib reference path computed this S044 pick from public CPU state",
        severity=QueryDiagnosticSeverity.INFO,
    )


def _query_diagnostic_code(diagnostic: QueryDiagnostic) -> str:
    code = diagnostic.code
    return code.value if isinstance(code, View3DMeshPickDiagnosticCode) else code


def _view3d_pick_scene_snapshot_id(
    entries: Iterable[QueryVisualEntry],
    *,
    snapshot: View3DProjectionSnapshot,
) -> str:
    import hashlib

    digest = hashlib.sha256()
    digest.update(snapshot.view_projection_snapshot_id.encode("utf-8"))
    for entry in entries:
        visual = entry.visual
        digest.update(type(visual).__name__.encode("utf-8"))
        digest.update(str(entry.z_order).encode("ascii"))
        if isinstance(visual, MeshVisual):
            digest.update(visual.id.encode("utf-8"))
            digest.update(visual.coordinate_space.value.encode("ascii"))
            digest.update(np.ascontiguousarray(visual.positions).tobytes())
            digest.update(np.ascontiguousarray(visual.faces).tobytes())
            digest.update(visual.depth_test.value.encode("ascii"))
            digest.update(visual.depth_write.value.encode("ascii"))
            digest.update(visual.face_culling.value.encode("ascii"))
            if visual.color is not None:
                digest.update(np.ascontiguousarray(visual.color).tobytes())
    return f"pick-scene:{digest.hexdigest()[:24]}"


def _float3(value: np.ndarray) -> tuple[float, float, float]:
    return (float(value[0]), float(value[1]), float(value[2]))


def _sub3(
    left: tuple[float, float, float], right: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _normalized3(value: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2])
    if norm == 0.0:
        raise ValueError("ray direction is degenerate")
    return (value[0] / norm, value[1] / norm, value[2] / norm)


def _mesh_face_rgba(
    visual: MeshVisual, face_index: int
) -> tuple[float, float, float, float]:
    color_mode = visual.resolved_color_mode()
    if visual.color is None:
        raise ValueError("MeshVisual color is required for face query")
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
