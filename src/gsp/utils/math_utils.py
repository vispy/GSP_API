# pip imports
import numpy as np

# local imports
from ..types.buffer import Buffer


class MathUtils:
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
        vertices_transformed = (mvp_matrix @ vertices_homogeneous.T).T  # shape (N, 4)

        # Perform perspective division to get normalized device coordinates (NDC)
        vertices_homo_transformed = vertices_transformed / vertices_transformed[:, 3:4]  # divide by w - shape (N, 4)
        vertices_3d_transformed = vertices_homo_transformed[:, :3]  # drop w-coordinate - shape (N, 3)

        # NOTE: no need to map NDC to screen coordinates as canvas is drawn directly in NDC coordinates 2d
        pass

        # return the transformed vertices
        return vertices_3d_transformed
