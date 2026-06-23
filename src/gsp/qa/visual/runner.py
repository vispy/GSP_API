"""Runner for the S023 visual QA harness."""

from __future__ import annotations

from datetime import datetime, timezone
import traceback
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from gsp.protocol import ImageVisual, MarkerVisual, PointVisual
from gsp.qa.visual.artifacts import (
    ensure_run_dirs,
    write_case_note,
    write_environment,
    write_json,
    write_manual_notes,
    write_run_manifest,
    write_scene_artifacts,
    write_summary,
)
from gsp.qa.visual.backend_ids import DATOVIZ_BACKEND_ALIASES, DATOVIZ_BACKEND_ID, MATPLOTLIB_BACKEND_ID
from gsp.qa.visual.case_spec import ProtocolVisual, VisualQACase
from gsp.qa.visual.cases import S023_SUITE, case_slug, list_cases
from gsp.qa.visual.contact_sheet import write_contact_sheets
from gsp.qa.visual.datoviz_probe import DatovizV04ProbeReport, probe_datoviz_v04
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer
from gsp_matplotlib.protocol_renderer import render_image_visual, render_marker_visual, render_point_visual


BackendStatus = Literal["rendered", "unsupported", "error"]


def run_visual_qa_suite(
    *,
    suite: str = S023_SUITE,
    out_dir: Path,
    backends: tuple[str, ...] = ("matplotlib", DATOVIZ_BACKEND_ID),
    case_ids: tuple[str, ...] = (),
    contact_sheet: bool = True,
    run_id: str | None = None,
    resolution: tuple[int, int] = (800, 600),
) -> dict[str, object]:
    """Run the visual QA suite and return its report."""
    if suite != S023_SUITE:
        raise ValueError(f"unknown visual QA suite: {suite}")
    normalized_backends = _normalize_backends(backends)
    selected_cases = _select_cases(case_ids)
    ensure_run_dirs(out_dir)
    resolved_run_id = run_id or datetime.now(timezone.utc).strftime("s023-%Y%m%dT%H%M%SZ")
    started_at = datetime.now(timezone.utc).isoformat()
    probe_report = probe_datoviz_v04()

    write_run_manifest(
        out_dir,
        {
            "schema_version": 1,
            "schema_kind": "gsp.visual_qa.run_manifest",
            "stage": "S023",
            "suite": suite,
            "run_id": resolved_run_id,
            "started_at": started_at,
            "backends": list(normalized_backends),
            "case_ids": [case.case_id for case in selected_cases],
            "resolution": list(resolution),
        },
    )
    write_environment(out_dir, probe_report)
    write_manual_notes(out_dir, tuple(case.case_id for case in selected_cases))

    case_reports: list[dict[str, object]] = []
    for case in selected_cases:
        scene = case.build()
        scene_path, arrays_path = write_scene_artifacts(out_dir, scene)
        write_case_note(out_dir, case.case_id, case.title, scene.notes)
        backend_reports: dict[str, object] = {}
        if MATPLOTLIB_BACKEND_ID in normalized_backends:
            backend_reports[MATPLOTLIB_BACKEND_ID] = _run_matplotlib(out_dir, case, scene.visuals, resolution)
        if DATOVIZ_BACKEND_ID in normalized_backends:
            backend_reports[DATOVIZ_BACKEND_ID] = _run_datoviz(out_dir, case, scene.visuals, resolution, probe_report)
        case_reports.append(
            {
                "case_id": case.case_id,
                "title": case.title,
                "family": case.family,
                "required_features": list(case.required_features),
                "scene_path": str(scene_path),
                "arrays_path": str(arrays_path),
                "manual_review_status": "pending",
                "backends": backend_reports,
            }
        )

    if contact_sheet:
        contact_paths = write_contact_sheets(out_dir, case_reports, normalized_backends)
    else:
        contact_paths = ()

    report: dict[str, object] = {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.report",
        "stage": "S023",
        "suite": suite,
        "run_id": resolved_run_id,
        "started_at": started_at,
        "environment_path": str(out_dir / "environment.json"),
        "datoviz_probe_summary": _probe_summary(probe_report),
        "contact_sheets": [str(path) for path in contact_paths],
        "cases": case_reports,
    }
    write_json(out_dir / "report.json", report)
    write_summary(out_dir, report)
    return report


