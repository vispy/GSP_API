# stdlib imports
from typing import Sequence
import time
import os

# pip imports
import numpy as np
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.artist

# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
from gsp_extra.object3d import Object3D
from gsp.utils.group_utils import GroupUtils


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    point_count = 200
    group_size = 200
    group_count = GroupUtils.get_group_count(vertex_count=point_count, groups=group_size)

    # Random positions - Create buffer from numpy array
    positions_numpy = np.zeros((point_count, 3), dtype=np.float32)

    # Make a line from -0.9 to 0.9 in x
    positions_numpy[:, 0] = np.linspace(-0.5, 0.5, point_count)
    positions_numpy[:, 1] = 0.0
    positions_numpy[:, 2] = -5.0

    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(bytearray([255, 0, 0, 255]) * colors_buffer.get_count(), 0, 1)

    # Create the Pixels visual and add it to the viewport
    pixels = Pixels(positions_buffer, colors_buffer, groups=group_size)

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
    # Build the scene
    # =============================================================================

    object3d_scene = Object3D("Main Scene")

    object3d_pixel = Object3D("Pixels Object3D")
    object3d_pixel.attach_visual(pixels)
    object3d_scene.add(object3d_pixel)

    object3d_camera = Object3D("Camera Object3D")
    object3d_camera.attach_camera(camera)
    object3d_scene.add(object3d_camera)

    # =============================================================================
    # matplotlib animation
    # =============================================================================

    # handle non-interactive mode for tests
    in_test = os.environ.get("GSP_TEST") == "True"
    if in_test:
        return

    def update(frame) -> Sequence[matplotlib.artist.Artist]:

        # Rotate parent object
        object3d_pixel.euler[2] = -time.time() % (2.0 * np.pi)

        object3d_scene.render_cooked(matplotlibRenderer, viewport, object3d_scene, camera)

        modified_artists = list(matplotlibRenderer._artists.values())
        return modified_artists

    funcAnimation = matplotlib.animation.FuncAnimation(matplotlibRenderer._figure, update, frames=180, interval=50)

    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
