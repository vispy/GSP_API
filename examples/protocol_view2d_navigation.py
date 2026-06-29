"""Example: retained View2D navigation and pan/zoom.

This example shows the S035 navigation model:

- Matplotlib: native drag and wheel events are adapted into semantic GSP actions.
- Datoviz v0.4: scripted actions update retained panel/View2D state without rebuilding visuals.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import os

import numpy as np

from gsp.protocol import (
    CanvasSize,
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

LIVE_CANVAS_SIZE = CanvasSize.reference_px(900, 650, reference_dpi=96.0)
MATPLOTLIB_LIVE_DPI = 120.0


def main() -> int:
    """Run the navigation review example."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("matplotlib", "datoviz", "datoviz-v04"), default="matplotlib")
    parser.add_argument("--scripted-smoke", action="store_true", help="Run deterministic pan/zoom actions and exit.")
    parser.add_argument("--frames", type=int, default=0, help="Datoviz frames to run; 0 means until window close.")
    args = parser.parse_args()

    if args.backend == "matplotlib":
        return _run_matplotlib(scripted_smoke=args.scripted_smoke or os.environ.get("GSP_TEST") == "True")
    return _run_datoviz(scripted_smoke=args.scripted_smoke or os.environ.get("GSP_TEST") == "True", frames=args.frames)


def _run_matplotlib(*, scripted_smoke: bool) -> int:
    import matplotlib

    if scripted_smoke:
        matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    visual = _point_visual()
    view = _initial_view()
    resolved = LIVE_CANVAS_SIZE.resolve(output_dpi=MATPLOTLIB_LIVE_DPI)
    fig, ax = plt.subplots(
        figsize=(
            resolved.framebuffer_width / MATPLOTLIB_LIVE_DPI,
            resolved.framebuffer_height / MATPLOTLIB_LIVE_DPI,
        ),
        dpi=MATPLOTLIB_LIVE_DPI,
    )
    setattr(fig, "_gsp_resolved_canvas", resolved)
    _configure_axes(ax, view)
    _render_matplotlib_live_points(ax, visual)
    session = _MatplotlibNavigationSession(fig, ax, view)

    if scripted_smoke:
        session.run_scripted_smoke()
        plt.close(fig)
        print(f"matplotlib scripted smoke: view={session.view.x_range},{session.view.y_range}")
        return 0

    fig.canvas.mpl_connect("button_press_event", session.on_button_press)
    fig.canvas.mpl_connect("button_release_event", session.on_button_release)
    fig.canvas.mpl_connect("motion_notify_event", session.on_motion)
    fig.canvas.mpl_connect("scroll_event", session.on_scroll)
    plt.show()
    return 0


def _run_datoviz(*, scripted_smoke: bool, frames: int) -> int:
    visual = _point_visual()
    view = _initial_view()
    with DatovizV04ProtocolRenderer(canvas_size=LIVE_CANVAS_SIZE, view=view) as renderer:
        renderer.add_point_visual(visual)
        if scripted_smoke:
            smoke = _ScriptedNavigationSmoke(view)
            for next_view in smoke.run():
                renderer.apply_retained_view2d_navigation(next_view)
            print(f"datoviz retained scripted smoke: view={renderer.view.x_range},{renderer.view.y_range}")
            return 0
        renderer.enable_native_panzoom()
        print("Datoviz v0.4 native panzoom enabled: drag to pan, wheel to zoom.")
        renderer.show(frame_count=frames)
    return 0


