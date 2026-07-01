"""Run the S035 retained View2D navigation performance smoke."""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import replace
import json
from pathlib import Path

import numpy as np

from gsp.protocol import (
    CoordinateSpace,
    LogicalPixelRect,
    NavigationPointerEvent,
    NavigationPointerEventKind,
    PointVisual,
    View2D,
    View2DNavigationController,
    View2DNavigationInputAdapter,
)
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer
from gsp_matplotlib.navigation import apply_view2d_navigation_action
from gsp_matplotlib.protocol_renderer import render_point_visual

UPLOAD_CALLS = {
    "add_visual",
    "image",
    "mesh",
    "point",
    "sampled_field_set_data",
    "set_data",
    "set_index_data",
    "set_texture",
}
RETAINED_UPDATE_CALLS = {"panel_view2d", "set_domain", "set_view2d"}


def main() -> int:
    """Run one or both S035 navigation smokes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("matplotlib", "datoviz-fake", "both"), default="both")
    parser.add_argument("--steps", type=int, default=40, help="Number of scripted navigation updates.")
    parser.add_argument("--points", type=int, default=25000, help="Point count used by the smoke scene.")
    parser.add_argument("--out", type=Path, help="Optional path for the JSON smoke report.")
    args = parser.parse_args()

    backends = ("matplotlib", "datoviz-fake") if args.backend == "both" else (args.backend,)
    report = {
        "stage": "S035",
        "updates_requested": args.steps,
        "points": args.points,
        "results": [run_smoke(backend, steps=args.steps, points=args.points) for backend in backends],
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if all(result["status"] == "passed" for result in report["results"]) else 1


def run_smoke(backend: str, *, steps: int, points: int) -> dict[str, object]:
    """Run one backend smoke and return a JSON-serializable result."""
    if steps <= 0:
        raise ValueError("steps must be positive")
    if points <= 0:
        raise ValueError("points must be positive")
    if backend == "matplotlib":
        return _run_matplotlib_smoke(steps=steps, points=points)
    if backend == "datoviz-fake":
        return _run_datoviz_fake_smoke(steps=steps, points=points)
    raise ValueError(f"unsupported backend: {backend}")


def _run_matplotlib_smoke(*, steps: int, points: int) -> dict[str, object]:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.0, 4.0), dpi=100.0)
    view = _initial_view()
    visual = _point_visual(points)
    render_point_visual(ax, visual, view=view)
    ax.set_xlim(view.x_range)
    ax.set_ylim(view.y_range)
    session = _ScriptedSession(view)
    updates = 0
    for next_view in session.run(steps):
        updates += 1
        view = next_view
        ax.set_xlim(view.x_range)
        ax.set_ylim(view.y_range)
        fig.canvas.draw()
    plt.close(fig)
    return {
        "backend": "matplotlib",
        "status": "passed",
        "navigation_updates": updates,
        "frames_drawn": updates,
        "visual_upload_calls_during_navigation": 0,
        "retained_update_calls_during_navigation": updates,
        "final_x_range": list(view.x_range),
        "final_y_range": list(view.y_range),
    }


def _run_datoviz_fake_smoke(*, steps: int, points: int) -> dict[str, object]:
    fake = _FakeDatovizV04()
    view = _initial_view()
    visual = _point_visual(points)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view=view)
    renderer.add_point_visual(visual)
    baseline_call_count = len(fake.calls)
    session = _ScriptedSession(view)
    updates = 0
    for next_view in session.run(steps):
        updates += 1
        renderer.apply_retained_view2d_navigation(next_view)
    navigation_calls = fake.calls[baseline_call_count:]
    upload_calls = _count_calls(navigation_calls, UPLOAD_CALLS)
    retained_update_calls = _count_calls(navigation_calls, RETAINED_UPDATE_CALLS)
    status = "passed" if upload_calls == 0 and retained_update_calls >= updates else "failed"
    return {
        "backend": "datoviz-fake",
        "status": status,
        "navigation_updates": updates,
        "frames_drawn": 0,
        "visual_upload_calls_during_navigation": upload_calls,
        "retained_update_calls_during_navigation": retained_update_calls,
        "set_domain_calls_during_navigation": _count_calls(navigation_calls, {"set_domain"}),
        "set_view2d_calls_during_navigation": _count_calls(navigation_calls, {"set_view2d"}),
        "final_x_range": list(renderer.view.x_range),
        "final_y_range": list(renderer.view.y_range),
    }


class _ScriptedSession:
    def __init__(self, view: View2D) -> None:
        self.view = view
        self.revision_index = 1
        self.panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=900.0, height=650.0)
        self.controller = View2DNavigationController(
            id="nav:main",
            panel_id=view.panel_id,
            view_id=view.id,
            current_view2d_revision="view-rev:1",
            home_view=view,
        )
        self.adapter = View2DNavigationInputAdapter(
            controller_id=self.controller.id,
            view2d_revision=self.controller.current_view2d_revision,
            panel_rect=self.panel_rect,
            layout_snapshot_id="layout:smoke",
        )

    def run(self, steps: int):
        self.adapter.handle_pointer_event(
            NavigationPointerEvent(NavigationPointerEventKind.BUTTON_PRESS, 450.0, 325.0, left_button=True)
        )
        for index in range(steps):
            event = self._event_for_step(index)
            action = self.adapter.handle_pointer_event(event)
            if action is None:
                continue
            result = apply_view2d_navigation_action(
                self.controller,
                self.view,
                self.panel_rect,
                action,
                next_view2d_revision=self._next_revision(),
                view_snapshot_id=f"view-snapshot:{self.revision_index}",
                expected_layout_snapshot_id="layout:smoke",
            )
            if not result.accepted or result.view is None or result.new_view2d_revision is None:
                raise RuntimeError(f"navigation action rejected: {result.diagnostics}")
            self.view = result.view
            self.controller = replace(self.controller, current_view2d_revision=result.new_view2d_revision)
            self.adapter.accept_navigation_result(result)
            yield self.view
        self.adapter.handle_pointer_event(
            NavigationPointerEvent(NavigationPointerEventKind.BUTTON_RELEASE, 530.0, 325.0)
        )

    def _event_for_step(self, index: int) -> NavigationPointerEvent:
        if index % 5 == 0:
            return NavigationPointerEvent(NavigationPointerEventKind.WHEEL, 450.0, 325.0, scroll_steps=1.0)
        x_px = 450.0 + float(index * 2)
        y_px = 325.0 + float((index % 3) - 1)
        return NavigationPointerEvent(NavigationPointerEventKind.MOUSE_MOVE, x_px, y_px)

    def _next_revision(self) -> str:
        self.revision_index += 1
        return f"view-rev:{self.revision_index}"


class _FakeDatovizV04:
    DVZ_COLOR_PIPELINE_LINEAR_SRGB = 10
    DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND = 11

    def __init__(self) -> None:
        self.calls = []

    def dvz_scene(self):
        self.calls.append(("scene",))
        return "scene"

    def dvz_figure(self, scene, width, height, flags):
        self.calls.append(("figure", scene, width, height, flags))
        return "figure"

    def dvz_figure_set_color_pipeline(self, figure, pipeline):
        self.calls.append(("figure_set_color_pipeline", figure, pipeline))
        return None

    def dvz_panel_full(self, figure):
        self.calls.append(("panel_full", figure))
        return "panel"

    class DvzPanelDesc:
        x = 0.0
        y = 0.0
        width = 0.0
        height = 0.0

    class FakePanelView2D:
        aspect = 0
        padding = 1.0

    def dvz_panel_view2d(self):
        self.calls.append(("panel_view2d",))
        return self.FakePanelView2D()

    def dvz_panel_set_view2d(self, panel, view):
        self.calls.append(("set_view2d", panel, view))
        return 0

    def dvz_panel_set_domain(self, panel, dim, minimum, maximum):
        self.calls.append(("set_domain", panel, dim, minimum, maximum))
        return 0

    def dvz_point(self, scene, flags):
        self.calls.append(("point", scene, flags))
        return "point-visual"

    def dvz_image(self, scene, flags):
        self.calls.append(("image", scene, flags))
        return "image-visual"

    def dvz_visual_set_data(self, visual, name, data):
        self.calls.append(("set_data", visual, name, np.array(data, copy=True)))
        return 0

    def dvz_visual_set_texture(self, visual, pixels, width, height):
        self.calls.append(("set_texture", visual, np.array(pixels, copy=True), width, height))
        return 0

    def dvz_panel_add_visual(self, panel, visual, attach_desc):
        self.calls.append(("add_visual", panel, visual, attach_desc))
        return 0

    class FakePointStyle:
        stroke_width = 1.0
        aspect = 2

    def dvz_point_style_desc(self):
        self.calls.append(("point_style_desc",))
        return self.FakePointStyle()

    def dvz_point_set_style(self, visual, style):
        self.calls.append(("point_set_style", visual, style))
        return 0

    class DvzColor(ctypes.Structure):
        _fields_ = (
            ("r", ctypes.c_uint8),
            ("g", ctypes.c_uint8),
            ("b", ctypes.c_uint8),
            ("a", ctypes.c_uint8),
        )

    def dvz_panel_set_background_color(self, panel, color):
        self.calls.append(("set_background_color", panel, (color.r, color.g, color.b, color.a)))
        return None

    class DvzVisualAttachDesc(ctypes.Structure):
        _fields_ = (
            ("struct_size", ctypes.c_uint),
            ("flags", ctypes.c_uint),
            ("z_layer", ctypes.c_int),
            ("controller_mode", ctypes.c_int),
            ("coord_space", ctypes.c_int),
            ("clip_rect", ctypes.c_int),
            ("viewport_rect", ctypes.c_int),
        )

    def dvz_scene_destroy(self, scene):
        self.calls.append(("destroy", scene))


def _count_calls(calls, names: set[str]) -> int:
    return sum(1 for call in calls if call[0] in names)


def _initial_view() -> View2D:
    return View2D(id="view:main", panel_id="panel:main", x_range=(-1.0, 1.0), y_range=(-1.0, 1.0))


def _point_visual(count: int) -> PointVisual:
    rng = np.random.default_rng(20260135)
    positions = rng.normal(loc=0.0, scale=0.35, size=(count, 2)).astype(np.float32)
    colors = np.empty((count, 4), dtype=np.uint8)
    colors[:, 0] = 80
    colors[:, 1] = np.clip((positions[:, 0] + 1.0) * 120.0, 30.0, 240.0).astype(np.uint8)
    colors[:, 2] = np.clip((positions[:, 1] + 1.0) * 120.0, 30.0, 240.0).astype(np.uint8)
    colors[:, 3] = 255
    sizes = np.full(count, 3.0, dtype=np.float32)
    return PointVisual(
        id="visual:navigation-smoke-points",
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.DATA,
    )


if __name__ == "__main__":
    raise SystemExit(main())
