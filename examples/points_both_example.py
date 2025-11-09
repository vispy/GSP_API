# stdlib imports
import os

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.constants import Constants
from gsp.core import Canvas, Viewport, VisualBase
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
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 100
    group_size = point_count
    group_count = GroupUtils.get_group_count(point_count, groups=group_size)

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Sizes - Create buffer and set data with numpy array
    sizes_numpy = np.array([40] * group_count, dtype=np.float32)
    sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    # all pixels red - Create buffer and fill it with a constant
    face_colors_buffer = Buffer(group_count, BufferType.rgba8)
    face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)

    # Edge colors - Create buffer and fill it with a constant
    edge_colors_buffer = Buffer(group_count, BufferType.rgba8)
    edge_colors_buffer.set_data(Constants.blue * group_count, 0, group_count)

    # Edge widths - Create buffer and fill it with a constant
    edge_widths_numpy = np.array([UnitUtils.pixel_to_point(0.5, canvas.get_dpi())] * group_count, dtype=np.float32)
    edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    # Create the Points visual and add it to the viewport
    points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer, groups=group_size)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Buffer(1, BufferType.mat4)
    projection_matrix.set_data(bytearray(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32).tobytes()), 0, 1)
    camera = Camera(view_matrix, projection_matrix)

    # =============================================================================
    # Render
    # =============================================================================

    # Create a renderer and render the scene
    renderer = MatplotlibRenderer(canvas) if os.environ.get("GSP_RENDERER", "matplotlib") == "matplotlib" else DatovizRenderer(canvas)
    renderer.render([viewport], [points], [model_matrix], [camera])
    renderer.show()


if __name__ == "__main__":
    main()
