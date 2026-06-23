"""Open the same protocol scene with Matplotlib or Datoviz v0.4."""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

from gsp.protocol import CoordinateSpace, ImageOrigin, ImageVisual, PointVisual
from gsp.protocol.visuals import ImageInterpolation
from gsp_datoviz.protocol_renderer import DatovizV04ProtocolRenderer
from gsp_matplotlib.protocol_renderer import render_image_visual, render_point_visual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("matplotlib", "datoviz", "datoviz-v04"), default="matplotlib")
    parser.add_argument("--frames", type=int, default=0, help="Datoviz frames to run; 0 means until window close")
    args = parser.parse_args()

    visuals = _scene_visuals()
    if args.backend == "matplotlib":
        fig, ax = plt.subplots(figsize=(6, 4), dpi=120)
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title("GSP protocol scene - Matplotlib")
        for visual in visuals:
            if isinstance(visual, PointVisual):
                render_point_visual(ax, visual)
            else:
                render_image_visual(ax, visual)
        plt.show()
        return 0

    with DatovizV04ProtocolRenderer(width=900, height=650) as renderer:
        for visual in visuals:
            if isinstance(visual, PointVisual):
                renderer.add_point_visual(visual)
            else:
                renderer.add_image_visual(visual)
        renderer.show(frame_count=args.frames)
    return 0


def _scene_visuals() -> tuple[ImageVisual, PointVisual]:
    image = _checker_image(12)
    image_visual = ImageVisual(
        id="visual:live-checker-image-ndc",
        image=image,
        extent=(-0.85, 0.85, -0.65, 0.65),
        coordinate_space=CoordinateSpace.NDC,
        interpolation=ImageInterpolation.NEAREST,
        origin=ImageOrigin.UPPER,
    )
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
    return image_visual, point_visual


def _checker_image(size: int) -> np.ndarray:
    grid = np.indices((size, size)).sum(axis=0) % 2
    image = np.zeros((size, size, 4), dtype=np.uint8)
    image[grid == 0] = np.array([245, 245, 245, 255], dtype=np.uint8)
    image[grid == 1] = np.array([35, 40, 45, 255], dtype=np.uint8)
    return image


if __name__ == "__main__":
    raise SystemExit(main())
