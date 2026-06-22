"""Debug JSON report helpers for conformance fixture replay."""

from __future__ import annotations

import json
from enum import Enum
from typing import TypeAlias

from gsp.protocol import GuideQueryPayload, QueryResult, TiledImageQueryPayload

from .matrix import BackendConformanceExpectation, backend_conformance_matrix
from .replay import InProcessReplayResult


JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def conformance_debug_report() -> dict[str, JsonValue]:
    """Return a JSON-safe debug report for the current in-process conformance matrix."""
    return {
        "report_kind": "gsp.conformance.debug-json",
        "version": "0.1",
        "schema_authority": False,
        "array_transport": "omitted",
        "backends": [_backend_report(entry) for entry in backend_conformance_matrix()],
    }


def conformance_debug_report_json() -> str:
    """Return deterministic debug JSON for humans and CI diagnostics.

    This is intentionally not a fixture schema or compatibility contract.
    """
    return json.dumps(conformance_debug_report(), indent=2, sort_keys=True) + "\n"


def _backend_report(entry: BackendConformanceExpectation) -> dict[str, JsonValue]:
    report: dict[str, JsonValue] = {
        "backend_id": entry.backend_id,
        "status": entry.status,
        "reason": entry.reason,
    }
    if entry.replay is not None:
        report["replay"] = _replay_report(entry.replay())
    return report


def _replay_report(replay: InProcessReplayResult) -> dict[str, JsonValue]:
    return {
        "server_name": replay.server_name,
        "visual_families": list(replay.visual_families),
        "extensions": list(replay.extensions),
        "queries": {
            "point": _query_result_report(replay.point_query),
            "guide": _query_result_report(replay.guide_query),
            "guide_miss": _query_result_report(replay.guide_miss),
            "tiled": _query_result_report(replay.tiled_query),
        },
        "tiled_mosaic": {
            "source_rect": list(replay.tiled_mosaic_source_rect),
            "shape": list(replay.tiled_mosaic_shape),
        },
    }


def _query_result_report(result: QueryResult) -> dict[str, JsonValue]:
    report: dict[str, JsonValue] = {
        "request_id": result.request_id,
        "status": result.status.value,
        "hit": result.hit,
        "panel_coordinate": list(result.panel_coordinate),
    }
    _set_if_present(report, "visual_id", result.visual_id)
    _set_if_present(report, "visual_family", _enum_value(result.visual_family))
    _set_if_present(report, "item_id", result.item_id)
    _set_if_present(report, "texel", _optional_number_list(result.texel))
    _set_if_present(report, "visual_coordinate", _optional_number_list(result.visual_coordinate))
    _set_if_present(report, "data_coordinate", _optional_number_list(result.data_coordinate))
    _set_if_present(report, "displayed_rgba", _optional_number_list(result.displayed_rgba))
    _set_if_present(report, "value", _jsonify_value(result.value))
    _set_if_present(report, "extension_payload_kind", result.extension_payload_kind)
    _set_if_present(report, "extension_payload", _extension_payload_report(result.extension_payload))
    _set_if_present(report, "diagnostic", result.diagnostic)
    return report


def _extension_payload_report(payload: object | None) -> JsonValue:
    if payload is None:
        return None
    if isinstance(payload, GuideQueryPayload):
        return {
            "guide_id": payload.guide_id,
            "role": payload.role,
            "axis_dimension": _enum_value(payload.axis_dimension),
            "tick_value": payload.tick_value,
            "text_value": payload.text_value,
        }
    if isinstance(payload, TiledImageQueryPayload):
        return {
            "source_id": payload.source_id,
            "level": payload.level,
            "tile_x": payload.tile_x,
            "tile_y": payload.tile_y,
            "texel_x": payload.texel_x,
            "texel_y": payload.texel_y,
            "source_x": payload.source_x,
            "source_y": payload.source_y,
            "uv": _optional_number_list(payload.uv),
            "value": _jsonify_value(payload.value),
        }
    return repr(payload)


def _set_if_present(report: dict[str, JsonValue], key: str, value: JsonValue) -> None:
    if value is not None:
        report[key] = value


def _enum_value(value: object | None) -> JsonValue:
    if value is None:
        return None
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, str):
        return value
    return repr(value)


def _optional_number_list(values: tuple[int, ...] | tuple[float, ...] | None) -> list[JsonValue] | None:
    if values is None:
        return None
    return list(values)


def _jsonify_value(value: object | None) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, tuple):
        return [_jsonify_value(item) for item in value]
    if isinstance(value, list):
        return [_jsonify_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonify_value(item) for key, item in value.items()}
    return repr(value)
