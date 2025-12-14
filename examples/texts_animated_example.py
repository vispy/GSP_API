# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.types.visual_base import VisualBase
from gsp.constants import Constants
from gsp.core import Canvas, Viewport
from gsp.visuals import Texts
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=256, height=256, dpi=127.5)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================
    string_count = 2

    # Random positions - Create buffer from numpy array
    positions_numpy = np.array([[-0.5, 0.0, 0.0], [0.5, 0.0, 0.0]], dtype=np.float32)
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # strings content
    strings: list[str] = ["Hello", "World"]

    # colors - Create buffer and fill it with a constant
    colors_buffer = Buffer(string_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.red + Constants.Color.green, 0, string_count)

    font_size_numpy = np.array([12, 12], dtype=np.float32)
    font_size_buffer = Bufferx.from_numpy(font_size_numpy, BufferType.float32)

    anchors_numpy = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    anchors_buffer = Bufferx.from_numpy(anchors_numpy, BufferType.vec2)

    angles_numpy = np.array([+np.pi / 4, -np.pi / 4], dtype=np.float32)
    angles_buffer = Bufferx.from_numpy(angles_numpy, BufferType.float32)

    font_name = "Arial"

    # Create the Texts visual
    texts = Texts(positions_buffer, strings, colors_buffer, font_size_buffer, anchors_buffer, angles_buffer, font_name)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    model_matrix = Bufferx.mat4_identity()
    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    animator = ExampleHelper.create_animator(renderer_base)

    @animator.event_listener
    def animator_callback(delta_time: float) -> list[VisualBase]:
        angles_numpy[0] += np.pi / 2 * delta_time
        angles_numpy[0] = angles_numpy[0] % (2 * np.pi)
        angles_buffer.set_data(bytearray(angles_numpy.tobytes()), 0, string_count)
        # print("angles_numpy[0]:", angles_numpy[0])q

        font_size_numpy[0] = 12 + np.sin(angles_numpy[0]) * 4
        font_size_buffer.set_data(bytearray(font_size_numpy.tobytes()), 0, string_count)

        changed_visuals: list[VisualBase] = [texts]
        return changed_visuals

    animator.start([viewport], [texts], [model_matrix], [camera])


if __name__ == "__main__":
    main()
