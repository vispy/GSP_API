# pip imports
import numpy as np

# local imports
from ..types.transbuf import TransBuf


class Geometry:
    """A class representing a 3D geometry with vertices."""

    __slots__ = ["_positions"]

    def __init__(self, positions: TransBuf) -> None:
        """A class representing a 3D geometry with vertices.

        Arguments:
            positions (TransBuf): array of vertex coordinates, shape (N, 3)
        """
        # assign attributes
        self._positions: TransBuf = positions

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_positions(self) -> TransBuf:
        """Get the vertex coordinates.

        Returns:
            TransBuf: array of vertex coordinates, shape (N, 3)
        """
        return self._positions

    def set_positions(self, positions: TransBuf) -> None:
        """Set the vertex coordinates.

        Args:
            positions (TransBuf): array of vertex coordinates, shape (N, 3)
        """
        self._positions = positions
        # self.check_attributes()

    # TODO fix it

    # # =============================================================================
    # # Sanity check functions
    # # =============================================================================

    # def check_attributes(self) -> None:
    #     """Check that the attributes are valid and consistent."""
    #     self.sanity_check_attributes(self._positions)

    # @staticmethod
    # def sanity_check_attributes_buffer(
    #     vertices: TransBuf,
    # ) -> None:
    #     """Same as .sanity_check_attributes() but accept only Buffers.

    #     Args:
    #         vertices (TransBuf): The vertex coordinates.
    #     """
    #     Geometry.sanity_check_attributes(vertices)

    # @staticmethod
    # def sanity_check_attributes(
    #     vertices: TransBuf,
    # ) -> None:
    #     """Check that the geometry attributes are valid and consistent.

    #     Args:
    #         vertices (TransBuf): The vertex coordinates.
    #     """
    #     pass
