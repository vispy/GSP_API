"""MeshPhongMaterial: flat per-face Phong shading using a list of lights carried on the material."""

# pip imports
from typing import Sequence

# local imports
from ..constants import Constants
from ..lights.light import Light
from .mesh_material import MeshMaterial
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.buffer_type import BufferType
from ..utils.transbuf_utils import TransBufUtils


class MeshPhongMaterial(MeshMaterial):
    """A material applying flat per-face Phong shading using a list of lights carried on the material."""

    def __init__(
        self,
        diffuse_color: TransBuf,
        specular_color: TransBuf,
        shininess: float,
        lights: Sequence[Light],
        edge_colors: TransBuf,
        edge_widths: TransBuf,
        face_sorting: bool,
        face_culling: Constants.FaceCulling,
    ):
        """Initialize a MeshPhongMaterial.

        Args:
            diffuse_color (TransBuf): rgba8 buffer, per-vertex or count-1. Used for both
                the diffuse term and (modulated by AmbientLight) the ambient term.
            specular_color (TransBuf): rgba8 buffer, typically count-1.
            shininess (float): Phong specular exponent.
            lights (Sequence[Light]): Lights illuminating this material. Positions on
                Point/Directional lights are in model space (same as vertex positions).
            edge_colors (TransBuf): rgba8 buffer of edge colors.
            edge_widths (TransBuf): float32 buffer of edge widths.
            face_sorting (bool): Whether to sort faces by depth (painter's algorithm).
            face_culling (Constants.FaceCulling): Face culling mode.
        """
        super().__init__()

        self._diffuse_color: TransBuf = diffuse_color
        """Diffuse / ambient base color, rgba8 buffer."""
        self._specular_color: TransBuf = specular_color
        """Specular color, rgba8 buffer."""
        self._shininess: float = shininess
        """Phong specular exponent."""
        self._lights: Sequence[Light] = lights
        """Lights illuminating the mesh. Positions are in model space."""
        self._edge_colors: TransBuf = edge_colors
        """Edge colors, rgba8 buffer."""
        self._edge_widths: TransBuf = edge_widths
        """Edge widths, float32 buffer."""
        self._face_sorting: bool = face_sorting if face_sorting is not None else True
        """Whether to sort faces by depth (painter's algorithm)."""
        self._face_culling: Constants.FaceCulling = face_culling if face_culling is not None else Constants.FaceCulling.FrontSide
        """Face culling mode."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_diffuse_color(self) -> TransBuf:
        """Get the diffuse base color."""
        return self._diffuse_color

    def set_diffuse_color(self, diffuse_color: TransBuf) -> None:
        """Set the diffuse base color."""
        self._diffuse_color = diffuse_color
        self.check_attributes()

    def get_specular_color(self) -> TransBuf:
        """Get the specular color."""
        return self._specular_color

    def set_specular_color(self, specular_color: TransBuf) -> None:
        """Set the specular color."""
        self._specular_color = specular_color
        self.check_attributes()

    def get_shininess(self) -> float:
        """Get the Phong specular exponent."""
        return self._shininess

    def set_shininess(self, shininess: float) -> None:
        """Set the Phong specular exponent."""
        self._shininess = shininess

    def get_lights(self) -> Sequence[Light]:
        """Get the lights illuminating this material."""
        return self._lights

    def set_lights(self, lights: Sequence[Light]) -> None:
        """Set the lights illuminating this material."""
        self._lights = lights

    def get_edge_colors(self) -> TransBuf:
        """Get the edge colors."""
        return self._edge_colors

    def set_edge_colors(self, edge_colors: TransBuf) -> None:
        """Set the edge colors."""
        self._edge_colors = edge_colors
        self.check_attributes()

    def get_edge_widths(self) -> TransBuf:
        """Get the edge widths."""
        return self._edge_widths

    def set_edge_widths(self, edge_widths: TransBuf) -> None:
        """Set the edge widths."""
        self._edge_widths = edge_widths
        self.check_attributes()

    def get_face_sorting(self) -> bool:
        """Get whether to sort faces by depth (painter's algorithm)."""
        return self._face_sorting

    def set_face_sorting(self, face_sorting: bool) -> None:
        """Set whether to sort faces by depth (painter's algorithm)."""
        self._face_sorting = face_sorting

    def get_face_culling(self) -> Constants.FaceCulling:
        """Get the face culling mode."""
        return self._face_culling

    def set_face_culling(self, face_culling: Constants.FaceCulling) -> None:
        """Set the face culling mode."""
        self._face_culling = face_culling

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes()

    def check_attributes_buffer(self) -> None:
        """Check that the attribute buffers are valid and consistent."""
        diffuse_buffer = TransBufUtils.to_buffer(self._diffuse_color)
        specular_buffer = TransBufUtils.to_buffer(self._specular_color)
        edge_colors_buffer = TransBufUtils.to_buffer(self._edge_colors)
        self.sanity_check_attributes_buffer(diffuse_buffer, specular_buffer, edge_colors_buffer)

    @staticmethod
    def sanity_check_attributes_buffer(
        diffuse_color: Buffer,
        specular_color: Buffer,
        edge_colors: Buffer,
    ) -> None:
        """Check that the geometry attribute buffers are valid and consistent.

        Args:
            diffuse_color (Buffer): The diffuse color buffer.
            specular_color (Buffer): The specular color buffer.
            edge_colors (Buffer): The edge colors buffer.
        """
        assert diffuse_color.get_type() == BufferType.rgba8, f"diffuse_color buffer must be rgba8, got {diffuse_color.get_type()}"
        assert specular_color.get_type() == BufferType.rgba8, f"specular_color buffer must be rgba8, got {specular_color.get_type()}"
        assert edge_colors.get_type() == BufferType.rgba8, f"edge_colors buffer must be rgba8, got {edge_colors.get_type()}"

    @staticmethod
    def sanity_check_attributes() -> None:
        """Check pre-buffer attributes (currently nothing to check)."""
        pass
