"""API review example: OBJ-style View3D mesh with flat Lambert shading.

This example loads the bundled Suzanne OBJ asset with a tiny local parser, normalizes it into the
accepted public View3D coordinate space, and renders generated face normals through S039 flat
Lambert shading. It deliberately ignores OBJ materials, UVs, and texture data.
"""

from __future__ import annotations

from pathlib import Path

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


def _load_obj_triangles(path: Path) -> tuple[np.ndarray, np.ndarray]:
    positions: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("v "):
            _, x, y, z, *_ = line.split()
            positions.append((float(x), float(y), float(z)))
        elif line.startswith("f "):
            refs = line.split()[1:]
            if len(refs) != 3:
                continue
            indices = tuple(int(ref.split("/", maxsplit=1)[0]) - 1 for ref in refs)
            faces.append(indices)
    if not positions or not faces:
        raise ValueError(f"OBJ file did not contain triangular mesh data: {path}")
    position_array = np.array(positions, dtype=np.float32)
    face_array = np.array(faces, dtype=np.uint32)
    center = (position_array.min(axis=0) + position_array.max(axis=0)) * 0.5
    scale = float(np.max(position_array.max(axis=0) - position_array.min(axis=0)))
    if scale <= 0.0:
        raise ValueError("OBJ mesh has degenerate bounds")
    position_array = (position_array - center) * (2.2 / scale)
    return position_array.astype(np.float32), face_array


def _face_colors(positions: np.ndarray, faces: np.ndarray) -> np.ndarray:
    centroids = positions[faces].mean(axis=1)
    z = centroids[:, 2]
    x = centroids[:, 0]
    z_norm = (z - z.min()) / max(float(z.max() - z.min()), 1.0e-6)
    x_norm = (x - x.min()) / max(float(x.max() - x.min()), 1.0e-6)
    red = np.clip(74 + 120 * z_norm, 0, 255)
    green = np.clip(112 + 85 * (1.0 - x_norm), 0, 255)
    blue = np.clip(145 + 70 * x_norm, 0, 255)
    alpha = np.full_like(red, 255)
    return np.stack([red, green, blue, alpha], axis=1).astype(np.uint8)


def build_scene() -> ReviewScene:
    positions, faces = _load_obj_triangles(
        Path(__file__).resolve().parents[1] / "models" / "suzanne_meshio.obj"
    )
    view3d = View3D(
        id="view:suzanne",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(2.9, -3.8, 2.4),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 0.0, 1.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=38.0,
            near_far=(0.1, 10.0),
        ),
        ambient_light_intensity=0.24,
        directional_light=DirectionalLight3D(
            direction_to_light=(-0.45, -0.2, 0.9),
            intensity=0.76,
        ),
    )
    mesh = MeshVisual(
        id="visual:suzanne-lambert",
        positions=positions,
        faces=faces,
        coordinate_space=CoordinateSpace.DATA,
        color=_face_colors(positions, faces),
        color_mode=MeshColorMode.FACE,
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )
    return ReviewScene(
        title="OBJ mesh flat Lambert",
        view3d=view3d,
        visuals=(mesh,),
        panel_text_guides=(
            PanelTextGuide(
                id="guide:title",
                panel_id="panel:main",
                role=PanelTextRole.TITLE,
                text="OBJ mesh flat Lambert",
            ),
        ),
        notes=(
            "Loads a bundled OBJ triangle mesh and renders only accepted public MeshVisual fields.",
            "OBJ materials, UVs, textures, and smooth normals are intentionally out of scope.",
        ),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
