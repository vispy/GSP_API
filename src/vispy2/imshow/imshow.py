"""Image display functionality for GSP_API."""

# stdlib imports
from typing import Literal

# pip imports
import numpy as np

# local imports
from gsp.transforms.transform_chain import TransformChain
from gsp.types import Buffer
from gsp.visuals.image import Image
from gsp_extra.bufferx import Bufferx
from gsp.types import TransBuf, Buffer, BufferType, Color
from gsp.utils.log_utils import logger


class ImshowImage:
    """Handle for updating image properties after display."""

    def __init__(
        self,
        data: Buffer,
        *,
        cmap: str | None = None,
        vmin: float | None = None,
        vmax: float | None = None,
        origin: Literal["upper", "lower"] = "upper",
        extent: tuple[float, float, float, float] | None = None,
        aspect: Literal["auto", "equal"] | float = "auto",
        interpolation: Literal["nearest", "bilinear", "bicubic"] = "nearest",
        alpha: float = 1.0,
    ) -> None:
        """Display a 2D image from a buffer.

        Args:
            data: Image buffer (2D for grayscale, 3D for RGB/RGBA).
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
        self._data = data
        self._cmap: str | None = None
        self._vmin: float | None = None
        self._vmax: float | None = None

    def set_data(self, data: Buffer) -> None:
        """Update image data. Useful for animations."""
        # TODO make needed buffer conversion and forward to Visual.Image
        raise NotImplementedError("not implemented")

    def set_cmap(self, cmap: str) -> None:
        """Change colormap dynamically. Only applies to grayscale images."""
        # TODO make needed buffer conversion and forward to Visual.Image
        raise NotImplementedError("not implemented")

    def set_clim(self, vmin: float, vmax: float) -> None:
        """Update value normalization range."""
        # TODO make needed buffer conversion and forward to Visual.Image
        raise NotImplementedError("not implemented")

    def get_data(self) -> Buffer:
        """Retrieve current image buffer."""
        # TODO make needed buffer conversion and forward to Visual.Image
        raise NotImplementedError("not implemented")

    def to_visual_image(self) -> Image:
        """Convert to GSP_API Image visual."""
        # TODO make needed buffer conversion and create Image visual
        raise NotImplementedError("not implemented")


# =============================================================================
#
# =============================================================================
def imshow(
    data: TransBuf | np.ndarray,
    *,
    cmap: str | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    origin: Literal["upper", "lower"] = "upper",
    extent: tuple[float, float, float, float] | None = None,
    aspect: Literal["auto", "equal"] | float = "auto",
    interpolation: Literal["nearest", "bilinear", "bicubic"] = "nearest",
    alpha: float = 1.0,
) -> ImshowImage:
    """Display a 2D image from a buffer.

    Args:
        data: Image buffer (2D for grayscale, 3D for RGB/RGBA).
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
    # =============================================================================
    # Convert data into data_buffer
    # =============================================================================
    if isinstance(data, np.ndarray):
        data = Bufferx.from_numpy(data, BufferType.float32)

    if isinstance(data, TransformChain):
        # NOTE Due to special case of imshow, we need to run the TransformChain immediately to obtain the data buffer. This is not ideal and should be refactored in the future.
        # All the modification of the image data should be done in the transformChain if you want the chain to be run() on the renderer(), especirally if
        # you render on the networkRenderer
        logger.info(
            "Due to special case of imshow, we need to run the TransformChain immediately to obtain the data buffer. This is not ideal and should be refactored in the future."
        )
        data_buffer: Buffer = data.run()
    else:
        data_buffer: Buffer = data

    if isinstance(data_buffer, Buffer) == False:
        raise ValueError("data must be a Buffer or TransformChain that produces a Buffer")

    # =============================================================================
    #
    # =============================================================================
    # Create the ImshowImage handle and return it
    imshowImage = ImshowImage(
        data_buffer,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        origin=origin,
        extent=extent,
        aspect=aspect,
        interpolation=interpolation,
        alpha=alpha,
    )

    # =============================================================================
    #
    # =============================================================================
    return imshowImage
