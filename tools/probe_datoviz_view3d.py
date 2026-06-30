#!/usr/bin/env python3
"""Probe Datoviz v0.4 public View3D/camera binding evidence for GSP S037."""

from __future__ import annotations

import json
from types import ModuleType
from typing import Any


REQUIRED_CAMERA_SYMBOLS = (
    "DvzCamera",
    "DvzCameraView",
    "DvzCameraProjection",
    "DvzCameraDesc",
    "dvz_camera_create",
    "dvz_camera_set_view",
    "dvz_camera_set_orthographic",
    "dvz_camera_mvp",
    "dvz_panel_set_camera",
    "dvz_panel_camera",
)

REQUIRED_MESH_DEPTH_SYMBOLS = (
    "dvz_mesh",
    "dvz_visual_set_data",
    "dvz_visual_set_index_data",
    "dvz_visual_set_depth_test",
)


def main() -> int:
    try:
        import datoviz as dvz
    except Exception as exc:  # noqa: BLE001 - probe reports environment state.
        print(
            json.dumps(
                {
                    "status": "unavailable",
                    "reason": f"{type(exc).__name__}: {exc}",
                },
                indent=2,
            )
        )
        return 1

    report = probe_datoviz_view3d(dvz)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"ready", "partial"} else 1


def probe_datoviz_view3d(dvz: ModuleType | Any) -> dict[str, object]:
    """Return structured evidence for Datoviz View3D binding readiness."""
    camera_symbols = _symbol_report(dvz, REQUIRED_CAMERA_SYMBOLS)
    mesh_depth_symbols = _symbol_report(dvz, REQUIRED_MESH_DEPTH_SYMBOLS)
    camera_view_fields = _ctypes_fields(dvz, "DvzCameraView")
    camera_desc_fields = _ctypes_fields(dvz, "DvzCameraDesc")
    camera_projection_fields = _ctypes_fields(dvz, "DvzCameraProjection")
    missing_evidence: list[str] = []

    if not all(camera_symbols.values()):
        missing_evidence.append("missing camera symbols")
    if not all(mesh_depth_symbols.values()):
        missing_evidence.append("missing mesh/depth symbols")
    if not {"eye", "target", "up"}.issubset(set(camera_view_fields)):
        missing_evidence.append("DvzCameraView does not expose eye/target/up fields")
    if not {"view", "projection"}.issubset(set(camera_desc_fields)):
        missing_evidence.append("DvzCameraDesc does not expose view/projection fields")
    if not {"type", "near_clip", "far_clip", "ortho_height"}.issubset(
        set(camera_projection_fields)
    ):
        missing_evidence.append("DvzCameraProjection fields are incomplete")

    orthographic_contract_gap = (
        "Datoviz camera orthographic binding exposes height/near/far; S036 requires explicit "
        "xlim/ylim, reversed x/y bounds, off-axis bounds, and deterministic panel-NDC3 parity."
    )
    missing_evidence.append(orthographic_contract_gap)

    status = "ready" if not missing_evidence else "partial"
    if any(item.startswith("DvzCameraView") or item.startswith("DvzCameraDesc") for item in missing_evidence):
        status = "not-ready"

    return {
        "status": status,
        "datoviz_module": getattr(dvz, "__file__", None),
        "datoviz_version": getattr(dvz, "__version__", None),
        "camera_symbols": camera_symbols,
        "mesh_depth_symbols": mesh_depth_symbols,
        "ctypes_fields": {
            "DvzCameraView": camera_view_fields,
            "DvzCameraDesc": camera_desc_fields,
            "DvzCameraProjection": camera_projection_fields,
        },
        "missing_evidence": missing_evidence,
        "conclusion": (
            "Do not claim Datoviz public View3D MeshVisual support until missing evidence is resolved."
            if missing_evidence
            else "Symbol-level evidence is ready for a runtime retained View3D mesh fixture."
        ),
    }


def _symbol_report(dvz: ModuleType | Any, names: tuple[str, ...]) -> dict[str, bool]:
    return {name: hasattr(dvz, name) for name in names}


def _ctypes_fields(dvz: ModuleType | Any, type_name: str) -> tuple[str, ...]:
    type_obj = getattr(dvz, type_name, None)
    fields = getattr(type_obj, "_fields_", None)
    if fields is None:
        return ()
    return tuple(str(name) for name, _field_type in fields)


if __name__ == "__main__":
    raise SystemExit(main())
