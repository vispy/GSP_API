"""Example demonstrating viewport events."""

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.types.viewport_events_types import CanvasResizeEvent, KeyEvent, MouseEvent
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.misc.colorama_utils import text_cyan, text_magenta


def main():
    """Example demonstrating viewport events."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(256, 512, 72.0)

    canvas_half_width = int(canvas.get_width() / 2.0)
    canvas_half_height = int(canvas.get_height() / 2.0)

    # Create a viewport and add it to the canvas
    viewport_1 = Viewport(0, 0, canvas.get_width(), canvas_half_height)
    viewport_2 = Viewport(0, canvas_half_height, canvas.get_width(), canvas_half_height)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 100

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Sizes - Create buffer and set data with numpy array
    sizes_numpy = np.array([40] * point_count, dtype=np.float32)
    sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    # all pixels red - Create buffer and fill it with a constant
    face_colors_red_buffer = Buffer(point_count, BufferType.rgba8)
    face_colors_red_buffer.set_data(Constants.Color.red * point_count, 0, point_count)

    # all pixels green - Create buffer and fill it with a constant
    face_colors_green_buffer = Buffer(point_count, BufferType.rgba8)
    face_colors_green_buffer.set_data(Constants.Color.green * point_count, 0, point_count)

    # Edge colors - Create buffer and fill it with a constant
    edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
    edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

    # Edge widths - Create buffer and fill it with a constant
    edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
    edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    # Create the Points visual and add it to the viewport
    points_1 = Points(positions_buffer, sizes_buffer, face_colors_red_buffer, edge_colors_buffer, edge_widths_buffer)
    points_2 = Points(positions_buffer, sizes_buffer, face_colors_green_buffer, edge_colors_buffer, edge_widths_buffer)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix_1 = Bufferx.mat4_identity()
    model_matrix_2 = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Create the renderer
    # =============================================================================

    renderer_name = ExampleHelper.get_renderer_name()
    # Create a renderer and render the scene
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Create ViewportEvents for each viewport according to the renderer type
    # =============================================================================

    viewport_events_1 = ExampleHelper.create_viewport_events(renderer_base, viewport_1)
    viewport_events_2 = ExampleHelper.create_viewport_events(renderer_base, viewport_2)

    # =============================================================================
    # Subscribe to events
    # =============================================================================

    # callback functions
    def on_key_press(key_event: KeyEvent):
        print(f"{text_cyan('Key press')}: {text_magenta(key_event.viewport_uuid)} {key_event}")

    def on_key_release(key_event: KeyEvent):
        print(f"{text_cyan('Key release')}: {text_magenta(key_event.viewport_uuid)} {key_event}")

    def on_button_press(mouse_event: MouseEvent):
        print(f"{text_cyan('Button press')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")

    def on_button_release(mouse_event: MouseEvent):
        print(f"{text_cyan('Button release')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")

    def on_mouse_move(mouse_event: MouseEvent):
        print(f"{text_cyan('Mouse move')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")

    def on_mouse_scroll(mouse_event: MouseEvent):
        print(f"{text_cyan('Mouse scroll')}: {text_magenta(mouse_event.viewport_uuid)} {mouse_event}")

    def on_canvas_resize(canvas_resize_event: CanvasResizeEvent):
        print(f"{text_cyan('Canvas resize')}: {text_magenta(canvas_resize_event.viewport_uuid)} {canvas_resize_event}")

    # Subscribe to events 1
    viewport_events_1.key_press_event.subscribe(on_key_press)
    viewport_events_1.key_release_event.subscribe(on_key_release)
    viewport_events_1.button_press_event.subscribe(on_button_press)
    viewport_events_1.button_release_event.subscribe(on_button_release)
    viewport_events_1.mouse_move_event.subscribe(on_mouse_move)
    viewport_events_1.mouse_scroll_event.subscribe(on_mouse_scroll)
    viewport_events_1.canvas_resize_event.subscribe(on_canvas_resize)

    # Subscribe to events 2
    viewport_events_2.key_press_event.subscribe(on_key_press)
    viewport_events_2.key_release_event.subscribe(on_key_release)
    viewport_events_2.button_press_event.subscribe(on_button_press)
    viewport_events_2.button_release_event.subscribe(on_button_release)
    viewport_events_2.mouse_move_event.subscribe(on_mouse_move)
    viewport_events_2.mouse_scroll_event.subscribe(on_mouse_scroll)
    viewport_events_2.canvas_resize_event.subscribe(on_canvas_resize)

    # =============================================================================
    # Render and show the scene
    # =============================================================================

    renderer_base.render([viewport_1, viewport_2], [points_1, points_2], [model_matrix_1, model_matrix_2], [camera, camera])
    renderer_base.show()


if __name__ == "__main__":
    main()
