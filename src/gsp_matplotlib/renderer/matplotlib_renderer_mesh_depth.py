"""Per-material attribute computation for MeshDepthMaterial."""

# pip imports
import numpy as np

# local imports
from gsp.materials.mesh_depth_material import MeshDepthMaterial
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.visuals.mesh import Mesh
from ..extra.bufferx import Bufferx
from ..utils.renderer_utils import RendererUtils


class RendererMeshDepth:
    """Compute per-face visual attributes for a Mesh using MeshDepthMaterial."""

    @staticmethod
    def compute_attributes(
        mesh: Mesh,
        geometry_indices_numpy: np.ndarray,
        vertices_view_numpy: np.ndarray,
        faces_vertices_ndc: np.ndarray,
        projection_matrix_numpy: np.ndarray,
        vertex_count: int,
        face_count: int,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute per-face (face_colors, edge_colors, edge_widths) for the given mesh.

        Face colors map linear view-space depth in [near, far] to grayscale in [1, 0]
        (white at the near plane, black at the far plane). Matches Three.js MeshDepthMaterial.

        Args:
            mesh (Mesh): The mesh being rendered.
            geometry_indices_numpy (np.ndarray): Triangle indices, shape (face_count, 3).
            vertices_view_numpy (np.ndarray): View-space vertices, shape (vertex_count, 3).
            faces_vertices_ndc (np.ndarray): Per-face NDC vertices (unused), shape (face_count, 3, 3).
            projection_matrix_numpy (np.ndarray): Camera projection matrix, shape (4, 4). Used to recover near/far.
            vertex_count (int): Number of vertices.
            face_count (int): Number of faces.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray]: face_colors (face_count, 4),
                edge_colors (face_count, 4), edge_widths (face_count,).
        """
        material = mesh.get_material()
        assert isinstance(material, MeshDepthMaterial), f"Expected MeshDepthMaterial, got {type(material)}"

        # Recover znear/zfar from an OpenGL right-handed perspective projection matrix.
        # P[2,2] = -(far+near)/(far-near), P[2,3] = -2*far*near/(far-near)
        m22 = projection_matrix_numpy[2, 2]
        m23 = projection_matrix_numpy[2, 3]
        znear = m23 / (m22 - 1.0)
        zfar = m23 / (m22 + 1.0)

        # OpenGL camera looks down -z, so positive depth is -view_z.
        faces_view_z = vertices_view_numpy[geometry_indices_numpy, 2]  # (face_count, 3)
        face_depth = -faces_view_z.mean(axis=1)
        face_grayscale = np.clip((zfar - face_depth) / (zfar - znear), 0.0, 1.0)
        face_colors_rgb = np.repeat(face_grayscale[:, np.newaxis], 3, axis=1)
        face_colors_alpha = np.ones((face_count, 1), dtype=face_colors_rgb.dtype)
        face_colors_per_face = np.concatenate([face_colors_rgb, face_colors_alpha], axis=1)

        edge_colors_buffer = TransBufUtils.to_buffer(material.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(material.get_edge_widths())
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer) / 255.0
        edge_widths_numpy = Bufferx.to_numpy(edge_widths_buffer).flatten()
        edge_colors_per_face = RendererUtils.to_per_face(edge_colors_numpy, face_count, vertex_count, geometry_indices_numpy)
        edge_widths_per_face = RendererUtils.to_per_face(edge_widths_numpy, face_count, vertex_count, geometry_indices_numpy)

        return face_colors_per_face, edge_colors_per_face, edge_widths_per_face
