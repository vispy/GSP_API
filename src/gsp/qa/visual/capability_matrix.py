"""Capability matrix generation for visual QA review packs."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from gsp.qa.visual.artifacts import write_json
from gsp.qa.visual.backend_ids import DATOVIZ_BACKEND_ID, MATPLOTLIB_BACKEND_ID


CAPABILITY_STATUSES = (
    "strict",
    "adapted",
    "experimental",
    "unsupported",
    "disabled",
    "crashed",
    "not_run",
)

_DATOVIZ_S029_STRICT_RENDER_CASES = {
    "point/basic_ndc": [],
    "point/diameter_ramp_ndc": [],
    "point/alpha_overlap_ndc": [],
    "marker/shapes_ndc": [],
    "marker/angle_size_stroke_ndc": [],
    "segment/width_cap_ndc": [],
    "segment/alpha_order_ndc": [],
    "path/subpaths_width_join_ndc": [],
    "image/checker_nearest_ndc": [
        "Datoviz uses retained RGBA8 image upload; S029 verifies nearest sampling, NDC extent, and upper-origin orientation"
    ],
    "image/origin_lower_ndc": [
        "Datoviz uses retained RGBA8 image upload; S029 verifies lower-origin texcoord adaptation and NDC extent"
    ],
    "image/scalar_gray_clim_ndc": [
        "GSP CPU maps scalar gray/clim data to canonical RGBA8 before Datoviz upload; S029 verifies rendered gray/clim output"
    ],
    "image/rgba_alpha_ndc": [
        "Datoviz uses retained RGBA8 image upload with legacy sRGB blending for Matplotlib parity"
    ],
    "overlay/point_over_image_ndc": [
        "S029 verifies Datoviz point-over-image layering for the rendered NDC overlay scope"
    ],
    "color/scalar_image_viridis_colorbar": [
        "GSP CPU maps the scalar image through the canonical viridis ColorScale before Datoviz RGBA8 upload",
        "Datoviz native colorbar rendering receives explicit GSP tick values and labels for the S029 case",
    ],
    "color/point_scalar_gray_range": [
        "GSP CPU maps scalar point values through the canonical gray ColorScale before Datoviz RGBA8 upload",
        "S029 verifies under-range and over-range endpoint clipping for the rendered point scope",
    ],
    "color/marker_scalar_fill_alpha": [
        "GSP CPU maps scalar marker fill values through the canonical magma ColorScale before Datoviz RGBA8 upload",
        "S029 verifies scalar fill alpha with a constant marker stroke for the rendered marker scope",
    ],
    "text/rotation_alpha_ndc": [
        "Datoviz retained text receives per-item NDC positions, UTF-8 ASCII strings, RGBA alpha, font size, center anchors, and rotation radians",
        "S029 verifies the rendered text draws above the orientation image with alpha blending and center-anchored rotation",
    ],
}

_DATOVIZ_S029_RENDERED_BLOCKERS = {
    "text/basic_ndc": [
        "default BASELINE text-anchor semantics are not strictly verified by the Datoviz adapter"
    ],
    "text/anchor_grid_ndc": [
        "baseline, top, center, and bottom text-box anchors need a focused fixture before strict promotion"
    ],
    "text/data_vs_ndc": [
        "DATA and NDC text placement is only proven under the identity [-1,+1] review-pack view"
    ],
    "text/multiline_unicode_smoke": [
        "Unicode fallback and multiline BASELINE anchoring remain unverified"
    ],
}


def build_capability_matrix(report: Mapping[str, object]) -> dict[str, object]:
    """Build a backend capability matrix from a visual QA report."""
    rows: list[dict[str, object]] = []
    cases = report.get("cases", [])
    if not isinstance(cases, list):
        raise TypeError("visual QA report cases must be a list")

    for case in cases:
        if not isinstance(case, Mapping):
            raise TypeError("visual QA report case entries must be mappings")
        backends = case.get("backends", {})
        if not isinstance(backends, Mapping):
            raise TypeError("visual QA report case backends must be a mapping")
        rows.append(_matrix_row(case, MATPLOTLIB_BACKEND_ID, backends))
        rows.append(_matrix_row(case, DATOVIZ_BACKEND_ID, backends))

    counts = Counter(str(row["status"]) for row in rows)
    summary = {status: counts.get(status, 0) for status in CAPABILITY_STATUSES}
    return {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.capability_matrix",
        "suite": report.get("suite"),
        "stage": report.get("stage"),
        "run_id": report.get("run_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status_taxonomy": list(CAPABILITY_STATUSES),
        "summary": summary,
        "rows": rows,
    }


def write_capability_matrix(out_dir: Path, report: Mapping[str, object]) -> dict[str, object]:
    """Write JSON and Markdown capability matrix artifacts."""
    matrix = build_capability_matrix(report)
    write_json(out_dir / "capability_matrix.json", matrix)
    (out_dir / "capability_matrix.md").write_text(
        _matrix_markdown(matrix), encoding="utf-8"
    )
    return matrix


def write_review_pack_index(
    out_dir: Path, report: Mapping[str, object], matrix: Mapping[str, object]
) -> None:
    """Write a compact review-pack index."""
    write_json(out_dir / "summary.json", _review_summary(report, matrix))
    (out_dir / "index.md").write_text(_index_markdown(report, matrix), encoding="utf-8")


def _matrix_row(
    case: Mapping[str, object], backend_id: str, backends: Mapping[str, object]
) -> dict[str, object]:
    backend_entry = backends.get(backend_id)
    if not isinstance(backend_entry, Mapping):
        return _base_row(case, backend_id) | {
            "status": "not_run",
            "rendering_supported": False,
            "query_supported": False,
            "reason_code": "backend_not_run",
            "known_adaptations": [],
            "known_missing_semantics": [],
            "promotion_blockers": ["backend was not selected for this review pack"],
            "evidence_artifacts": [],
        }

    backend_status = str(backend_entry.get("status", "not_run"))
    if backend_id == MATPLOTLIB_BACKEND_ID:
        return _matplotlib_row(case, backend_entry, backend_status)
    return _datoviz_row(case, backend_entry, backend_status)


def _matplotlib_row(
    case: Mapping[str, object],
    backend_entry: Mapping[str, object],
    backend_status: str,
) -> dict[str, object]:
    if backend_status == "rendered":
        status = "strict"
        reason_code = "matplotlib_reference_rendered"
        blockers: list[str] = []
    elif backend_status == "error":
        status = "crashed"
        reason_code = "matplotlib_reference_error"
        blockers = ["Matplotlib reference render failed"]
    else:
        status = "not_run"
        reason_code = "matplotlib_reference_not_run"
        blockers = ["Matplotlib reference was not rendered"]
    return _base_row(case, MATPLOTLIB_BACKEND_ID) | {
        "status": status,
        "rendering_supported": backend_status == "rendered",
        "query_supported": False,
        "reason_code": reason_code,
        "known_adaptations": [],
        "known_missing_semantics": [],
        "promotion_blockers": blockers,
        "evidence_artifacts": _evidence_artifacts(backend_entry),
    }


def _datoviz_row(
    case: Mapping[str, object],
    backend_entry: Mapping[str, object],
    backend_status: str,
) -> dict[str, object]:
    reason = _backend_reason(backend_entry)
    if backend_status == "rendered":
        promotion = _datoviz_rendered_promotion(case)
        if promotion is not None:
            status = "strict"
            reason_code = "datoviz_rendered_strict_s029_family_audit"
            adaptations = promotion
            missing: list[str] = []
            blockers: list[str] = []
        else:
            status = "adapted"
            reason_code = "datoviz_rendered_pending_promotion_audit"
            adaptations = ["Datoviz rendering is reviewable but not yet promoted to strict"]
            missing = []
            blockers = _datoviz_rendered_blockers(case)
    elif backend_status == "error":
        status = "crashed"
        reason_code = "datoviz_runtime_error"
        adaptations = []
        missing = [reason] if reason else []
        blockers = ["runtime error must be isolated before promotion"]
    else:
        reason_code, status, missing = _classify_datoviz_unsupported(reason)
        adaptations = []
        blockers = _datoviz_blockers(reason_code)

    return _base_row(case, DATOVIZ_BACKEND_ID) | {
        "status": status,
        "rendering_supported": backend_status == "rendered",
        "query_supported": False,
        "reason_code": reason_code,
        "known_adaptations": adaptations,
        "known_missing_semantics": missing,
        "promotion_blockers": blockers,
        "evidence_artifacts": _evidence_artifacts(backend_entry),
    }


def _datoviz_rendered_promotion(case: Mapping[str, object]) -> list[str] | None:
    case_id = case.get("case_id")
    if not isinstance(case_id, str):
        return None
    return _DATOVIZ_S029_STRICT_RENDER_CASES.get(case_id)


def _datoviz_rendered_blockers(case: Mapping[str, object]) -> list[str]:
    case_id = case.get("case_id")
    if isinstance(case_id, str):
        blockers = _DATOVIZ_S029_RENDERED_BLOCKERS.get(case_id)
        if blockers is not None:
            return blockers
    return ["strict promotion requires a family-specific capability audit"]


def _classify_datoviz_unsupported(reason: str) -> tuple[str, str, list[str]]:
    if "offscreen QA is disabled" in reason:
        return (
            "datoviz_offscreen_disabled",
            "disabled",
            ["Datoviz offscreen rendering was not opted in for this run"],
        )
    if "missing dvz_" in reason or "facade is missing" in reason:
        return ("datoviz_backend_symbol_missing", "unsupported", [reason])
    if "TextVisual support is unavailable" in reason or "NDC text positions only" in reason:
        return (
            "gsp_datoviz_text_adapter_unverified",
            "unsupported",
            [
                "Datoviz retained text symbols are present in current v0.4 probes, "
                "but the GSP adapter has not verified text placement, anchors, "
                "font-size, rotation, DATA mapping, and query semantics"
            ],
        )
    if "NDC mesh positions only" in reason:
        return (
            "datoviz_data_coordinates_unsupported",
            "unsupported",
            ["DATA coordinates/View2D mapping are not wired through this Datoviz mesh path"],
        )
    if "axis_guide_render_unsupported" in reason:
        return (
            "datoviz_axis_guide_contract_unverified",
            "unsupported",
            [
                "axis guide rendering, explicit tick labels, panel title placement, "
                "and guide query semantics are unverified"
            ],
        )
    if "colorbar_render_unsupported" in reason:
        return (
            "datoviz_colorbar_contract_unverified",
            "unsupported",
            ["native Datoviz colorbar facade requirements are unavailable"],
        )
    if "missing color scale" in reason:
        return (
            "qa_datoviz_color_scales_not_wired",
            "unsupported",
            ["visual QA runner did not pass color scales into the Datoviz renderer for this case"],
        )
    if "scalar_visual_family_unsupported" in reason:
        return (
            "datoviz_scalar_visual_family_unsupported",
            "unsupported",
            ["scalar color mapping for this visual family is not implemented by the Datoviz adapter"],
        )
    if "GSP_TRANSFORM_MISSING_REF" in reason:
        return (
            "datoviz_named_transform_unresolved",
            "unsupported",
            ["named transform resources are not resolved by the Datoviz CPU transform adapter"],
        )
    if "GSP_VIEW2D_MISSING" in reason or "NDC point positions only" in reason:
        return (
            "datoviz_data_coordinates_unsupported",
            "unsupported",
            ["DATA coordinates require a View2D for Datoviz CPU panel-NDC adaptation"],
        )
    return ("datoviz_adapter_unsupported", "unsupported", [reason] if reason else [])


def _datoviz_blockers(reason_code: str) -> list[str]:
    if reason_code == "datoviz_offscreen_disabled":
        return ["rerun with Datoviz offscreen opt-in or subprocess isolation"]
    if reason_code == "datoviz_backend_symbol_missing":
        return ["Datoviz Python facade must expose the required v0.4 symbol"]
    if reason_code == "qa_datoviz_color_scales_not_wired":
        return ["pass QA color scales and colorbar guides into the Datoviz renderer"]
    if reason_code == "datoviz_named_transform_unresolved":
        return ["resolve named transform resources before Datoviz dispatch"]
    if reason_code == "datoviz_data_coordinates_unsupported":
        return ["wire View2D/DATA mapping through the Datoviz adapter"]
    if reason_code == "datoviz_axis_guide_contract_unverified":
        return ["wire Datoviz axis guides, panel titles, explicit tick labels, and guide query semantics"]
    return ["promote only after a focused Datoviz capability audit"]


def _backend_reason(backend_entry: Mapping[str, object]) -> str:
    for key in ("reason", "message"):
        value = backend_entry.get(key)
        if isinstance(value, str):
            return value
    unsupported_path = backend_entry.get("unsupported_path")
    if isinstance(unsupported_path, str):
        path = Path(unsupported_path)
        if path.exists():
            try:
                import json

                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return ""
            diagnostics = payload.get("diagnostics")
            if isinstance(diagnostics, Mapping):
                message = diagnostics.get("message")
                if isinstance(message, str):
                    return message
            reason = payload.get("reason")
            if isinstance(reason, str):
                return reason
    return ""


def _base_row(case: Mapping[str, object], backend_id: str) -> dict[str, object]:
    required_features = case.get("required_features", [])
    protocol_scope = (
        [str(value) for value in required_features]
        if isinstance(required_features, (list, tuple))
        else []
    )
    return {
        "case_id": str(case.get("case_id", "")),
        "family": str(case.get("family", "")),
        "backend": backend_id,
        "protocol_scope": protocol_scope,
    }


def _evidence_artifacts(backend_entry: Mapping[str, object]) -> list[str]:
    artifacts: list[str] = []
    for key in ("artifact_path", "unsupported_path", "log_path"):
        value = backend_entry.get(key)
        if isinstance(value, str):
            artifacts.append(value)
    return artifacts


def _review_summary(
    report: Mapping[str, object], matrix: Mapping[str, object]
) -> dict[str, object]:
    raw_rows = matrix.get("rows", [])
    rows = raw_rows if isinstance(raw_rows, list) else []
    datoviz_rows = [
        row
        for row in rows
        if isinstance(row, Mapping) and row.get("backend") == DATOVIZ_BACKEND_ID
    ]
    datoviz_counts = Counter(str(row.get("status")) for row in datoviz_rows)
    raw_cases = report.get("cases", [])
    cases = raw_cases if isinstance(raw_cases, list) else []
    return {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.review_summary",
        "suite": report.get("suite"),
        "run_id": report.get("run_id"),
        "case_count": len(cases),
        "datoviz_status_counts": {
            status: datoviz_counts.get(status, 0) for status in CAPABILITY_STATUSES
        },
        "capability_matrix_path": "capability_matrix.json",
        "contact_sheets": report.get("contact_sheets", []),
    }


def _matrix_markdown(matrix: Mapping[str, object]) -> str:
    rows = matrix.get("rows", [])
    lines = [
        "# Backend Capability Matrix",
        "",
        f"Run id: `{matrix.get('run_id')}`",
        "",
        "| Case | Backend | Status | Reason code | Rendering | Query |",
        "|---|---|---|---|---|---|",
    ]
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            lines.append(
                "| "
                f"`{row.get('case_id')}` | "
                f"{row.get('backend')} | "
                f"{row.get('status')} | "
                f"`{row.get('reason_code')}` | "
                f"{row.get('rendering_supported')} | "
                f"{row.get('query_supported')} |"
            )
    return "\n".join(lines) + "\n"


def _index_markdown(report: Mapping[str, object], matrix: Mapping[str, object]) -> str:
    summary = matrix.get("summary", {})
    lines = [
        "# Visual QA Review Pack",
        "",
        f"Run id: `{report.get('run_id')}`",
        f"Suite: `{report.get('suite')}`",
        "",
        "## Entry Points",
        "",
        "- `report.json`: raw visual QA run report",
        "- `capability_matrix.json`: machine-readable capability matrix",
        "- `capability_matrix.md`: human-readable capability matrix",
        "- `summary.json`: compact review-pack summary",
        "- `contact_sheets/`: Matplotlib-left / Datoviz-right sheets when both backends ran",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    if isinstance(summary, Mapping):
        for status in CAPABILITY_STATUSES:
            lines.append(f"| {status} | {summary.get(status, 0)} |")
    return "\n".join(lines) + "\n"
