"""Example demonstrating the AxesDisplay with pan and zoom functionality.

## Glossary
- a value is a 16 bytes
- a sample is 384 values, one per channel, at a given time point
- a zoomout level is a downsampling level of the original data by a factor of 2^zoomout_level, thus the number of samples in the
  file at a given zoomout level is file_full_sample_count / (2^zoomout_level)
"""

# import matplotlib

# # logger.debug(f"Using matplotlib backend: {matplotlib.get_backend()}")
# matplotlib.use("QtAgg")
# logger.debug(f"Using matplotlib backend: {matplotlib.get_backend()}")

# set DVZ_LOG_LEVEL=4 env variable to see datoviz debug logs
import os

os.environ["DVZ_LOG_LEVEL"] = "4"


# stdlib imports
from dataclasses import dataclass
import time
import typing

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.core.texture import Texture
from gsp.types.image_interpolation import ImageInterpolation
from gsp.visuals import Image
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType, VisualBase
from gsp.utils.transbuf_utils import TransBufUtils
from gsp_extra.misc.render_item import RenderItem
from vispy_2.axes.axes_display import AxesDisplay
from vispy_2.axes.axes_panzoom import AxesPanZoom
from common.asset_downloader import AssetDownloader
from gsp.utils.log_utils import logger

# =============================================================================
#
# =============================================================================


@dataclass(frozen=True)
class PyramidConfig:
    """Configuration for the pyramid image visual. Fixed over time."""

    value_dtype: type = np.float16
    """Data point type for memory-efficient storage."""

    value_min: float = -5e-4
    """Minimum value for data normalization."""

    value_max: float = +5e-4
    """Maximum value for data normalization."""

    channel_count: int = 384
    """Number of recording channels (typical for Neuropixels probes). 1 sample is one time data point across all channels."""

    sample_size_bytes: int = channel_count * np.dtype(value_dtype).itemsize
    """Size of one sample in bytes. One sample is one time point across all channels (so 384 values * 2 bytes each for float16)."""

    max_zoomout: int = 11
    """Maximum zoomout level (2^11 = 2048x downsampling)."""

    min_zoomout: int = 7
    """Minimum zoomout level (2^7 = 128x downsampling)."""

    file_x_min_dunit: float = +0.0
    """Minimum x data unit of the file."""

    file_x_max_dunit: float = +2.0
    """Maximum x data unit of the file."""

    file_zoom0_size_bytes: int = 10_797_276_672
    """File size in bytes."""

    file_zoom0_sample_count: int = file_zoom0_size_bytes // sample_size_bytes
    """Number of samples in the file."""

    texture_margin_percent: float = 0.25
    """Margin percentage to add to texture extent to add margin. and not update too often."""

    texture_max_width_pixels: int = 2048
    """Maximum texture width in pixels to avoid too large textures."""


@dataclass()
class PyramidParams:
    """Parameters for the pyramid image visual. May change over time."""

    image_extent_target_dunit = (
        PyramidConfig.file_x_min_dunit,
        PyramidConfig.file_x_max_dunit,
        -PyramidConfig.channel_count / 2,
        PyramidConfig.channel_count / 2,
    )
    """Target image extent in data units (left, right, bottom, top). It is recomputed on pan/zoom"""

    current_zoomout_level: int = PyramidConfig.max_zoomout
    """Current zoomout level of the texture in the image visual. It is recomputed on pan/zoom."""


