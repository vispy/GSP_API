"""API review example: S039 flat Lambert face-normal mesh shading."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    DirectionalLight3D,
    MeshNormalGeneration,
    MeshNormalMode,
    MeshShading,
    MeshVisual,
    OrthographicProjection3D,
    PanelTextGuide,
    PanelTextRole,
    View3D,
)


def build_scene() -> ReviewScene:
    positions = np.array(
        [
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [0.0, 1.0, 0.0],
            [-0.7, -0.8, 0.8],
            [0.9, -0.7, 0.4],
            [0.0, 0.8, -0.2],
        ],
        dtype=np.float32,
    )
    faces = np.array([[0, 1, 2], [3, 5, 4]], dtype=np.uint32)
    colors = np.array(
        [[230, 57, 70, 255], [42, 157, 143, 255]],
        dtype=np.uint8,
    )
    view3d = View3D(
        id="view:lambert",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 4.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-1.6, 1.6),
            ylim=(-1.4, 1.4),
            near_far=(0.0, 8.0),
        ),
        ambient_light_intensity=0.25,
        directional_light=DirectionalLight3D(
            direction_to_light=(0.0, 0.0, 1.0),
            intensity=0.7,
        ),
    )
    mesh = MeshVisual(
        id="visual:flat-lambert",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.DATA,
        color=colors,
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )
    return ReviewScene(
        title="S039 flat Lambert",
        view3d=view3d,
        visuals=(mesh,),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="S039 flat Lambert",
            ),
        ),
        notes=(
            "Reviews flat Lambert face-normal material math resolved from canonical protocol fields.",
            "Matplotlib resolves face colors on CPU; Datoviz v0.4 reports unsupported until strict S039 support exists.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
