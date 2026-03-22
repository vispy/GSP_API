# pip imports
import numpy as np


class Geometry:
    """A class representing a 3D geometry with vertices."""

    def __init__(self, vertices: np.ndarray | None = None) -> None:
        """A class representing a 3D geometry with vertices.

        Arguments:
            vertices (np.ndarray): array of vertex coordinates, shape (N, 3)
        """
        # assign attributes
        self.vertices: np.ndarray = vertices if vertices is not None else np.zeros((0, 3)).astype(np.float32)
        """array of vertex coordinates, shape (N, 3)"""

        # sanity check - make sure we have triangular faces
        assert self.vertices.ndim == 2 and self.vertices.shape[1] == 3, f"vertices_coords should be of shape [N, 3], got {self.vertices.shape}"
