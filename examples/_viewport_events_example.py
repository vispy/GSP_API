# stdlib imports
import os
import typing

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_datoviz.renderer import DatovizRenderer
from gsp_network.renderer.network_renderer import NetworkRenderer
from gsp_extra.viewport_events.viewport_events_matplotlib import ViewportEventsMatplotlib
from gsp_extra.viewport_events.viewport_events_network import ViewportEventsNetwork
from gsp_extra.viewport_events.viewport_events_datoviz import ViewportEventsDatoviz
from gsp_extra.viewport_events.viewport_events_types import KeyEvent, MouseEvent
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from gsp.utils.unit_utils import UnitUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(512, 512, 72.0)

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
    # Create the renderer
    # =============================================================================

    renderer_name = ExampleHelper.get_renderer_name()
    # Create a renderer and render the scene
    renderer = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Setup the Viewport Events
    # =============================================================================
    def on_key_press(key_event: KeyEvent):
        print(f"Key press: {key_event}")

    def on_mouse_move(mouse_event: MouseEvent):
        print(f"Mouse move: {mouse_event}")

    if renderer_name == "matplotlib":
        assert isinstance(renderer, MatplotlibRenderer), "renderer must be MatplotlibRenderer"
        matplotlib_renderer = typing.cast(MatplotlibRenderer, renderer)
        viewport_events_1 = ViewportEventsMatplotlib(matplotlib_renderer, viewport_1)
        viewport_events_1.key_press_event.subscribe(on_key_press)
        viewport_events_1.mouse_move_event.subscribe(on_mouse_move)

        viewport_events_2 = ViewportEventsMatplotlib(matplotlib_renderer, viewport_2)
        viewport_events_2.key_press_event.subscribe(on_key_press)
        viewport_events_2.mouse_move_event.subscribe(on_mouse_move)
    elif renderer_name == "datoviz":
        assert isinstance(renderer, DatovizRenderer), "renderer must be DatovizRenderer"
        datoviz_renderer = typing.cast(DatovizRenderer, renderer)
        viewport_events_1 = ViewportEventsDatoviz(datoviz_renderer, viewport_1)
        viewport_events_1.key_press_event.subscribe(on_key_press)
        viewport_events_1.mouse_move_event.subscribe(on_mouse_move)

        viewport_events_2 = ViewportEventsDatoviz(datoviz_renderer, viewport_2)
        viewport_events_2.key_press_event.subscribe(on_key_press)
        viewport_events_2.mouse_move_event.subscribe(on_mouse_move)
    elif renderer_name == "network":
        assert isinstance(renderer, NetworkRenderer), "renderer must be NetworkRenderer"
        network_renderer = typing.cast(NetworkRenderer, renderer)
        viewport_events_1 = ViewportEventsNetwork(network_renderer, viewport_1)
        viewport_events_1.key_press_event.subscribe(on_key_press)
        viewport_events_1.mouse_move_event.subscribe(on_mouse_move)

        viewport_events_2 = ViewportEventsNetwork(network_renderer, viewport_2)
        viewport_events_2.key_press_event.subscribe(on_key_press)
        viewport_events_2.mouse_move_event.subscribe(on_mouse_move)
    else:
        raise NotImplementedError(f"Viewport events not implemented for renderer: {renderer_name}")

    # =============================================================================
    # Render and show the scene
    # =============================================================================
    renderer.render([viewport_1, viewport_2], [points, points], [model_matrix_1, model_matrix_2], [camera, camera])
    renderer.show()


if __name__ == "__main__":
    main()
