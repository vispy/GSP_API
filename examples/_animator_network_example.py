# stdlib imports
import os
import typing
from typing import Literal

# pip imports
import numpy as np

# local imports
from examples.gsp_extra.gsp_animator.gsp_animator_network import GspAnimatorNetwork
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.types.visual_base import VisualBase
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.gsp_animator.gsp_animator_matplotlib import GspAnimatorMatplotlib
from gsp_network.renderer.network_renderer import NetworkRenderer


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

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

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================
    # Create a renderer and render the scene
    renderer_name = typing.cast(Literal["matplotlib", "datoviz"], os.environ.get("GSP_RENDERER", "matplotlib"))
    renderer = NetworkRenderer(canvas, server_base_url="http://localhost:5000", renderer_name=renderer_name)

    # init the animator with the renderer
    animator_network = GspAnimatorNetwork(renderer)

    @animator_network.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        sizes_numpy = np.random.rand(point_count).astype(np.float32) * 40.0 + 10.0
        sizes_buffer.set_data(bytearray(sizes_numpy.tobytes()), 0, sizes_buffer.get_count())

        changed_visuals: list[VisualBase] = [points]
        return changed_visuals

    # start the animation loop
    animator_network.start([viewport], [points], [model_matrix], [camera])


if __name__ == "__main__":
    main()
