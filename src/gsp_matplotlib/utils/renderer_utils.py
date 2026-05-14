# pip imports
import matplotlib.artist
import numpy as np

# local imports
from gsp.constants import Constants


class RendererUtils:
    """Utility functions for matplotlib rendering in GSP."""

    @staticmethod
    def compute_faces_visible(faces_vertices_2d: np.ndarray, face_culling: Constants.FaceCulling) -> np.ndarray:
        """Compute which faces are visible based on their normals and the camera position.

        Returns:
            np.ndarray: A boolean array indicating which faces are visible.
        """
        # For each face, compute the cross product of the edges in 2D (NDC, y is up).
        # - cross_z > 0  → CCW in screen space → FrontSide (OpenGL / glTF convention)
        # - cross_z < 0  → CW  in screen space → BackSide
        # - cross_z == 0 → degenerate (line or point)
        faces_edges_2d_a = faces_vertices_2d[:, 1] - faces_vertices_2d[:, 0]
        faces_edges_2d_b = faces_vertices_2d[:, 2] - faces_vertices_2d[:, 0]
        faces_cross_z = faces_edges_2d_a[:, 0] * faces_edges_2d_b[:, 1] - faces_edges_2d_a[:, 1] * faces_edges_2d_b[:, 0]
        # this is the threshold below which a face is considered degenerated and trigger exception when inverting matrix
        faces_cross_threshold = 1e-6
        if face_culling == Constants.FaceCulling.FrontSide:
            faces_visible = faces_cross_z >= faces_cross_threshold
        elif face_culling == Constants.FaceCulling.BackSide:
            faces_visible = faces_cross_z <= -faces_cross_threshold
        elif face_culling == Constants.FaceCulling.BothSides:
            # If the face is degenerated (line or point), it is not visible
            faces_visible = np.abs(faces_cross_z) > faces_cross_threshold
        else:
            raise ValueError(f"Unknown face culling mode: {face_culling}")

        # print(f"faces_visible: {faces_visible.sum()}/{len(faces_visible)}")
        return faces_visible

    @staticmethod
    def to_per_face(array: np.ndarray, face_count: int, vertex_count: int, geometry_indices: np.ndarray) -> np.ndarray:
        """Broadcast a per-vertex, per-mesh, or already-per-face attribute to per-face.

        Args:
            array (np.ndarray): The attribute, shape (face_count, ...), (vertex_count, ...), or (1, ...).
            face_count (int): Number of faces.
            vertex_count (int): Number of vertices.
            geometry_indices (np.ndarray): Triangle indices, shape (face_count, 3).

        Returns:
            np.ndarray: The attribute broadcast/indexed to shape (face_count, ...).
        """
        if array.shape[0] == face_count:
            return array
        if array.shape[0] == vertex_count:
            return array[geometry_indices[:, 0]]
        if array.shape[0] == 1:
            return np.broadcast_to(array, (face_count,) + array.shape[1:]).copy()
        raise ValueError(f"unexpected attribute length {array.shape[0]}; expected 1, face_count={face_count}, or vertex_count={vertex_count}")

    @staticmethod
    def compute_face_normals_view(vertices_view: np.ndarray, geometry_indices: np.ndarray) -> np.ndarray:
        """Compute per-face normals in view space via the triangle cross product.

        Args:
            vertices_view (np.ndarray): Vertices in view (camera) space, shape (vertex_count, 3).
            geometry_indices (np.ndarray): Triangle indices, shape (face_count, 3).

        Returns:
            np.ndarray: Unit per-face normals in view space, shape (face_count, 3).
        """
        faces_vertices_view = vertices_view[geometry_indices]  # (face_count, 3, 3)
        edge_a = faces_vertices_view[:, 1] - faces_vertices_view[:, 0]
        edge_b = faces_vertices_view[:, 2] - faces_vertices_view[:, 0]
        face_normals = np.cross(edge_a, edge_b)
        norms = np.linalg.norm(face_normals, axis=1, keepdims=True)
        # avoid division by zero on degenerate faces; they'll be culled separately
        norms = np.where(norms == 0.0, 1.0, norms)
        return face_normals / norms

    @staticmethod
    def compute_face_depths_ndc(faces_vertices_ndc: np.ndarray) -> np.ndarray:
        """Compute per-face depth as the mean NDC z over the triangle vertices.

        Args:
            faces_vertices_ndc (np.ndarray): Per-face vertices in NDC, shape (face_count, 3, 3).

        Returns:
            np.ndarray: Mean NDC z per face, shape (face_count,).
        """
        return faces_vertices_ndc[:, :, 2].mean(axis=1)
