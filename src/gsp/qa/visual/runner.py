"""Runner for the S023 visual QA harness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
import traceback
from pathlib import Path
from typing import Literal

import matplotlib

matplotlib.use("Agg")
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np

from gsp.protocol import (
    AffineTransform2DResource,
    AxisDimension,
    AxisGuide,
    CanvasSize,
    ColorScale,
    ColorbarGuide,
    CoordinateSpace,
    ImageVisual,
    GUIDE_QUERY_PAYLOAD_KIND,
    LogicalPixelRect,
    MeshShading,
    MeshVisual,
    MarkerVisual,
    PanelTextGuide,
    PathVisual,
    PointVisual,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    SegmentVisual,
    TextAnchorX,
    TextAnchorY,
    TextVisual,
    Texture2D,
    TickSpecKind,
    ResolvedGuideBox,
    ResolvedLayoutSnapshot,
    View2D,
    View3D,
)
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
from gsp.qa.visual.backend_ids import (
    DATOVIZ_BACKEND_ALIASES,
    DATOVIZ_BACKEND_ID,
    MATPLOTLIB_BACKEND_ID,
)
from gsp.qa.visual.case_spec import ProtocolVisual, VisualQACase
from gsp.qa.visual.cases import (
    S023_SUITE,
    S024_SUITE,
    S025_SUITE,
    S026_SUITE,
    S027_SUITE,
    S028_SUITE,
    S034_SUITE,
    S050_SUITE,
    S051_SUITE,
    S059_SUITE,
    case_slug,
    list_cases,
)
from gsp.qa.visual.contact_sheet import write_contact_sheets
from gsp.qa.visual.datoviz_probe import DatovizV04ProbeReport, probe_datoviz_v04
from gsp_datoviz.capabilities import datoviz_v04_grid_clip_to_plot_rect_ready_for_source
from gsp_datoviz.protocol_renderer import (
    DatovizColorPipeline,
    DatovizV04ProtocolRenderer,
    DatovizV04Unavailable,
    DatovizV04Unsupported,
)
from gsp_matplotlib.protocol_renderer import (
    render_colorbar_guide,
    render_image_visual,
    render_marker_visual,
    render_mesh_visual,
    render_path_visual,
    render_point_visual,
    render_segment_visual,
    render_text_visual,
)
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides
from gsp_matplotlib.layout import resolve_matplotlib_layout_snapshot


BackendStatus = Literal["rendered", "unsupported", "error"]
DATOVIZ_QA_OFFSCREEN_ENV = "GSP_DATOVIZ_QA_ENABLE_OFFSCREEN"


@dataclass(frozen=True, slots=True)
class _DatovizGuideAxisConfiguration:
    x_label: str | None
    y_label: str | None
    grid: bool
    backend_auto_ticks: bool
    x_tick_values: tuple[float, ...]
    x_tick_labels: tuple[str, ...] | None
    y_tick_values: tuple[float, ...]
    y_tick_labels: tuple[str, ...] | None


def run_visual_qa_suite(
    *,
    suite: str = S023_SUITE,
    out_dir: Path,
    backends: tuple[str, ...] = ("matplotlib", DATOVIZ_BACKEND_ID),
    case_ids: tuple[str, ...] = (),
    contact_sheet: bool = True,
    run_id: str | None = None,
    resolution: tuple[int, int] = (800, 600),
    device_scale: float = 1.0,
    datoviz_color_pipeline: DatovizColorPipeline = "legacy_srgb_blend",
) -> dict[str, object]:
    """Run the visual QA suite and return its report."""
    if suite not in (
        S023_SUITE,
        S024_SUITE,
        S025_SUITE,
        S026_SUITE,
        S027_SUITE,
        S028_SUITE,
        S034_SUITE,
        S050_SUITE,
        S051_SUITE,
        S059_SUITE,
    ):
        raise ValueError(f"unknown visual QA suite: {suite}")
    normalized_backends = _normalize_backends(backends)
    selected_cases = _select_cases(case_ids, suite=suite)
    ensure_run_dirs(out_dir)
    resolved_run_id = run_id or datetime.now(timezone.utc).strftime(
        f"{suite}-%Y%m%dT%H%M%SZ"
    )
    started_at = datetime.now(timezone.utc).isoformat()
    probe_report = probe_datoviz_v04()

    write_run_manifest(
        out_dir,
        {
            "schema_version": 1,
            "schema_kind": "gsp.visual_qa.run_manifest",
            "stage": suite.upper(),
            "suite": suite,
            "run_id": resolved_run_id,
            "started_at": started_at,
            "backends": list(normalized_backends),
            "case_ids": [case.case_id for case in selected_cases],
            "resolution": list(resolution),
            "device_scale": device_scale,
            "datoviz_color_pipeline": datoviz_color_pipeline,
        },
    )
    write_environment(out_dir, probe_report)
    write_manual_notes(out_dir, tuple(case.case_id for case in selected_cases))

    case_reports: list[dict[str, object]] = []
    for case in selected_cases:
        scene = case.build()
        scene_path, arrays_path = write_scene_artifacts(out_dir, scene)
        write_case_note(out_dir, case.case_id, case.title, scene.notes)
        view = _scene_view(scene.views)
        view3d = scene.view3d
        if view is not None and view3d is not None:
            raise ValueError("visual QA scenes cannot combine View2D and View3D")
        transform_resources = _transform_resource_map(scene.transform_resources)
        backend_reports: dict[str, object] = {}
        if MATPLOTLIB_BACKEND_ID in normalized_backends:
            backend_reports[MATPLOTLIB_BACKEND_ID] = _run_matplotlib(
                out_dir,
                case,
                scene.visuals,
                resolution,
                color_scales={scale.id: scale for scale in scene.color_scales},
                axis_guides=scene.axis_guides,
                panel_text_guides=scene.panel_text_guides,
                colorbar_guides=scene.colorbar_guides,
                view=view,
                view3d=view3d,
                transform_resources=transform_resources,
                device_scale=device_scale,
            )
        if DATOVIZ_BACKEND_ID in normalized_backends:
            backend_reports[DATOVIZ_BACKEND_ID] = _run_datoviz(
                out_dir,
                case,
                scene.visuals,
                resolution,
                probe_report,
                datoviz_color_pipeline,
                color_scales={scale.id: scale for scale in scene.color_scales},
                texture_resources={
                    texture.id: texture for texture in scene.texture_resources
                },
                colorbar_guides=scene.colorbar_guides,
                axis_guides=scene.axis_guides,
                panel_text_guides=scene.panel_text_guides,
                view=view,
                view3d=view3d,
                transform_resources=transform_resources,
            )
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
        contact_paths = write_contact_sheets(
            out_dir, case_reports, normalized_backends, suite=suite
        )
    else:
        contact_paths = ()

    report: dict[str, object] = {
        "schema_version": 1,
        "schema_kind": "gsp.visual_qa.report",
        "stage": suite.upper(),
        "suite": suite,
        "run_id": resolved_run_id,
        "started_at": started_at,
        "environment_path": str(out_dir / "environment.json"),
        "datoviz_probe_summary": _probe_summary(probe_report),
        "datoviz_color_pipeline": datoviz_color_pipeline,
        "device_scale": device_scale,
        "contact_sheets": [str(path) for path in contact_paths],
        "cases": case_reports,
    }
    write_json(out_dir / "report.json", report)
    write_summary(out_dir, report)
    return report


def _normalize_backends(backends: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for backend in backends:
        backend_id = (
            DATOVIZ_BACKEND_ID if backend in DATOVIZ_BACKEND_ALIASES else backend
        )
        if backend_id not in (MATPLOTLIB_BACKEND_ID, DATOVIZ_BACKEND_ID):
            raise ValueError(f"unknown visual QA backend: {backend}")
        if backend_id not in normalized:
            normalized.append(backend_id)
    return tuple(normalized)


def _select_cases(case_ids: tuple[str, ...], *, suite: str) -> tuple[VisualQACase, ...]:
    cases = list_cases(suite=suite)
    if not case_ids:
        return cases
    by_id = {case.case_id: case for case in cases}
    missing = tuple(case_id for case_id in case_ids if case_id not in by_id)
    if missing:
        raise ValueError(f"unknown visual QA cases: {missing}")
    return tuple(by_id[case_id] for case_id in case_ids)


def _run_matplotlib(
    out_dir: Path,
    case: VisualQACase,
    visuals: tuple[ProtocolVisual, ...],
    resolution: tuple[int, int],
    *,
    color_scales: dict[str, ColorScale],
    axis_guides: tuple[AxisGuide, ...],
    panel_text_guides: tuple[PanelTextGuide, ...],
    colorbar_guides: tuple[ColorbarGuide, ...],
    view: View2D | None,
    view3d: View3D | None,
    transform_resources: dict[str, AffineTransform2DResource],
    device_scale: float,
) -> dict[str, object]:
    artifact_path = (
        out_dir / "backends" / "matplotlib" / f"{case_slug(case.case_id)}.png"
    )
    log_path = (
        out_dir / "backends" / "matplotlib" / f"{case_slug(case.case_id)}.log.txt"
    )
    if _has_texture2d_unlit_visual(visuals):
        return _write_matplotlib_unsupported(
            out_dir
            / "backends"
            / "matplotlib"
            / f"{case_slug(case.case_id)}.unsupported.json",
            log_path,
            case,
            reason=(
                "meshvisual_material_texture2d_unlit_unsupported: Matplotlib "
                "visual QA does not render S050 textured meshes"
            ),
            diagnostics={
                "capability": "meshvisual.material.texture2d_unlit.v1",
                "status": "unsupported",
            },
        )
    canvas_size = CanvasSize.pixel_exact(resolution[0], resolution[1])
    resolved_canvas = canvas_size.resolve(output_dpi=100.0, device_scale=device_scale)
    fig, ax = plt.subplots(
        figsize=(
            resolved_canvas.framebuffer_width / resolved_canvas.output_dpi,
            resolved_canvas.framebuffer_height / resolved_canvas.output_dpi,
        ),
        dpi=resolved_canvas.output_dpi,
    )
    setattr(fig, "_gsp_resolved_canvas", resolved_canvas)
    try:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        has_layout_guides = bool(axis_guides or panel_text_guides)
        layout_snapshot: ResolvedLayoutSnapshot | None = None
        if not has_layout_guides:
            ax.set_position((0.0, 0.0, 1.0, 1.0))
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_aspect("equal", adjustable="box")
        if axis_guides or panel_text_guides:
            ax.set_axis_on()
        else:
            ax.set_axis_off()
        for visual in visuals:
            _render_matplotlib_visual(
                ax,
                visual,
                color_scales=color_scales,
                view=view,
                view3d=view3d,
                transform_resources=transform_resources,
            )
        for guide in colorbar_guides:
            render_colorbar_guide(ax, guide, color_scales=color_scales)
        if view is not None and axis_guides:
            render_axis_guides(ax, view, axis_guides)
        if panel_text_guides:
            render_panel_text_guides(ax, panel_text_guides)
        if has_layout_guides:
            fig.tight_layout(pad=0.8)
            layout_snapshot = resolve_matplotlib_layout_snapshot(
                fig,
                ax,
                snapshot_id=f"layout:{case_slug(case.case_id)}:matplotlib",
                view=view,
                axis_guides=axis_guides,
                panel_text_guides=panel_text_guides,
                device_scale=device_scale,
            )
        fig.savefig(
            artifact_path, dpi=resolved_canvas.output_dpi, facecolor=fig.get_facecolor()
        )
        log_path.write_text("rendered\n", encoding="utf-8")
        report: dict[str, object] = {
            "backend_id": "matplotlib",
            "status": "rendered",
            "artifact_path": str(artifact_path),
            "log_path": str(log_path),
        }
        if layout_snapshot is not None:
            report["layout_snapshot_id"] = layout_snapshot.snapshot_id
            report["layout_snapshot"] = _layout_snapshot_report(layout_snapshot)
        return report
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


def _layout_snapshot_report(snapshot: ResolvedLayoutSnapshot) -> dict[str, object]:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "view_id": snapshot.view_id,
        "render_target": {
            "logical_width_px": snapshot.render_target.logical_width_px,
            "logical_height_px": snapshot.render_target.logical_height_px,
            "device_scale": snapshot.render_target.device_scale,
            "framebuffer_width_px": snapshot.render_target.framebuffer_width_px,
            "framebuffer_height_px": snapshot.render_target.framebuffer_height_px,
            "dpi": snapshot.render_target.dpi,
            "pixel_origin": snapshot.render_target.pixel_origin.value,
        },
        "panel_rect_px": _rect_report(snapshot.panel_rect_px),
        "plot_rect_px": _rect_report(snapshot.plot_rect_px),
        "grid_clip_rect_px": (
            _rect_report(snapshot.grid_clip_rect_px)
            if snapshot.grid_clip_rect_px is not None
            else None
        ),
        "title_boxes": [_guide_box_report(box) for box in snapshot.title_boxes],
        "axis_label_boxes": [
            _guide_box_report(box) for box in snapshot.axis_label_boxes
        ],
        "tick_label_box_count": len(snapshot.tick_label_boxes),
        "guide_box_count": len(snapshot.guide_boxes),
        "z_layer_count": len(snapshot.z_layers),
        "diagnostics": [
            {"code": diagnostic.code, "status": diagnostic.status.value}
            for diagnostic in snapshot.diagnostics
        ],
    }


def _guide_box_report(box: ResolvedGuideBox) -> dict[str, object]:
    return {
        "guide_id": box.guide_id,
        "kind": box.kind,
        "role": box.role,
        "rect_px": _rect_report(box.rect_px),
    }


def _rect_report(rect: LogicalPixelRect) -> dict[str, float]:
    return {
        "x": rect.x,
        "y": rect.y,
        "width": rect.width,
        "height": rect.height,
    }


def _run_datoviz(
    out_dir: Path,
    case: VisualQACase,
    visuals: tuple[ProtocolVisual, ...],
    resolution: tuple[int, int],
    probe_report: DatovizV04ProbeReport,
    datoviz_color_pipeline: DatovizColorPipeline,
    *,
    color_scales: dict[str, ColorScale],
    texture_resources: dict[str, Texture2D],
    colorbar_guides: tuple[ColorbarGuide, ...],
    axis_guides: tuple[AxisGuide, ...],
    panel_text_guides: tuple[PanelTextGuide, ...],
    view: View2D | None,
    view3d: View3D | None,
    transform_resources: dict[str, AffineTransform2DResource],
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
            datoviz_color_pipeline=datoviz_color_pipeline,
        )
    if os.environ.get(DATOVIZ_QA_OFFSCREEN_ENV) != "1":
        return _write_datoviz_unsupported(
            unsupported_path,
            log_path,
            case,
            reason=(
                "Datoviz in-process offscreen QA is disabled by default because "
                f"native offscreen view creation can abort the Python process; set "
                f"{DATOVIZ_QA_OFFSCREEN_ENV}=1 to opt in."
            ),
            diagnostics={"env_var": DATOVIZ_QA_OFFSCREEN_ENV, "required_value": "1"},
            datoviz_color_pipeline=datoviz_color_pipeline,
        )
    guide_diagnostics = _datoviz_guide_diagnostics(
        axis_guides,
        panel_text_guides,
        view,
        grid_clip_to_plot_rect=_datoviz_probe_grid_clip_to_plot_rect(probe_report),
    )
    guide_configuration = _datoviz_guide_axis_configuration(axis_guides, view)
    if axis_guides and view is None:
        return _write_datoviz_unsupported(
            unsupported_path,
            log_path,
            case,
            reason="axis_guide_render_unsupported: Datoviz guide rendering requires a View2D",
            diagnostics=guide_diagnostics,
            datoviz_color_pipeline=datoviz_color_pipeline,
        )
    canvas_size = CanvasSize.pixel_exact(resolution[0], resolution[1])
    try:
        renderer_view = None if guide_configuration is not None else view
        with DatovizV04ProtocolRenderer(
            canvas_size=canvas_size,
            color_pipeline=datoviz_color_pipeline,
            color_scales=color_scales,
            texture_resources=texture_resources,
            view=renderer_view,
            view3d=view3d,
            transform_resources=transform_resources,
        ) as renderer:
            if guide_configuration is not None:
                if view is None:
                    raise DatovizV04Unsupported(
                        "axis_guide_render_unsupported: Datoviz guide rendering requires a View2D"
                    )
                renderer.configure_view2d_axes(
                    view,
                    x_label=guide_configuration.x_label,
                    y_label=guide_configuration.y_label,
                    grid=guide_configuration.grid,
                    backend_auto_ticks=guide_configuration.backend_auto_ticks,
                    x_tick_values=guide_configuration.x_tick_values,
                    x_tick_labels=guide_configuration.x_tick_labels,
                    y_tick_values=guide_configuration.y_tick_values,
                    y_tick_labels=guide_configuration.y_tick_labels,
                )
            for visual in visuals:
                _render_datoviz_visual(renderer, visual)
            for guide in colorbar_guides:
                renderer.add_colorbar_guide(guide)
            for title_visual in _datoviz_panel_text_visuals(panel_text_guides):
                renderer.add_text_visual(title_visual)
            png = renderer.capture_png_bytes()
            layout_snapshot_diagnostics: dict[str, object]
            try:
                resolve_partial_layout_snapshot = getattr(
                    renderer, "resolve_partial_layout_snapshot"
                )
                layout_snapshot = resolve_partial_layout_snapshot(
                    snapshot_id_prefix=f"layout:{case_slug(case.case_id)}:datoviz"
                )
            except (
                AttributeError,
                DatovizV04Unavailable,
                DatovizV04Unsupported,
            ) as snapshot_exc:
                layout_snapshot = None
                layout_snapshot_diagnostics = {
                    "layout_snapshot_partial": "unsupported",
                    "layout_snapshot_blocker": str(snapshot_exc),
                }
            else:
                layout_snapshot_diagnostics = _datoviz_layout_snapshot_diagnostics(
                    renderer, case, layout_snapshot
                )
        artifact_path.write_bytes(png)
        log_path.write_text("rendered\n", encoding="utf-8")
        report: dict[str, object] = {
            "backend_id": DATOVIZ_BACKEND_ID,
            "status": "rendered",
            "artifact_path": str(artifact_path),
            "log_path": str(log_path),
            "datoviz_color_pipeline": datoviz_color_pipeline,
        }
        if layout_snapshot is not None:
            report["layout_snapshot_id"] = layout_snapshot.snapshot_id
            report["layout_snapshot"] = _layout_snapshot_report(layout_snapshot)
        if layout_snapshot_diagnostics:
            report["layout_snapshot_diagnostics"] = layout_snapshot_diagnostics
        if guide_diagnostics:
            report["guide_diagnostics"] = (
                guide_diagnostics | layout_snapshot_diagnostics
            )
        elif layout_snapshot_diagnostics:
            report["guide_diagnostics"] = layout_snapshot_diagnostics
        return report
    except Exception as exc:  # noqa: BLE001 - local GPU/display/runtime failures are structured unsupported data.
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        return _write_datoviz_unsupported(
            unsupported_path,
            log_path,
            case,
            reason=f"{type(exc).__name__}: {exc}",
            diagnostics={"exception_type": type(exc).__name__, "message": str(exc)},
            datoviz_color_pipeline=datoviz_color_pipeline,
        )


def _render_matplotlib_visual(
    ax: Axes,
    visual: ProtocolVisual,
    *,
    color_scales: dict[str, ColorScale],
    view: View2D | None,
    view3d: View3D | None,
    transform_resources: dict[str, AffineTransform2DResource],
) -> None:
    if isinstance(visual, PointVisual):
        render_point_visual(
            ax,
            visual,
            color_scales=color_scales,
            view=view,
            transform_resources=transform_resources,
        )
    elif isinstance(visual, MarkerVisual):
        render_marker_visual(
            ax,
            visual,
            color_scales=color_scales,
            view=view,
            transform_resources=transform_resources,
        )
    elif isinstance(visual, SegmentVisual):
        render_segment_visual(
            ax, visual, view=view, transform_resources=transform_resources
        )
    elif isinstance(visual, PathVisual):
        render_path_visual(
            ax, visual, view=view, transform_resources=transform_resources
        )
    elif isinstance(visual, ImageVisual):
        render_image_visual(ax, visual, color_scales=color_scales)
    elif isinstance(visual, TextVisual):
        render_text_visual(
            ax, visual, view=view, transform_resources=transform_resources
        )
    elif isinstance(visual, MeshVisual):
        render_mesh_visual(
            ax,
            visual,
            view=view,
            view3d=view3d,
            transform_resources=transform_resources,
        )
    else:
        raise TypeError(f"unsupported visual type: {type(visual).__name__}")


def _has_texture2d_unlit_visual(visuals: tuple[ProtocolVisual, ...]) -> bool:
    return any(
        isinstance(visual, MeshVisual)
        and visual.canonical_shading() is MeshShading.TEXTURE2D_UNLIT
        for visual in visuals
    )


def _datoviz_layout_snapshot_diagnostics(
    renderer: object,
    case: VisualQACase,
    layout_snapshot: ResolvedLayoutSnapshot,
) -> dict[str, object]:
    diagnostics: dict[str, object] = {
        "layout_snapshot_partial": "available",
        "layout_snapshot_id": layout_snapshot.snapshot_id,
    }
    guide_box = _first_queryable_guide_box(layout_snapshot)
    guide_contribution_count = sum(
        1 for layer in layout_snapshot.z_layers if layer.layer == "guide"
    )
    diagnostics["rendered_contribution_count"] = guide_contribution_count
    diagnostics["rendered_contribution"] = (
        "native-verified" if guide_contribution_count > 0 else "missing"
    )
    if guide_box is None:
        diagnostics.update(
            {
                "guide_box": "missing",
                "guide_identity": "missing",
                "guide_query": "missing",
                "all_rendered_guide_query": "missing",
                "layout_snapshot_id_equality": "missing",
            }
        )
        return diagnostics

    diagnostics["guide_box"] = "native-verified"
    diagnostics["guide_box_id"] = guide_box.guide_id
    query_panel = getattr(renderer, "query_panel", None)
    if not callable(query_panel):
        diagnostics.update(
            {
                "guide_identity": "unsupported",
                "guide_query": "unsupported",
                "all_rendered_guide_query": "unsupported",
                "layout_snapshot_id_equality": "unsupported",
            }
        )
        return diagnostics

    center = (
        guide_box.rect_px.x + guide_box.rect_px.width / 2.0,
        guide_box.rect_px.y + guide_box.rect_px.height / 2.0,
    )
    guide_result = query_panel(
        QueryRequest(
            id=f"query:{case_slug(case.case_id)}:datoviz-guide",
            panel_id="panel:main",
            coordinate=center,
            coordinate_space=QueryCoordinateSpace.PANEL,
            scope=QueryScope.GUIDES,
            hit_policy=QueryHitPolicy.FRONTMOST,
            requested_extension_payload_kinds=(GUIDE_QUERY_PAYLOAD_KIND,),
            layout_snapshot_id=layout_snapshot.snapshot_id,
        )
    )
    all_rendered_result = query_panel(
        QueryRequest(
            id=f"query:{case_slug(case.case_id)}:datoviz-all-rendered-guide",
            panel_id="panel:main",
            coordinate=center,
            coordinate_space=QueryCoordinateSpace.PANEL,
            scope=QueryScope.ALL_RENDERED,
            hit_policy=QueryHitPolicy.FRONTMOST,
            requested_extension_payload_kinds=(GUIDE_QUERY_PAYLOAD_KIND,),
            layout_snapshot_id=layout_snapshot.snapshot_id,
        )
    )
    _record_datoviz_guide_query_diagnostics(
        diagnostics,
        guide_result,
        all_rendered_result,
        guide_id=guide_box.guide_id,
        layout_snapshot_id=layout_snapshot.snapshot_id,
    )
    return diagnostics


def _first_queryable_guide_box(
    layout_snapshot: ResolvedLayoutSnapshot,
) -> ResolvedGuideBox | None:
    for boxes in (
        layout_snapshot.tick_label_boxes,
        layout_snapshot.axis_label_boxes,
        layout_snapshot.title_boxes,
        layout_snapshot.legend_boxes,
        layout_snapshot.colorbar_boxes,
        layout_snapshot.guide_boxes,
    ):
        for box in boxes:
            if box.rect_px.width > 0.0 and box.rect_px.height > 0.0:
                return box
    return None


def _record_datoviz_guide_query_diagnostics(
    diagnostics: dict[str, object],
    guide_result: QueryResult,
    all_rendered_result: QueryResult,
    *,
    guide_id: str,
    layout_snapshot_id: str,
) -> None:
    diagnostics["guide_query_status"] = guide_result.status.value
    diagnostics["all_rendered_guide_query_status"] = all_rendered_result.status.value
    diagnostics["guide_query_layout_snapshot_id"] = guide_result.layout_snapshot_id
    diagnostics["all_rendered_guide_query_layout_snapshot_id"] = (
        all_rendered_result.layout_snapshot_id
    )
    diagnostics["guide_identity"] = (
        "native-verified"
        if guide_result.status == QueryStatus.HIT and guide_result.visual_id == guide_id
        else "mismatch"
    )
    diagnostics["guide_query"] = (
        "native-verified"
        if guide_result.status == QueryStatus.HIT
        and guide_result.layout_snapshot_id == layout_snapshot_id
        else guide_result.status.value
    )
    diagnostics["all_rendered_guide_query"] = (
        "native-verified"
        if all_rendered_result.status == QueryStatus.HIT
        and all_rendered_result.layout_snapshot_id == layout_snapshot_id
        else all_rendered_result.status.value
    )
    diagnostics["layout_snapshot_id_equality"] = (
        "native-verified"
        if guide_result.layout_snapshot_id
        == all_rendered_result.layout_snapshot_id
        == layout_snapshot_id
        else "mismatch"
    )


def _render_datoviz_visual(
    renderer: DatovizV04ProtocolRenderer, visual: ProtocolVisual
) -> None:
    if isinstance(visual, PointVisual):
        renderer.add_point_visual(visual)
    elif isinstance(visual, MarkerVisual):
        renderer.add_marker_visual(visual)
    elif isinstance(visual, SegmentVisual):
        renderer.add_segment_visual(visual)
    elif isinstance(visual, PathVisual):
        renderer.add_path_visual(visual)
    elif isinstance(visual, ImageVisual):
        renderer.add_image_visual(visual)
    elif isinstance(visual, TextVisual):
        renderer.add_text_visual(visual)
    elif isinstance(visual, MeshVisual):
        renderer.add_mesh_visual(visual)
    else:
        raise TypeError(f"unsupported visual type: {type(visual).__name__}")


def _datoviz_guide_axis_configuration(
    axis_guides: tuple[AxisGuide, ...],
    view: View2D | None,
) -> _DatovizGuideAxisConfiguration | None:
    if not axis_guides:
        return None
    if view is None:
        return None

    x_guide = _axis_guide_for_dimension(axis_guides, AxisDimension.X)
    y_guide = _axis_guide_for_dimension(axis_guides, AxisDimension.Y)
    x_values, x_labels = _explicit_tick_payload(x_guide)
    y_values, y_labels = _explicit_tick_payload(y_guide)
    return _DatovizGuideAxisConfiguration(
        x_label=x_guide.label_text if x_guide is not None else None,
        y_label=y_guide.label_text if y_guide is not None else None,
        grid=any(guide.grid_visible for guide in axis_guides),
        backend_auto_ticks=not (x_values or y_values),
        x_tick_values=x_values,
        x_tick_labels=x_labels,
        y_tick_values=y_values,
        y_tick_labels=y_labels,
    )


def _axis_guide_for_dimension(
    axis_guides: tuple[AxisGuide, ...],
    dimension: AxisDimension,
) -> AxisGuide | None:
    matches = [guide for guide in axis_guides if guide.dimension is dimension]
    if len(matches) > 1:
        raise ValueError(f"visual QA Datoviz path supports one {dimension.value} guide")
    return matches[0] if matches else None


def _explicit_tick_payload(
    guide: AxisGuide | None,
) -> tuple[tuple[float, ...], tuple[str, ...] | None]:
    if guide is None or guide.tick_spec.kind is not TickSpecKind.EXPLICIT:
        return (), None
    return guide.tick_spec.explicit_values, guide.tick_spec.explicit_labels


def _datoviz_guide_diagnostics(
    axis_guides: tuple[AxisGuide, ...],
    panel_text_guides: tuple[PanelTextGuide, ...],
    view: View2D | None,
    *,
    grid_clip_to_plot_rect: bool,
) -> dict[str, object]:
    diagnostics: dict[str, object] = {}
    if axis_guides:
        diagnostics["axis_guide_count"] = len(axis_guides)
        diagnostics["axis_provider"] = "datoviz.v04.panel_axis.wip"
        diagnostics["axis_rendering"] = "adapted-review"
        diagnostics["auto_ticks"] = "backend-native"
        diagnostics["guide_query"] = "unsupported"
        diagnostics["all_rendered_guide_query"] = "unsupported"
        diagnostics["view2d_present"] = view is not None
        diagnostics["datoviz_view2d_carrier"] = (
            "dvz_panel_set_domain+DvzPanelView2D policy" if view is not None else "none"
        )
        diagnostics["ordered_ranges_preserved"] = view is not None
        diagnostics["legacy_panel_domain_sync"] = "compat-before-dvz_panel_set_view2d"
        diagnostics["grid_clip_to_plot_rect"] = (
            "native-verified" if grid_clip_to_plot_rect else "unsupported"
        )
        if grid_clip_to_plot_rect:
            diagnostics["grid_clip_evidence"] = (
                "datoviz-native-axis-grid-plot-viewport-clip"
            )
        else:
            diagnostics["grid_clip_blockers"] = [
                "grid_clip_not_enforced",
                "grid_clip_native_api_unverified",
            ]
        if any(guide.tick_spec.kind is TickSpecKind.EXPLICIT for guide in axis_guides):
            diagnostics["explicit_ticks"] = (
                "binding-dependent; dvz_axis_set_ticks when exposed, backend-native ticks otherwise"
            )
    if panel_text_guides:
        diagnostics["panel_text_guide_count"] = len(panel_text_guides)
        diagnostics["panel_title"] = "adapted-review"
        diagnostics["panel_text_adapter"] = "datoviz.ndc_text_visual"
        diagnostics["panel_text_guides_adapted"] = [
            {"id": guide.id, "role": guide.role.value, "text": guide.text}
            for guide in panel_text_guides
        ]
    return diagnostics


def _datoviz_probe_grid_clip_to_plot_rect(
    probe_report: DatovizV04ProbeReport,
) -> bool:
    source = probe_report.sibling_source.get("path")
    source_path = source if isinstance(source, str) else None
    return datoviz_v04_grid_clip_to_plot_rect_ready_for_source(source_path)


def _datoviz_panel_text_visuals(
    panel_text_guides: tuple[PanelTextGuide, ...],
) -> tuple[TextVisual, ...]:
    visuals: list[TextVisual] = []
    for guide in panel_text_guides:
        visuals.append(
            TextVisual(
                id=f"visual:{guide.id}:datoviz-adapted-title",
                texts=(guide.text,),
                positions=np.array([[0.0, 0.92]], dtype=np.float32),
                coordinate_space=CoordinateSpace.NDC,
                rgba=np.array([28, 28, 28, 255], dtype=np.uint8),
                font_size_px=20.0,
                anchor_x=TextAnchorX.CENTER,
                anchor_y=TextAnchorY.TOP,
                z_order=8,
            )
        )
    return tuple(visuals)


def _scene_view(views: tuple[View2D, ...]) -> View2D | None:
    if len(views) > 1:
        raise ValueError("visual QA scenes currently support at most one View2D")
    return views[0] if views else None


def _transform_resource_map(
    resources: tuple[AffineTransform2DResource, ...],
) -> dict[str, AffineTransform2DResource]:
    return {resource.id: resource for resource in resources}


def _write_datoviz_unsupported(
    unsupported_path: Path,
    log_path: Path,
    case: VisualQACase,
    *,
    reason: str,
    diagnostics: object,
    datoviz_color_pipeline: DatovizColorPipeline | None = None,
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
    if datoviz_color_pipeline is not None:
        payload["datoviz_color_pipeline"] = datoviz_color_pipeline
    write_json(unsupported_path, payload)
    if not log_path.exists():
        log_path.write_text(reason + "\n", encoding="utf-8")
    report: dict[str, object] = {
        "backend_id": DATOVIZ_BACKEND_ID,
        "status": "unsupported",
        "unsupported_path": str(unsupported_path),
        "log_path": str(log_path),
        "reason": reason,
    }
    if datoviz_color_pipeline is not None:
        report["datoviz_color_pipeline"] = datoviz_color_pipeline
    return report


def _write_matplotlib_unsupported(
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
        "backend_id": MATPLOTLIB_BACKEND_ID,
        "case_id": case.case_id,
        "status": "unsupported",
        "reason": reason,
        "diagnostics": diagnostics,
    }
    write_json(unsupported_path, payload)
    log_path.write_text(reason + "\n", encoding="utf-8")
    return {
        "backend_id": MATPLOTLIB_BACKEND_ID,
        "status": "unsupported",
        "unsupported_path": str(unsupported_path),
        "log_path": str(log_path),
        "reason": reason,
    }


def _probe_summary(probe_report: DatovizV04ProbeReport) -> dict[str, object]:
    unexpected_hits = probe_report.banned_symbol_check.get("unexpected_hits", [])
    unexpected_hit_count = (
        len(unexpected_hits) if isinstance(unexpected_hits, list) else 0
    )
    return {
        "installed_package": dict(probe_report.installed_package),
        "source_revision": probe_report.sibling_source.get("revision"),
        "facade_imported": probe_report.imports["datoviz"].imported,
        "raw_imported": probe_report.imports["datoviz.raw"].imported,
        "minimal_point_supported": probe_report.minimal_point_scene.supported,
        "capture": dict(probe_report.capture),
        "unexpected_banned_hits": unexpected_hit_count,
    }
