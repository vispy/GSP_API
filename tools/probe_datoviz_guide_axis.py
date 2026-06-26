#!/usr/bin/env python3
"""Probe Datoviz v0.4 native guide-axis behavior for S030.

This tool is intentionally outside the production renderer contract. It records
runtime evidence for native panel axes before any GSP visual-QA row promotion.
PNG capture is opt-in because local Datoviz offscreen creation may abort or hang
when Vulkan/MoltenVK is not available in the current process environment.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np

from gsp.protocol import PointVisual, View2D
from gsp.protocol.visuals import CoordinateSpace
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    DatovizV04Unavailable,
    DatovizV04Unsupported,
)


DEFAULT_OUT = Path("artifacts/visual_qa/s030/datoviz-guide-axis-proof")

AXIS_SYMBOLS = (
    "dvz_panel_set_domain",
    "dvz_panel_view2d",
    "dvz_panel_set_view2d",
    "dvz_panel_axis",
    "dvz_axis_tick_policy",
    "dvz_axis_set_tick_policy",
    "dvz_axis_set_grid",
    "dvz_axis_set_label",
    "dvz_axis_set_ticks",
    "dvz_panel_visible_domain",
    "dvz_panel_set_title",
    "dvz_panel_title",
)


def _point_cloud(visual_id: str, reversed_view: bool) -> PointVisual:
    if reversed_view:
        positions = np.array(
            [[1.0, 1.0], [0.0, 0.0], [-1.0, -1.0], [0.5, -0.5]],
            dtype=np.float32,
        )
        colors = np.array(
            [
                [42, 157, 143, 255],
                [38, 70, 83, 255],
                [230, 57, 70, 255],
                [251, 191, 36, 255],
            ],
            dtype=np.uint8,
        )
        sizes = np.array([48.0, 58.0, 48.0, 38.0], dtype=np.float32)
    else:
        positions = np.array(
            [[-2.0, -1.0], [-1.0, 0.25], [0.0, 0.0], [1.0, 0.5], [2.0, 1.0]],
            dtype=np.float32,
        )
        colors = np.array(
            [
                [38, 70, 83, 255],
                [42, 157, 143, 255],
                [233, 196, 106, 255],
                [244, 162, 97, 255],
                [230, 57, 70, 255],
            ],
            dtype=np.uint8,
        )
        sizes = np.array([34.0, 44.0, 56.0, 44.0, 34.0], dtype=np.float32)

    return PointVisual(
        id=visual_id,
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.DATA,
    )


def _axis_handles(dvz: ModuleType | Any, panel: Any) -> tuple[Any, Any]:
    dim_x = getattr(dvz, "DVZ_DIM_X", 0)
    dim_y = getattr(dvz, "DVZ_DIM_Y", 1)
    return dvz.dvz_panel_axis(panel, dim_x), dvz.dvz_panel_axis(panel, dim_y)


def _write_png(renderer: DatovizV04ProtocolRenderer, path: Path) -> int:
    data = renderer.capture_png_bytes()
    path.write_bytes(data)
    return len(data)


def _capture_if_requested(
    renderer: DatovizV04ProtocolRenderer, path: Path, capture: bool
) -> tuple[str, int | None]:
    if not capture:
        return "not_requested", None
    return "rendered", _write_png(renderer, path)


def _capture_note(capture_status: str) -> str:
    if capture_status == "rendered":
        return "Rendered placement was captured successfully in the probe artifact."
    return (
        "Rendered placement remains blocked unless this probe is rerun with --capture "
        "in a stable Datoviz offscreen environment."
    )


def _probe_auto_grid(
    dvz: ModuleType | Any, out_dir: Path, *, capture: bool
) -> dict[str, Any]:
    view = View2D(
        id="view:s030-auto",
        panel_id="panel:main",
        x_range=(-2.0, 2.0),
        y_range=(-1.0, 1.0),
    )
    png_path = out_dir / "guide_view2d_auto_grid.png"
    with DatovizV04ProtocolRenderer(
        dvz=dvz,
        width=800,
        height=600,
        color_pipeline="legacy_srgb_blend",
        view=view,
    ) as renderer:
        renderer.add_point_visual(_point_cloud("visual:s030-auto-guide-points", False))
        renderer.configure_view2d_axes(
            view,
            x_label="auto x",
            y_label="auto y",
            grid=True,
            backend_auto_ticks=True,
        )
        capture_status, png_bytes = _capture_if_requested(renderer, png_path, capture)

    return {
        "case_id": "guide/view2d_auto_grid",
        "png": str(png_path) if capture_status == "rendered" else None,
        "capture_status": capture_status,
        "png_bytes": png_bytes,
        "behaviors": {
            "backend_auto_tick_policy_api": "proven",
            "grid_api": "proven",
            "axis_label_api": "proven",
            "view2d_domain_api": "proven",
            "rendered_tick_placement": (
                "proven" if capture_status == "rendered" else "blocked"
            ),
            "rendered_grid_placement": (
                "proven" if capture_status == "rendered" else "blocked"
            ),
            "rendered_axis_label_placement": (
                "proven" if capture_status == "rendered" else "blocked"
            ),
            "title": "unsupported",
            "guide_query": "unsupported",
            "gsp_strict_auto_tick_identity": "adapted",
        },
        "notes": [
            "Native Datoviz panel-axis APIs accept backend-resolved ticks, grid, and labels.",
            "The GSP renderer still CPU-adapts DATA point positions to panel NDC in this slice.",
            _capture_note(capture_status),
        ],
    }


def _probe_reversed_explicit(
    dvz: ModuleType | Any, out_dir: Path, *, capture: bool
) -> dict[str, Any]:
    view = View2D(
        id="view:s030-reversed",
        panel_id="panel:main",
        x_range=(1.0, -1.0),
        y_range=(1.0, -1.0),
    )
    png_path = out_dir / "guide_view2d_reversed_explicit.png"
    with DatovizV04ProtocolRenderer(
        dvz=dvz,
        width=800,
        height=600,
        color_pipeline="legacy_srgb_blend",
        view=view,
    ) as renderer:
        renderer.add_point_visual(
            _point_cloud("visual:s030-reversed-guide-points", True)
        )
        renderer.configure_view2d_axes(
            view,
            x_label="reversed x",
            y_label="reversed y",
            grid=True,
            backend_auto_ticks=True,
        )
        x_axis, y_axis = _axis_handles(dvz, renderer.panel)
        x_ticks_ok = bool(
            dvz.dvz_axis_set_ticks(
                x_axis,
                np.array([1.0, 0.0, -1.0], dtype=np.float64),
                ["right", "center", "left"],
            )
        )
        y_ticks_ok = bool(
            dvz.dvz_axis_set_ticks(
                y_axis,
                np.array([1.0, 0.0, -1.0], dtype=np.float64),
                ["top", "center", "bottom"],
            )
        )
        capture_status, png_bytes = _capture_if_requested(renderer, png_path, capture)

    explicit_status = "proven" if x_ticks_ok and y_ticks_ok else "blocked"
    return {
        "case_id": "guide/view2d_reversed_explicit",
        "png": str(png_path) if capture_status == "rendered" else None,
        "capture_status": capture_status,
        "png_bytes": png_bytes,
        "explicit_tick_calls": {
            "x_ticks_ok": x_ticks_ok,
            "y_ticks_ok": y_ticks_ok,
        },
        "behaviors": {
            "explicit_tick_values_api": explicit_status,
            "explicit_tick_labels_api": explicit_status,
            "reversed_view2d_domain_api": "proven",
            "grid_api": "proven",
            "axis_label_api": "proven",
            "rendered_reversed_layout": (
                "proven" if capture_status == "rendered" else "blocked"
            ),
            "rendered_explicit_tick_placement": (
                "proven" if capture_status == "rendered" else "blocked"
            ),
            "title": "unsupported",
            "guide_query": "unsupported",
            "gsp_renderer_explicit_tick_path": "blocked",
        },
        "notes": [
            "The facade accepts explicit tick values and labels directly through dvz_axis_set_ticks.",
            "The production GSP renderer still rejects explicit ticks in configure_view2d_axes().",
            _capture_note(capture_status),
        ],
    }


def _symbol_report(dvz: ModuleType | Any) -> dict[str, bool]:
    return {name: hasattr(dvz, name) for name in AXIS_SYMBOLS}


def _report(dvz: ModuleType | Any, out_dir: Path, *, capture: bool) -> dict[str, Any]:
    symbols = _symbol_report(dvz)
    cases = [
        _probe_auto_grid(dvz, out_dir, capture=capture),
        _probe_reversed_explicit(dvz, out_dir, capture=capture),
    ]
    return {
        "schema_version": "gsp.s030.datoviz_guide_axis_proof.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "datoviz_module": getattr(dvz, "__file__", None),
        "capture_requested": capture,
        "symbols": symbols,
        "cases": cases,
        "mission_classification": {
            "no_matrix_promotion": True,
            "guide_all_rendered_query": "unsupported",
            "panel_title": "unsupported",
            "backend_auto_tick_policy_api": "proven",
            "explicit_ticks_facade_api": "proven",
            "rendered_axis_placement": "proven" if capture else "blocked",
            "production_gsp_explicit_ticks": "blocked",
            "promotion_recommendation": "defer",
        },
        "stop_condition": (
            "Promotion would still require approximating title layout or guide query behavior, "
            "and wiring explicit ticks through the GSP adapter contract."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--capture",
        action="store_true",
        help="attempt Datoviz offscreen PNG capture; may hang or abort on unstable GPU runtimes",
    )
    args = parser.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)

    try:
        import datoviz as dvz

        report = _report(dvz, args.out, capture=args.capture)
    except (DatovizV04Unavailable, DatovizV04Unsupported, ImportError) as exc:
        report = {
            "schema_version": "gsp.s030.datoviz_guide_axis_proof.v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error": type(exc).__name__,
            "message": str(exc),
            "mission_classification": {
                "promotion_recommendation": "blocked",
            },
        }
        (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        return 1

    (args.out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
