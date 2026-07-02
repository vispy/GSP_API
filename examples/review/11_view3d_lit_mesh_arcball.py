"""API review example: lit View3D mesh with arcball-style orbit review."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    DirectionalLight3D,
    MeshColorMode,
    MeshNormalGeneration,
    MeshNormalMode,
    MeshShading,
    MeshVisual,
    PanelTextGuide,
    PanelTextRole,
    PerspectiveProjection3D,
    View3D,
)


def build_scene() -> ReviewScene:
    rows = 7
    cols = 9
    xs = np.linspace(-2.2, 2.2, cols, dtype=np.float32)
    ys = np.linspace(-1.6, 1.6, rows, dtype=np.float32)
    positions: list[tuple[float, float, float]] = []
    for y in ys:
        for x in xs:
            z = (
                0.38 * np.cos(float(x) * 1.4)
                + 0.22 * np.sin(float(y) * 2.1)
                + 0.12 * np.sin(float(x + y) * 2.5)
            )
            positions.append((float(x), float(y), float(z)))
    position_array = np.array(positions, dtype=np.float32)

    faces: list[tuple[int, int, int]] = []
    colors: list[tuple[int, int, int, int]] = []
    for row in range(rows - 1):
        for col in range(cols - 1):
            i0 = row * cols + col
            i1 = i0 + 1
            i2 = i0 + cols
            i3 = i2 + 1
            faces.extend(((i0, i1, i3), (i0, i3, i2)))
            height = float(np.mean(position_array[[i0, i1, i2, i3], 2]))
            warm = int(np.clip(150 + height * 95, 80, 235))
            cool = int(np.clip(145 - height * 70, 60, 210))
            colors.extend(
                (
                    (warm, 92, cool, 255),
                    (warm, 92, cool, 255),
                )
            )

    view3d = View3D(
        id="view:lit-mesh",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(3.2, -3.4, 2.7),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 0.0, 1.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=44.0,
            near_far=(0.1, 12.0),
        ),
        ambient_light_intensity=0.28,
        directional_light=DirectionalLight3D(
            direction_to_light=(-0.35, -0.2, 1.0),
            intensity=0.72,
        ),
    )
    mesh = MeshVisual(
        id="visual:lit-review-mesh",
        positions=position_array,
        faces=np.array(faces, dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array(colors, dtype=np.uint8),
        color_mode=MeshColorMode.FACE,
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )
    return ReviewScene(
        title="Lit View3D mesh",
        view3d=view3d,
        visuals=(mesh,),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="Lit View3D mesh",
            ),
        ),
        notes=(
            "Reviews accepted S039/S040 flat Lambert face-normal shading on a faceted DATA-space mesh.",
            "Matplotlib live review uses GSP orbit/pan/zoom as an arcball-style manual inspection path.",
            "Datoviz resolves Lambert colors on the CPU and renders the static public View3D camera.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
