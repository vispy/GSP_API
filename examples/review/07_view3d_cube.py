"""API review example: static View3D cube mesh with perspective projection."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    MeshColorMode,
    MeshVisual,
    PanelTextGuide,
    PanelTextRole,
    PerspectiveProjection3D,
    View3D,
)


def build_scene() -> ReviewScene:
    positions = np.array(
        [
            [-1.0, -1.0, -1.0],
            [1.0, -1.0, -1.0],
            [1.0, 1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, -1.0, 1.0],
            [1.0, -1.0, 1.0],
            [1.0, 1.0, 1.0],
            [-1.0, 1.0, 1.0],
        ],
        dtype=np.float32,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
            [4, 6, 5],
            [4, 7, 6],
            [0, 4, 5],
            [0, 5, 1],
            [1, 5, 6],
            [1, 6, 2],
            [2, 6, 7],
            [2, 7, 3],
            [3, 7, 4],
            [3, 4, 0],
        ],
        dtype=np.uint32,
    )
    colors = np.array(
        [
            [69, 123, 157, 255],
            [69, 123, 157, 255],
            [42, 157, 143, 255],
            [42, 157, 143, 255],
            [230, 57, 70, 255],
            [230, 57, 70, 255],
            [244, 162, 97, 255],
            [244, 162, 97, 255],
            [38, 70, 83, 255],
            [38, 70, 83, 255],
            [131, 197, 190, 255],
            [131, 197, 190, 255],
        ],
        dtype=np.uint8,
    )
    view3d = View3D(
        id="view:cube",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(3.0, 3.0, 3.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=42.0,
            near_far=(0.1, 12.0),
        ),
    )
    cube = MeshVisual(
        id="visual:view3d-cube",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.DATA,
        color=colors,
        color_mode=MeshColorMode.FACE,
    )
    return ReviewScene(
        title="Static View3D cube",
        view3d=view3d,
        visuals=(cube,),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="Static View3D cube",
            ),
        ),
        notes=(
            "Reviews (N,3) MeshVisual DATA positions projected through Camera3D and PerspectiveProjection3D.",
            "Datoviz v0.4 renders this with the native panel camera when camera bounds bindings are available.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
