"""API review example: point annotations with TextVisual."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import CoordinateSpace, PointVisual, TextAnchorX, TextAnchorY, TextVisual


def build_scene() -> ReviewScene:
    positions = np.array([[-0.55, -0.25], [0.0, 0.35], [0.52, -0.05]], dtype=np.float32)
    label_positions = positions + np.array([[0.0, 0.20]], dtype=np.float32)
    return ReviewScene(
        title="Text label API review",
        visuals=(
            PointVisual(id="visual:labeled-points", positions=positions, colors=np.array([[230, 57, 70, 255], [42, 157, 143, 255], [69, 123, 157, 255]], dtype=np.uint8), sizes=34.0, coordinate_space=CoordinateSpace.NDC),
            TextVisual(id="visual:labels", texts=("alpha", "beta", "gamma"), positions=label_positions, coordinate_space=CoordinateSpace.NDC, rgba=np.repeat(np.array([[20, 20, 20, 255]], dtype=np.uint8), 3, axis=0), font_size_px=18.0, anchor_x=TextAnchorX.CENTER, anchor_y=TextAnchorY.BOTTOM, z_order=2),
        ),
        notes=("Reviews TextVisual text arrays, NDC placement, anchor semantics, font size in pixels, and z-order over points.",),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
