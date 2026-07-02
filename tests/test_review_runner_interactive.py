"""Regression tests for interactive review-example runner behavior."""

from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    MeshVisual,
    OrthographicProjection3D,
    PanelTextGuide,
    PanelTextRole,
    PerspectiveProjection3D,
    PointVisual,
    View2D,
    View3D,
)
from gsp_datoviz.protocol_renderer import DatovizV04Unavailable

REVIEW_DIR = Path(__file__).resolve().parents[1] / "examples" / "review"
if str(REVIEW_DIR) not in sys.path:
    sys.path.insert(0, str(REVIEW_DIR))

import _review_runner as review_runner  # noqa: E402


def _point_scene() -> review_runner.ReviewScene:
    view = View2D(
        id="view:review-test",
        panel_id="panel:main",
        x_range=(0.0, 10.0),
        y_range=(0.0, 10.0),
    )
    return review_runner.ReviewScene(
        title="interactive test",
        view=view,
        visuals=(
            PointVisual(
                id="visual:point",
                positions=np.array([[5.0, 5.0]], dtype=np.float32),
                colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
                sizes=10.0,
                coordinate_space=CoordinateSpace.DATA,
            ),
        ),
    )


def _view3d_scene() -> review_runner.ReviewScene:
    view3d = View3D(
        id="view:review-3d",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-2.0, 2.0),
            ylim=(-2.0, 2.0),
            near_far=(1.0, 10.0),
        ),
    )
    return review_runner.ReviewScene(
        title="interactive 3d test",
        view3d=view3d,
        visuals=(
            MeshVisual(
                id="visual:triangle3d",
                positions=np.array(
                    [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]],
                    dtype=np.float32,
                ),
                faces=np.array([[0, 1, 2]], dtype=np.uint32),
                coordinate_space=CoordinateSpace.DATA,
                color=np.array([40, 120, 220, 255], dtype=np.uint8),
            ),
        ),
    )


def _perspective_view3d_scene() -> review_runner.ReviewScene:
    view3d = View3D(
        id="view:review-3d-perspective",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=60.0,
            near_far=(0.1, 20.0),
        ),
    )
    return review_runner.ReviewScene(
        title="interactive perspective 3d test",
        view3d=view3d,
        visuals=(
            MeshVisual(
                id="visual:triangle3d-perspective",
                positions=np.array(
                    [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]],
                    dtype=np.float32,
                ),
                faces=np.array([[0, 1, 2]], dtype=np.uint32),
                coordinate_space=CoordinateSpace.DATA,
                color=np.array([40, 120, 220, 255], dtype=np.uint8),
            ),
        ),
    )


def _oblique_view3d_scene() -> review_runner.ReviewScene:
    scene = _perspective_view3d_scene()
    assert scene.view3d is not None
    return review_runner.ReviewScene(
        title=scene.title,
        view3d=View3D(
            id=scene.view3d.id,
            panel_id=scene.view3d.panel_id,
            camera=Camera3D(
                eye=(1.8, -2.2, 1.5),
                target=(0.0, 0.0, 0.0),
                up=(0.0, 0.0, 1.0),
            ),
            projection=scene.view3d.projection,
        ),
        visuals=scene.visuals,
    )


def test_datoviz_title_background_kept_for_2d_review_scenes() -> None:
    guide = PanelTextGuide(
        id="guide:title",
        panel_id="panel:main",
        role=PanelTextRole.TITLE,
        text="2D title",
    )

    backgrounds = review_runner._panel_text_background_visuals((guide,))

    assert len(backgrounds) == 1
    assert backgrounds[0].id == "visual:datoviz-panel-title-background"


def test_datoviz_title_background_skipped_for_view3d_review_scenes() -> None:
    guide = PanelTextGuide(
        id="guide:title",
        panel_id="panel:main",
        role=PanelTextRole.TITLE,
        text="3D title",
    )

    backgrounds = review_runner._panel_text_background_visuals(
        (guide,),
        include_background=False,
    )

    assert backgrounds == ()


