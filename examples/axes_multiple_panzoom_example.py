"""Example demonstrating the AxesDisplay with pan and zoom functionality with multiple axes."""

# stdlib imports
import time

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType, VisualBase
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.misc.render_item import RenderItem
from vispy_2.axes.axes_display import AxesDisplay
from vispy_2.axes.axes_panzoom import AxesPanZoom


def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=512, height=512, dpi=127)

    # =============================================================================
    #
    # =============================================================================

    viewport_1 = Viewport(int(canvas.get_width() * 0.10), int(canvas.get_height() * 0.1), int(canvas.get_width() * 0.35), int(canvas.get_height() * 0.8))
    viewport_2 = Viewport(int(canvas.get_width() * 0.60), int(canvas.get_height() * 0.1), int(canvas.get_width() * 0.35), int(canvas.get_height() * 0.8))

    axes_display_1 = AxesDisplay(canvas, viewport_1)
    axes_display_2 = AxesDisplay(canvas, viewport_2)
    axes_display_1.set_limits_dunit(-2.0, +2.0, -2.0, +2.0)
    axes_display_2.set_limits_dunit(-2.0, +2.0, -2.0, +2.0)

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    animator = ExampleHelper.create_animator(renderer_base)

    viewport_events_1 = ExampleHelper.create_viewport_events(renderer_base, axes_display_1.get_inner_viewport())
    viewport_events_2 = ExampleHelper.create_viewport_events(renderer_base, axes_display_2.get_inner_viewport())
    axes_pan_zoom_1 = AxesPanZoom(viewport_events_1, base_scale=1.1, axes_display=axes_display_1)
    axes_pan_zoom_2 = AxesPanZoom(viewport_events_2, base_scale=1.1, axes_display=axes_display_2)

    # Set zoom range limits in data units
    axes_pan_zoom_1.set_zoom_range_limits_dunit(2.0, 10.0, 2.0, 10.0)
    # Set pan limits in data units
    axes_pan_zoom_1.set_pan_limits_dunit(-15.0, +15.0, -15.0, +15.0)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_points(point_count: int, viewport: Viewport, axes_transform_numpy: np.ndarray, y_offset: float) -> list[RenderItem]:
        # Generate a sinusoidal distribution of points
        sin_scale = 3.0
        x_values = np.linspace(-1.0, +1.0, point_count, dtype=np.float32)
        y_values = np.sin(x_values * np.pi * sin_scale).astype(np.float32) + y_offset
        z_values = np.zeros(point_count, dtype=np.float32)
        positions_numpy = np.vstack((x_values, y_values, z_values)).T.astype(np.float32)

        # positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([10] * point_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

        # Create model matrix to transform points into axes data space
        model_matrix_numpy = np.eye(4, dtype=np.float32)
        model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
        model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # model_matrix = Bufferx.mat4_identity()

        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        render_items: list[RenderItem] = []
        render_items.append(RenderItem(viewport, points, model_matrix, camera))
        return render_items

    axes_transform_numpy_1 = axes_display_1.get_transform_matrix_numpy()
    axes_transform_numpy_2 = axes_display_2.get_transform_matrix_numpy()
    render_items_points_1 = generate_visual_points(100, viewport_1, axes_transform_numpy_1, y_offset=0.0)
    render_items_points_2 = generate_visual_points(100, viewport_2, axes_transform_numpy_2, y_offset=0.3)

    # =============================================================================
    #
    # =============================================================================

    def render_axes():
        """Event handle to update points model matrices on axes limits change."""
        # Get the axes transform matrix
        axes_transform_numpy_1 = axes_display_1.get_transform_matrix_numpy()
        axes_transform_numpy_2 = axes_display_2.get_transform_matrix_numpy()

        render_items_all: list[RenderItem] = []

        for render_item in render_items_points_1:
            model_matrix_numpy_1 = np.eye(4, dtype=np.float32)
            model_matrix_numpy_1 = axes_transform_numpy_1 @ model_matrix_numpy_1
            render_item.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy_1]), BufferType.mat4)
        render_items_all.extend(render_items_points_1)

        for render_item in render_items_points_2:
            model_matrix_numpy_2 = np.eye(4, dtype=np.float32)
            model_matrix_numpy_2 = axes_transform_numpy_2 @ model_matrix_numpy_2
            render_item.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy_2]), BufferType.mat4)
        render_items_all.extend(render_items_points_2)

        render_items_axes_1 = axes_display_1.get_render_items()
        render_items_axes_2 = axes_display_2.get_render_items()
        render_items_all.extend(render_items_axes_1)
        render_items_all.extend(render_items_axes_2)

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
    axes_display_1.new_limits_event.subscribe(on_new_limits)
    axes_display_2.new_limits_event.subscribe(on_new_limits)

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
