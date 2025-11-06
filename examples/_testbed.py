# stdlib imports
import os
from typing import Sequence
import time

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
    matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])

    # =============================================================================
    #
    # =============================================================================

    # camera_world = np.eye(4, dtype=np.float32) @ glm.translate(np.array([0.0, 0.3, 0.0], dtype=np.float32))
    camera_world = np.eye(4, dtype=np.float32) @ glm.translate(np.array([0.0, 0.0, 2.0], dtype=np.float32))

    # projection_matrix_numpy = glm.perspective(45.0, canvas.get_width() / canvas.get_height(), 0.1, 100.0)
    projection_matrix_numpy = glm.ortho(-1.0, 1.0, -1.0, 1.0, 0.1, 100.0)
    projection_matrix_buffer = Bufferx.from_numpy(np.array([projection_matrix_numpy], dtype=np.float32), BufferType.mat4)
    camera.set_projection_matrix(projection_matrix_buffer)

    view_matrix_numpy = np.linalg.inv(camera_world)
    view_matrix_buffer = Bufferx.from_numpy(np.array([view_matrix_numpy]), BufferType.mat4)
    camera.set_view_matrix(view_matrix_buffer)

    # =============================================================================
    # matplotlib animation
    # =============================================================================
    # Create a matplotlib animation function
    def update(frame) -> Sequence[matplotlib.artist.Artist]:
        angle = time.time() / np.pi * 180 * 2.0
        scale_matrix = glm.scale(np.array([1.0, 1.0, 1.0], dtype=np.float32))

        rotation_order = "XYZ"
        model_angle_x = 0.0
        model_angle_y = 0.0
        model_angle_z = angle
        # compute the rotation matrix in the specified order
        rotation_matrix = np.eye(4, dtype=np.float32)
        for axis in rotation_order:
            if axis == "X":
                rotation_matrix = rotation_matrix @ glm.xrotate(model_angle_x)
            elif axis == "Y":
                rotation_matrix = rotation_matrix @ glm.yrotate(model_angle_y)
            elif axis == "Z":
                rotation_matrix = rotation_matrix @ glm.zrotate(model_angle_z)

        model_position_x = 0.0
        model_position_y = 0.0
        model_position_z = np.sin(time.time()) * 0.5 - 5.0
        translation_matrix = glm.translate(np.array([model_position_x, model_position_y, model_position_z], dtype=np.float32))

        model_matrix_numpy = scale_matrix @ rotation_matrix @ translation_matrix

        # model_matrix_numpy = glm.zrotate(model_angle_z)
        model_matrix.set_data(bytearray(np.array([model_matrix_numpy], dtype=np.float32).tobytes()), 0, 1)

        matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])

        modified_artists = list(matplotlibRenderer._artists.values())
        return modified_artists

    ani = matplotlib.animation.FuncAnimation(matplotlibRenderer._figure, update, frames=180, interval=50)

    # handle non-interactive mode for tests
    inTest = os.environ.get("GSP_INTERACTIVE_MODE") == "False"
    if inTest:
        return

    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
