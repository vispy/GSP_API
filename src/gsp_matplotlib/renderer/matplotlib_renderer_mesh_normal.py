"""Per-material attribute computation for MeshNormalMaterial."""

# pip imports
import numpy as np

# local imports
from gsp.materials.mesh_normal_material import MeshNormalMaterial
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.visuals.mesh import Mesh
from ..extra.bufferx import Bufferx
from ..utils.renderer_utils import RendererUtils


class RendererMeshNormal:
    """Compute per-face visual attributes for a Mesh using MeshNormalMaterial."""

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

        Face colors map the unit view-space normal to RGB via ``n * 0.5 + 0.5``.

        Args:
            mesh (Mesh): The mesh being rendered.
            geometry_indices_numpy (np.ndarray): Triangle indices, shape (face_count, 3).
            vertices_view_numpy (np.ndarray): View-space vertices, shape (vertex_count, 3).
            faces_vertices_ndc (np.ndarray): Per-face NDC vertices (unused), shape (face_count, 3, 3).
            projection_matrix_numpy (np.ndarray): Camera projection matrix (unused by Normal), shape (4, 4).
            vertex_count (int): Number of vertices.
            face_count (int): Number of faces.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray]: face_colors (face_count, 4),
                edge_colors (face_count, 4), edge_widths (face_count,).
        """
        material = mesh.get_material()
        assert isinstance(material, MeshNormalMaterial), f"Expected MeshNormalMaterial, got {type(material)}"

        face_normals = RendererUtils.compute_face_normals_view(vertices_view_numpy, geometry_indices_numpy)
        face_colors_rgb = face_normals * 0.5 + 0.5
        face_colors_alpha = np.ones((face_count, 1), dtype=face_colors_rgb.dtype)
        face_colors_per_face = np.concatenate([face_colors_rgb, face_colors_alpha], axis=1)

        edge_colors_buffer = TransBufUtils.to_buffer(material.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(material.get_edge_widths())
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer) / 255.0
        edge_widths_numpy = Bufferx.to_numpy(edge_widths_buffer).flatten()
        edge_colors_per_face = RendererUtils.to_per_face(edge_colors_numpy, face_count, vertex_count, geometry_indices_numpy)
        edge_widths_per_face = RendererUtils.to_per_face(edge_widths_numpy, face_count, vertex_count, geometry_indices_numpy)

        return face_colors_per_face, edge_colors_per_face, edge_widths_per_face
