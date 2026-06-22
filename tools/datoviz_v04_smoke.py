#!/usr/bin/env python
"""Smoke-test the Datoviz v0.4 facade used by the GSP protocol adapter."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import numpy as np

from gsp.protocol import ImageVisual, PointVisual, QueryCoordinateSpace, QueryRequest
from gsp_datoviz.capabilities import datoviz_v04_capture_diagnostics, datoviz_v04_capture_ready
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    datoviz_v04_sampled_field_diagnostics,
    datoviz_v04_sampled_field_ready,
    is_datoviz_v04_facade,
)
from gsp_datoviz.query import datoviz_v04_query_binding_diagnostics, datoviz_v04_query_binding_ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-query-ready",
        action="store_true",
        help="fail if DvzQueryResult is not decodable from Python",
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
            report["bounded_query_status"] = query_result.status.value
            report["bounded_query_diagnostic"] = query_result.diagnostic
    except Exception as exc:
        report["error"] = f"GSP Datoviz v0.4 adapter smoke failed: {type(exc).__name__}: {exc}"
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    report["ok"] = True
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
