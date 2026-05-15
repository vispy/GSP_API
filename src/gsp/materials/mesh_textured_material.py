"""MeshTexturedMaterial: per-face Phong shading with a texture as the diffuse term."""

# pip imports
from typing import Sequence

# local imports
from ..constants import Constants
from ..core.texture import Texture
from ..lights.light import Light
from .mesh_material import MeshMaterial
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..types.buffer_type import BufferType
from ..utils.transbuf_utils import TransBufUtils


class MeshTexturedMaterial(MeshMaterial):
    """A material that samples a texture per face and shades the result with Phong lighting."""

    def __init__(
        self,
        texture: Texture,
        color: TransBuf,
        specular_color: TransBuf,
        shininess: float,
        lights: Sequence[Light],
        face_sorting: bool,
        face_culling: Constants.FaceCulling,
    ):
        """Initialize a MeshTexturedMaterial.

        Args:
            texture (Texture): Texture whose data buffer is rgba8 with length width * height.
            color (TransBuf): rgba8 buffer used as a uniform tint multiplied with the texture sample.
            specular_color (TransBuf): rgba8 buffer for the Phong specular color, typically count-1.
            shininess (float): Phong specular exponent.
            lights (Sequence[Light]): Lights illuminating this material. Point/Directional positions
                are in model space (same convention as MeshPhongMaterial).
            face_sorting (bool): Whether to sort faces by depth (painter's algorithm).
            face_culling (Constants.FaceCulling): Face culling mode.
        """
        super().__init__()

        self._texture: Texture = texture
        """Texture for the diffuse term, rgba8 buffer of length width * height."""
        self._color: TransBuf = color
        """Uniform tint multiplied with the texture sample, rgba8 buffer."""
        self._specular_color: TransBuf = specular_color
        """Specular color, rgba8 buffer."""
        self._shininess: float = shininess
        """Phong specular exponent."""
        self._lights: Sequence[Light] = lights
        """Lights illuminating the mesh. Positions are in model space."""
        self._face_sorting: bool = face_sorting if face_sorting is not None else True
        """Whether to sort faces by depth (painter's algorithm)."""
        self._face_culling: Constants.FaceCulling = face_culling if face_culling is not None else Constants.FaceCulling.FrontSide
        """Face culling mode."""

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_texture(self) -> Texture:
        """Get the texture."""
        return self._texture

    def set_texture(self, texture: Texture) -> None:
        """Set the texture."""
        self._texture = texture
        self.check_attributes()

    def get_color(self) -> TransBuf:
        """Get the tint color."""
        return self._color

    def set_color(self, color: TransBuf) -> None:
        """Set the tint color."""
        self._color = color
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
        color_buffer = TransBufUtils.to_buffer(self._color)
        specular_buffer = TransBufUtils.to_buffer(self._specular_color)
        texture_data_buffer = TransBufUtils.to_buffer(self._texture.get_data())
        self.sanity_check_attributes_buffer(
            color_buffer,
            specular_buffer,
            texture_data_buffer,
            self._texture.get_width(),
            self._texture.get_height(),
        )

    @staticmethod
    def sanity_check_attributes_buffer(
        color: Buffer,
        specular_color: Buffer,
        texture_data: Buffer,
        texture_width: int,
        texture_height: int,
    ) -> None:
        """Check that the buffers are valid and consistent.

        Args:
            color (Buffer): The tint color buffer.
            specular_color (Buffer): The specular color buffer.
            texture_data (Buffer): The texture pixel data buffer.
            texture_width (int): Texture width in pixels.
            texture_height (int): Texture height in pixels.
        """
        assert color.get_type() == BufferType.rgba8, f"color buffer must be rgba8, got {color.get_type()}"
        assert specular_color.get_type() == BufferType.rgba8, f"specular_color buffer must be rgba8, got {specular_color.get_type()}"
        assert texture_data.get_type() == BufferType.rgba8, f"texture data buffer must be rgba8, got {texture_data.get_type()}"
        assert (
            texture_data.get_count() == texture_width * texture_height
        ), f"texture data buffer length {texture_data.get_count()} does not match width * height = {texture_width * texture_height}"

    @staticmethod
    def sanity_check_attributes() -> None:
        """Check pre-buffer attributes (currently nothing to check)."""
        pass