def test_matplotlib_interactive_navigation_rerenders_data_visual_positions() -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _point_scene()
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        initial_offset = np.array(ax.collections[0].get_offsets()[0], dtype=np.float64)

        session = review_runner._MatplotlibReviewNavigationSession(
            fig, ax, scene, color_scales={}
        )
        rect = session._panel_rect()
        session.on_button_press(
            SimpleNamespace(
                inaxes=ax,
                x=rect.x + rect.width * 0.5,
                y=rect.y + rect.height * 0.5,
                button=1,
            )
        )
        session.on_motion(
            SimpleNamespace(
                inaxes=ax,
                x=rect.x + rect.width * 0.6,
                y=rect.y + rect.height * 0.5,
            )
        )

        updated_offset = np.array(ax.collections[0].get_offsets()[0], dtype=np.float64)
        assert updated_offset[0] != initial_offset[0]
    finally:
        plt.close(fig)


def test_matplotlib_interactive_view3d_navigation_rerenders_mesh() -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _view3d_scene()
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        initial_vertices = ax.collections[0].get_paths()[0].vertices.copy()

        session = review_runner._MatplotlibReviewView3DNavigationSession(
            fig, ax, scene, color_scales={}
        )
        rect = session._panel_rect()
        session.on_button_press(
            SimpleNamespace(
                inaxes=ax,
                x=rect.x + rect.width * 0.5,
                y=rect.y + rect.height * 0.5,
                button=1,
            )
        )
        session.on_motion(
            SimpleNamespace(
                inaxes=ax,
                x=rect.x + rect.width * 0.6,
                y=rect.y + rect.height * 0.5,
            )
        )

        assert session.view3d.revision == 1
        updated_vertices = ax.collections[0].get_paths()[0].vertices.copy()
        assert not np.allclose(updated_vertices, initial_vertices)

        session.on_scroll(SimpleNamespace(inaxes=ax, step=1.0))
        assert session.view3d.revision == 2
        assert session.view3d.projection.xlim != scene.view3d.projection.xlim

        session.on_key_press(SimpleNamespace(key="r"))
        assert session.view3d.revision == 3
        assert session.view3d.camera == scene.view3d.camera
        assert session.view3d.projection == scene.view3d.projection
    finally:
        plt.close(fig)


def test_matplotlib_interactive_view3d_orbit_uses_arcball_camera_update() -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _view3d_scene()
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        session = review_runner._MatplotlibReviewView3DNavigationSession(
            fig, ax, scene, color_scales={}
        )
        rect = session._panel_rect()

        camera = session._arcball_camera_from_pixels(
            rect.x + rect.width * 0.5,
            rect.y + rect.height * 0.5,
            rect.x + rect.width * 0.6,
            rect.y + rect.height * 0.6,
        )

        assert camera.target == scene.view3d.camera.target
        assert camera.eye != scene.view3d.camera.eye
        assert camera.up != scene.view3d.camera.up
        assert np.linalg.norm(np.subtract(camera.eye, camera.target)) == pytest.approx(
            np.linalg.norm(np.subtract(scene.view3d.camera.eye, scene.view3d.camera.target))
        )
    finally:
        plt.close(fig)


