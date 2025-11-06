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
from gsp.core import Canvas, Viewport, VisualBase
from gsp.visuals import Points
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
from gsp_extra.object3d import Object3D


def main():
    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())
    # canvas_half_width = canvas.get_width() // 2
    # viewport_1 = Viewport(0, 0, canvas.get_width() // 2, canvas.get_height() // 2)
    # viewport_2 = Viewport(canvas.get_width() // 2, canvas.get_height() // 2, canvas.get_width() // 2, canvas.get_height() // 2)

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
    # matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])

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

    # object3d_scene.render(matplotlibRenderer, viewport, object3d_scene, camera)

    # =============================================================================
    #
    # =============================================================================

    # camera_world = np.eye(4, dtype=np.float32) @ glm.translate(np.array([0.0, 0.0, 2.0], dtype=np.float32))

    # # projection_matrix_numpy = glm.perspective(45.0, canvas.get_width() / canvas.get_height(), 0.1, 100.0)
    # projection_matrix_numpy = glm.ortho(-1.0, 1.0, -1.0, 1.0, 0.1, 100.0)
    # projection_matrix_buffer = Bufferx.from_numpy(np.array([projection_matrix_numpy], dtype=np.float32), BufferType.mat4)
    # camera.set_projection_matrix(projection_matrix_buffer)

    # view_matrix_numpy = np.linalg.inv(camera_world)
    # view_matrix_buffer = Bufferx.from_numpy(np.array([view_matrix_numpy]), BufferType.mat4)
    # camera.set_view_matrix(view_matrix_buffer)

    # =============================================================================
    # matplotlib animation
    # =============================================================================

    # handle non-interactive mode for tests
    inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
    if inTest:
        return

    def update(frame) -> Sequence[matplotlib.artist.Artist]:

        # Rotate parent object
        object3d_pixel.euler[2] = -time.time() % (2.0 * np.pi)
        # object3d_pixel.scale[:] = 0.8 + 0.5 * np.sin(time.time())
        # object3d_pixel.position[0] = 0.8 * np.cos(time.time() * 3.0)

        # Change camera position
        # camera_radius = 0.8
        # object3d_camera.position[0] = camera_radius * np.cos(time.time())
        # object3d_camera.position[1] = camera_radius * np.sin(time.time())

        object3d_scene.render(matplotlibRenderer, viewport, object3d_scene, camera)

        modified_artists = list(matplotlibRenderer._artists.values())
        return modified_artists

    funcAnimation = matplotlib.animation.FuncAnimation(matplotlibRenderer._figure, update, frames=180, interval=50)

    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
