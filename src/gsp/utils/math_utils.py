"""Mathematical utility functions for GSP.

This module provides mathematical operations and transformations
used throughout the GSP library, including:
- Model-View-Projection (MVP) transformations for 3D graphics
"""

# pip imports
import numpy as np
import typing

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
        return typing.cast(np.ndarray, vertices_mvp_transformed)

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
        return typing.cast(np.ndarray, vertices_3d_transformed)

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
            model_matrix (np.ndarray): The model/world transformation matrix of shape (4, 4).
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

        return typing.cast(np.ndarray, mvp_matrix)

    @staticmethod
    def apply_transform_matrix(vertices: np.ndarray, transform_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Applies a transform matrix to vertices, returning transformed xyz and NDC coordinates.

        ## When transform_matrix = Projection @ View @ Model:
        - Input vertices are in object/model space
        - After MVP transform: vertices are in clip space (homogeneous coordinates)
        - After perspective divide: vertices are in NDC (Normalized Device Coordinates)
        - NDC range is typically [-1, 1] for each axis (ready for rasterization)
        - This is the standard graphics pipeline path
        - The returned xyz coordinates are the clip space positions (before perspective divide).
        - The returned NDC coordinates are the normalized device coordinates (after perspective divide).

        ## When transform_matrix = Model: (Model matrix is world matrix)
        - Input vertices are in object/model space
        - After Model transform: vertices are in world space
        - This is useful for computing world space positions for lighting, etc.
        - The returned xyz coordinates are the world space positions.
          (The NDC result is not meaningful in this case.)

        Args:
            vertices (np.ndarray): Input vertices of shape (N, 3).
            transform_matrix (np.ndarray): A 4x4 transform matrix (e.g., MVP or Model).

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing:
                - Transformed xyz coordinates of shape (N, 3) (clip space for MVP, world space for Model).
                - Perspective-divided coordinates of shape (N, 3) (NDC for MVP, not meaningful for Model).
        """
        # sanity checks
        assert vertices.shape[1] == 3 and vertices.ndim == 2, f"vertices should be of shape [N, 3]. Got {vertices.shape}"
        assert transform_matrix.shape == (4, 4), f"transform should be of shape [4, 4]. Got {transform_matrix.shape}"

        # make vertices homogeneous
        vertices_homogeneous = np.hstack([vertices, np.ones((vertices.shape[0], 1), dtype=vertices.dtype)])  # [N, 4]

        # apply transform (column-vector convention: M @ v)
        vertices_transformed = (transform_matrix @ vertices_homogeneous.T).T  # [N, 4]

        # extract xyz and w components
        vertices_xyz = vertices_transformed[:, :3]  # [N, 3]
        vertices_w = vertices_transformed[:, 3:4]  # [N, 1]

        # avoid division by zero for perspective divide
        vertices_w = np.where(vertices_w == 0, 1e-6, vertices_w)

        # perspective divide to get NDC
        vertices_ndc = vertices_xyz / vertices_w  # [N, 3]

        return vertices_xyz, vertices_ndc