def test_matplotlib_interactive_view3d_orbit_uses_press_anchor_for_drag(
    monkeypatch: Any,
) -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _view3d_scene()
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        session = review_runner._MatplotlibReviewView3DNavigationSession(
            fig, ax, scene, color_scales={}
        )
        rect = session._panel_rect()
        calls: list[tuple[float, float, float, float, View3D | None]] = []

        def fake_arcball_camera(
            last_x_px: float,
            last_y_px: float,
            x_px: float,
            y_px: float,
            *,
            base_view3d: View3D | None = None,
        ) -> Camera3D:
            calls.append((last_x_px, last_y_px, x_px, y_px, base_view3d))
            return scene.view3d.camera

        monkeypatch.setattr(session, "_arcball_camera_from_pixels", fake_arcball_camera)
        monkeypatch.setattr(session, "_apply_payload", lambda *_args, **_kwargs: None)

        press_x = rect.x + rect.width * 0.5
        press_y = rect.y + rect.height * 0.5
        session.on_button_press(
            SimpleNamespace(inaxes=ax, x=press_x, y=press_y, button=1)
        )
        session.on_motion(
            SimpleNamespace(
                inaxes=ax,
                x=rect.x + rect.width * 0.6,
                y=press_y,
            )
        )
        session.on_motion(
            SimpleNamespace(
                inaxes=ax,
                x=rect.x + rect.width * 0.7,
                y=press_y,
            )
        )

        assert len(calls) == 2
        assert calls[0][:2] == pytest.approx((press_x, press_y))
        assert calls[1][:2] == pytest.approx((press_x, press_y))
        assert calls[0][4] is scene.view3d
        assert calls[1][4] is scene.view3d
    finally:
        plt.close(fig)


def test_matplotlib_interactive_view3d_arcball_axis_uses_camera_basis() -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _oblique_view3d_scene()
    assert scene.view3d is not None
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        session = review_runner._MatplotlibReviewView3DNavigationSession(
            fig, ax, scene, color_scales={}
        )
        rect = session._panel_rect()

        camera = session._arcball_camera_from_pixels(
            rect.x + rect.width * 0.5,
            rect.y + rect.height * 0.5,
            rect.x + rect.width * 0.6,
            rect.y + rect.height * 0.5,
        )

        original = np.subtract(scene.view3d.camera.eye, scene.view3d.camera.target)
        rotated = np.subtract(camera.eye, camera.target)
        basis = scene.view3d.camera.basis()
        expected_axis = -np.asarray(basis.true_up, dtype=np.float64)
        expected = review_runner._rotate_vector(
            original,
            expected_axis,
            2.0 * np.arctan2(0.2, 1.0 + np.sqrt(1.0 - 0.2**2)),
        )
        np.testing.assert_allclose(rotated, expected, rtol=1.0e-6, atol=1.0e-6)
    finally:
        plt.close(fig)


def test_matplotlib_interactive_view3d_pans_perspective_at_target_distance() -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _perspective_view3d_scene()
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        session = review_runner._MatplotlibReviewView3DNavigationSession(
            fig, ax, scene, color_scales={}
        )
        rect = session._panel_rect()

        payload = session._pan_payload_from_pixels(80.0, -60.0)

        target_distance = 5.0
        y_span = 2.0 * target_distance * np.tan(np.deg2rad(60.0) * 0.5)
        x_span = y_span * (rect.width / rect.height)
        assert payload.delta_view_right == pytest.approx(-80.0 / rect.width * x_span)
        assert payload.delta_view_up == pytest.approx(60.0 / rect.height * y_span)
    finally:
        plt.close(fig)


def test_matplotlib_interactive_view3d_scroll_zooms_perspective_by_dolly() -> None:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    scene = _perspective_view3d_scene()
    fig, ax = plt.subplots()
    try:
        review_runner._render_matplotlib_scene(fig, ax, scene, color_scales={})
        session = review_runner._MatplotlibReviewView3DNavigationSession(
            fig, ax, scene, color_scales={}
        )

        session.on_scroll(SimpleNamespace(inaxes=ax, step=1.0))

        assert session.view3d.revision == scene.view3d.revision + 1
        assert session.view3d.camera.eye[2] == pytest.approx(5.0 / 1.1)
        assert session.view3d.camera.target == scene.view3d.camera.target
        assert session.view3d.projection == scene.view3d.projection
    finally:
        plt.close(fig)


def test_review_runner_defaults_live_mode_to_interactive_navigation(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["example.py", "--backend", "matplotlib", "--frames", "1"],
    )

    args = review_runner._parse_args()

    assert args.offscreen is False
    assert args.interactive_navigation is True


