# stdlib imports
import os

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_datoviz.renderer import DatovizRenderer
from gsp_extra.bufferx import Bufferx
from gsp.constants import Constants
from gsp.utils.group_utils import GroupUtils


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    pixel_count = 3000
    group_size = 1500
    group_count = GroupUtils.get_group_count(pixel_count, group_size)
    assert pixel_count % group_size == 0, "Pixels count must be divisible by group size"

    # Random positions - Create buffer from numpy array
    positions_numpy_1 = np.random.rand(pixel_count // 2, 3).astype(np.float32) * +1.0
    positions_numpy_2 = np.random.rand(pixel_count // 2, 3).astype(np.float32) * -1.0
    positions_numpy = np.vstack((positions_numpy_1, positions_numpy_2))
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.red + Constants.Color.green, 0, 2)

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, group_size)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Buffer(1, BufferType.mat4)
    projection_matrix.set_data(bytearray(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32).tobytes()), 0, 1)
    camera = Camera(view_matrix, projection_matrix)

    # Create a renderer and render the scene
    datovizRenderer = DatovizRenderer(canvas)
    datovizRenderer.render([viewport], [pixels], [model_matrix], [camera])

    # handle non-interactive mode for tests
    inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
    if inTest:
        return

    # run the datoviz app to show the window
    datovizRenderer.dvz_app.run()


if __name__ == "__main__":
    main()
