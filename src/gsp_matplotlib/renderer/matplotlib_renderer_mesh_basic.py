"""Per-material attribute computation for MeshBasicMaterial."""

# pip imports
import numpy as np

# local imports
from gsp.materials.mesh_basic_material import MeshBasicMaterial
from gsp.utils.transbuf_utils import TransBufUtils
from gsp.visuals.mesh import Mesh
from ..extra.bufferx import Bufferx
from ..utils.renderer_utils import RendererUtils


class RendererMeshBasic:
    """Compute per-face visual attributes for a Mesh using MeshBasicMaterial."""

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

        Args:
            mesh (Mesh): The mesh being rendered.
            geometry_indices_numpy (np.ndarray): Triangle indices, shape (face_count, 3).
            vertices_view_numpy (np.ndarray): View-space vertices (unused by Basic), shape (vertex_count, 3).
            faces_vertices_ndc (np.ndarray): Per-face NDC vertices (unused by Basic), shape (face_count, 3, 3).
            projection_matrix_numpy (np.ndarray): Camera projection matrix (unused by Basic), shape (4, 4).
            vertex_count (int): Number of vertices.
            face_count (int): Number of faces.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray]: face_colors (face_count, 4),
                edge_colors (face_count, 4), edge_widths (face_count,). All in matplotlib units
                (RGBA in [0, 1] for colors).
        """
        material = mesh.get_material()
        assert isinstance(material, MeshBasicMaterial), f"Expected MeshBasicMaterial, got {type(material)}"

        face_colors_buffer = TransBufUtils.to_buffer(material.get_colors())
        edge_colors_buffer = TransBufUtils.to_buffer(material.get_edge_colors())
        edge_widths_buffer = TransBufUtils.to_buffer(material.get_edge_widths())

        # rgba8 colors are 0-255; matplotlib wants 0-1
        face_colors_numpy = Bufferx.to_numpy(face_colors_buffer) / 255.0
        edge_colors_numpy = Bufferx.to_numpy(edge_colors_buffer) / 255.0
        edge_widths_numpy = Bufferx.to_numpy(edge_widths_buffer).flatten()

        face_colors_per_face = RendererUtils.to_per_face(face_colors_numpy, face_count, vertex_count, geometry_indices_numpy)
        edge_colors_per_face = RendererUtils.to_per_face(edge_colors_numpy, face_count, vertex_count, geometry_indices_numpy)
        edge_widths_per_face = RendererUtils.to_per_face(edge_widths_numpy, face_count, vertex_count, geometry_indices_numpy)

        return face_colors_per_face, edge_colors_per_face, edge_widths_per_face
