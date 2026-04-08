# pip imports
import numpy as np

# local imports
from .material import Material
from ..types.transbuf import TransBuf


class MeshMaterial(Material):
    """A simple material class to hold texture mesh material properties."""

    __slots__ = "_colors"

    def __init__(
        self,
        colors: TransBuf,
    ):
        """Initialize a MeshMaterial instance."""
        super().__init__()

        self._colors: TransBuf = colors
        """Vertex colors of the mesh, shape (N, 4) RGBA format."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_colors(self) -> TransBuf:
        """Get the vertex colors.

        Returns:
            TransBuf: Vertex colors of the mesh, shape (N, 4) RGBA format.
        """
        return self._colors

    def set_colors(self, colors: TransBuf) -> None:
        """Set the vertex colors.

        Args:
            colors (TransBuf): Vertex colors of the mesh, shape (N, 4) RGBA format.
        """
        self._colors = colors
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._colors)

    @staticmethod
    def sanity_check_attributes_buffer(
        colors: TransBuf,
    ) -> None:
        """Same as .sanity_check_attributes() but accept only Buffers.

        Args:
            colors (TransBuf): The vertex colors.
        """
        MeshMaterial.sanity_check_attributes(colors)

    @staticmethod
    def sanity_check_attributes(
        colors: TransBuf,
    ) -> None:
        """Check that the geometry attributes are valid and consistent.

        Args:
            colors (TransBuf): The vertex colors of the mesh, BufType.rgba8.
        """
        pass
