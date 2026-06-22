#!/usr/bin/env python
"""Smoke-test the Datoviz v0.4 facade used by the GSP protocol adapter."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import numpy as np

from gsp.protocol import ImageVisual, PointVisual, QueryCoordinateSpace, QueryRequest
from gsp.protocol.query import QueryStatus
from gsp_datoviz.capabilities import datoviz_v04_capture_diagnostics, datoviz_v04_capture_ready
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    datoviz_v04_sampled_field_diagnostics,
    datoviz_v04_sampled_field_ready,
    is_datoviz_v04_facade,
)
from gsp_datoviz.query import datoviz_v04_query_binding_diagnostics, datoviz_v04_query_binding_ready


_REQUIRED_QUERY_RESULT_FIELDS = (
    "request_id",
    "status",
    "hit",
    "panel_position",
    "visual_id",
    "item_id",
    "texel_id",
    "display_rgba",
    "value_kind",
    "scalar",
    "vector",
    "label",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-query-ready",
        action="store_true",
        help="fail if DvzQueryResult is not decodable from Python",
    )
    parser.add_argument(
        "--require-live-query-hit",
        action="store_true",
        help="fail if the adapter cannot queue, render, poll, and decode a live hit",
    )
    args = parser.parse_args()

    report: dict[str, Any] = {"ok": False}
    try:
        import datoviz as dvz
    except Exception as exc:
        report.update({"error": f"Datoviz import failed: {type(exc).__name__}: {exc}"})
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    report["datoviz_file"] = getattr(dvz, "__file__", None)
    report["datoviz_version"] = getattr(dvz, "__version__", None)
    report["is_v04_facade"] = is_datoviz_v04_facade(dvz)
    report["query_ready"] = datoviz_v04_query_binding_ready(dvz)
    report["query_diagnostics"] = datoviz_v04_query_binding_diagnostics(dvz)
    report["query_result_fields"] = _query_result_fields(dvz)
    report["query_result_field_readback"] = _query_result_field_readback(dvz)
    report["sampled_field_ready"] = datoviz_v04_sampled_field_ready(dvz)
    report["sampled_field_diagnostics"] = datoviz_v04_sampled_field_diagnostics(dvz)
    report["capture_ready"] = datoviz_v04_capture_ready(dvz)
    report["capture_diagnostics"] = datoviz_v04_capture_diagnostics(dvz)

    if not report["is_v04_facade"]:
        report["error"] = "Datoviz import is not the v0.4 dvz_* facade"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    if args.require_query_ready and not report["query_ready"]:
        report["error"] = "Datoviz query binding is not Python-decodable"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    try:
        with DatovizV04ProtocolRenderer(dvz=dvz, width=64, height=64) as renderer:
            caps = renderer.capabilities()
            report["query_modes"] = caps.query_modes
            report["output_formats"] = caps.output_formats
            renderer.add_point_visual(
                PointVisual(
                    id="visual:smoke-points",
                    positions=np.array([[0.0, 0.0]], dtype=np.float32),
                    colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
                    sizes=9.0,
                )
            )
            renderer.add_image_visual(
                ImageVisual(
                    id="visual:smoke-image",
                    image=np.zeros((2, 2, 4), dtype=np.uint8),
                    extent=(-0.5, 0.5, -0.5, 0.5),
                )
            )
            query_result = renderer.query_panel(
                QueryRequest(
                    id="query:smoke",
                    panel_id="panel:main",
                    coordinate=(32.0, 32.0),
                    coordinate_space=QueryCoordinateSpace.PANEL,
                )
            )
            report["live_query_status"] = query_result.status.value
            report["live_query_hit"] = query_result.hit
            report["live_query_visual_family"] = (
                query_result.visual_family.value if hasattr(query_result.visual_family, "value") else query_result.visual_family
            )
            report["live_query_visual_id"] = query_result.visual_id
            report["live_query_item_id"] = query_result.item_id
            report["live_query_texel"] = query_result.texel
            report["live_query_displayed_rgba"] = query_result.displayed_rgba
            report["live_query_value"] = query_result.value
            report["live_query_diagnostic"] = query_result.diagnostic
    except Exception as exc:
        report["error"] = f"GSP Datoviz v0.4 adapter smoke failed: {type(exc).__name__}: {exc}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    if args.require_live_query_hit and report.get("live_query_status") != QueryStatus.HIT.value:
        report["error"] = "GSP Datoviz v0.4 adapter did not produce a live query hit"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    report["ok"] = True
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _query_result_fields(dvz: Any) -> dict[str, bool]:
    query_result_type = getattr(dvz, "DvzQueryResult", None)
    fields = getattr(query_result_type, "_fields_", ())
    field_names = {name for name, *_ in fields}
    return {name: name in field_names for name in _REQUIRED_QUERY_RESULT_FIELDS}


def _query_result_field_readback(dvz: Any) -> dict[str, Any] | None:
    query_result_type = getattr(dvz, "DvzQueryResult", None)
    if query_result_type is None or not hasattr(query_result_type, "_fields_"):
        return None

    result = query_result_type()
    result.request_id = 123
    result.status = 2
    result.hit = False
    result.panel_position[0] = 12.0
    result.panel_position[1] = 34.0
    result.visual_id = 456
    result.item_id = 7
    result.texel_id = 8
    result.display_rgba[0] = 0.25
    result.display_rgba[1] = 0.5
    result.display_rgba[2] = 0.75
    result.display_rgba[3] = 1.0
    result.scalar = 3.5
    result.vector[0] = 1.0
    result.vector[1] = 2.0
    result.vector[2] = 3.0
    result.vector[3] = 4.0
    result.label = b"query-label"
    return {
        "request_id": result.request_id,
        "status": int(result.status),
        "hit": bool(result.hit),
        "panel_position": tuple(result.panel_position),
        "visual_id": result.visual_id,
        "item_id": result.item_id,
        "texel_id": result.texel_id,
        "display_rgba": tuple(result.display_rgba),
        "scalar": result.scalar,
        "vector": tuple(result.vector),
        "label": bytes(result.label).split(b"\x00", 1)[0].decode("utf-8"),
    }


if __name__ == "__main__":
    raise SystemExit(main())
