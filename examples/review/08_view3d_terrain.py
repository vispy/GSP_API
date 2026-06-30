"""API review example: static View3D terrain-like mesh."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    Camera3D,
    CoordinateSpace,
    MeshColorMode,
    MeshVisual,
    OrthographicProjection3D,
    PanelTextGuide,
    PanelTextRole,
    View3D,
)


def build_scene() -> ReviewScene:
    xs = np.linspace(-2.0, 2.0, 9, dtype=np.float32)
    ys = np.linspace(-2.0, 2.0, 9, dtype=np.float32)
    positions = []
    for y in ys:
        for x in xs:
            z = 0.45 * np.sin(float(x) * 1.7) * np.cos(float(y) * 1.2)
            positions.append((float(x), float(y), z))
    position_array = np.array(positions, dtype=np.float32)

    faces = []
    colors = []
    columns = len(xs)
    for row in range(len(ys) - 1):
        for col in range(len(xs) - 1):
            i0 = row * columns + col
            i1 = i0 + 1
            i2 = i0 + columns
            i3 = i2 + 1
            faces.extend(((i0, i1, i3), (i0, i3, i2)))
            height = float(np.mean(position_array[[i0, i1, i2, i3], 2]))
            green = int(np.clip(145 + height * 120, 80, 220))
            blue = int(np.clip(110 - height * 80, 40, 180))
            colors.extend(((70, green, blue, 255), (70, green, blue, 255)))

    face_array = np.array(faces, dtype=np.uint32)
    color_array = np.array(colors, dtype=np.uint8)
    view3d = View3D(
        id="view:terrain",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(3.2, 3.5, 3.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 0.0, 1.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-3.0, 3.0),
            ylim=(-2.4, 2.6),
            near_far=(0.0, 8.0),
        ),
    )
    terrain = MeshVisual(
        id="visual:view3d-terrain",
        positions=position_array,
        faces=face_array,
        coordinate_space=CoordinateSpace.DATA,
        color=color_array,
        color_mode=MeshColorMode.FACE,
    )
    return ReviewScene(
        title="Static View3D terrain",
        view3d=view3d,
        visuals=(terrain,),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="Static View3D terrain",
            ),
        ),
        notes=(
            "Reviews a finite (N,3) DATA mesh grid through static orthographic View3D projection.",
            "Colors are per-face RGBA; there are no public materials, lights, or terrain-specific primitives.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