# =============================================================================
# Helper for pyramid texture
# =============================================================================
class PyramidTextureHelper:

    @staticmethod
    def file_level_memmap(zoomout_level: int) -> np.memmap:
        """Load pyramid file from memmap file for given zoomout level.

        memmap() the whole file, so from PyramidConfig.file_x_min_dunit to PyramidConfig.file_x_max_dunit

        Args:
            zoomout_level (int): Zoomout level to load.

        Returns:
            file_level_numpy (np.memmap): Loaded memmap numpy array of shape (sample_count, channel_count).
        """
        # compute file size and sample count for the zoomout level
        file_level_size_bytes = PyramidConfig.file_zoom0_size_bytes // (2**zoomout_level)
        file_level_sample_count = file_level_size_bytes // PyramidConfig.sample_size_bytes

        # TMP: CRAP: TO REMOVE:
        # file_level_sample_count = 2**zoomout_level

        # load and memmap the file
        file_path = AssetDownloader.download_data(f"textures/pyramid/res_{zoomout_level:02}.bin")
        file_level_numpy = np.memmap(file_path, shape=(file_level_sample_count, PyramidConfig.channel_count), dtype=np.float16, mode="r")

        # logger.debug(f"Loading memmap from: {file_path}")

        # return
        return file_level_numpy

    @staticmethod
    def texture_load(zoomout_level: int, image_x_min_dunit: float, image_x_max_dunit: float) -> Texture:
        """Load texture for given zoomout level.

        Args:
            zoomout_level (int): Zoomout level to load texture for.
            axes_display (AxesDisplay): AxesDisplay containing the image.
            image_x_min_dunit (float): Minimum x data unit of the image extent.
            image_x_max_dunit (float): Maximum x data unit of the image extent.

        Returns:
            texture (Texture): Loaded texture.
        """
        # Sanity check
        assert (
            image_x_min_dunit >= PyramidConfig.file_x_min_dunit
        ), f"image_x_min_dunit {image_x_min_dunit} is less than file_x_min_dunit {PyramidConfig.file_x_min_dunit}"
        assert (
            image_x_max_dunit <= PyramidConfig.file_x_max_dunit
        ), f"image_x_max_dunit {image_x_max_dunit} is greater than file_x_max_dunit {PyramidConfig.file_x_max_dunit}"

        # load the file level data
        file_level_numpy = PyramidTextureHelper.file_level_memmap(zoomout_level)

        file_sample_per_dunit = file_level_numpy.shape[0] / (PyramidConfig.file_x_max_dunit - PyramidConfig.file_x_min_dunit)

        file_sample_index_min = int((image_x_min_dunit - PyramidConfig.file_x_min_dunit) * file_sample_per_dunit)
        file_sample_index_max = int((image_x_max_dunit - PyramidConfig.file_x_min_dunit) * file_sample_per_dunit)

        logger.debug(
            f"texture_load - zoomout_level: {zoomout_level}, image_x_min_dunit: {image_x_min_dunit:.3f}, image_x_max_dunit: {image_x_max_dunit:.3f}, file_sample_index_min: {file_sample_index_min}, file_sample_index_max: {file_sample_index_max}"
        )

        file_sliced_numpy = file_level_numpy[file_sample_index_min:file_sample_index_max, :]

        # scale file_level_numpy to [0, 255] uint8
        array_clipped_numpy = np.clip(file_sliced_numpy, PyramidConfig.value_min, PyramidConfig.value_max)
        array_normalized_numpy = (array_clipped_numpy - PyramidConfig.value_min) / (PyramidConfig.value_max - PyramidConfig.value_min)  # Normalize to [0, 1]
        array_scaled_numpy = (array_normalized_numpy * 255.0).astype(np.uint8)  # Scale to [0, 255] and convert to uint8

        # Load pyramid data from memmap file
        image_width = file_sliced_numpy.shape[0]
        image_height = PyramidConfig.channel_count

        # create texture from scaled data
        texture_numpy = np.zeros((image_height, image_width, 4), dtype=np.uint8)
        texture_numpy[:, :, 0] = array_scaled_numpy.T  # R
        texture_numpy[:, :, 1] = array_scaled_numpy.T  # G
        texture_numpy[:, :, 2] = array_scaled_numpy.T  # B
        texture_numpy[:, :, 3] = 255  # A

        # linearize the texture data, thus we can do a buffer out of it
        texture_numpy = texture_numpy.reshape((image_width * image_height, 4))

        # create buffer and texture
        texture_buffer = Bufferx.from_numpy(texture_numpy, BufferType.rgba8)
        texture = Texture(texture_buffer, image_width, image_height)

        # logger.debug(f"Loading image from: {file_path}")
        return texture

    @staticmethod
    def get_axes_pixel_per_dunit(axes_display: AxesDisplay) -> float:
        """Compute the number of pixels per data unit for the axes display.

        This is an approximation of the desired samples count per data unit in the texture.

        Args:
            axes_display (AxesDisplay): AxesDisplay containing the image.

        Returns:
            axes_pixel_per_dunit (float): Number of pixels per data unit.
        """
        # Get axes limits
        axes_x_min_dunit, axes_x_max_dunit, _, _ = axes_display.get_limits_dunit()

        # compute axes pixels per data unit - pixels per data unit ~= desired samples per data unit
        axes_inner_viewport = axes_display.get_inner_viewport()
        viewport_width_pixels = axes_inner_viewport.get_width()
        axes_pixel_per_dunit = viewport_width_pixels / (axes_x_max_dunit - axes_x_min_dunit)

        return axes_pixel_per_dunit

    @staticmethod
    def get_desired_zoomout_level(image_x_min_dunit: float, image_x_max_dunit: float) -> int:
        """Compute the zoomout level needed to fit the image extent in the maximum texture width.

        Args:
            image_x_min_dunit (float): Minimum x data unit of the image extent.
            image_x_max_dunit (float): Maximum x data unit of the image extent.

        Returns:
            zoomout_level (int): Zoomout level needed to fit the image extent in the maximum texture width.
        """
        image_x_range_dunit = image_x_max_dunit - image_x_min_dunit
        file_sample_per_dunit = PyramidConfig.file_zoom0_sample_count / (PyramidConfig.file_x_max_dunit - PyramidConfig.file_x_min_dunit)

        desired_zoomout_level = PyramidConfig.max_zoomout
        for zoomout_level in range(PyramidConfig.min_zoomout, PyramidConfig.max_zoomout + 1):
            level_sample_per_dunit = file_sample_per_dunit / (2**zoomout_level)
            texture_width_pixels = level_sample_per_dunit * image_x_range_dunit

            # logger.debug(
            #     "zoomout_level_for_max_texture_width:",
            #     f"zoomout_level={zoomout_level}",
            #     f"level_sample_per_dunit={level_sample_per_dunit:.3f}",
            #     f"texture_width_pixels={texture_width_pixels:.1f}",
            # )

            if texture_width_pixels <= PyramidConfig.texture_max_width_pixels:
                desired_zoomout_level = zoomout_level
                break

        # logger.debug(f"selected zoomout_level_for_max_texture_width: {desired_zoomout_level}")

        return desired_zoomout_level


