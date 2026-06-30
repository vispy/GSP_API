"""Shared runner for API review examples.

The example files keep the scene construction visible; this helper only handles
backend selection, live display, screenshots, and comparison artifacts.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import json
import os
from pathlib import Path
import sys
import traceback
from typing import Any, Callable

import numpy as np

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    CanvasSize,
    ColorScale,
    ColorbarGuide,
    CoordinateSpace,
    ImageVisual,
    LogicalPixelRect,
    MarkerVisual,
    MeshVisual,
    NavigationPointerEvent,
    NavigationPointerEventKind,
    PanelTextGuide,
    PanelTextRole,
    PointVisual,
    SegmentVisual,
    TextAnchorX,
    TextAnchorY,
    TextVisual,
    TickSpecKind,
    View2D,
    View2DNavigationController,
    View2DNavigationInputAdapter,
)
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer, DatovizV04Unavailable
from gsp_matplotlib.guides import render_axis_guides, render_panel_text_guides
from gsp_matplotlib.navigation import apply_view2d_navigation_action
from gsp_matplotlib.protocol_renderer import (
    render_colorbar_guide,
    render_image_visual,
    render_marker_visual,
    render_mesh_visual,
    render_point_visual,
    render_segment_visual,
    render_text_visual,
)

Visual = (
    PointVisual | MarkerVisual | SegmentVisual | ImageVisual | TextVisual | MeshVisual
)
SceneBuilder = Callable[[], "ReviewScene"]
DATOVIZ_OFFSCREEN_ENV = "GSP_DATOVIZ_QA_ENABLE_OFFSCREEN"
REVIEW_REFERENCE_DPI_ENV = "GSP_REVIEW_REFERENCE_DPI"
REVIEW_MONITOR_DPI_ENV = "GSP_REVIEW_MONITOR_DPI"
REVIEW_DEFAULT_RESOLUTION = (1280, 720)
REVIEW_REFERENCE_DPI = 96.0
REVIEW_OUTPUT_DPI = 100.0


@dataclass(frozen=True, slots=True)
class ReviewScene:
    """Small protocol scene used by a review example."""

    title: str
    visuals: tuple[Visual, ...]
    view: View2D | None = None
    axis_guides: tuple[AxisGuide, ...] = ()
    panel_text_guides: tuple[PanelTextGuide, ...] = ()
    color_scales: tuple[ColorScale, ...] = ()
    colorbar_guides: tuple[ColorbarGuide, ...] = ()
    notes: tuple[str, ...] = ()


def run_review(builder: SceneBuilder) -> int:
    """Run an API review scene through one or both backends."""
    args = _parse_args()
    scene = builder()
    out_dir = args.out_dir or Path("artifacts/example_review") / Path(sys.argv[0]).stem
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "README.md").write_text(_artifact_readme(scene), encoding="utf-8")

    backends = ("matplotlib", "datoviz") if args.backend == "both" else (args.backend,)
    statuses: list[dict[str, object]] = []
    live = not args.offscreen
    for backend in backends:
        if backend == "matplotlib":
            statuses.append(
                _run_matplotlib(
                    scene,
                    out_dir,
                    args.resolution,
                    live=live,
                    interactive_navigation=args.interactive_navigation,
                )
            )
        else:
            statuses.append(
                _run_datoviz(
                    scene,
                    out_dir,
                    args.resolution,
                    live=live,
                    frames=args.frames,
                    allow_offscreen=args.offscreen,
                    interactive_navigation=args.interactive_navigation,
                )
            )
    if args.offscreen and len(statuses) > 1:
        _write_compare(out_dir, statuses)
    (out_dir / "summary.json").write_text(
        json.dumps(statuses, indent=2) + "\n", encoding="utf-8"
    )
    for status in statuses:
        print(
            f"{status['backend']}: {status['status']} ({status.get('path') or status.get('reason', '')})"
        )
    return 0 if any(status["status"] == "rendered" for status in statuses) else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a GSP API review example.")
    parser.add_argument(
        "--backend", choices=("matplotlib", "datoviz", "both"), default="matplotlib"
    )
    parser.add_argument(
        "--offscreen",
        action="store_true",
        help="Write PNG artifacts instead of opening live windows.",
    )
    parser.add_argument(
        "--live",
        action="store_false",
        dest="offscreen",
        help="Open live windows. This is the default.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Artifact directory; defaults to artifacts/example_review/<example>.",
    )
    parser.add_argument(
        "--resolution",
        type=_parse_resolution,
        default=REVIEW_DEFAULT_RESOLUTION,
        help="Capture/window size, e.g. 1280x720.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="Datoviz live frame count; 0 means run until close.",
    )
    parser.add_argument(
        "--datoviz-offscreen",
        action="store_true",
        dest="offscreen",
        help="Deprecated alias for --offscreen.",
    )
    parser.add_argument(
        "--interactive-navigation",
        action="store_true",
        help="In live mode, enable S035 View2D drag-to-pan and wheel-to-zoom when the scene has a View2D.",
    )
    parser.set_defaults(offscreen=False)
    args = parser.parse_args()
    if args.offscreen and args.interactive_navigation:
        parser.error("--interactive-navigation requires live mode")
    return args


def _parse_resolution(value: str) -> tuple[int, int]:
    try:
        width, height = value.lower().split("x", 1)
        parsed = (int(width), int(height))
    except Exception as exc:  # noqa: BLE001 - argparse reports the value.
        raise argparse.ArgumentTypeError(
            "resolution must look like WIDTHxHEIGHT"
        ) from exc
    if parsed[0] <= 0 or parsed[1] <= 0:
        raise argparse.ArgumentTypeError("resolution values must be positive")
    return parsed


def _run_matplotlib(
    scene: ReviewScene,
    out_dir: Path,
    resolution: tuple[int, int],
    *,
    live: bool,
    interactive_navigation: bool,
) -> dict[str, object]:
    import matplotlib

    if not live:
        matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    path = out_dir / "matplotlib.png"
    log_path = out_dir / "matplotlib.log.txt"
    canvas_size = _canvas_size_for_review(resolution, live=live)
    output_dpi = _matplotlib_output_dpi_for_review(canvas_size, live=live)
    resolved_canvas = canvas_size.resolve(output_dpi=output_dpi)
    fig, ax = plt.subplots(
        figsize=(
            resolved_canvas.framebuffer_width / output_dpi,
            resolved_canvas.framebuffer_height / output_dpi,
        ),
        dpi=output_dpi,
    )
    setattr(fig, "_gsp_resolved_canvas", resolved_canvas)
    try:
        color_scales = {scale.id: scale for scale in scene.color_scales}
        _render_matplotlib_scene(fig, ax, scene, color_scales=color_scales)
        if live:
            if interactive_navigation and scene.view is not None:
                session = _MatplotlibReviewNavigationSession(
                    fig, ax, scene, color_scales=color_scales
                )
                session.connect()
                print(
                    "Matplotlib GSP navigation enabled: drag to pan, wheel to zoom."
                )
            plt.show()
        else:
            fig.savefig(
                path, dpi=resolved_canvas.output_dpi, facecolor=fig.get_facecolor()
            )
        log_path.write_text("rendered\n", encoding="utf-8")
        report = {
            "backend": "matplotlib",
            "status": "rendered",
            "log_path": str(log_path),
        }
        if not live:
            report["path"] = str(path)
        return report
    except Exception as exc:  # noqa: BLE001 - examples should leave structured artifacts.
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        return {
            "backend": "matplotlib",
            "status": "error",
            "reason": f"{type(exc).__name__}: {exc}",
            "log_path": str(log_path),
        }
    finally:
        plt.close(fig)


def _configure_matplotlib_axes(ax: object, scene: ReviewScene) -> None:
    ax.figure.patch.set_facecolor("white")
    ax.set_facecolor("white")
    if scene.view is not None:
        ax.set_xlim(*scene.view.x_range)
        ax.set_ylim(*scene.view.y_range)
    else:
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
    ax.set_aspect("auto")
    if scene.axis_guides or scene.panel_text_guides:
        ax.set_axis_on()
    else:
        ax.set_position((0, 0, 1, 1))
        ax.set_axis_off()


def _render_matplotlib_scene(
    fig: object,
    ax: object,
    scene: ReviewScene,
    *,
    color_scales: dict[str, ColorScale],
) -> None:
    for extra_ax in list(fig.axes):
        if extra_ax is not ax:
            extra_ax.remove()
    ax.clear()
    _configure_matplotlib_axes(ax, scene)
    for visual in scene.visuals:
        _render_matplotlib_visual(
            ax, visual, color_scales=color_scales, view=scene.view
        )
    for guide in scene.colorbar_guides:
        render_colorbar_guide(ax, guide, color_scales=color_scales)
    if scene.view is not None and scene.axis_guides:
        render_axis_guides(ax, scene.view, scene.axis_guides)
    if scene.panel_text_guides:
        render_panel_text_guides(ax, scene.panel_text_guides)
    if scene.axis_guides or scene.panel_text_guides or scene.colorbar_guides:
        fig.tight_layout(pad=0.8)


def _render_matplotlib_visual(
    ax: object,
    visual: Visual,
    *,
    color_scales: dict[str, ColorScale],
    view: View2D | None,
) -> None:
    if isinstance(visual, PointVisual):
        render_point_visual(ax, visual, color_scales=color_scales, view=view)
    elif isinstance(visual, MarkerVisual):
        render_marker_visual(ax, visual, color_scales=color_scales, view=view)
    elif isinstance(visual, SegmentVisual):
        render_segment_visual(ax, visual, view=view)
    elif isinstance(visual, ImageVisual):
        render_image_visual(ax, visual, color_scales=color_scales)
    elif isinstance(visual, TextVisual):
        render_text_visual(ax, visual, view=view)
    elif isinstance(visual, MeshVisual):
        render_mesh_visual(ax, visual, view=view)
    else:  # pragma: no cover - typing guard for new visuals.
        raise TypeError(f"unsupported visual type: {type(visual).__name__}")


class _MatplotlibReviewNavigationSession:
    """Attach S035 View2D navigation to a live Matplotlib review scene."""

    def __init__(
        self,
        fig: Any,
        ax: Any,
        scene: ReviewScene,
        *,
        color_scales: dict[str, ColorScale],
    ) -> None:
        if scene.view is None:
            raise ValueError("interactive navigation requires a View2D")
        self.fig = fig
        self.ax = ax
        self.scene = scene
        self.color_scales = color_scales
        self.view = scene.view
        self.revision_index = 1
        self.controller = View2DNavigationController(
            id="nav:review",
            panel_id=self.view.panel_id,
            view_id=self.view.id,
            current_view2d_revision="view-rev:1",
            home_view=self.view,
        )
        self.adapter = View2DNavigationInputAdapter(
            controller_id=self.controller.id,
            view2d_revision=self.controller.current_view2d_revision,
            panel_rect=self._panel_rect(),
            layout_snapshot_id="layout:matplotlib-review-live",
        )

    def connect(self) -> None:
        self.fig.canvas.mpl_connect("button_press_event", self.on_button_press)
        self.fig.canvas.mpl_connect("button_release_event", self.on_button_release)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect("scroll_event", self.on_scroll)

    def on_button_press(self, event: Any) -> None:
        if event.inaxes is not self.ax or event.x is None or event.y is None:
            return
        self.adapter.set_panel_rect(self._panel_rect())
        self.adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.BUTTON_PRESS,
                x_px=float(event.x),
                y_px=float(event.y),
                left_button=event.button == 1,
            )
        )

    def on_button_release(self, event: Any) -> None:
        if event.x is None or event.y is None:
            return
        self.adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.BUTTON_RELEASE,
                x_px=float(event.x),
                y_px=float(event.y),
            )
        )

    def on_motion(self, event: Any) -> None:
        if event.inaxes is not self.ax or event.x is None or event.y is None:
            return
        self._apply_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.MOUSE_MOVE,
                x_px=float(event.x),
                y_px=float(event.y),
            )
        )

    def on_scroll(self, event: Any) -> None:
        if event.inaxes is not self.ax or event.x is None or event.y is None:
            return
        self.adapter.set_panel_rect(self._panel_rect())
        self._apply_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.WHEEL,
                x_px=float(event.x),
                y_px=float(event.y),
                scroll_steps=float(event.step),
            )
        )

    def _apply_event(self, event: NavigationPointerEvent) -> None:
        action = self.adapter.handle_pointer_event(event)
        if action is None:
            return
        result = apply_view2d_navigation_action(
            self.controller,
            self.view,
            self.adapter.panel_rect,
            action,
            next_view2d_revision=self._next_revision(),
            view_snapshot_id=f"view-snapshot:{self.revision_index}",
            expected_layout_snapshot_id="layout:matplotlib-review-live",
        )
        if (
            not result.accepted
            or result.view is None
            or result.new_view2d_revision is None
        ):
            print(f"navigation rejected: {result.diagnostics}")
            return
        self.view = result.view
        self.scene = replace(self.scene, view=self.view)
        self.controller = replace(
            self.controller, current_view2d_revision=result.new_view2d_revision
        )
        self.adapter.accept_navigation_result(result)
        _render_matplotlib_scene(
            self.fig, self.ax, self.scene, color_scales=self.color_scales
        )
        self.fig.canvas.draw_idle()

    def _next_revision(self) -> str:
        self.revision_index += 1
        return f"view-rev:{self.revision_index}"

    def _panel_rect(self) -> LogicalPixelRect:
        self.fig.canvas.draw()
        bbox = self.ax.bbox
        return LogicalPixelRect(
            x=float(bbox.x0),
            y=float(bbox.y0),
            width=float(bbox.width),
            height=float(bbox.height),
        )


def _run_datoviz(
    scene: ReviewScene,
    out_dir: Path,
    resolution: tuple[int, int],
    *,
    live: bool,
    frames: int,
    allow_offscreen: bool,
    interactive_navigation: bool,
) -> dict[str, object]:
    path = out_dir / "datoviz.png"
    unsupported_path = out_dir / "datoviz.unsupported.json"
    log_path = out_dir / "datoviz.log.txt"
    if not live and not (
        allow_offscreen or os.environ.get(DATOVIZ_OFFSCREEN_ENV) == "1"
    ):
        reason = f"Datoviz offscreen capture is opt-in; pass --offscreen or set {DATOVIZ_OFFSCREEN_ENV}=1."
        payload = {"backend": "datoviz", "status": "unsupported", "reason": reason}
        unsupported_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        log_path.write_text(reason + "\n", encoding="utf-8")
        return {
            "backend": "datoviz",
            "status": "unsupported",
            "reason": reason,
            "unsupported_path": str(unsupported_path),
        }
    try:
        color_scales = {scale.id: scale for scale in scene.color_scales}
        axis_config = _axis_config(scene.axis_guides, scene.view)
        renderer_view = None if axis_config is not None else scene.view
        canvas_size = _canvas_size_for_review(resolution, live=live)
        with DatovizV04ProtocolRenderer(
            canvas_size=canvas_size,
            color_scales=color_scales,
            view=renderer_view,
        ) as renderer:
            if axis_config is not None and scene.view is not None:
                renderer.configure_view2d_axes(scene.view, **axis_config)
            for visual in scene.visuals:
                _render_datoviz_visual(renderer, visual)
            for guide in scene.colorbar_guides:
                renderer.add_colorbar_guide(guide)
            for visual in _panel_text_background_visuals(scene.panel_text_guides):
                _render_datoviz_visual(renderer, visual)
            for visual in _panel_text_as_text_visuals(scene.panel_text_guides):
                renderer.add_text_visual(visual)
            if live:
                if interactive_navigation and scene.view is not None:
                    try:
                        renderer.enable_gsp_view2d_navigation(scene.view)
                    except DatovizV04Unavailable as exc:
                        print(
                            "Datoviz GSP navigation unavailable; opening static live window: "
                            f"{exc}"
                        )
                    else:
                        print(
                            "Datoviz GSP navigation enabled: drag to pan, wheel to zoom."
                        )
                renderer.show(frame_count=frames)
            else:
                path.write_bytes(renderer.capture_png_bytes())
        log_path.write_text("rendered\n", encoding="utf-8")
        report = {
            "backend": "datoviz",
            "status": "rendered",
            "classification": "review.adapted",
            "diagnostics": _datoviz_review_diagnostics(scene),
            "log_path": str(log_path),
        }
        if not live:
            report["path"] = str(path)
        return report
    except Exception as exc:  # noqa: BLE001 - local Datoviz availability varies.
        log_path.write_text(traceback.format_exc(), encoding="utf-8")
        payload = {
            "backend": "datoviz",
            "status": "unsupported",
            "reason": f"{type(exc).__name__}: {exc}",
            "log_path": str(log_path),
        }
        unsupported_path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        return {**payload, "unsupported_path": str(unsupported_path)}


def _canvas_size_for_review(resolution: tuple[int, int], *, live: bool) -> CanvasSize:
    if live:
        canvas_size = CanvasSize.reference_px(
            resolution[0],
            resolution[1],
            reference_dpi=_review_reference_dpi(),
        )
        monitor_dpi = _review_monitor_dpi()
        if monitor_dpi is not None:
            canvas_size = canvas_size.with_monitor_dpi_override(monitor_dpi)
        return canvas_size
    return CanvasSize.pixel_exact(resolution[0], resolution[1])


def _matplotlib_output_dpi_for_review(canvas_size: CanvasSize, *, live: bool) -> float:
    if not live:
        return REVIEW_OUTPUT_DPI
    return canvas_size.reference_dpi


def _review_reference_dpi() -> float:
    return _positive_float_env(REVIEW_REFERENCE_DPI_ENV, REVIEW_REFERENCE_DPI)


def _review_monitor_dpi() -> float | None:
    value = os.environ.get(REVIEW_MONITOR_DPI_ENV)
    if value is None or not value.strip():
        return None
    return _positive_float_env(REVIEW_MONITOR_DPI_ENV, REVIEW_REFERENCE_DPI)


def _positive_float_env(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive float") from exc
    if parsed <= 0.0:
        raise ValueError(f"{name} must be a positive float")
    return parsed


def _render_datoviz_visual(
    renderer: DatovizV04ProtocolRenderer, visual: Visual
) -> None:
    if isinstance(visual, PointVisual):
        renderer.add_point_visual(visual)
    elif isinstance(visual, MarkerVisual):
        renderer.add_marker_visual(visual)
    elif isinstance(visual, SegmentVisual):
        renderer.add_segment_visual(visual)
    elif isinstance(visual, ImageVisual):
        renderer.add_image_visual(visual)
    elif isinstance(visual, TextVisual):
        renderer.add_text_visual(visual)
    elif isinstance(visual, MeshVisual):
        renderer.add_mesh_visual(visual)
    else:  # pragma: no cover - typing guard for new visuals.
        raise TypeError(f"unsupported visual type: {type(visual).__name__}")


def _axis_config(
    axis_guides: tuple[AxisGuide, ...], view: View2D | None
) -> dict[str, object] | None:
    if not axis_guides or view is None:
        return None
    x_guide = next(
        (guide for guide in axis_guides if guide.dimension is AxisDimension.X), None
    )
    y_guide = next(
        (guide for guide in axis_guides if guide.dimension is AxisDimension.Y), None
    )
    x_values, x_labels = _explicit_ticks(x_guide)
    y_values, y_labels = _explicit_ticks(y_guide)
    return {
        "x_label": x_guide.label_text if x_guide is not None else None,
        "y_label": y_guide.label_text if y_guide is not None else None,
        "grid": any(guide.grid_visible for guide in axis_guides),
        "backend_auto_ticks": not (x_values or y_values),
        "x_tick_values": x_values,
        "x_tick_labels": x_labels,
        "y_tick_values": y_values,
        "y_tick_labels": y_labels,
    }


def _explicit_ticks(
    guide: AxisGuide | None,
) -> tuple[tuple[float, ...], tuple[str, ...] | None]:
    if guide is None or guide.tick_spec.kind is not TickSpecKind.EXPLICIT:
        return (), None
    return guide.tick_spec.explicit_values, guide.tick_spec.explicit_labels


def _panel_text_as_text_visuals(
    guides: tuple[PanelTextGuide, ...],
) -> tuple[TextVisual, ...]:
    visuals: list[TextVisual] = []
    y = 0.98
    for guide in guides:
        if guide.role is not PanelTextRole.TITLE:
            continue
        visuals.append(
            TextVisual(
                id=f"visual:{guide.id}:datoviz-title",
                texts=(guide.text,),
                positions=np.array([[0.0, y]], dtype=np.float32),
                coordinate_space=CoordinateSpace.NDC,
                rgba=np.array([30, 30, 30, 255], dtype=np.uint8),
                font_size_px=24.0,
                anchor_x=TextAnchorX.CENTER,
                anchor_y=TextAnchorY.TOP,
                z_order=10,
            )
        )
        y -= 0.07
    return tuple(visuals)


def _panel_text_background_visuals(
    guides: tuple[PanelTextGuide, ...],
) -> tuple[MeshVisual, ...]:
    if not any(guide.role is PanelTextRole.TITLE for guide in guides):
        return ()
    return (
        MeshVisual(
            id="visual:datoviz-panel-title-background",
            positions=np.array(
                [[-1.0, 0.86], [1.0, 0.86], [1.0, 1.0], [-1.0, 1.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            order=8.0,
        ),
    )


def _datoviz_review_diagnostics(scene: ReviewScene) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    if any(guide.role is PanelTextRole.TITLE for guide in scene.panel_text_guides):
        diagnostics.append(
            {
                "code": "panel_text_guide_as_screen_text",
                "status": "adapted",
                "message": (
                    "PanelTextGuide TITLE rendered as adapted screen text; it does not "
                    "participate in GSP layout strictness."
                ),
            }
        )
        diagnostics.append(
            {
                "code": "guide_query_missing",
                "status": "unsupported",
                "message": "Datoviz review title does not provide guide query geometry.",
            }
        )
    if any(guide.grid_visible for guide in scene.axis_guides):
        diagnostics.append(
            {
                "code": "grid_clip_not_enforced",
                "status": "adapted",
                "message": (
                    "Datoviz review grid clipping is a review artifact and is not a "
                    "layout-strict plot-rectangle guarantee."
                ),
            }
        )
    return diagnostics


def _write_compare(out_dir: Path, statuses: list[dict[str, object]]) -> None:
    images = [
        (status["backend"], Path(status["path"]))
        for status in statuses
        if status.get("status") == "rendered" and status.get("path")
    ]
    if len(images) < 2:
        (out_dir / "compare_notes.md").write_text(
            "# Compare notes\n\nA side-by-side comparison requires rendered PNGs from both backends.\n",
            encoding="utf-8",
        )
        return
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(images), figsize=(6 * len(images), 4), dpi=120)
    if len(images) == 1:
        axes = [axes]
    for ax, (backend, path) in zip(axes, images, strict=True):
        ax.imshow(mpimg.imread(path))
        ax.set_title(backend)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(out_dir / "compare.png", dpi=120)
    plt.close(fig)


def _artifact_readme(scene: ReviewScene) -> str:
    notes = "\n".join(f"- {note}" for note in scene.notes) or "- No extra notes."
    return f"# {scene.title}\n\n## Notes\n\n{notes}\n"
