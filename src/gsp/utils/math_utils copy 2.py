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
        mvp_matrix = projection_matrix @ view_matrix @ model_matrix

        # convert vertices to homogeneous coordinates (x, y, z) -> (x, y, z, w=1.0)
        ws_column = np.ones((vertices.shape[0], 1), dtype=np.float32)
        vertices_homogeneous = np.hstack((vertices, ws_column))  # shape (N, 4) for N vertices

        # Apply the MVP transformation to the vertices
        vertices_mvp_transformed = (mvp_matrix @ vertices_homogeneous.T).T  # shape (N, 4)

        # return the transformed vertices
        return vertices_mvp_transformed

    @staticmethod
    def apply_mvp_to_vertices(vertices: np.ndarray, model_matrix: np.ndarray, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> np.ndarray:
        """Applies Model-View-Projection transformation to the vertices.

        Args:
            vertices (np.ndarray): Input vertices of shape (N, 3).
            model_matrix (np.ndarray): Model matrix of shape (4, 4).
            view_matrix (np.ndarray): View matrix of shape (4, 4).
            projection_matrix (np.ndarray): Projection matrix of shape (4, 4).

        Returns:
            np.ndarray: Transformed vertices of shape (N, 3).
        """
        # Apply the MVP transformation to the vertices
        vertices_mvp_transformed = MathUtils.apply_mvp_to_vertices_transform(vertices, model_matrix, view_matrix, projection_matrix)

        # Perform perspective division to get normalized device coordinates (NDC)
        vertices_homo_transformed = vertices_mvp_transformed / vertices_mvp_transformed[:, 3:4]  # divide by w - shape (N, 4)
        vertices_3d_transformed = vertices_homo_transformed[:, :3]  # drop w-coordinate - shape (N, 3)

        # NOTE: no need to map NDC to screen coordinates as canvas is drawn directly in NDC coordinates 2d
        pass

        # return the transformed vertices
        return vertices_3d_transformed

    # =============================================================================
    # New version... TODO remove the old asap
    # - reviewed by claude
    # =============================================================================

    @staticmethod
    def compute_mvp_matrix(model_matrix: np.ndarray, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> np.ndarray:
        """Compute the Model-View-Projection (MVP) matrix for a 3D object.

        # Useful resources:
        - https://www.scratchapixel.com/lessons/3d-basic-rendering/perspective-and-orthographic-projection-matrix/building-basic-perspective-projection-matrix.html
        - http://www.codinglabs.net/article_world_view_projection_matrix.aspx
        - https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_model_view_projection

        Args:
            model_matrix (np.ndarray): The model transformation matrix of shape (4, 4).
            view_matrix (np.ndarray): The view transformation matrix of shape (4, 4).
            projection_matrix (np.ndarray): The projection transformation matrix of shape (4, 4).

        Returns:
            np.ndarray: The combined Model-View-Projection (MVP) matrix of shape (4, 4).
        """
        # sanity checks
        assert model_matrix.shape == (4, 4), f"Expected model_matrix shape (4, 4), got {model_matrix.shape}"
        assert view_matrix.shape == (4, 4), f"Expected view_matrix shape (4, 4), got {view_matrix.shape}"
        assert projection_matrix.shape == (4, 4), f"Expected projection_matrix shape (4, 4), got {projection_matrix.shape}"

        # Compute the Model-View-Projection (MVP) matrix
        mvp_matrix = projection_matrix @ view_matrix @ model_matrix  # shape (4, 4)

        return mvp_matrix

    @staticmethod
    def apply_mvp_to_vertices_clip_homogeneous_new(vertices: np.ndarray, mvp_matrix: np.ndarray) -> np.ndarray:
        """Applies Model-View-Projection transformation to the vertices.

        Args:
            vertices (np.ndarray): Input vertices of shape (N, 3).
            mvp_matrix (np.ndarray): Model-View-Projection matrix of shape (4, 4).

        Returns:
            np.ndarray: MVP transformed vertices of shape (N, 4).
        """
        # sanity checks
        assert vertices.ndim == 2 and vertices.shape[1] == 3, f"Expected vertices shape (N, 3), got {vertices.shape}"
        assert mvp_matrix.shape == (4, 4), f"Expected mvp_matrix shape (4, 4), got {mvp_matrix.shape}"

        # make vertices homogeneous - (x, y, z) -> (x, y, z, w=1.0)
        ws_column = np.ones((vertices.shape[0], 1), dtype=np.float32)
        vertices_homogeneous = np.hstack((vertices, ws_column))  # shape (N, 4) for N vertices

        # Apply mvp_matrix to the homogeneous vertices
        vertices_clip_homogeneous = (mvp_matrix @ vertices_homogeneous.T).T  # shape (N, 4) for N vertices

        # now we return vertices_clip_homogeneous - shape (N, 4)
        # - still homogeneous coordinates, perspective division to be done later
        return vertices_clip_homogeneous

    @staticmethod
    def apply_mvp_to_vertices_new(
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
            tuple[np.ndarray, np.ndarray]: A tuple containing:
            - vertices_clip_3d: Transformed vertices in clip space (before perspective division) of shape (N, 3).
            - vertices_ndc: Transformed vertices in Normalized Device Coordinates (NDC) of shape (N, 3).
        """
        # Apply the MVP transformation to the vertices - resulting shape (N, 4) for N vertices in homogeneous coordinates
        vertices_clip_homo = MathUtils.apply_mvp_to_vertices_transform_new(vertices, model_matrix, view_matrix, projection_matrix)

        # get w for perspective divide
        vertices_w = vertices_clip_homo[:, 3:4]  # [N, 1]

        # extract xyz from clip-space coordinates
        vertices_clip_3d = vertices_clip_homo[:, :3]  # [N, 3]

        # avoid division by zero
        vertices_w[vertices_w == 0] = 1e-6

        # Perform perspective divide to get normalized device coordinates (NDC)
        vertices_ndc = vertices_clip_3d / vertices_w  # [N, 3]

        return vertices_clip_3d, vertices_ndc
