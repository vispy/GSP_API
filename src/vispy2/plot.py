"""Unified scatter API to create Points, Pixels or Markers visuals."""

# stdlib imports
from typing import Optional, Union, Literal

# pip imports
import numpy as np

# local imports
from gsp.types import TransBuf, Buffer, BufferType
from gsp.constants import Constants
from gsp.visuals.points import Points
from gsp.visuals.paths import Paths
from gsp.types.cap_style import CapStyle
from gsp.types.join_style import JoinStyle
from gsp.types.visual_base import VisualBase
from gsp_extra.bufferx import Bufferx
from gsp_extra.misc.render_item import RenderItem


def _generate_markers(positions: TransBuf) -> list[VisualBase]:
    assert isinstance(positions, Buffer), "positions should be a Buffer at this point"
    position_count = positions.get_count()

    sizes_numpy = np.array([50] * position_count, dtype=np.float32)
    sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    face_colors = Buffer(position_count, BufferType.rgba8)
    face_colors.set_data(Constants.Color.red * position_count, 0, position_count)

    edge_colors = Buffer(position_count, BufferType.rgba8)
    edge_colors.set_data(Constants.Color.blue * position_count, 0, position_count)

    edge_widths_numpy = np.array([1.0] * position_count, dtype=np.float32)
    edge_widths = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    visual = Points(positions, sizes, face_colors, edge_colors, edge_widths)
    return [visual]


def _generate_paths(positions: TransBuf) -> list[VisualBase]:
    assert isinstance(positions, Buffer), "positions should be a Buffer at this point"
    position_count = positions.get_count()

    path_sizes_numpy = np.array([position_count], dtype=np.uint32)
    path_sizes_buffer = Bufferx.from_numpy(path_sizes_numpy, BufferType.uint32)

    # all pixels red - Create buffer and fill it with a constant
    colors_buffer = Buffer(position_count, BufferType.rgba8)
    colors_buffer.set_data(Constants.Color.blue * position_count, 0, position_count)

    line_widths_numpy = np.array([2.0] * position_count, dtype=np.float32).reshape(-1, 1)
    line_widths_buffer = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

    # Create the Pixels visual and add it to the viewport
    paths = Paths(positions, path_sizes_buffer, colors_buffer, line_widths_buffer, CapStyle.ROUND, JoinStyle.ROUND)
    return [paths]


def plot(
    x: TransBuf | np.ndarray,
    y: TransBuf | np.ndarray,
) -> list[VisualBase]:
    """Create a line visual connecting the given x and y coordinates."""
    # If positions is a numpy array, convert it to a Buffer
    if isinstance(x, np.ndarray):
        x = Bufferx.from_numpy(x, BufferType.vec3)
    if isinstance(y, np.ndarray):
        y = Bufferx.from_numpy(y, BufferType.vec3)

    # sanity check - x and y should have the same count
    if isinstance(x, Buffer) and isinstance(y, Buffer):
        if x.get_count() != y.get_count():
            raise ValueError("x and y should have the same count")

    # =============================================================================
    # TMP: mock implementation
    # =============================================================================

    assert isinstance(x, Buffer) and isinstance(y, Buffer), "x and y should be Buffers at this point"
    position_count = x.get_count()

    positions_numpy = np.zeros((position_count, 3), dtype=np.float32)
    x_numpy = Bufferx.to_numpy(x)
    y_numpy = Bufferx.to_numpy(y)
    for i in range(position_count):
        positions_numpy[i, 0] = x_numpy[i, 0]
        positions_numpy[i, 1] = y_numpy[i, 0]
        positions_numpy[i, 2] = 0.0
    positions = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    visualMarkers = _generate_markers(positions)
    visualPaths = _generate_paths(positions)

    visuals = []
    visuals.extend(visualPaths)
    visuals.extend(visualMarkers)
    return visuals
