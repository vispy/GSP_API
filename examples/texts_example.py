# stdlib imports
import os
import pathlib
from typing import Literal
import typing

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
from gsp.visuals import Segments
from gsp.types import CapStyle
from gsp.utils.unit_utils import UnitUtils


def main():
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=512, height=256, dpi=127.5)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    def index_to_position_x(position_index: int, string_count: int) -> float:
        position_inc = 2.0 / (string_count + 1)
        return -1 + (position_index + 1) * position_inc

    def create_visual_texts(vertical_alignment: Literal["top", "center", "bottom"]) -> Texts:
        string_count = 6

        # set position_y based on vertical_alignment
        if vertical_alignment == "top":
            position_y = 0.5
        elif vertical_alignment == "center":
            position_y = 0.0
        elif vertical_alignment == "bottom":
            position_y = -0.5
        else:
            raise ValueError(f"invalid vertical_alignment: {vertical_alignment}")

        # Random positions - Create buffer from numpy array
        positions_numpy = np.array(
            [[index_to_position_x(i, string_count), position_y, 0.0] for i in range(string_count)],
            dtype=np.float32,
        )
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # strings content
        strings: list[str] = ["Hello", "Hello", "Foo", "Foo", "Bar", "Bar"]

        # colors - Create buffer and fill it with a constant
        colors_buffer = Buffer(string_count, BufferType.rgba8)
        colors_buffer.set_data(
            Constants.Color.red + Constants.Color.red + Constants.Color.blue + Constants.Color.blue + Constants.Color.cyan + Constants.Color.cyan,
            0,
            string_count,
        )

        font_size_1 = 10
        font_size_2 = 15
        font_size_numpy = np.array([font_size_1, font_size_2, font_size_1, font_size_2, font_size_1, font_size_2], dtype=np.float32)
        font_size_buffer = Bufferx.from_numpy(font_size_numpy, BufferType.float32)

        if vertical_alignment == "top":
            anchors_numpy = np.array([[+1.0, -1.0], [+1.0, -1.0], [0.0, -1.0], [0.0, -1.0], [-1.0, -1.0], [-1.0, -1.0]], dtype=np.float32)
        elif vertical_alignment == "center":
            anchors_numpy = np.array([[+1.0, +0.0], [+1.0, +0.0], [0.0, +0.0], [0.0, +0.0], [-1.0, +0.0], [-1.0, +0.0]], dtype=np.float32)
        elif vertical_alignment == "bottom":
            anchors_numpy = np.array([[+1.0, +1.0], [+1.0, +1.0], [0.0, +1.0], [0.0, +1.0], [-1.0, +1.0], [-1.0, +1.0]], dtype=np.float32)
        else:
            raise ValueError(f"invalid vertical_alignment: {vertical_alignment}")
        anchors_buffer = Bufferx.from_numpy(anchors_numpy, BufferType.vec2)

        angle_1 = -np.pi / 6
        angle_2 = +np.pi / 6
        if vertical_alignment == "top":
            angles_numpy = np.array([angle_1, angle_2, 0.0, 0.0, angle_2, angle_1], dtype=np.float32)
        elif vertical_alignment == "center":
            angles_numpy = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        elif vertical_alignment == "bottom":
            angles_numpy = np.array([angle_2, angle_1, 0.0, 0.0, angle_1, angle_2], dtype=np.float32)
        else:
            raise ValueError(f"invalid vertical_alignment: {vertical_alignment}")
        # angles_numpy = np.array([+np.pi / 4, -np.pi / 4, 0.0], dtype=np.float32)
        angles_buffer = Bufferx.from_numpy(angles_numpy, BufferType.float32)

        font_name = "Arial"

        # Create the Texts visual
        texts = Texts(positions_buffer, strings, colors_buffer, font_size_buffer, anchors_buffer, angles_buffer, font_name)

        return texts

    def create_visual_segments_vertical() -> VisualBase:
        segments_count = 6

        positions_numpy = np.array(
            [
                [index_to_position_x(0, segments_count), +1.0, 0.0],
                [index_to_position_x(0, segments_count), -1.0, 0.0],
                [index_to_position_x(1, segments_count), +1.0, 0.0],
                [index_to_position_x(1, segments_count), -1.0, 0.0],
                [index_to_position_x(2, segments_count), +1.0, 0.0],
                [index_to_position_x(2, segments_count), -1.0, 0.0],
                [index_to_position_x(3, segments_count), +1.0, 0.0],
                [index_to_position_x(3, segments_count), -1.0, 0.0],
                [index_to_position_x(4, segments_count), +1.0, 0.0],
                [index_to_position_x(4, segments_count), -1.0, 0.0],
                [index_to_position_x(5, segments_count), +1.0, 0.0],
                [index_to_position_x(5, segments_count), -1.0, 0.0],
            ],
            dtype=np.float32,
        )
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        line_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * segments_count, dtype=np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

        colors_buffer = Buffer(segments_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.light_gray * segments_count, 0, segments_count)

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.BUTT, colors_buffer)
        return segments

    def create_visual_segments_horizontal() -> VisualBase:
        segments_count = 3

        positions_numpy = np.array(
            [
                [-1.0, -0.5, 0.0],
                [+1.0, -0.5, 0.0],
                [-1.0, +0.0, 0.0],
                [+1.0, +0.0, 0.0],
                [-1.0, +0.5, 0.0],
                [+1.0, +0.5, 0.0],
            ],
            dtype=np.float32,
        )
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        line_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * segments_count, dtype=np.float32)
        line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

        colors_buffer = Buffer(segments_count, BufferType.rgba8)
        colors_buffer.set_data(Constants.Color.light_gray * segments_count, 0, segments_count)

        segments = Segments(positions_buffer, line_widths_buffer, CapStyle.BUTT, colors_buffer)
        return segments

    texts_top = create_visual_texts("top")
    texts_center = create_visual_texts("center")
    texts_bottom = create_visual_texts("bottom")

    segments_vertical = create_visual_segments_vertical()
    segments_horizontal = create_visual_segments_horizontal()

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
    renderer_base.render(
        [viewport, viewport, viewport, viewport, viewport],
        [texts_top, texts_center, texts_bottom, segments_vertical, segments_horizontal],
        [model_matrix, model_matrix, model_matrix, model_matrix, model_matrix],
        [camera, camera, camera, camera, camera],
    )
    renderer_base.show()


if __name__ == "__main__":
    main()
