# stdlib imports
from typing import Sequence
import time
import os

# pip imports
import numpy as np
import matplotlib.pyplot
import matplotlib.artist


# local imports
from gsp.core import Canvas, Viewport, VisualBase
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
from gsp.constants import Constants
from gsp.utils.transbuf_utils import TransBufUtils


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
    group_count = 1
    assert pixel_count % group_count == 0, "Pixels count must be divisible by group count"

    # Random positions - Create buffer from numpy array
    positions_numpy = np.random.rand(pixel_count, 3).astype(np.float32) * 2.0 - 1
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.red + Constants.green, 0, 1)

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, group_count)
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
    matplotlibRenderer = MatplotlibRenderer(canvas)

    # =============================================================================
    #
    # =============================================================================

    # handle non-interactive mode for tests
    inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
    if inTest:
        return

    print("Switching to 1 groups")

    if True:
        colors_buffer = Buffer(1, BufferType.rgba8)
        colors_buffer.set_data(Constants.red, 0, 1)
        vertex_count = TransBufUtils.to_buffer(pixels.get_positions()).get_count()
        groups = [vertex_count]
        pixels.set_attributes(colors=colors_buffer, groups=groups)

        matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])
        # matplotlib.pyplot.show(block=True)

    print("Switching to 2 groups")

    if True:
        colors_buffer = Buffer(2, BufferType.rgba8)
        colors_buffer.set_data(Constants.red + Constants.green, 0, 2)
        groups = [
            [i for i in range(len(positions_numpy)) if positions_numpy[i][1] > 0],
            [i for i in range(len(positions_numpy)) if positions_numpy[i][1] <= 0],
        ]
        pixels.set_attributes(colors=colors_buffer, groups=groups)

        matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])
        matplotlib.pyplot.show(block=True)

    # =============================================================================
    # matplotlib animation
    # =============================================================================

    def update(frame) -> Sequence[matplotlib.artist.Artist]:
        group_config = int(time.time() % 2)
        print(f"group_config: {group_config}")
        if group_config == 0:
            colors_buffer = Buffer(1, BufferType.rgba8)
            colors_buffer.set_data(Constants.red, 0, 1)
            vertex_count = TransBufUtils.to_buffer(pixels.get_positions()).get_count()
            groups = [vertex_count]
            pixels.set_attributes(colors=colors_buffer, groups=groups)
        elif group_config == 1:
            colors_buffer = Buffer(2, BufferType.rgba8)
            colors_buffer.set_data(Constants.red + Constants.green, 0, 2)
            groups = [
                [i for i in range(len(positions_numpy)) if positions_numpy[i][1] > 0],
                [i for i in range(len(positions_numpy)) if positions_numpy[i][1] <= 0],
            ]
            pixels.set_attributes(colors=colors_buffer, groups=groups)
        else:
            assert False, "unreachable"

        matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])

        modified_artists = list(matplotlibRenderer._artists.values())
        return modified_artists

    # funcAnimation = matplotlib.animation.FuncAnimation(matplotlibRenderer._figure, update, frames=180, interval=2)

    # matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
