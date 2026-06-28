"""API review example: scalar image with explicit extent and grayscale clim."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import CoordinateSpace, ImageColormap, ImageInterpolation, ImageOrigin, ImageVisual


def build_scene() -> ReviewScene:
    rows, cols = np.mgrid[0:96, 0:128]
    image = (np.sin(cols / 9.0) + np.cos(rows / 13.0)).astype(np.float32)
    return ReviewScene(
        title="Scalar image API review",
        visuals=(
            ImageVisual(
                id="visual:image",
                image=image,
                extent=(-0.85, 0.85, -0.65, 0.65),
                coordinate_space=CoordinateSpace.NDC,
                interpolation=ImageInterpolation.NEAREST,
                origin=ImageOrigin.LOWER,
                colormap=ImageColormap.GRAY,
                clim=(-2.0, 2.0),
            ),
        ),
        notes=("Reviews scalar image arrays, NDC extent, lower-origin row semantics, nearest sampling, grayscale colormap, and clim.",),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