# =============================================================================
# Helper for Pyramid Image
# =============================================================================
class PyramidImageHelper:
    @staticmethod
    def image_compute_limits_dunit(image: Image) -> typing.Tuple[float, float, float, float]:
        """Compute image limits in data units.

        Args:
            axes_display (AxesDisplay): AxesDisplay containing the image.
            image (Image): Image visual to compute limits for.

        Returns:
            Tuple of (x_min_dunit, x_max_dunit, y_min_dunit, y_max_dunit).
        """
        # Get image position
        position_buffer = TransBufUtils.to_buffer(image.get_position())
        position_numpy = Bufferx.to_numpy(position_buffer)

        # Get image extent
        image_extent = PyramidParams.image_extent_target_dunit
        image_x_min_dunit = float(position_numpy[0, 0]) + image_extent[0]
        image_x_max_dunit = float(position_numpy[0, 0]) + image_extent[1]
        image_y_min_dunit = float(position_numpy[0, 1]) + image_extent[2]
        image_y_max_dunit = float(position_numpy[0, 1]) + image_extent[3]

        # return limits
        logger.debug(f"Image limits in data units: image_x_min_dunit={image_x_min_dunit:.3f}, image_x_max_dunit={image_x_max_dunit:.3f}")
        return (image_x_min_dunit, image_x_max_dunit, image_y_min_dunit, image_y_max_dunit)

    @staticmethod
    def image_build(viewport: Viewport, axes_transform_numpy: np.ndarray) -> RenderItem:
        """Generate a image visual render item. Image is dummy.

        It creates a dummy image visual with a dummy texture at creation.
        The image visual will be updated later based on axes limits.

        Args:
            viewport (Viewport): Viewport to create the image visual in.
            axes_transform_numpy: Numpy array of the axes transform matrix.

        Returns:
            render_item (RenderItem): RenderItem containing the image visual.
        """
        # =============================================================================
        # Dummy texture at creation, will be updated later
        # =============================================================================

        texture_numpy = np.zeros((1, 1, 4), dtype=np.uint8)
        texture_buffer = Bufferx.from_numpy(texture_numpy.reshape((1, 4)), BufferType.rgba8)
        texture = Texture(data=texture_buffer, width=1, height=1)

        # =============================================================================
        # Create a image visual
        # =============================================================================

        # Define image position (4 vertices for a quad)
        position_x_dunit = -100.0  # Known to be invalid at creation, will be updated later
        position_numpy = np.array([[position_x_dunit, PyramidConfig.channel_count / 2, 0.0]], dtype=np.float32)
        position_buffer = Bufferx.from_numpy(position_numpy, BufferType.vec3)

        # image extent in data units - known to be invalid at creation, will be updated later
        image_extent_dunit = (-0.1, +0.1, -0.1, +0.1)

        # Create the Image visual and add it to the viewport
        image = Image(texture, position_buffer, image_extent_dunit, ImageInterpolation.NEAREST)

        # =============================================================================
        # Compute the visual rendering matrixes
        # =============================================================================

        # Create model matrix to transform points into axes data space
        model_matrix_numpy = np.eye(4, dtype=np.float32)
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # Create a camera (identity for 2D rendering)
        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        # =============================================================================
        # Create the RenderItem
        # =============================================================================

        # Create the RenderItem
        render_item = RenderItem(viewport, image, model_matrix, camera)

        # Return the render item
        return render_item

    @staticmethod
    def image_should_be_updated(axes_display: AxesDisplay, image_visual: Image) -> bool:
        """Determine if the image visual should be updated based on axes limits.

        Args:
            axes_display (AxesDisplay): AxesDisplay containing the image.
            image_visual (Image): Image visual to check.

        Returns:
            should_update (bool): True if the image should be updated, False otherwise.
        """
        should_update: bool = False
        # Get axes limits
        axes_x_min_dunit, axes_x_max_dunit, _, _ = axes_display.get_limits_dunit()
        image_x_min_dunit, image_x_max_dunit, _, _ = PyramidImageHelper.image_compute_limits_dunit(image_visual)

        PyramidTextureHelper.get_desired_zoomout_level(
            image_x_min_dunit=image_x_min_dunit,
            image_x_max_dunit=image_x_max_dunit,
        )

        # logger.debug(
        #     f"image_x_min_dunit: {image_x_min_dunit:.2f}, image_x_max_dunit: {image_x_max_dunit:.2f}, axes_x_min_dunit: {axes_x_min_dunit:.2f}, axes_x_max_dunit: {axes_x_max_dunit:.2f}"
        # )

        # =============================================================================
        # Handle if we must update due to panning
        # =============================================================================

        # if image_x_min_dunit is greater than axes_x_min_dunit and image_x_min_dunit is not at the file limit, update the image
        if image_x_min_dunit > axes_x_min_dunit and image_x_min_dunit != PyramidConfig.file_x_min_dunit:
            should_update = True
            logger.debug(
                f"update due to panning left - image_x_min_dunit: {image_x_min_dunit:.3f}, axes_x_min_dunit: {axes_x_min_dunit:.3f}, file_x_min_dunit: {PyramidConfig.file_x_min_dunit:.3f}"
            )

        # logger.debug(f"image_x_min_dunit: {image_x_min_dunit:.4f}, axes_x_min_dunit: {axes_x_min_dunit:.4f}")
        # return False

        # if image_x_max_dunit is less than axes_x_max_dunit and image_x_max_dunit is not at the file limit, update the image
        if image_x_max_dunit < axes_x_max_dunit and image_x_max_dunit != PyramidConfig.file_x_max_dunit:
            should_update = True
            logger.debug(
                f"update due to panning right - image_x_max_dunit: {image_x_max_dunit:.3f}, axes_x_max_dunit: {axes_x_max_dunit:.3f}, file_x_max_dunit: {PyramidConfig.file_x_max_dunit:.3f}"
            )

        # =============================================================================
        # Handle if we must update due to zooming
        # =============================================================================

        # TODO update based on zoomout level
        # desired_zoomout_level = PyramidTextureHelper.get_desired_zoomout_level_BAD(axes_display, image_x_min_dunit, image_x_max_dunit)
        desired_zoomout_level = PyramidTextureHelper.get_desired_zoomout_level(
            image_x_min_dunit=image_x_min_dunit,
            image_x_max_dunit=image_x_max_dunit,
        )
        logger.debug(f"image_should_be_updated: desired_zoomout_level: {desired_zoomout_level}")
        if desired_zoomout_level != PyramidParams.current_zoomout_level:
            should_update = True
            logger.debug(
                f"update due to zooming - desired_zoomout_level: {desired_zoomout_level}, current_zoomout_level: {PyramidParams.current_zoomout_level}"
            )

        # =============================================================================
        # No updated needed
        # =============================================================================

        return should_update

    @staticmethod
    def image_update(axes_display: AxesDisplay, image: Image) -> None:
        """Update the image visual based on axes limits.

        It may change the position/extent/texture of the image visual.

        Args:
            axes_display (AxesDisplay): AxesDisplay containing the image.
            image (Image): Image visual to update.
        """
        # get axes limits
        axes_x_min_dunit, axes_x_max_dunit, _, _ = axes_display.get_limits_dunit()
        axes_x_range_dunit = axes_x_max_dunit - axes_x_min_dunit

        # compute new image image_x_min_dunit
        if axes_x_min_dunit - axes_x_range_dunit * PyramidConfig.texture_margin_percent > PyramidConfig.file_x_min_dunit:
            image_x_min_dunit = axes_x_min_dunit - axes_x_range_dunit * PyramidConfig.texture_margin_percent
        else:
            image_x_min_dunit = PyramidConfig.file_x_min_dunit

        # compute new image image_x_max_dunit
        if axes_x_max_dunit + axes_x_range_dunit * PyramidConfig.texture_margin_percent < PyramidConfig.file_x_max_dunit:
            image_x_max_dunit = axes_x_max_dunit + axes_x_range_dunit * PyramidConfig.texture_margin_percent
        else:
            image_x_max_dunit = PyramidConfig.file_x_max_dunit

        # logger.debug(f"Updating image to x=({image_x_min_dunit}, {image_x_max_dunit})")

        # compute new image position - center of the image extent
        image_position_x_dunit = (image_x_min_dunit + image_x_max_dunit) / 2.0
        position_numpy = np.array([[image_position_x_dunit, +PyramidConfig.channel_count / 2, 0.0]], dtype=np.float32)
        position_buffer = Bufferx.from_numpy(position_numpy, BufferType.vec3)

        # =============================================================================
        # Compute new image position/extent/texture
        # =============================================================================

        # Compute new image extent target
        PyramidParams.image_extent_target_dunit = (
            image_x_min_dunit - image_position_x_dunit,
            image_x_max_dunit - image_position_x_dunit,
            -PyramidConfig.channel_count / 2,
            +PyramidConfig.channel_count / 2,
        )

        # compute new zoomout level based on axes range
        # TODO
        texture_zoomout_level = PyramidTextureHelper.get_desired_zoomout_level(
            image_x_min_dunit=image_x_min_dunit,
            image_x_max_dunit=image_x_max_dunit,
        )
        # texture_zoomout_level = PyramidConfig.max_zoomout
        texture = PyramidTextureHelper.texture_load(texture_zoomout_level, image_x_min_dunit, image_x_max_dunit)

        # =============================================================================
        # Actually update position, extent, texture
        # =============================================================================

        # Update image visual position
        image.set_position(position_buffer)

        # Update image visual extent
        image.set_image_extent(PyramidParams.image_extent_target_dunit)

        # update current zoomout level
        PyramidParams.current_zoomout_level = texture_zoomout_level

        # Update image visual texture
        image.set_texture(texture)


