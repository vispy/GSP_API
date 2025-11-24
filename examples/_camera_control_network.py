# stdlib imports
import os

# pip imports
import numpy as np

# local imports
from gsp_extra.animator.animator_network import GspAnimatorNetwork
from gsp_extra.animator.animator_matplotlib import GspAnimatorMatplotlib
from gsp_extra.window_events.window_event_matplotlib import WindowEventMatplotlib
from gsp_extra.window_events.window_event_types import KeyboardEvent, MouseEvent
from gsp_extra.camera_controls.object_controls_awsd import ObjectControlAwsd
from gsp_extra.camera_controls.object_controls_trackball import ObjectControlsTrackball

from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_network.renderer import NetworkRenderer
from gsp_extra.bufferx import Bufferx
from gsp.utils.unit_utils import UnitUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(512, 512, 72.0)

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

    # =============================================================================
    #
    # =============================================================================

    # Create a renderer and render the scene
    renderer = NetworkRenderer(canvas, server_base_url="http://localhost:5000", remote_renderer_name="datoviz")

    # start the animation loop
    animator = GspAnimatorNetwork(renderer)

    window_event = WindowEventMatplotlib(mpl_figure=animator.get_mpl_figure())
    object_controls = ObjectControlAwsd(model_matrix, window_event)
    # object_controls = ObjectControlsTrackball(model_matrix, window_event)

    animator.start([viewport], [points], [model_matrix], [camera])


if __name__ == "__main__":
    main()
