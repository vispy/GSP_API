"""Open the same protocol scene with Matplotlib or Datoviz v0.4."""

from __future__ import annotations

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

from gsp.protocol import CanvasSize, CoordinateSpace, PointVisual
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer
from gsp_matplotlib.protocol_renderer import render_point_visual

LIVE_CANVAS_SIZE = CanvasSize.reference_px(900, 650, reference_dpi=96.0)
MATPLOTLIB_LIVE_DPI = 120.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        choices=("matplotlib", "datoviz", "datoviz-v04"),
        default="matplotlib",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=0,
        help="Datoviz frames to run; 0 means until window close",
    )
    args = parser.parse_args()

    visuals = _scene_visuals()
    if args.backend == "matplotlib":
        resolved = LIVE_CANVAS_SIZE.resolve(output_dpi=MATPLOTLIB_LIVE_DPI)
        fig, ax = plt.subplots(
            figsize=(
                resolved.framebuffer_width / MATPLOTLIB_LIVE_DPI,
                resolved.framebuffer_height / MATPLOTLIB_LIVE_DPI,
            ),
            dpi=MATPLOTLIB_LIVE_DPI,
        )
        setattr(fig, "_gsp_resolved_canvas", resolved)
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("GSP protocol scene - Matplotlib")
        for visual in visuals:
            render_point_visual(ax, visual)
        if os.environ.get("GSP_TEST") == "True":
            plt.close(fig)
        else:
            plt.show()
        return 0

    with DatovizV04ProtocolRenderer(canvas_size=LIVE_CANVAS_SIZE) as renderer:
        for visual in visuals:
            renderer.add_point_visual(visual)
        renderer.show(frame_count=args.frames)
    return 0


def _scene_visuals() -> tuple[PointVisual]:
    positions = np.array(
        [
            [-0.55, -0.25],
            [-0.22, 0.22],
            [0.15, -0.05],
            [0.52, 0.32],
        ],
        dtype=np.float32,
    )
    colors = np.array(
        [
            [230, 57, 70, 230],
            [42, 157, 143, 230],
            [244, 162, 97, 230],
            [69, 123, 157, 230],
        ],
        dtype=np.uint8,
    )
    sizes = np.array([16.0, 28.0, 42.0, 58.0], dtype=np.float32)
    point_visual = PointVisual(
        id="visual:live-points-ndc",
        positions=positions,
        colors=colors,
        sizes=sizes,
        coordinate_space=CoordinateSpace.NDC,
    )
    return (point_visual,)


if __name__ == "__main__":
    raise SystemExit(main())