# =============================================================================
#
# ========================================================== ===================
def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # =============================================================================
    # Create canvas+renderer+animator
    # =============================================================================

    # Create a canvas
    canvas = Canvas(width=600, height=600, dpi=127)
    # Create renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    # Create animator
    animator = ExampleHelper.create_animator(renderer_base)

    # =============================================================================
    # Create AxesDisplay
    # =============================================================================

    # Create a inner viewport for the axes display
    viewport_margin_x = int(canvas.get_width() * 0.1)
    viewport_margin_y = int(canvas.get_height() * 0.1)
    viewport_position_x = viewport_margin_x
    viewport_position_y = viewport_margin_y
    viewport_width = int(canvas.get_width() - 2.0 * viewport_margin_x)
    viewport_height = int(canvas.get_height() - 2.0 * viewport_margin_y)
    inner_viewport = Viewport(viewport_position_x, viewport_position_y, viewport_width, viewport_height)

    # Create an AxesDisplay for the inner viewport
    axes_display = AxesDisplay(canvas, inner_viewport)

    # Set initial limits in data units - will be update by the pan/zoom handler
    # axes_display.set_limits_dunit(-0.2, 0.2, 0.0, PyramidConfig.channel_count)
    axes_display.set_limits_dunit(0, 0.5, 0.0, PyramidConfig.channel_count)

    # =============================================================================
    # Create pan/zoom handler for the axes display
    # =============================================================================

    panzoom_enabled = True
    if panzoom_enabled:
        viewport_events = ExampleHelper.create_viewport_events(renderer_base, axes_display.get_inner_viewport())
        axes_pan_zoom = AxesPanZoom(viewport_events, base_scale=1.1, axes_display=axes_display)

        # Set pan/zoom limits in data units - only y limits are limited
        axes_pan_zoom.set_pan_limits_dunit(None, None, 0.0, PyramidConfig.channel_count)
        axes_pan_zoom.set_zoom_range_limits_dunit(
            x_min_range_dunit=None,
            x_max_range_dunit=None,
            y_min_range_dunit=PyramidConfig.channel_count,
            y_max_range_dunit=PyramidConfig.channel_count,
        )

    # =============================================================================
    # Create Pyramid Image visual
    # =============================================================================

    axes_transform_numpy = axes_display.get_transform_matrix_numpy()
    render_item_image = PyramidImageHelper.image_build(inner_viewport, axes_transform_numpy)

    # =============================================================================
    # Rendering function
    # =============================================================================

    def render_axes(force_update: bool = False) -> None:
        """Event handle to update points model matrices on axes limits change."""
        image_visual = typing.cast(Image, render_item_image.visual_base)

        # =============================================================================
        # Update image visual if needed by axes limits change
        # =============================================================================

        should_update: bool = False
        if force_update is False:
            should_update = PyramidImageHelper.image_should_be_updated(axes_display, image_visual)

        # logger.debug(f"render_axes: should_update: {should_update}, force_update: {force_update}")

        if should_update or force_update:
            PyramidImageHelper.image_update(axes_display, image_visual)

        # =============================================================================
        # Update model_matrix_numpy to adapt the pan/zoom of axes_display
        # =============================================================================

        # Get the axes transform matrix
        axes_transform_numpy = axes_display.get_transform_matrix_numpy()

        # Update model matrices to fit panzoom positions for all visuals
        model_matrix_numpy = np.eye(4, dtype=np.float32)
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        render_item_image.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # =============================================================================
        # Update image extent to keep it constant in data units when the axes limits change due to zoom
        # =============================================================================

        # Compute scale vector from axes limits
        x_min_dunit, x_max_dunit, y_min_dunit, y_max_dunit = axes_display.get_limits_dunit()
        extent_scale_vector = np.array([2.0 / (x_max_dunit - x_min_dunit), 2.0 / (y_max_dunit - y_min_dunit), 1.0])

        # apply scale vector to image extent
        image_extent_current_dunit = (
            PyramidParams.image_extent_target_dunit[0] * float(extent_scale_vector[0]),
            PyramidParams.image_extent_target_dunit[1] * float(extent_scale_vector[0]),
            PyramidParams.image_extent_target_dunit[2] * float(extent_scale_vector[1]),
            PyramidParams.image_extent_target_dunit[3] * float(extent_scale_vector[1]),
        )

        # update image visual extent
        image_visual = typing.cast(Image, render_item_image.visual_base)
        image_visual.set_image_extent(image_extent_current_dunit)

        # =============================================================================
        # Render items
        # =============================================================================

        # Collect all render items for the axes display
        render_items_axes = axes_display.get_render_items()

        # Combine all render items
        render_items_all = [render_item_image] + render_items_axes

        # Render all render items
        renderer_base.render(
            [render_item.viewport for render_item in render_items_all],
            [render_item.visual_base for render_item in render_items_all],
            [render_item.model_matrix for render_item in render_items_all],
            [render_item.camera for render_item in render_items_all],
        )

    # =============================================================================
    # Render everything once before starting the animator
    # - then rerender only on axes limits change
    # - limit rerender frequency to avoid blinking during interaction
    # =============================================================================

    # Initial render
    render_axes(force_update=True)

    if panzoom_enabled:
        # define variables to control rendering frequency
        needs_render: bool = False
        """Flag indicating if a render is needed."""
        last_render_time: float = 0.0
        """Time of the last render."""
        max_delta_time_between_renders: float = 1.0 / 60.0  # seconds
        """Maximum time between renders to limit rendering frequency."""

        # Define the event handler for new limits for the axes display
        def on_new_limits():
            """Event handler for new limits for the axes display.

            Actually the rendering actually happens in the animator callback, thus we can limit the rendering frequency there
            """
            nonlocal needs_render
            needs_render = True

        # Subscribe to new limits event - thus updating axes visuals on zoom/pan
        axes_display.new_limits_event.subscribe(on_new_limits)

        @animator.event_listener
        def animator_callback(delta_time: float) -> list[VisualBase]:
            nonlocal needs_render, last_render_time, max_delta_time_between_renders

            # render only if needed and enough time has passed since last render
            if needs_render and (time.time() - last_render_time) >= max_delta_time_between_renders:
                render_axes()
                needs_render = False
                last_render_time = time.time()

            changed_visuals: list[VisualBase] = []
            return changed_visuals

    # =============================================================================
    # Start the animation loop
    # =============================================================================

    # start the animation loop
    animator.start([], [], [], [])


if __name__ == "__main__":
    main()
