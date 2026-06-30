"""Tests for the accepted S025 MeshVisual protocol model."""

import numpy as np
import pytest

from gsp.protocol import (
    CoordinateSpace,
    DepthMode,
    DirectionalLight3D,
    FaceCulling,
    MeshColorMode,
    MeshNormalGeneration,
    MeshNormalMode,
    MeshShading,
    MeshVisual,
    OpacityPolicy,
    Camera3D,
    OrthographicProjection3D,
    View3D,
    validate_mesh_visual_flat_lambert,
)


POSITIONS_2D = np.array(
    [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]], dtype=np.float32
)
FACES = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)


def test_mesh_visual_accepts_strict_uniform_2d_mesh():
    visual = MeshVisual(
        id="visual:mesh",
        positions=POSITIONS_2D,
        faces=FACES,
        coordinate_space=CoordinateSpace.NDC,
        color=np.array([255, 0, 0, 255], dtype=np.uint8),
    )

    assert visual.resolved_color_mode() == MeshColorMode.UNIFORM
    assert visual.resolved_normal_mode() == MeshNormalMode.NONE
    assert visual.shading == MeshShading.UNLIT_RGBA
    assert visual.canonical_shading() == MeshShading.UNLIT_RGBA
    assert visual.face_culling == FaceCulling.NONE
    assert visual.depth_test == DepthMode.AUTO
    assert visual.depth_write == DepthMode.AUTO
    assert visual.opacity_policy == OpacityPolicy.ORDINARY_ALPHA


def test_mesh_visual_accepts_per_face_color():
    visual = MeshVisual(
        id="visual:mesh",
        positions=POSITIONS_2D,
        faces=FACES,
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
        color_mode=MeshColorMode.FACE,
    )

    assert visual.resolved_color_mode() == MeshColorMode.FACE


def test_mesh_visual_accepts_explicit_vertex_color():
    visual = MeshVisual(
        id="visual:mesh",
        positions=POSITIONS_2D,
        faces=FACES,
        coordinate_space=CoordinateSpace.NDC,
        color=np.ones((4, 4), dtype=np.float32),
        color_mode=MeshColorMode.VERTEX,
    )

    assert visual.resolved_color_mode() == MeshColorMode.VERTEX


def test_mesh_visual_rejects_ambiguous_color_mode():
    positions = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32)
    faces = np.array([[0, 1, 2], [0, 2, 1], [1, 2, 0]], dtype=np.uint32)

    with pytest.raises(ValueError, match="ambiguous"):
        MeshVisual(
            id="visual:mesh",
            positions=positions,
            faces=faces,
            coordinate_space=CoordinateSpace.NDC,
            color=np.ones((3, 4), dtype=np.float32),
        )


def test_mesh_visual_rejects_invalid_faces():
    with pytest.raises(ValueError, match="reference positions"):
        MeshVisual(
            id="visual:mesh",
            positions=POSITIONS_2D,
            faces=np.array([[0, 1, 4]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )


def test_mesh_visual_rejects_bad_color_shape():
    with pytest.raises(ValueError, match="shape"):
        MeshVisual(
            id="visual:mesh",
            positions=POSITIONS_2D,
            faces=FACES,
            coordinate_space=CoordinateSpace.NDC,
            color=np.ones((3, 4), dtype=np.float32),
            color_mode=MeshColorMode.FACE,
        )


def test_mesh_visual_rejects_degenerate_triangle():
    with pytest.raises(ValueError, match="degenerate"):
        MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0], [1, 0], [2, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )


def test_mesh_visual_accepts_face_normals_for_3d_mesh():
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
        normals=np.array([[0, 0, 1]], dtype=np.float32),
        normal_mode=MeshNormalMode.FACE,
    )

    assert visual.resolved_normal_mode() == MeshNormalMode.FACE


def test_mesh_visual_rejects_face_flat_generation_for_2d_positions():
    with pytest.raises(ValueError, match="requires 3D"):
        MeshVisual(
            id="visual:mesh",
            positions=POSITIONS_2D,
            faces=FACES,
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
            normal_generation=MeshNormalGeneration.FACE_FLAT,
        )


def test_mesh_visual_accepts_s039_flat_lambert_explicit_face_normals():
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
        shading=MeshShading.FLAT_LAMBERT,
        normals=np.array([[0, 0, 10]], dtype=np.float32),
        normal_mode=MeshNormalMode.FACE,
    )

    assert visual.canonical_shading() is MeshShading.FLAT_LAMBERT
    np.testing.assert_allclose(
        visual.normalized_face_normals(),
        np.array([[0.0, 0.0, 1.0]], dtype=np.float32),
    )
    validate_mesh_visual_flat_lambert(visual, view3d=_canonical_view3d())


def test_mesh_visual_accepts_s039_generated_face_normals():
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )

    assert visual.resolved_normal_mode() is MeshNormalMode.FACE
    np.testing.assert_allclose(
        visual.normalized_face_normals(),
        np.array([[0.0, 0.0, 1.0]], dtype=np.float32),
    )


def test_mesh_visual_s039_generated_normals_follow_winding():
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
        faces=np.array([[0, 2, 1]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )

    np.testing.assert_allclose(
        visual.normalized_face_normals(),
        np.array([[0.0, 0.0, -1.0]], dtype=np.float32),
    )


def test_mesh_visual_s039_flat_lambert_rejects_missing_view3d():
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
        shading=MeshShading.FLAT_LAMBERT,
        normals=np.array([[0, 0, 1]], dtype=np.float32),
        normal_mode=MeshNormalMode.FACE,
    )

    with pytest.raises(ValueError, match="flat_lambert_requires_view3d"):
        validate_mesh_visual_flat_lambert(visual, view3d=None)


def test_mesh_visual_s039_flat_lambert_rejects_ndc_and_vertex_normals():
    with pytest.raises(ValueError, match="flat_lambert_requires_data3d_positions"):
        MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            shading=MeshShading.FLAT_LAMBERT,
            normals=np.array([[0, 0, 1]], dtype=np.float32),
            normal_mode=MeshNormalMode.FACE,
        )

    with pytest.raises(ValueError, match="flat_lambert_requires_face_normals"):
        MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            shading=MeshShading.FLAT_LAMBERT,
            normals=np.ones((3, 3), dtype=np.float32),
            normal_mode=MeshNormalMode.VERTEX,
        )


def test_mesh_visual_s039_rejects_legacy_lambert_and_normal_conflicts():
    with pytest.raises(ValueError, match="legacy_lambert_shading_not_canonical"):
        MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            shading=MeshShading.LAMBERT,
        )

    with pytest.raises(ValueError, match="normal_source_conflict"):
        MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            shading=MeshShading.FLAT_LAMBERT,
            normals=np.array([[0, 0, 1]], dtype=np.float32),
            normal_mode=MeshNormalMode.FACE,
            normal_generation=MeshNormalGeneration.FACE_FLAT,
        )


def _canonical_view3d() -> View3D:
    return View3D(
        id="view:main3d",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(near_far=(1.0, 10.0)),
        directional_light=DirectionalLight3D(direction_to_light=(0.0, 0.0, 1.0)),
    )
