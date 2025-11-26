# stdlib imports
import os
from typing import Literal
import typing

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp_extra.animator.animator_datoviz import GspAnimatorDatoviz
from gsp_extra.viewport_events.viewport_events_datoviz import ViewportEventsDatoviz
from gsp_datoviz.renderer.datoviz_renderer import DatovizRenderer
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_network.renderer import NetworkRenderer
from gsp_extra.animator.animator_matplotlib import GspAnimatorMatplotlib
from gsp_extra.animator.animator_network import GspAnimatorNetwork

from gsp_extra.viewport_events.viewport_events_network import ViewportEventsNetwork
from gsp_extra.viewport_events.viewport_events_matplotlib import ViewportEventsMatplotlib

from gsp_extra.camera_controls.object_controls_awsd import ObjectControlAwsd
from gsp_extra.camera_controls.object_controls_trackball import ObjectControlsTrackball

from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils


def main():
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

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    # Create Viewport events
    # =============================================================================

    if renderer_name == "matplotlib":
        matplotlib_renderer = typing.cast(MatplotlibRenderer, renderer)
        viewport_events_1 = ViewportEventsMatplotlib(matplotlib_renderer, viewport_1)
        viewport_events_2 = ViewportEventsMatplotlib(matplotlib_renderer, viewport_2)
    elif renderer_name == "datoviz":
        datoviz_renderer = typing.cast(DatovizRenderer, renderer)
        viewport_events_1 = ViewportEventsDatoviz(datoviz_renderer, viewport_1)
        viewport_events_2 = ViewportEventsDatoviz(datoviz_renderer, viewport_2)
    elif renderer_name == "network":
        network_renderer = typing.cast(NetworkRenderer, renderer)
        viewport_events_1 = ViewportEventsNetwork(network_renderer, viewport_1)
        viewport_events_2 = ViewportEventsNetwork(network_renderer, viewport_2)
    else:
        raise ValueError(f"Unsupported renderer for this example: {renderer_name}")

    # =============================================================================
    #
    # =============================================================================

    # object_controls_1 = ObjectControlAwsd(model_matrix_1, viewport_events_1)
    object_controls_1 = ObjectControlsTrackball(model_matrix_1, viewport_events_1)
    # object_controls_2 = ObjectControlAwsd(model_matrix_2, viewport_events_2)
    object_controls_2 = ObjectControlsTrackball(model_matrix_2, viewport_events_2)

    # =============================================================================
    # Create animator
    # =============================================================================

    if renderer_name == "matplotlib":
        matplotlib_renderer = typing.cast(MatplotlibRenderer, renderer)
        animator = GspAnimatorMatplotlib(matplotlib_renderer)
    elif renderer_name == "datoviz":
        datoviz_renderer = typing.cast(DatovizRenderer, renderer)
        animator = GspAnimatorDatoviz(datoviz_renderer)
    elif renderer_name == "network":
        network_renderer = typing.cast(NetworkRenderer, renderer)
        animator = GspAnimatorNetwork(network_renderer)
    else:
        raise ValueError(f"Unsupported renderer for this example: {renderer_name}")

    animator.start([viewport_1, viewport_2], [points, points], [model_matrix_1, model_matrix_2], [camera, camera])


if __name__ == "__main__":
    main()
