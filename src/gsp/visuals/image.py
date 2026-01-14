"""Visual for displaying a 2D texture."""

from ..core.texture import Texture
from ..types.buffer import Buffer
from ..types.transbuf import TransBuf
from ..types.visual_base import VisualBase


class Image(VisualBase):
    """Visual for displaying a 2D texture."""

    __slots__ = ["_texture", "_position", "_image_extent"]

    def __init__(self, texture: Texture, position: TransBuf, image_extent: tuple[float, float, float, float]) -> None:
        """Create an image visual from a texture.

        Args:
            texture: Texture containing the image data to display.
            position: Position of the image in the scene.
            image_extent: Extent of the image as (left, right, bottom, top).
        """
        super().__init__()

        self._texture: Texture = texture
        self._position: TransBuf = position
        self._image_extent: tuple[float, float, float, float] = image_extent

        self.check_attributes()

    def __repr__(self) -> str:
        """Return string representation of the Image visual."""
        return f"Image(texture={self._texture})"

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_texture(self) -> Texture:
        """Get the texture used by the image visual."""
        return self._texture

    def set_texture(self, texture: Texture) -> None:
        """Set the texture used by the image visual."""
        self._texture = texture
        self.check_attributes()

    def get_position(self) -> TransBuf:
        """Get the position of the image visual."""
        return self._position

    def set_position(self, position: TransBuf) -> None:
        """Set the position of the image visual."""
        self._position = position
        self.check_attributes()

    def get_image_extent(self) -> tuple[float, float, float, float]:
        """Get the extent of the image visual."""
        return self._image_extent

    def set_image_extent(self, image_extent: tuple[float, float, float, float]) -> None:
        """Set the extent of the image visual."""
        self._image_extent = image_extent
        self.check_attributes()

    def set_attributes(
        self, texture: Texture | None = None, position: TransBuf | None = None, image_extent: tuple[float, float, float, float] | None = None
    ) -> None:
        """Set multiple attributes at once and validate them."""
        if texture is not None:
            self._texture = texture
        if position is not None:
            self._position = position
        if image_extent is not None:
            self._image_extent = image_extent
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self._texture, self._position, self._image_extent)

    @staticmethod
    def sanity_check_attributes_buffer(texture: Texture, position: Buffer, image_extent: tuple[float, float, float, float]) -> None:
        """Sanity check when attributes are already concrete buffers."""
        Image.sanity_check_attributes(texture, position, image_extent)

    @staticmethod
    def sanity_check_attributes(texture: Texture, position: TransBuf, image_extent: tuple[float, float, float, float]) -> None:
        """Sanity check the attributes of the Image visual."""
        if not isinstance(texture, Texture):
            raise TypeError(f"Texture must be a Texture instance, got {type(texture)}")

        # Additional checks can be added here as needed
