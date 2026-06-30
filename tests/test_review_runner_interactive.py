"""Regression tests for interactive review-example runner behavior."""

from __future__ import annotations

from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

import numpy as np

from gsp.protocol import CoordinateSpace, PointVisual, View2D
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

