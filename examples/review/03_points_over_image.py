"""API review example: point overlay on an RGBA image."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import CoordinateSpace, ImageInterpolation, ImageOrigin, ImageVisual, PointVisual


def build_scene() -> ReviewScene:
    image = np.zeros((80, 120, 4), dtype=np.uint8)
    image[..., 0] = np.linspace(40, 220, image.shape[1], dtype=np.uint8)
    image[..., 1] = np.linspace(200, 80, image.shape[0], dtype=np.uint8)[:, None]
    image[..., 2] = 140
    image[..., 3] = 255
    positions = np.array([[-0.55, -0.25], [-0.15, 0.18], [0.25, -0.05], [0.55, 0.32]], dtype=np.float32)
    return ReviewScene(
        title="Point overlay API review",
        visuals=(
            ImageVisual(id="visual:background", image=image, extent=(-0.8, 0.8, -0.55, 0.55), coordinate_space=CoordinateSpace.NDC, interpolation=ImageInterpolation.LINEAR, origin=ImageOrigin.UPPER),
            PointVisual(id="visual:overlay-points", positions=positions, colors=np.array([[255, 255, 255, 255], [20, 20, 20, 255], [240, 240, 80, 255], [40, 220, 240, 255]], dtype=np.uint8), sizes=np.array([24, 34, 44, 54], dtype=np.float32), coordinate_space=CoordinateSpace.NDC),
        ),
        notes=("Reviews composition order, RGBA image upload, alpha-ready colors, and overlay point sizing in NDC space.",),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
