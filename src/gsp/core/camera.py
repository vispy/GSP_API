"""Camera module for the GSP library."""
# stdlib imports
from typing import Any

# local imports
from ..types.transbuf import TransBuf
from ..utils.uuid_utils import UuidUtils


class Camera:
    """Camera class representing a view and projection matrix for 3D rendering."""
    __slots__ = ["_uuid", "_view_matrix", "_projection_matrix", "userData"]

    def __init__(self, view_matrix: TransBuf, projection_matrix: TransBuf):
        """Initialize a Camera instance. Just a container for view and projection matrices.

        Args:
            view_matrix (TransBuf): View matrix - [view-matrix](https://www.opengl-tutorial.org/beginners-tutorials/tutorial-3-matrices/#the-view-matrix)
            projection_matrix (TransBuf): Projection matrix - [projection-matrix](https://www.opengl-tutorial.org/beginners-tutorials/tutorial-3-matrices/#the-projection-matrix)
        """
        self._uuid: str = UuidUtils.generate_uuid()
        self._view_matrix: TransBuf = view_matrix
        self._projection_matrix: TransBuf = projection_matrix
        self.userData: dict[str, Any] = {}
        """A dictionary for storing custom user data associated with the Camera instance."""

    def __repr__(self) -> str:
        """Return string representation of the Camera instance."""
        return f"Camera(uuid={self._uuid})"

    def get_uuid(self) -> str:
        """Get the UUID of the Camera instance.

        Returns:
            str: The UUID of the Camera.
        """
        return self._uuid

    def set_view_matrix(self, view_matrix: TransBuf):
        """Set the view matrix of the Camera.

        Args:
            view_matrix (TransBuf): The new view matrix.
        """
        self._view_matrix = view_matrix

    def get_view_matrix(self) -> TransBuf:
        """Get the view matrix of the Camera.

        Returns:
            TransBuf: The view matrix.
        """
        return self._view_matrix

    def set_projection_matrix(self, projection_matrix: TransBuf):
        """Set the projection matrix of the Camera.

        Args:
            projection_matrix (TransBuf): The new projection matrix.
        """
        self._projection_matrix = projection_matrix

    def get_projection_matrix(self) -> TransBuf:
        """Get the projection matrix of the Camera.

        Returns:
            TransBuf: The projection matrix.
        """
        return self._projection_matrix