def _normalize_backends(backends: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for backend in backends:
        backend_id = DATOVIZ_BACKEND_ID if backend in DATOVIZ_BACKEND_ALIASES else backend
        if backend_id not in (MATPLOTLIB_BACKEND_ID, DATOVIZ_BACKEND_ID):
            raise ValueError(f"unknown visual QA backend: {backend}")
        if backend_id not in normalized:
            normalized.append(backend_id)
    return tuple(normalized)


def _select_cases(case_ids: tuple[str, ...]) -> tuple[VisualQACase, ...]:
    cases = list_cases()
    if not case_ids:
        return cases
    by_id = {case.case_id: case for case in cases}
    missing = tuple(case_id for case_id in case_ids if case_id not in by_id)
    if missing:
        raise ValueError(f"unknown visual QA cases: {missing}")
    return tuple(by_id[case_id] for case_id in case_ids)


def _run_matplotlib(out_dir: Path, case: VisualQACase, visuals: tuple[ProtocolVisual, ...], resolution: tuple[int, int]) -> dict[str, object]:
    artifact_path = out_dir / "backends" / "matplotlib" / f"{case_slug(case.case_id)}.png"
    log_path = out_dir / "backends" / "matplotlib" / f"{case_slug(case.case_id)}.log.txt"
    width, height = resolution
    fig, ax = plt.subplots(figsize=(width / 100.0, height / 100.0), dpi=100)
    try:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.set_position((0.0, 0.0, 1.0, 1.0))
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_aspect("equal", adjustable="box")
        ax.set_axis_off()
        for visual in visuals:
            _render_matplotlib_visual(ax, visual)
        fig.savefig(artifact_path, dpi=100, facecolor=fig.get_facecolor())
        log_path.write_text("rendered\n", encoding="utf-8")
        return {"backend_id": "matplotlib", "status": "rendered", "artifact_path": str(artifact_path), "log_path": str(log_path)}
    except Exception as exc:  # noqa: BLE001 - report renderer failures as artifacts.
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        return {
            "backend_id": "matplotlib",
            "status": "error",
            "error_type": type(exc).__name__,
            "message": str(exc),
            "log_path": str(log_path),
        }
    finally:
        plt.close(fig)


def _run_datoviz(
    out_dir: Path,
    case: VisualQACase,
    visuals: tuple[ProtocolVisual, ...],
    resolution: tuple[int, int],
    probe_report: DatovizV04ProbeReport,
) -> dict[str, object]:
    backend_dir = out_dir / "backends" / DATOVIZ_BACKEND_ID
    artifact_path = backend_dir / f"{case_slug(case.case_id)}.png"
    unsupported_path = backend_dir / f"{case_slug(case.case_id)}.unsupported.json"
    log_path = backend_dir / f"{case_slug(case.case_id)}.log.txt"
    if not probe_report.minimal_point_scene.supported:
        return _write_datoviz_unsupported(
            unsupported_path,
            log_path,
            case,
            reason="Datoviz v0.4 retained-scene point probe is unsupported",
            diagnostics=probe_report.minimal_point_scene.to_json(),
        )
    width, height = resolution
    try:
        with DatovizV04ProtocolRenderer(width=width, height=height) as renderer:
            for visual in visuals:
                _render_datoviz_visual(renderer, visual)
            png = renderer.capture_png_bytes()
        artifact_path.write_bytes(png)
        log_path.write_text("rendered\n", encoding="utf-8")
        return {"backend_id": DATOVIZ_BACKEND_ID, "status": "rendered", "artifact_path": str(artifact_path), "log_path": str(log_path)}
    except Exception as exc:  # noqa: BLE001 - local GPU/display/runtime failures are structured unsupported data.
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        return _write_datoviz_unsupported(
            unsupported_path,
            log_path,
            case,
            reason=f"{type(exc).__name__}: {exc}",
            diagnostics={"exception_type": type(exc).__name__, "message": str(exc)},
        )


def _render_matplotlib_visual(ax: Axes, visual: ProtocolVisual) -> None:
    if isinstance(visual, PointVisual):
        render_point_visual(ax, visual)
    elif isinstance(visual, MarkerVisual):
        render_marker_visual(ax, visual)
    elif isinstance(visual, ImageVisual):
        render_image_visual(ax, visual)
    else:
        raise TypeError(f"unsupported visual type: {type(visual).__name__}")


def _render_datoviz_visual(renderer: DatovizV04ProtocolRenderer, visual: ProtocolVisual) -> None:
    if isinstance(visual, PointVisual):
        renderer.add_point_visual(visual)
    elif isinstance(visual, MarkerVisual):
        renderer.add_marker_visual(visual)
    elif isinstance(visual, ImageVisual):
        renderer.add_image_visual(visual)
    else:
        raise TypeError(f"unsupported visual type: {type(visual).__name__}")


def _write_datoviz_unsupported(
    unsupported_path: Path,
    log_path: Path,
    case: VisualQACase,
    *,
    reason: str,
    diagnostics: object,
) -> dict[str, object]:
    payload = {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.unsupported",
        "backend_id": DATOVIZ_BACKEND_ID,
        "case_id": case.case_id,
        "status": "unsupported",
        "reason": reason,
        "diagnostics": diagnostics,
    }
    write_json(unsupported_path, payload)
    if not log_path.exists():
        log_path.write_text(reason + "\n", encoding="utf-8")
    return {
        "backend_id": DATOVIZ_BACKEND_ID,
        "status": "unsupported",
        "unsupported_path": str(unsupported_path),
        "log_path": str(log_path),
        "reason": reason,
    }


def _probe_summary(probe_report: DatovizV04ProbeReport) -> dict[str, object]:
    unexpected_hits = probe_report.banned_symbol_check.get("unexpected_hits", [])
    unexpected_hit_count = len(unexpected_hits) if isinstance(unexpected_hits, list) else 0
    return {
        "installed_package": dict(probe_report.installed_package),
        "source_revision": probe_report.sibling_source.get("revision"),
        "facade_imported": probe_report.imports["datoviz"].imported,
        "raw_imported": probe_report.imports["datoviz.raw"].imported,
        "minimal_point_supported": probe_report.minimal_point_scene.supported,
        "capture": dict(probe_report.capture),
        "unexpected_banned_hits": unexpected_hit_count,
    }
