# stdlib imports
import os

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
import gsp_extra.glm as glm


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 10
    group_count = 1

    # Random positions - Create buffer from numpy array
    positions_numpy = np.zeros((point_count, 3), dtype=np.float32)

    # Make a line from -0.9 to 0.9 in x
    positions_numpy[:, 0] = np.linspace(-0.5, 0.5, point_count)
    positions_numpy[:, 1] = 0.0
    positions_numpy[:, 2] = -5.0

    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Sizes - Create buffer and set data with numpy array
    sizes_numpy = np.array([40] * group_count, dtype=np.float32)
    sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    # all pixels red - Create buffer and fill it with a constant
    face_colors_buffer = Buffer(group_count, BufferType.rgba8)
    face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * face_colors_buffer.get_count(), 0, 1)

    # Edge colors - Create buffer and fill it with a constant
    edge_colors_buffer = Buffer(group_count, BufferType.rgba8)
    edge_colors_buffer.set_data(bytearray(b"\x00\xff\x00\xff") * edge_colors_buffer.get_count(), 0, 1)

    # Edge widths - Create buffer and fill it with a constant
    edge_widths_buffer = Buffer(group_count, BufferType.float32)
    edge_widths_buffer.set_data(bytearray(np.array([0.5 * 72.0 / canvas.get_dpi()] * group_count, dtype=np.float32).tobytes()), 0, 1)

    # Create the Points visual and add it to the viewport
    pixels = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer, group_count)

    # model_matrix_numpy = np.eye(4, dtype=np.float32)
    model_matrix_numpy = glm.zrotate(20.0)
    model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Buffer(1, BufferType.mat4)
    projection_matrix.set_data(bytearray(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32).tobytes()), 0, 1)
    camera = Camera(view_matrix, projection_matrix)

    # Create a renderer and render the scene
    matplotlibRenderer = MatplotlibRenderer(canvas)
    matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])

    # handle non-interactive mode for tests
    inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
    if inTest:
        return

    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
