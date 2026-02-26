"""Unified scatter API to create Points, Pixels or Markers visuals.

- https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
"""

# pip imports
import numpy as np

# local imports
from .fmt_utils import FmtUtils, ParsedFormat
from gsp.constants import Constants
from gsp.types import TransBuf, Buffer, BufferType, Color
from gsp.constants import Constants
from gsp.visuals.points import Points
from gsp.visuals.markers import Markers, MarkerShape
from gsp.visuals.paths import Paths
from gsp.types.cap_style import CapStyle
from gsp.types.join_style import JoinStyle
from gsp.types.visual_base import VisualBase
from gsp_extra.bufferx import Bufferx
from gsp_extra.misc.render_item import RenderItem


# =============================================================================
#
# =============================================================================


def _generate_markers(
    positions: TransBuf,
    parsed_fmt: ParsedFormat,
    *,
    marker_edge_color: Color | None = None,
    marker_edge_width: float | None = None,
    marker_face_color: Color | None = None,
    marker_size: float | None = None,
) -> list[VisualBase]:
    assert isinstance(positions, Buffer), "positions should be a Buffer at this point"
    position_count = positions.get_count()

    # Handle default values for marker properties
    if marker_edge_color is None:
        marker_edge_color = Constants.Color.blue
    if marker_edge_width is None:
        marker_edge_width = 0.0
    if marker_face_color is None:
        marker_face_color = Constants.Color.red
    if marker_size is None:
        marker_size = 50.0

    marker_shape = FmtUtils.str_to_gsp_marker(parsed_fmt.marker) if parsed_fmt.marker is not None else MarkerShape.disc

    sizes_numpy = np.array([marker_size] * position_count, dtype=np.float32)
    sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    face_colors_gsp = FmtUtils.str_to_gsp_color(parsed_fmt.color) if parsed_fmt.color is not None else marker_face_color
    face_colors = Buffer(position_count, BufferType.rgba8)
    face_colors.set_data(face_colors_gsp * position_count, 0, position_count)

    # No edge (edge width = 0)
    edge_colors = Buffer(position_count, BufferType.rgba8)
    edge_colors.set_data(Constants.Color.blue * position_count, 0, position_count)
    edge_widths_numpy = np.array([0.0] * position_count, dtype=np.float32)
    edge_widths = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    visual = Markers(marker_shape, positions, sizes, face_colors, edge_colors, edge_widths)
    return [visual]


def _generate_paths(
    positions: TransBuf,
    parsed_fmt: ParsedFormat,
    *,
    line_width: float | None = None,
    line_cap_style: CapStyle | None = None,
    line_join_style: JoinStyle | None = None,
) -> list[VisualBase]:
    assert isinstance(positions, Buffer), "positions should be a Buffer at this point"
    position_count = positions.get_count()

    # Handle default values for line properties
    if line_width is None:
        line_width = 2.0
    if line_cap_style is None:
        line_cap_style = CapStyle.ROUND
    if line_join_style is None:
        line_join_style = JoinStyle.ROUND

    # Sanity check - only support solid line style for now, as datoviz doesnt support dashed paths
    if parsed_fmt.linestyle is not None and parsed_fmt.linestyle != "-":
        raise NotImplementedError(f"Only solid line style '-' is supported for now (datoviz doesnt supposed dashed paths), but got '{parsed_fmt.linestyle}'")

    path_sizes_numpy = np.array([position_count], dtype=np.uint32)
    path_sizes = Bufferx.from_numpy(path_sizes_numpy, BufferType.uint32)

    colors_gsp = FmtUtils.str_to_gsp_color(parsed_fmt.color) if parsed_fmt.color is not None else Constants.Color.red
    colors = Buffer(position_count, BufferType.rgba8)
    colors.set_data(colors_gsp * position_count, 0, position_count)

    line_widths_numpy = np.array([line_width] * position_count, dtype=np.float32).reshape(-1, 1)
    line_widths = Bufferx.from_numpy(line_widths_numpy, BufferType.float32)

    # Create the Pixels visual and add it to the viewport
    paths = Paths(positions, path_sizes, colors, line_widths, line_cap_style, line_join_style)
    return [paths]


# =============================================================================
#
# =============================================================================


