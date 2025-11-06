# stdlib imports
import os

# pip imports
import numpy as np
import matplotlib.pyplot


# local imports
from gsp.core import Canvas, Viewport, VisualBase, Camera
from gsp.visuals import Pixels
from gsp.constants import Constants
from gsp.types import Buffer, BufferType
from gsp.transforms import TransformChain
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
from gsp_extra.transform_links import TransformLinkImmediate
from gsp.utils import GroupUtils


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 96.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 1024

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # define groups
    groups = [
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] > 0],
        [i for i in range(len(positions_numpy)) if positions_numpy[i][1] <= 0],
    ]
    group_count = GroupUtils.get_group_count(groups)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.red + Constants.green, 0, 2)
    colors_transform = TransformChain(buffer_count=group_count, buffer_type=BufferType.rgba8)
    colors_transform.add(TransformLinkImmediate(colors_buffer))

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, groups)
    model_matrix = Bufferx.mat4_identity()

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Create a camera
    view_matrix = Bufferx.mat4_identity()
    projection_matrix = Buffer(1, BufferType.mat4)
    projection_matrix.set_data(
        bytearray(
            np.array(
                [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ],
                dtype=np.float32,
            ).tobytes()
        ),
        0,
        1,
    )
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
