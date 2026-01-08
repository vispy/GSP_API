"""Example demonstrating viewport NDC metric conversions."""

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType
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
    canvas = Canvas(width=400, height=400, dpi=127)

    # =============================================================================
    #
    # =============================================================================

    # Create a inner viewport
    # inner_viewport = Viewport(int(canvas.get_width() / 4), int(canvas.get_height() / 4), int(canvas.get_width() / 2), int(canvas.get_height() / 2))
    inner_viewport = Viewport(int(canvas.get_width() * 0.1), int(canvas.get_height() * 0.1), int(canvas.get_width() * 0.8), int(canvas.get_height() * 0.8))
    # inner_viewport = Viewport(int(canvas.get_width() / 3), int(canvas.get_height() / 4), int(canvas.get_width() / 3), int(canvas.get_height() / 2))

    axes_display = AxesDisplay(canvas, inner_viewport)
    axes_display.set_limits_dunit(-2.0, +2.0, -2.0, +2.0)
    axes_render_items = axes_display.get_render_items()

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    viewport_events = ExampleHelper.create_viewport_events(renderer_base, axes_display.get_inner_viewport())
    axes_pan_zoom = AxesPanZoom(viewport_events, base_scale=1.1, axes_display=axes_display)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_points(point_count: int, viewport: Viewport, axes_transform_numpy: np.ndarray) -> list[RenderItem]:
        # Generate a sinusoidal distribution of points
        sin_scale = 3.0
        x_values = np.linspace(-1.0, +1.0, point_count, dtype=np.float32)
        y_values = np.sin(x_values * np.pi * sin_scale).astype(np.float32)
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

    axes_transform_numpy = axes_display.get_transform_matrix_numpy()
    render_items_points = generate_visual_points(100, inner_viewport, axes_transform_numpy)

    # =============================================================================
    #
    # =============================================================================

    render_items = render_items_points + axes_render_items
    # render_items = render_items_axes

    # =============================================================================
    #
    # =============================================================================
    def on_new_limits():
        """Event handle to update points model matrices on axes limits change."""
        # Get the axes transform matrix
        axes_transform_numpy = axes_display.get_transform_matrix_numpy()

        # Update model matrices for all visuals
        for render_item in render_items_points:
            model_matrix_numpy = np.eye(4, dtype=np.float32)
            model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
            render_item.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # Collect all render items for the axes display
        render_items_axes = axes_display.get_render_items()

        # Combine all render items
        render_items = render_items_points + render_items_axes

        # Render all render items
        renderer_base.render(
            [render_item.viewport for render_item in render_items],
            [render_item.visual_base for render_item in render_items],
            [render_item.model_matrix for render_item in render_items],
            [render_item.camera for render_item in render_items],
        )

    # Subscribe to new limits event - thus updating axes visuals on zoom/pan
    axes_display.new_limits_event.subscribe(on_new_limits)

    # Initial render
    on_new_limits()

    # =============================================================================
    #
    # =============================================================================
    # renderer_base.show()

    animator = ExampleHelper.create_animator(renderer_base)

    # @animator.event_listener
    # def animator_callback(delta_time: float) -> list[VisualBase]:
    #     # print(f"{text_cyan('Animator callback')}: delta_time={delta_time:.4f} sec")

    #     changed_visuals: list[VisualBase] = []
    #     return changed_visuals

    # start the animation loop
    animator.start(
        [],
        [],
        [],
        [],
        # [render_item.viewport for render_item in render_items],
        # [render_item.visual_base for render_item in render_items],
        # [render_item.model_matrix for render_item in render_items],
        # [render_item.camera for render_item in render_items],
    )


if __name__ == "__main__":
    main()
