"""Datoviz v0.4 query result decoding."""

from __future__ import annotations

from math import sqrt
from typing import Any, cast

from gsp.protocol import (
    QueryCoordinateSpace,
    QueryRequest,
    QueryResult,
    QueryStatus,
    VIEW3D_QUERY_PAYLOAD_KIND,
    View3D,
    View3DDiagnosticCode,
    View3DProjectionSnapshot,
    View3DQueryPayload,
    VisualFamily,
    unproject_view3d_panel_ndc_point,
)


DVZ_QUERY_STATUS_UNKNOWN = 0
DVZ_QUERY_STATUS_HIT = 1
DVZ_QUERY_STATUS_MISS = 2
DVZ_QUERY_STATUS_OUTSIDE_PANEL = 3
DVZ_QUERY_STATUS_STALE_DROPPED = 4
DVZ_QUERY_STATUS_NO_CAPABLE_VISUAL = 5
DVZ_QUERY_STATUS_UNSUPPORTED_TARGET = 6
DVZ_QUERY_STATUS_UNSUPPORTED_VISUAL_FAMILY = 7
DVZ_QUERY_STATUS_UNSUPPORTED_QUERY_PROFILE = 8
DVZ_QUERY_STATUS_UNSUPPORTED_GPU_FORMAT = 9
DVZ_QUERY_STATUS_GPU_EXEC_FAILED = 10
DVZ_QUERY_STATUS_READBACK_FAILED = 11
DVZ_QUERY_STATUS_DECODE_FAILED = 12

DVZ_SCENE_VISUAL_FAMILY_POINT = 1
DVZ_SCENE_VISUAL_FAMILY_IMAGE = 7

DVZ_QUERY_VALUE_NONE = 0
DVZ_QUERY_VALUE_SCALAR = 1
DVZ_QUERY_VALUE_VEC2 = 2
DVZ_QUERY_VALUE_VEC3 = 3
DVZ_QUERY_VALUE_VEC4 = 4
DVZ_QUERY_VALUE_CATEGORY = 5
DVZ_QUERY_VALUE_TEXT = 6

_REQUIRED_DVZ_QUERY_FUNCTIONS = (
    "dvz_query_request",
    "dvz_panel_query_px",
    "dvz_scene_poll_query",
)

_UNSUPPORTED_STATUSES = {
    DVZ_QUERY_STATUS_NO_CAPABLE_VISUAL,
    DVZ_QUERY_STATUS_UNSUPPORTED_TARGET,
    DVZ_QUERY_STATUS_UNSUPPORTED_VISUAL_FAMILY,
    DVZ_QUERY_STATUS_UNSUPPORTED_QUERY_PROFILE,
    DVZ_QUERY_STATUS_UNSUPPORTED_GPU_FORMAT,
}

_FAILED_STATUSES = {
    DVZ_QUERY_STATUS_UNKNOWN,
    DVZ_QUERY_STATUS_GPU_EXEC_FAILED,
    DVZ_QUERY_STATUS_READBACK_FAILED,
    DVZ_QUERY_STATUS_DECODE_FAILED,
}


def decode_dvz_query_result(raw: Any) -> QueryResult:
    """Decode a Datoviz v0.4 `DvzQueryResult`-shaped object into GSP query output.

    The decoder accepts ctypes objects and simple synthetic objects with matching field names. It
    does not advertise Datoviz query support by itself; capability promotion is a later runtime
    parity step once execution and application-id mapping are validated.
    """
    request_id = f"query:datoviz-{_field(raw, 'request_id', 0)}"
    panel_coordinate = _panel_coordinate(raw)
    status = _int_field(raw, "status", DVZ_QUERY_STATUS_UNKNOWN)

    if status == DVZ_QUERY_STATUS_HIT:
        return _decode_hit(raw, request_id, panel_coordinate)
    if status == DVZ_QUERY_STATUS_MISS:
        return QueryResult(
            request_id=request_id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=panel_coordinate,
        )
    if status == DVZ_QUERY_STATUS_OUTSIDE_PANEL:
        return QueryResult(
            request_id=request_id,
            status=QueryStatus.OUTSIDE_PANEL,
            hit=False,
            panel_coordinate=panel_coordinate,
        )
    if status == DVZ_QUERY_STATUS_STALE_DROPPED:
        return QueryResult(
            request_id=request_id,
            status=QueryStatus.DROPPED,
            hit=False,
            panel_coordinate=panel_coordinate,
            diagnostic="Datoviz query result was stale or dropped",
        )
    if status in _UNSUPPORTED_STATUSES:
        return QueryResult(
            request_id=request_id,
            status=QueryStatus.UNSUPPORTED,
            hit=False,
            panel_coordinate=panel_coordinate,
            diagnostic=f"Datoviz query unsupported: {_status_name(status)}",
        )
    if status in _FAILED_STATUSES:
        return QueryResult(
            request_id=request_id,
            status=QueryStatus.FAILED,
            hit=False,
            panel_coordinate=panel_coordinate,
            diagnostic=f"Datoviz query failed: {_status_name(status)}",
        )
    return QueryResult(
        request_id=request_id,
        status=QueryStatus.FAILED,
        hit=False,
        panel_coordinate=panel_coordinate,
        diagnostic=f"Datoviz query returned unknown status {status}",
    )


