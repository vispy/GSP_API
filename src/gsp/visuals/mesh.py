# local imports
from ..types import VisualBase
from ..core.texture import Texture
from ..geometry import MeshGeometry
from ..materials import MeshMaterial, MeshPhongMaterial, MeshBasicMaterial, MeshNormalMaterial, MeshDepthMaterial, MeshTexturedMaterial


class Mesh(VisualBase):
    """A class representing a 3D mesh with geometry and material properties."""

    __slots__ = ("name", "geometry", "material")

    def __init__(self, geometry: MeshGeometry | None = None, material: MeshMaterial | None = None) -> None:
        super().__init__()

        self.name = f"a {Mesh.__name__}"
        self.geometry: MeshGeometry = geometry if geometry is not None else MeshGeometry()
        """Geometry of the textured mesh."""
        self.material: MeshMaterial = material if material is not None else MeshMaterial()
        """Material of the textured mesh."""

        # perform sanity checks
        self.sanity_checks()

    def sanity_checks(self) -> None:
        """Perform sanity checks on the geometry and material of the textured mesh."""
        if isinstance(self.material, MeshBasicMaterial):
            pass
        elif isinstance(self.material, MeshNormalMaterial):
            pass
        elif isinstance(self.material, MeshDepthMaterial):
            pass
        elif isinstance(self.material, MeshPhongMaterial):
            pass
        elif isinstance(self.material, MeshTexturedMaterial):
            assert self.geometry.uvs is not None, f"The geometry must have texture coordinates (uvs) defined for a textured mesh"
            assert self.material.texture is not None, f"The material must have a texture defined for a textured mesh"
            assert len(self.geometry.uvs) == len(
                self.geometry.vertices
            ), f"The number of uvs must be equal to the number of vertices, got {len(self.geometry.uvs)} uvs and {len(self.geometry.vertices)} vertices"
        else:
            raise TypeError(f"The material must be of type MeshPhongMaterial or MeshBasicMaterial, got {type(self.material)}")
