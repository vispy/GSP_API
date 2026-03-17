"""Image display functionality for GSP_API."""

# stdlib imports
from typing import Literal
import numpy as np

# local imports
from gsp.types import BufferType
from gsp.visuals.image import Image
from gsp.core.texture import Texture
from gsp.types.image_interpolation import ImageInterpolation
from gsp_extra.bufferx import Bufferx


class ImshowImage:
    """Handle for updating image properties after display."""

    def __init__(
        self,
        texture: Texture,
        *,
        cmap: str | None = None,
        vmin: float | None = None,
        vmax: float | None = None,
        origin: Literal["upper", "lower"] = "upper",
        extent: tuple[float, float, float, float] | None = None,
        aspect: Literal["auto", "equal"] | float = "auto",
        image_interpolation: ImageInterpolation = ImageInterpolation.NEAREST,
        alpha: float = 1.0,
    ) -> None:
        """Display a 2D image from a texture.

        Args:
            texture: Image texture (2D for grayscale, 3D for RGB/RGBA).
            cmap: Colormap name for single-channel images (ignored for RGB/RGBA).
            vmin: Minimum value for normalization. If None, uses data minimum.
            vmax: Maximum value for normalization. If None, uses data maximum.
            origin: Array origin placement. "upper" = top-left, "lower" = bottom-left.
            extent: Custom spatial coordinates [left, right, bottom, top].
            aspect: "auto" stretches to fill, "equal" preserves 1:1, or numeric ratio.
            image_interpolation: Pixel interpolation method.
            alpha: Transparency, 0.0 (transparent) to 1.0 (opaque).

        Returns:
            ImshowImage for updating image properties.
        """
        self._texture = texture
        self._cmap = cmap
        self._vmin = vmin
        self._vmax = vmax
        self._origin = origin
        self._extent = extent
        self._aspect = aspect
        self._image_interpolation = image_interpolation
        self._alpha = alpha

        # Create Image visual
        self._image_visual = self._create_image_visual()

    def _create_image_visual(self) -> Image:
        """Create an Image visual from texture."""
        # Extract dimensions from texture
        width = self._texture.get_width()
        height = self._texture.get_height()

        # Determine image extent (spatial coordinates)
        if self._extent is None:
            aspect_ratio = width / height
            image_extent = (-0.5, +0.5, -0.5 / aspect_ratio, +0.5 / aspect_ratio)
        else:
            image_extent = self._extent

        # Adjust extent for origin
        if self._origin == "upper":
            left, right, bottom, top = image_extent
            image_extent = (left, right, top, bottom)  # Flip bottom/top

        # Define image position (4 vertices for a quad)
        positionX = (image_extent[0] + image_extent[1]) / 2
        positionY = (image_extent[2] + image_extent[3]) / 2
        image_extent = (image_extent[0] - positionX, image_extent[1] - positionX, image_extent[2] - positionY, image_extent[3] - positionY)
        positions_numpy = np.array([[positionX, positionY, 0.0]], dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Create and return Image visual
        return Image(
            texture=self._texture,
            position=positions_buffer,
            image_extent=image_extent,
            image_interpolation=self._image_interpolation,
        )

    def set_data(self, texture: Texture) -> None:
        """Update texture data. Useful for animations."""
        if (texture.get_width(), texture.get_height()) != (
            self._texture.get_width(),
            self._texture.get_height(),
        ):
            raise ValueError(
                f"New texture size {texture.get_width()}x{texture.get_height()} does not match "
                f"original size {self._texture.get_width()}x{self._texture.get_height()}"
            )
        self._texture = texture
        self._image_visual.set_texture(texture)

    def set_cmap(self, cmap: str) -> None:
        """Change colormap dynamically. Only applies to grayscale images."""
        self._cmap = cmap
        # NOTE: Colormap application depends on backend implementation
        # For now, store the value for future use

    def set_clim(self, vmin: float, vmax: float) -> None:
        """Update value normalization range."""
        if vmin >= vmax:
            raise ValueError(f"vmin ({vmin}) must be less than vmax ({vmax})")
        self._vmin = vmin
        self._vmax = vmax
        # NOTE: Value normalization depends on backend/shader implementation

    def get_texture(self) -> Texture:
        """Retrieve current image texture."""
        return self._texture

    def to_visual_image(self) -> Image:
        """Convert to GSP_API Image visual."""
        return self._image_visual


# =============================================================================
# Public API
# =============================================================================
def imshow(
    texture: Texture,
    *,
    cmap: str | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    origin: Literal["upper", "lower"] = "upper",
    extent: tuple[float, float, float, float] | None = None,
    aspect: Literal["auto", "equal"] | float = "auto",
    interpolation: ImageInterpolation = ImageInterpolation.NEAREST,
    alpha: float = 1.0,
) -> ImshowImage:
    """Display a 2D image from a texture.

    Args:
        texture: Image texture (2D for grayscale, 3D for RGB/RGBA).
        cmap: Colormap name for single-channel images (ignored for RGB/RGBA).
        vmin: Minimum value for normalization. If None, uses data minimum.
        vmax: Maximum value for normalization. If None, uses data maximum.
        origin: Array origin placement. "upper" = top-left, "lower" = bottom-left.
        extent: Custom spatial coordinates [left, right, bottom, top].
        aspect: "auto" stretches to fill, "equal" preserves 1:1, or numeric ratio.
        interpolation: Pixel interpolation method.
        alpha: Transparency, 0.0 (transparent) to 1.0 (opaque).

    Returns:
        ImshowImage for updating image properties.
    """
    return ImshowImage(
        texture,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        origin=origin,
        extent=extent,
        aspect=aspect,
        image_interpolation=interpolation,
        alpha=alpha,
    )