def test_review_runner_static_live_opt_out(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "example.py",
            "--backend",
            "matplotlib",
            "--frames",
            "1",
            "--no-interactive-navigation",
        ],
    )

    args = review_runner._parse_args()

    assert args.offscreen is False
    assert args.interactive_navigation is False


def test_review_runner_offscreen_default_is_not_interactive(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["example.py", "--backend", "matplotlib", "--offscreen"],
    )

    args = review_runner._parse_args()

    assert args.offscreen is True
    assert args.interactive_navigation is False


def test_datoviz_live_input_unavailable_still_opens_static_live_window(
    tmp_path: Path, monkeypatch: Any, capsys: Any
) -> None:
    instances: list[FakeDatovizRenderer] = []

    class FakeDatovizRenderer:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.show_calls = 0
            instances.append(self)

        def __enter__(self) -> "FakeDatovizRenderer":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def add_point_visual(self, visual: Any) -> None:
            return None

        def enable_gsp_view2d_navigation(self, view: Any) -> None:
            raise DatovizV04Unavailable("missing live input symbols")

        def show(self, *, frame_count: int) -> None:
            self.show_calls += 1
            assert frame_count == 1

    monkeypatch.setattr(
        review_runner, "DatovizV04ProtocolRenderer", FakeDatovizRenderer
    )

    result = review_runner._run_datoviz(
        _point_scene(),
        tmp_path,
        (320, 240),
        live=True,
        frames=1,
        allow_offscreen=False,
        interactive_navigation=True,
    )

    assert result["status"] == "rendered"
    assert instances[0].show_calls == 1
    assert "opening static live window" in capsys.readouterr().out


def test_datoviz_view3d_navigation_unavailable_still_opens_static_live_window(
    tmp_path: Path, monkeypatch: Any, capsys: Any
) -> None:
    instances: list[FakeDatovizRenderer] = []

    class FakeDatovizRenderer:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.show_calls = 0
            instances.append(self)

        def __enter__(self) -> "FakeDatovizRenderer":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def add_mesh_visual(self, visual: Any) -> None:
            return None

        def add_text_visual(self, visual: Any) -> None:
            return None

        def show(self, *, frame_count: int) -> None:
            self.show_calls += 1
            assert frame_count == 1

    monkeypatch.setattr(
        review_runner, "DatovizV04ProtocolRenderer", FakeDatovizRenderer
    )

    result = review_runner._run_datoviz(
        _view3d_scene(),
        tmp_path,
        (320, 240),
        live=True,
        frames=1,
        allow_offscreen=False,
        interactive_navigation=True,
    )

    assert result["status"] == "rendered"
    assert instances[0].show_calls == 1
    assert "missing enable_native_view3d_arcball" in capsys.readouterr().out


def test_datoviz_view3d_navigation_enables_native_arcball(
    tmp_path: Path, monkeypatch: Any, capsys: Any
) -> None:
    instances: list[FakeDatovizRenderer] = []

    class FakeDatovizRenderer:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self.show_calls = 0
            instances.append(self)

        def __enter__(self) -> "FakeDatovizRenderer":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def add_mesh_visual(self, visual: Any) -> None:
            return None

        def add_text_visual(self, visual: Any) -> None:
            return None

        def enable_native_view3d_arcball(self) -> None:
            self.enabled_arcball = True

        def show(self, *, frame_count: int) -> None:
            self.show_calls += 1
            assert frame_count == 1

    monkeypatch.setattr(
        review_runner, "DatovizV04ProtocolRenderer", FakeDatovizRenderer
    )

    result = review_runner._run_datoviz(
        _view3d_scene(),
        tmp_path,
        (320, 240),
        live=True,
        frames=1,
        allow_offscreen=False,
        interactive_navigation=True,
    )

    assert result["status"] == "rendered"
    assert instances[0].show_calls == 1
    assert instances[0].enabled_arcball is True
    assert "Datoviz native View3D arcball enabled" in capsys.readouterr().out
