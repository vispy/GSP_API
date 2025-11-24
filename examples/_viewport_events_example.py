# stdlib imports
import os

# pip imports
import numpy as np

# local imports
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

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

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix_1 = Bufferx.mat4_identity()
    model_matrix_2 = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create a renderer and render the scene
    renderer = MatplotlibRenderer(canvas)
    renderer.render([viewport_1, viewport_2], [points, points], [model_matrix_1, model_matrix_2], [camera, camera])

    from gsp_extra.viewport_events.viewport_events_matplotlib import ViewportEventsMatplotlib
    from gsp_extra.viewport_events.viewport_events_types import KeyboardEvent, MouseEvent

    viewport_events = ViewportEventsMatplotlib(mpl_figure=renderer.get_mpl_figure())

    def on_key_press(keyboard_event: KeyboardEvent):
        print(f"Key press: {keyboard_event}")

    def on_mouse_move(mouse_event: MouseEvent):
        print(f"Mouse move: {mouse_event}")

    viewport_events.key_press_event.subscribe(on_key_press)
    viewport_events.mouse_move_event.subscribe(on_mouse_move)

    renderer.show()


if __name__ == "__main__":
    main()