def plot(
    x: TransBuf | np.ndarray,
    y: TransBuf | np.ndarray | None = None,
    *,
    fmt: str | None = None,
    marker_edge_color: Color | None = None,
    marker_edge_width: float | None = None,
    marker_face_color: Color | None = None,
    marker_size: float | None = None,
    line_width: float | None = None,
    line_cap_style: CapStyle | None = None,
    line_join_style: JoinStyle | None = None,
) -> list[VisualBase]:
    """Create a line visual connecting the given x and y coordinates.

    Args:
        x (TransBuf | np.ndarray): The x coordinates of the points.
        y (TransBuf | np.ndarray | None): The y coordinates of the points. If None, y will be set to x.
        fmt (str | None): The format string for the plot (e.g., 'o' for markers, '-' for lines). '[marker][line][color]'
        marker_edge_color (bytearray | None): The edge color for markers, as an RGBA bytearray. If None, it will be determined by the fmt string or default to blue.
        marker_edge_width (float | None): The edge width for markers. If None, it will be determined by the fmt string or default to 1.0.
        marker_face_color (bytearray | None): The face color for markers, as an RGBA bytearray. If None, it will be determined by the fmt string or default to red.
        marker_size (float | None): The size for markers. If None, it will be determined by the fmt string or default to 10.0.
        line_width (float | None): The width of the line. If None, it will be determined by the fmt string or default to 2.0.
        line_cap_style (CapStyle | None): The cap style for the line. If None, it will be determined by the fmt string or default to CapStyle.ROUND.
        line_join_style (JoinStyle | None): The join style for the line. If None, it will be determined by the fmt string or default to JoinStyle.ROUND.
    """
    returned_visuals: list[VisualBase] = []

    # =============================================================================
    # Convert any numpy to Buffer if needed
    # =============================================================================

    # If positions is a numpy array, convert it to a Buffer
    if isinstance(x, np.ndarray):
        x = Bufferx.from_numpy(x, BufferType.float32)
    if isinstance(y, np.ndarray):
        y = Bufferx.from_numpy(y, BufferType.float32)

    # =============================================================================
    # Sanity check
    # =============================================================================

    # sanity check - x and y should have the same count
    if isinstance(x, Buffer) and isinstance(y, Buffer):
        if x.get_count() != y.get_count():
            raise ValueError("x and y should have the same count")

    # =============================================================================
    # Handle case where y is None
    # =============================================================================

    assert isinstance(x, Buffer), "x  should be Buffers at this point"
    position_count = x.get_count()

    if y is None:
        y = x
        x = Bufferx.from_numpy(np.arange(position_count, dtype=np.float32), BufferType.float32)

    assert isinstance(x, Buffer), "x should be Buffers at this point"
    assert isinstance(y, Buffer), "y should be Buffers at this point"

    # =============================================================================
    # Build Positions from x, y
    # =============================================================================

    positions_numpy = np.zeros((position_count, 3), dtype=np.float32)
    x_numpy = Bufferx.to_numpy(x)
    y_numpy = Bufferx.to_numpy(y)
    for i in range(position_count):
        positions_numpy[i, 0] = x_numpy[i, 0]
        positions_numpy[i, 1] = y_numpy[i, 0]
        positions_numpy[i, 2] = 0.0
    positions = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # =============================================================================
    # Parse fmt (or build default ParsedFormat if fmt is None)
    # =============================================================================

    parsed_fmt = FmtUtils.parse_fmt(fmt) if fmt is not None else ParsedFormat(color=None, marker=None, linestyle=None)
    print(f"Parsed fmt: {parsed_fmt}")

    # =============================================================================
    # Generate visuals for markers
    # =============================================================================

    # Add a Markers visual if marker is specified in fmt
    if parsed_fmt.marker is not None:
        visualMarkers = _generate_markers(
            positions,
            parsed_fmt,
            marker_edge_color=marker_edge_color,
            marker_edge_width=marker_edge_width,
            marker_face_color=marker_face_color,
            marker_size=marker_size,
        )
        returned_visuals.extend(visualMarkers)

    # =============================================================================
    # Generate visuals for lines
    # =============================================================================

    # all pixels red - Create buffer and fill it with a constant
    visualPaths = _generate_paths(
        positions,
        parsed_fmt,
        line_width=line_width,
        line_cap_style=line_cap_style,
        line_join_style=line_join_style,
    )
    returned_visuals.extend(visualPaths)

    # =============================================================================
    # Return the plot() visuals
    # =============================================================================

    return returned_visuals
