"""Unified plotting API for creating line and marker visualizations.

Provides a matplotlib-style plot() function that generates line and/or marker visuals
from x, y coordinate data. Supports matplotlib-style format strings for flexible styling.

Example:
    from vispy2 import plot
    import numpy as np

    x = np.linspace(0, 2*np.pi, 100)
    y = np.sin(x)

    # Plot with blue circles and red line
    visuals = plot(x, y, fmt='bo-', marker_size=50)

References:
  - https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
"""

# pip imports
import numpy as np

# local imports
from .fmt_utils import FmtUtils, ParsedFormat
from gsp.constants import Constants
from gsp.types import TransBuf, Buffer, BufferType, Color
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
        marker_size = 100.0

    marker_shape = FmtUtils.str_to_gsp_marker(parsed_fmt.marker) if parsed_fmt.marker is not None else MarkerShape.disc

    sizes_numpy = np.array([marker_size] * position_count, dtype=np.float32)
    sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

    face_colors_gsp = FmtUtils.str_to_gsp_color(parsed_fmt.color) if parsed_fmt.color is not None else marker_face_color
    face_colors = Buffer(position_count, BufferType.rgba8)
    face_colors.set_data(face_colors_gsp * position_count, 0, position_count)

    # Edge styling
    edge_colors = Buffer(position_count, BufferType.rgba8)
    edge_colors.set_data(marker_edge_color * position_count, 0, position_count)
    edge_widths_numpy = np.array([marker_edge_width] * position_count, dtype=np.float32)
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
    """Create line and/or marker visualizations from x, y coordinates.

    Supports matplotlib-style format strings to control output style. By default, generates
    a line connecting the points. If a marker is specified, adds markers to each point.

    Args:
        x (TransBuf | np.ndarray): The x coordinates of the points. Can be a Buffer or numpy array.
        y (TransBuf | np.ndarray | None): The y coordinates of the points. If None, x values
            are treated as y, and x becomes [0, 1, 2, ..., n-1].
        fmt (str | None): Matplotlib-style format string controlling visualization style.
            Format: [marker][line style][color]
            Examples:
                - 'o': circle markers only
                - '-': line only (default if no fmt specified)
                - 'ro-': red color, circle markers with line
                - 'b^': blue triangles only
                - 'C0-': first color cycle color with line
            Supported markers: o, s, ^, v, <, >, *, X, D, |, _
            Supported colors: b, g, r, c, m, y, k, w, C0-C10 (color cycle)
            Supported line styles: - (solid line only)
        marker_edge_color (Color | None): Edge color for markers. Defaults to blue.
        marker_edge_width (float | None): Edge width for markers. Defaults to 0.0 (no edge).
        marker_face_color (Color | None): Face color for markers. Defaults to red.
        marker_size (float | None): Size of markers. Defaults to 100.0.
        line_width (float | None): Width of connecting line. Defaults to 2.0.
        line_cap_style (CapStyle | None): End style for line segments. Defaults to ROUND.
        line_join_style (JoinStyle | None): Join style for line segments. Defaults to ROUND.

    Returns:
        list[VisualBase]: Visual objects (Markers and/or Paths) ready to render.
            Typically contains one Markers and/or one Paths visual.

    Raises:
        ValueError: If format string contains invalid characters or unsupported line styles.

    Examples:
        >>> import numpy as np
        >>> from vispy2 import plot
        >>> x = np.linspace(0, 2*np.pi, 50)
        >>> y = np.sin(x)
        >>> visuals = plot(x, y, fmt='ro-')  # Red circles with line
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

    # Generate paths (lines) if:
    # 1. A linestyle is explicitly specified (e.g., '-' for solid line), OR
    # 2. Neither markers nor lines are specified (default to line behavior)
    #
    # Do NOT generate paths if only markers are specified (e.g., fmt='o')
    should_generate_lines = parsed_fmt.linestyle is not None or (
        parsed_fmt.marker is None and parsed_fmt.linestyle is None
    )

    if should_generate_lines:
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