class _MatplotlibNavigationSession:
    def __init__(self, fig, ax, view: View2D) -> None:
        self.fig = fig
        self.ax = ax
        self.view = view
        self.revision_index = 1
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
            panel_rect=self._panel_rect(),
            layout_snapshot_id="layout:matplotlib-live",
        )

    def on_button_press(self, event) -> None:
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

    def on_button_release(self, event) -> None:
        if event.x is None or event.y is None:
            return
        self.adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.BUTTON_RELEASE,
                x_px=float(event.x),
                y_px=float(event.y),
            )
        )

    def on_motion(self, event) -> None:
        if event.inaxes is not self.ax or event.x is None or event.y is None:
            return
        self._apply_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.MOUSE_MOVE,
                x_px=float(event.x),
                y_px=float(event.y),
            )
        )

    def on_scroll(self, event) -> None:
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

    def run_scripted_smoke(self) -> None:
        rect = self._panel_rect()
        self.adapter.set_panel_rect(rect)
        events = (
            NavigationPointerEvent(NavigationPointerEventKind.BUTTON_PRESS, rect.x + 250.0, rect.y + 200.0, left_button=True),
            NavigationPointerEvent(NavigationPointerEventKind.MOUSE_MOVE, rect.x + 320.0, rect.y + 200.0),
            NavigationPointerEvent(NavigationPointerEventKind.BUTTON_RELEASE, rect.x + 320.0, rect.y + 200.0),
            NavigationPointerEvent(NavigationPointerEventKind.WHEEL, rect.x + 360.0, rect.y + 240.0, scroll_steps=2.0),
        )
        for event in events:
            self._apply_event(event)

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
            expected_layout_snapshot_id="layout:matplotlib-live",
        )
        if not result.accepted or result.view is None or result.new_view2d_revision is None:
            print(f"navigation rejected: {result.diagnostics}")
            return
        self.view = result.view
        self.controller = replace(self.controller, current_view2d_revision=result.new_view2d_revision)
        self.adapter.accept_navigation_result(result)
        _configure_axes(self.ax, self.view)
        self.fig.canvas.draw_idle()

    def _next_revision(self) -> str:
        self.revision_index += 1
        return f"view-rev:{self.revision_index}"

    def _panel_rect(self) -> LogicalPixelRect:
        self.fig.canvas.draw()
        bbox = self.ax.bbox
        return LogicalPixelRect(x=float(bbox.x0), y=float(bbox.y0), width=float(bbox.width), height=float(bbox.height))


class _ScriptedNavigationSmoke:
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
            layout_snapshot_id="layout:scripted",
        )

    def run(self):
        events = (
            NavigationPointerEvent(NavigationPointerEventKind.BUTTON_PRESS, 350.0, 300.0, left_button=True),
            NavigationPointerEvent(NavigationPointerEventKind.MOUSE_MOVE, 430.0, 300.0),
            NavigationPointerEvent(NavigationPointerEventKind.BUTTON_RELEASE, 430.0, 300.0),
            NavigationPointerEvent(NavigationPointerEventKind.WHEEL, 460.0, 315.0, scroll_steps=1.0),
        )
        for event in events:
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
                expected_layout_snapshot_id="layout:scripted",
            )
            if not result.accepted or result.view is None or result.new_view2d_revision is None:
                raise RuntimeError(f"scripted navigation rejected: {result.diagnostics}")
            self.view = result.view
            self.controller = replace(self.controller, current_view2d_revision=result.new_view2d_revision)
            self.adapter.accept_navigation_result(result)
            yield self.view

    def _next_revision(self) -> str:
        self.revision_index += 1
        return f"view-rev:{self.revision_index}"


def _configure_axes(ax, view: View2D) -> None:
    ax.set_title("GSP S035 View2D navigation")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(view.x_range)
    ax.set_ylim(view.y_range)
    ax.grid(True, alpha=0.25)


def _render_matplotlib_live_points(ax, visual: PointVisual) -> None:
    colors = visual.colors.astype(np.float32) / 255.0
    ax.scatter(
        visual.positions[:, 0],
        visual.positions[:, 1],
        s=np.square(visual.sizes.astype(np.float32)),
        c=colors,
    )


def _initial_view() -> View2D:
    return View2D(id="view:main", panel_id="panel:main", x_range=(-1.0, 1.0), y_range=(-1.0, 1.0))


def _point_visual() -> PointVisual:
    rng = np.random.default_rng(12345)
    positions = rng.normal(loc=0.0, scale=0.32, size=(6000, 2)).astype(np.float32)
    colors = np.empty((positions.shape[0], 4), dtype=np.uint8)
    colors[:, 0] = np.clip((positions[:, 0] + 1.0) * 110.0, 40.0, 235.0).astype(np.uint8)
    colors[:, 1] = np.clip((positions[:, 1] + 1.0) * 120.0, 50.0, 245.0).astype(np.uint8)
    colors[:, 2] = 170
    colors[:, 3] = 160
    sizes = np.full(positions.shape[0], 4.0, dtype=np.float32)
    return PointVisual(
        id="visual:navigation-points",
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.DATA,
    )


if __name__ == "__main__":
    raise SystemExit(main())
