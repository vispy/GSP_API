"""API review example: panel NDC3 mesh depth ordering."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    CoordinateSpace,
    MeshColorMode,
    MeshVisual,
    PanelTextGuide,
    PanelTextRole,
)


def build_scene() -> ReviewScene:
    positions = np.array(
        [
            [-0.72, -0.62, 0.0],
            [0.72, -0.62, 0.0],
            [0.0, 0.72, 0.0],
            [-0.58, 0.58, 0.75],
            [0.58, 0.58, 0.75],
            [0.0, -0.74, 0.75],
        ],
        dtype=np.float32,
    )
    faces = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32)
    colors = np.array(
        [[230, 57, 70, 255], [69, 123, 157, 255]],
        dtype=np.uint8,
    )
    mesh = MeshVisual(
        id="visual:view3d-ndc-depth",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.NDC,
        color=colors,
        color_mode=MeshColorMode.FACE,
    )
    return ReviewScene(
        title="NDC3 opaque depth ordering",
        visuals=(mesh,),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="NDC3 opaque depth ordering",
            ),
        ),
        notes=(
            "Reviews (N,3) MeshVisual NDC positions interpreted as panel NDC3.",
            "The red nearer triangle should draw over the farther blue triangle in the overlap.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