def datoviz_query_view3d_ray_context(
    request: QueryRequest,
    view: View3D,
    snapshot: View3DProjectionSnapshot,
    *,
    panel_bounds: tuple[float, float, float, float],
) -> QueryResult:
    """Return a canonical S036 View3D ray context for the Datoviz adapter.

    This is projection-inverse readback from public GSP state. It does not claim Datoviz GPU visual
    hit picking for 3D meshes.
    """
    if request.coordinate_space is not QueryCoordinateSpace.PANEL:
        return _unsupported_query_result(
            request,
            f"{View3DDiagnosticCode.QUERY_3D_VISUAL_HIT_DEFERRED.value}: "
            "Datoviz View3D ray readback requires panel coordinates",
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


def _unsupported_query_result(request: QueryRequest, diagnostic: str) -> QueryResult:
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.UNSUPPORTED,
        hit=False,
        panel_coordinate=request.coordinate,
        diagnostic=diagnostic,
        layout_snapshot_id=request.layout_snapshot_id,
        view_snapshot_id=request.view_snapshot_id,
    )


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


def _sub3(
    left: tuple[float, float, float], right: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _normalized3(value: tuple[float, float, float]) -> tuple[float, float, float]:
    norm = sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2])
    if norm == 0.0:
        raise ValueError("ray direction is degenerate")
    return (value[0] / norm, value[1] / norm, value[2] / norm)


def _decode_hit(raw: Any, request_id: str, panel_coordinate: tuple[float, float]) -> QueryResult:
    visual_family = _visual_family(raw)
    value = _value(raw)
    return QueryResult(
        request_id=request_id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=panel_coordinate,
        visual_id=_visual_id(raw),
        visual_family=visual_family,
        item_id=_item_id(raw, visual_family),
        texel=_texel(raw, visual_family),
        visual_coordinate=_optional_pair(raw, "visual_position", "has_visual_position"),
        data_coordinate=_optional_pair(raw, "data_position", "has_data_position"),
        displayed_rgba=_display_rgba(raw),
        value=value,
    )


def _field(raw: Any, name: str, default: object | None = None) -> object | None:
    return getattr(raw, name, default)


def _int_field(raw: Any, name: str, default: int = 0) -> int:
    return int(cast(Any, _field(raw, name, default) or 0))


def _float_field(raw: Any, name: str, default: float = 0.0) -> float:
    return float(cast(Any, _field(raw, name, default) or 0.0))


def _panel_coordinate(raw: Any) -> tuple[float, float]:
    value = _field(raw, "panel_position")
    sequence = _sequence(value)
    if sequence is not None and len(sequence) >= 2:
        return (float(cast(Any, sequence[0])), float(cast(Any, sequence[1])))
    framebuffer = _field(raw, "framebuffer_position")
    framebuffer_sequence = _sequence(framebuffer)
    if framebuffer_sequence is not None and len(framebuffer_sequence) >= 2:
        return (float(cast(Any, framebuffer_sequence[0])), float(cast(Any, framebuffer_sequence[1])))
    return (0.0, 0.0)


def _visual_id(raw: Any) -> str:
    return f"datoviz:visual:{_int_field(raw, 'visual_id')}"


def _visual_family(raw: Any) -> VisualFamily | str | None:
    family = _int_field(raw, "visual_family")
    if family == DVZ_SCENE_VISUAL_FAMILY_POINT:
        return VisualFamily.POINT
    if family == DVZ_SCENE_VISUAL_FAMILY_IMAGE:
        return VisualFamily.IMAGE
    return None


def _item_id(raw: Any, family: VisualFamily | str | None) -> int | None:
    if family != VisualFamily.POINT:
        return None
    return _int_field(raw, "item_id")


def _texel(raw: Any, family: VisualFamily | str | None) -> tuple[int, int] | None:
    if family != VisualFamily.IMAGE:
        return None
    texel_id = _int_field(raw, "texel_id")
    if texel_id > 0:
        return (0, texel_id)
    item_id = _int_field(raw, "item_id")
    if item_id > 0:
        return (0, item_id)
    return None


