# pip imports
import os
import numpy as np
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.artist
import typing
from typing import Sequence
import time


# local imports
from gsp.core import Canvas, Viewport
from gsp.visuals import Pixels
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp_extra.bufferx import Bufferx
from gsp_extra.object3d import Object3D
import gsp_extra.mpl3d.glm as glm
from gsp.utils.group_utils import GroupUtils


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

    if False:
        positions_numpy = np.zeros((10, 3), dtype=np.float32)
        # Make a line from -0.9 to 0.9 in x
        positions_numpy[:, 0] = np.linspace(-0.5, 0.5, point_count)
        positions_numpy[:, 1] = 0.0
        positions_numpy[:, 2] = -5.0
    elif True:
        # Make a 3d cube of points - only the edges - 10 points per edge
        edge_points = []
        cube_size = 0.3
        points_per_edge = 200
        for x in [-cube_size, cube_size]:
            for y in [-cube_size, cube_size]:
                for z in np.linspace(-cube_size, cube_size, points_per_edge):
                    edge_points.append([x, y, z])
        for x in [-cube_size, cube_size]:
            for z in [-cube_size, cube_size]:
                for y in np.linspace(-cube_size, cube_size, points_per_edge):
                    edge_points.append([x, y, z])
        for y in [-cube_size, cube_size]:
            for z in [-cube_size, cube_size]:
                for x in np.linspace(-cube_size, cube_size, points_per_edge):
                    edge_points.append([x, y, z])
        positions_numpy = np.array(edge_points, dtype=np.float32)
    else:
        assert False, "Unknown position setup"

    point_count = positions_numpy.__len__()
    group_size = point_count
    group_count = GroupUtils.get_group_count(vertex_count=point_count, groups=group_size)

    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(group_count, BufferType.rgba8)
    colors_buffer.set_data(bytearray([255, 0, 0, 255]) * group_count, 0, group_count)

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

    object3d_scene.render_scene(matplotlibRenderer, viewport, object3d_scene, camera)

    # =============================================================================
    #
    # =============================================================================

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

    def update(frame) -> Sequence[matplotlib.artist.Artist]:

        # Rotate parent object
        object3d_pixel.euler[0] = -time.time() % (1.0 * np.pi)
        object3d_pixel.euler[1] = -time.time() % (2.0 * np.pi)
        object3d_pixel.euler[2] = -time.time() % (3.0 * np.pi)
        object3d_pixel.scale[:] = 0.8 + 0.5 * np.sin(time.time())

        object3d_scene.render_scene(matplotlibRenderer, viewport, object3d_scene, camera)

        modified_artists = list(matplotlibRenderer._artists.values())
        return modified_artists

    funcAnimation = matplotlib.animation.FuncAnimation(matplotlibRenderer._figure, update, frames=180, interval=50)

    # handle non-interactive mode for tests
    in_test = os.environ.get("GSP_TEST") == "True"
    if in_test:
        return

    matplotlib.pyplot.show()


if __name__ == "__main__":
    main()
