"""API review example: S039 flat Lambert face-normal mesh shading."""

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
    OrthographicProjection3D,
    PanelTextGuide,
    PanelTextRole,
    View3D,
)


def _build_faceted_lambert_mesh() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build a compact low-poly surface with varied face normals."""
    segment_count = 10
    angles = np.linspace(0.0, 2.0 * np.pi, segment_count, endpoint=False)
    outer_radius = np.array([1.42, 0.98], dtype=np.float32)
    inner_radius = np.array([0.72, 0.48], dtype=np.float32)

    positions: list[tuple[float, float, float]] = [(0.0, 0.0, 0.72)]
    for angle in angles:
        ridge = 0.34 + 0.06 * np.sin(2.0 * angle) + 0.04 * np.cos(3.0 * angle)
        positions.append(
            (
                float(inner_radius[0] * np.cos(angle)),
                float(inner_radius[1] * np.sin(angle)),
                float(ridge),
            )
        )
    for index, angle in enumerate(angles):
        rim = -0.08 + 0.04 * np.sin(float(index) * 1.7)
        positions.append(
            (
                float(outer_radius[0] * np.cos(angle)),
                float(outer_radius[1] * np.sin(angle)),
                float(rim),
            )
        )

    center = 0
    inner_start = 1
    outer_start = inner_start + segment_count
    faces: list[tuple[int, int, int]] = []
    colors: list[tuple[int, int, int, int]] = []
    top_palette = (
        (244, 162, 97, 255),
        (231, 111, 81, 255),
        (233, 196, 106, 255),
        (42, 157, 143, 255),
        (38, 70, 83, 255),
    )
    rim_palette = (
        (69, 123, 157, 255),
        (29, 53, 87, 255),
        (87, 117, 144, 255),
        (129, 178, 154, 255),
        (224, 122, 95, 255),
    )
    for index in range(segment_count):
        next_index = (index + 1) % segment_count
        inner = inner_start + index
        inner_next = inner_start + next_index
        outer = outer_start + index
        outer_next = outer_start + next_index
        faces.append((center, inner, inner_next))
        colors.append(top_palette[index % len(top_palette)])
        faces.append((inner, outer, outer_next))
        colors.append(rim_palette[index % len(rim_palette)])
        faces.append((inner, outer_next, inner_next))
        colors.append(rim_palette[(index + 2) % len(rim_palette)])

    return (
        np.array(positions, dtype=np.float32),
        np.array(faces, dtype=np.uint32),
        np.array(colors, dtype=np.uint8),
    )


def build_scene() -> ReviewScene:
    positions, faces, colors = _build_faceted_lambert_mesh()
    view3d = View3D(
        id="view:lambert",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(2.4, -3.2, 2.6),
            target=(0.0, 0.0, 0.22),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-1.9, 1.9),
            ylim=(-1.45, 1.55),
            near_far=(0.0, 8.0),
        ),
        ambient_light_intensity=0.22,
        directional_light=DirectionalLight3D(
            direction_to_light=(-0.35, -0.2, 1.0),
            intensity=0.78,
        ),
    )
    mesh = MeshVisual(
        id="visual:flat-lambert",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.DATA,
        color=colors,
        color_mode=MeshColorMode.FACE,
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
            "Reviews flat Lambert face-normal material math on a faceted DATA-space mesh.",
            "Matplotlib resolves face colors on CPU; Datoviz v0.4 uses the S040 CPU-resolved strict path.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
