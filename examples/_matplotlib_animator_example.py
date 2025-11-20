# stdlib imports
import os

# pip imports
import numpy as np

# local imports
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


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # init the matplotlib renderer
    renderer = MatplotlibRenderer(canvas)

    # init the animator with the renderer
    animator_matplotlib = GspAnimatorMatplotlib(renderer)

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
    @animator_matplotlib.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        new_sizes = np.random.uniform(10, 100, (point_count,)).astype(np.float32)
        # copy inplace to avoid reallocations
        sizes_numpy[:] = new_sizes

        changed_visuals: list[VisualBase] = [points]
        return changed_visuals

    # start the animation loop
    animator_matplotlib.start(canvas, [viewport], [camera])


if __name__ == "__main__":
    main()
