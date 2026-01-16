"""Example demonstrating the AxesDisplay with pan and zoom functionality."""

# stdlib imports
import pathlib
import time
import typing

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport, viewport
from gsp.core.camera import Camera
from gsp.visuals import Image
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType, VisualBase
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.misc.render_item import RenderItem
from gsp_extra.misc.texture_utils import TextureUtils
from gsp_extra.mpl3d import glm
from vispy_2.axes.axes_display import AxesDisplay
from vispy_2.axes.axes_panzoom import AxesPanZoom


def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=400, height=400, dpi=127)

    # =============================================================================
    #
    # =============================================================================

    # Create a inner viewport
    # inner_viewport = Viewport(int(canvas.get_width() / 4), int(canvas.get_height() / 4), int(canvas.get_width() / 2), int(canvas.get_height() / 2))
    inner_viewport = Viewport(int(canvas.get_width() * 0.1), int(canvas.get_height() * 0.1), int(canvas.get_width() * 0.8), int(canvas.get_height() * 0.8))
    # inner_viewport = Viewport(int(canvas.get_width() / 3), int(canvas.get_height() / 8), int(canvas.get_width() / 3), int(canvas.get_height() / 2))

    # Create an AxesDisplay for the inner viewport
    axes_display = AxesDisplay(canvas, inner_viewport)
    # Set initial limits in data units
    axes_display.set_limits_dunit(-2.0, +2.0, -2.0, +2.0)

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    animator = ExampleHelper.create_animator(renderer_base)

    viewport_events = ExampleHelper.create_viewport_events(renderer_base, axes_display.get_inner_viewport())
    axes_pan_zoom = AxesPanZoom(viewport_events, base_scale=1.1, axes_display=axes_display)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_image(viewport: Viewport, axes_transform_numpy: np.ndarray, image_extent: typing.Tuple[float, float, float, float]) -> RenderItem:
        # =============================================================================
        # Read image and create texture
        # =============================================================================

        image_path = pathlib.Path(__file__).parent / "images" / "image.png"
        texture = TextureUtils.load_image(str(image_path))

        # =============================================================================
        # Create a image visual
        # =============================================================================

        # Define image position (4 vertices for a quad)
        positions_numpy = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Define image extent (left, right, bottom, top)
        image_extent = (-0.5, 0.5, -0.5, 0.5)

        # Create the Image visual and add it to the viewport
        image = Image(texture, positions_buffer, image_extent)

        # Create model matrix to transform points into axes data space
        model_matrix_numpy = np.eye(4, dtype=np.float32)
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # model_matrix = Bufferx.mat4_identity()

        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        render_item = RenderItem(viewport, image, model_matrix, camera)

        return render_item

    axes_transform_numpy = axes_display.get_transform_matrix_numpy()
    image_extent = (-1, 1, -1, 1)
    render_item_image = generate_visual_image(inner_viewport, axes_transform_numpy, image_extent)

    # =============================================================================
    #
    # =============================================================================

    def render_axes():
        """Event handle to update points model matrices on axes limits change."""
        # Get the axes transform matrix
        axes_transform_numpy = axes_display.get_transform_matrix_numpy()

        # Update model matrices for all visuals
        model_matrix_numpy = np.eye(4, dtype=np.float32)
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        render_item_image.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # Update image extent to keep it constant in data units
        if True:
            # Compute scale vector from axes limits
            x_min_dunit, x_max_dunit, y_min_dunit, y_max_dunit = axes_display.get_limits_dunit()
            scale_vector = np.array([2.0 / (x_max_dunit - x_min_dunit), 2.0 / (y_max_dunit - y_min_dunit), 1.0])
            # apply scale vector to image extent
            image_extent_current = (
                image_extent[0] * scale_vector[0],
                image_extent[1] * scale_vector[0],
                image_extent[2] * scale_vector[1],
                image_extent[3] * scale_vector[1],
            )
            # upadte image visual extent
            image_visual = typing.cast(Image, render_item_image.visual_base)
            image_visual.set_image_extent(image_extent_current)

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
    render_axes()

    # define variables to control rendering frequency
    needs_render: bool = False
    last_render_time: float = 0.0
    max_delta_time_between_renders: float = 1.0 / 60.0  # seconds

    # Define the event handler for new limits for the axes display
    def on_new_limits():
        """Event handle to update points model matrices on axes limits change."""
        nonlocal needs_render
        needs_render = True

    # Subscribe to new limits event - thus updating axes visuals on zoom/pan
    axes_display.new_limits_event.subscribe(on_new_limits)

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        # print(f"{text_cyan('Animator callback')}: delta_time={delta_time:.4f} sec")
        nonlocal needs_render, last_render_time, max_delta_time_between_renders

        if needs_render and (time.time() - last_render_time) >= max_delta_time_between_renders:
            render_axes()
            needs_render = False
            last_render_time = time.time()

        changed_visuals: list[VisualBase] = []
        return changed_visuals

    # =============================================================================
    #
    # =============================================================================

    # start the animation loop
    animator.start([], [], [], [])


if __name__ == "__main__":
    main()
