"""Mathematical utility functions for GSP.

This module provides mathematical operations and transformations
used throughout the GSP library, including:
- Model-View-Projection (MVP) transformations for 3D graphics
"""

# pip imports
import numpy as np

# local imports
from ..types.buffer import Buffer


class MathUtils:
    """Utility class for mathematical operations in GSP.

    This class provides static methods for common mathematical operations
    used in graphics programming, such as matrix transformations.
    """

    @staticmethod
    def apply_mvp_to_vertices_transform(vertices: np.ndarray, model_matrix: np.ndarray, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> np.ndarray:
        """Applies Model-View-Projection transformation to the vertices.

        Args:
            vertices (np.ndarray): Input vertices of shape (N, 3).
            model_matrix (np.ndarray): Model matrix of shape (4, 4).
            view_matrix (np.ndarray): View matrix of shape (4, 4).
            projection_matrix (np.ndarray): Projection matrix of shape (4, 4).

        Returns:
            np.ndarray: MVP transformed vertices of shape (N, 4).
        """
        # sanity checks
        assert vertices.ndim == 2 and vertices.shape[1] == 3, f"Expected vertices shape (N, 3), got {vertices.shape}"
        assert model_matrix.shape == (4, 4), f"Expected model_matrix shape (4, 4), got {model_matrix.shape}"
        assert view_matrix.shape == (4, 4), f"Expected view_matrix shape (4, 4), got {view_matrix.shape}"
        assert projection_matrix.shape == (4, 4), f"Expected projection_matrix shape (4, 4), got {projection_matrix.shape}"

        # Compute the Model-View-Projection (MVP) matrix
        mvp_matrix = projection_matrix @ view_matrix @ model_matrix  # shape (4, 4)

        # make vertices homogeneous - (x, y, z) -> (x, y, z, w=1.0)
        ws_column = np.ones((vertices.shape[0], 1), dtype=np.float32)
        vertices_homogeneous = np.hstack((vertices, ws_column))  # shape (N, 4) for N vertices

        # Apply mvp_matrix to the homogeneous vertices
        vertices_world_homogeneous = (mvp_matrix @ vertices_homogeneous.T).T  # shape (N, 4) for N vertices

        # return vertices_world_homogeneous # shape (N, 4) - still homogeneous coordinates, perspective division to be done later
        return vertices_world_homogeneous

    @staticmethod
    def apply_mvp_to_vertices(
        vertices: np.ndarray,
        model_matrix: np.ndarray,
        view_matrix: np.ndarray,
        projection_matrix: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Applies Model-View-Projection transformation to the vertices.

        Args:
            vertices (np.ndarray): Input vertices of shape (N, 3).
            model_matrix (np.ndarray): Model matrix of shape (4, 4).
            view_matrix (np.ndarray): View matrix of shape (4, 4).
            projection_matrix (np.ndarray): Projection matrix of shape (4, 4).

        Returns:
            np.ndarray: Transformed vertices of shape (N, 3).
        """
        # Apply the MVP transformation to the vertices - resulting shape (N, 4) for N vertices in homogeneous coordinates
        vertices_world_homo = MathUtils.apply_mvp_to_vertices_transform(vertices, model_matrix, view_matrix, projection_matrix)

        # Perform perspective division to get normalized device coordinates (NDC)

        # get w for perspective divide
        vertices_w = vertices_world_homo[:, 3:4]  # [N, 1]
        # drop w for clip space
        vertices_clip = vertices_world_homo[:, :3]  # [N, 3]

        # avoid division by zero
        vertices_w[vertices_w == 0] = 1e-6

        # Perform perspective divide to get normalized device coordinates (NDC)
        vertices_ndc = vertices_clip / vertices_w  # [N, 3]

        return vertices_ndc, vertices_clip