def _optional_pair(raw: Any, name: str, flag_name: str) -> tuple[float, float] | None:
    if not bool(_field(raw, flag_name, False)):
        return None
    value = _field(raw, name)
    sequence = _sequence(value)
    if sequence is None or len(sequence) < 2:
        return None
    return (float(cast(Any, sequence[0])), float(cast(Any, sequence[1])))


def _display_rgba(raw: Any) -> tuple[float, float, float, float] | None:
    if not bool(_field(raw, "has_display_rgba", False)):
        return None
    value = _field(raw, "display_rgba")
    sequence = _sequence(value)
    if sequence is None or len(sequence) < 4:
        return None
    return (
        float(cast(Any, sequence[0])),
        float(cast(Any, sequence[1])),
        float(cast(Any, sequence[2])),
        float(cast(Any, sequence[3])),
    )


def _value(raw: Any) -> object | None:
    kind = _int_field(raw, "value_kind", DVZ_QUERY_VALUE_NONE)
    if kind == DVZ_QUERY_VALUE_NONE:
        return None
    if kind == DVZ_QUERY_VALUE_SCALAR:
        return _float_field(raw, "scalar")
    if kind in (DVZ_QUERY_VALUE_VEC2, DVZ_QUERY_VALUE_VEC3, DVZ_QUERY_VALUE_VEC4):
        size = kind
        vector = _field(raw, "vector")
        sequence = _sequence(vector)
        if sequence is not None and len(sequence) >= size:
            return tuple(float(cast(Any, sequence[index])) for index in range(size))
        return None
    if kind == DVZ_QUERY_VALUE_CATEGORY:
        return _int_field(raw, "category_id")
    if kind == DVZ_QUERY_VALUE_TEXT:
        return _decode_text(_field(raw, "label", ""))
    return None


def _decode_text(value: object | None) -> str:
    if isinstance(value, bytes):
        return value.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
    sequence = _sequence(value)
    if sequence is not None:
        raw = bytes(int(cast(Any, item)) for item in sequence if int(cast(Any, item)) != 0)
        return raw.decode("utf-8", errors="replace")
    return str(value or "")


def _sequence(value: object | None) -> Any | None:
    if value is None or isinstance(value, (str, bytes, bytearray)):
        return None
    try:
        len(cast(Any, value))
        cast(Any, value)[0]
    except (IndexError, TypeError):
        return None
    return value


def _status_name(status: int) -> str:
    return {
        DVZ_QUERY_STATUS_UNKNOWN: "unknown",
        DVZ_QUERY_STATUS_HIT: "hit",
        DVZ_QUERY_STATUS_MISS: "miss",
        DVZ_QUERY_STATUS_OUTSIDE_PANEL: "outside-panel",
        DVZ_QUERY_STATUS_STALE_DROPPED: "stale-dropped",
        DVZ_QUERY_STATUS_NO_CAPABLE_VISUAL: "no-capable-visual",
        DVZ_QUERY_STATUS_UNSUPPORTED_TARGET: "unsupported-target",
        DVZ_QUERY_STATUS_UNSUPPORTED_VISUAL_FAMILY: "unsupported-visual-family",
        DVZ_QUERY_STATUS_UNSUPPORTED_QUERY_PROFILE: "unsupported-query-profile",
        DVZ_QUERY_STATUS_UNSUPPORTED_GPU_FORMAT: "unsupported-gpu-format",
        DVZ_QUERY_STATUS_GPU_EXEC_FAILED: "gpu-exec-failed",
        DVZ_QUERY_STATUS_READBACK_FAILED: "readback-failed",
        DVZ_QUERY_STATUS_DECODE_FAILED: "decode-failed",
    }.get(status, f"unknown-{status}")


def datoviz_v04_query_binding_ready(dvz: Any) -> bool:
    """Return whether a Datoviz facade exposes the minimal decodable query binding."""
    return not datoviz_v04_query_binding_diagnostics(dvz)


def datoviz_v04_query_binding_diagnostics(dvz: Any) -> tuple[str, ...]:
    """Return missing Datoviz v0.4 query binding requirements."""
    missing = [name for name in _REQUIRED_DVZ_QUERY_FUNCTIONS if not hasattr(dvz, name)]
    query_result_type = getattr(dvz, "DvzQueryResult", None)
    if query_result_type is None:
        missing.append("DvzQueryResult")
    elif not hasattr(query_result_type, "_fields_"):
        missing.append("DvzQueryResult._fields_")
    return tuple(f"missing {name}" for name in missing)
