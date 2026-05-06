# local imports
from ..types import VisualBase
from ..core.texture import Texture
from ..geometry import MeshGeometry
from ..materials import MeshMaterial


class Mesh(VisualBase):
    """A class representing a 3D mesh with geometry and material properties."""

    __slots__ = ("_geometry", "_material")

    def __init__(self, geometry: MeshGeometry, material: MeshMaterial) -> None:
        """A class representing a 3D mesh with geometry and material properties.

        Arguments:
            geometry (MeshGeometry): geometry of the mesh
            material (MeshMaterial): material of the mesh
        """
        super().__init__()

        self._geometry: MeshGeometry = geometry
        """Geometry of the textured mesh."""
        self._material: MeshMaterial = material
        """Material of the textured mesh."""

        # perform sanity checks
        self.check_attributes()

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_geometry(self) -> MeshGeometry:
        """Get the geometry of the mesh.

        Returns:
            MeshGeometry: geometry of the mesh
        """
        return self._geometry

    def set_geometry(self, geometry: MeshGeometry) -> None:
        """Set the geometry of the mesh.

        Args:
            geometry (MeshGeometry): geometry of the mesh
        """
        self._geometry = geometry
        self.check_attributes()

    def get_material(self) -> MeshMaterial:
        """Get the material of the mesh.

        Returns:
            MeshMaterial: material of the mesh
        """
        return self._material

    def set_material(self, material: MeshMaterial) -> None:
        """Set the material of the mesh.

        Args:
            material (MeshMaterial): material of the mesh
        """
        self._material = material
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._geometry, self._material)

    @staticmethod
    def sanity_check_attributes_buffer(
        geometry: MeshGeometry,
        material: MeshMaterial,
    ) -> None:
        """Same as .sanity_check_attributes() but accept only Buffers.

        It is meant to be used after converting TransBuf to Buffer.

        Args:
            geometry (MeshGeometry): geometry of the mesh
            material (MeshMaterial): material of the mesh
        """
        # perform sanity checks on geometry and material attributes
        geometry.check_attributes()
        material.check_attributes()

        Mesh.sanity_check_attributes(geometry, material)

    @staticmethod
    def sanity_check_attributes(
        geometry: MeshGeometry,
        material: MeshMaterial,
    ) -> None:
        """Validate attribute dimensions and compatibility.

        Args:
            geometry (MeshGeometry): geometry of the mesh
            material (MeshMaterial): material of the mesh
        """
        pass
