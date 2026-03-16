"""Helper class to parse matplotlib-style format strings for plotting.

This module provides utilities to parse matplotlib-style format strings and convert them to
GSP-compatible visual properties.

Supported format: [marker][linestyle][color]
- Examples: 'o' (circle), 'r-' (red line), 'go-' (green circles with line), 'm^' (magenta triangles)

Supported colors:
  Single-letter: 'b' (blue), 'g' (green), 'r' (red), 'c' (cyan), 'm' (magenta),
  'y' (yellow), 'k' (black), 'w' (white)
  Color cycle: 'C0' (blue), 'C1' (green), 'C2' (red), etc. (matplotlib default cycle)

Supported markers:
  'o' (circle), 's' (square), '^' (triangle up), 'v' (triangle down),
  '<' (triangle left), '>' (triangle right), '*' (asterisk), 'X' (cross),
  'D' (diamond), '|' (vertical bar), '_' (horizontal bar)

Supported line styles:
  '-' (solid line only). Other matplotlib line styles (--  dash, -. dash-dot, : dotted)
  are not currently supported by the datoviz backend and will raise an error.

References:
  - https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
"""

# stdlib imports
from dataclasses import dataclass
import re

# local imports
from gsp.constants import Constants
from gsp.types.marker_shape import MarkerShape
from gsp.types.color import Color


@dataclass
class ParsedFormat:
    """Represents the parsed components of a matplotlib-style format string."""

    color: str | None = None
    marker: str | None = None
    linestyle: str | None = None


# Matplotlib default color cycle (CSS colors mapped to GSP colors)
# Reference: https://matplotlib.org/stable/gallery/style_sheets/default_style_changes.html
_COLOR_CYCLE = [
    "b",  # C0: blue
    "g",  # C1: green (actually #1f77b4, #ff7f0e, #2ca02c in matplotlib but we map to GSP colors)
    "r",  # C2: red
    "c",  # C3: cyan
    "m",  # C4: magenta
    "y",  # C5: yellow
    "k",  # C6: black
    "w",  # C7: white
    "b",  # C8: blue (cycle repeats)
    "g",  # C9: green
    "r",  # C10: red
]


class FmtUtils:
    """Helper class to parse matplotlib-style format strings for plotting."""

    # List of all matplotlib markers - Not all are supported in GSP, but we need this for parsing
    FMT_MARKERS = {
        ".",  # point marker
        ",",  # pixel marker
        "o",  # circle marker
        "v",  # triangle_down marker
        "^",  # triangle_up marker
        "<",  # triangle_left marker
        ">",  # triangle_right marker
        "1",  # tri_down marker
        "2",  # tri_up marker
        "3",  # tri_left marker
        "4",  # tri_right marker
        "8",  # octagon marker
        "s",  # square marker
        "p",  # pentagon marker
        "P",  # plus (filled) marker
        "*",  # star marker
        "h",  # hexagon1 marker
        "H",  # hexagon2 marker
        "+",  # plus marker
        "x",  # x marker
        "X",  # x (filled) marker
        "D",  # diamond marker
        "d",  # thin_diamond marker
        "|",  # vline marker
        "_",  # hline marker
    }

    # List of line styles - longest first to ensure correct parsing
    FMT_LINE_STYLES = [
        "--",  # dashed line style
        "-.",  # dash-dot line style
        "-",  # solid line style
        ":",  # dotted line style
    ]  # longest first

    # List of single-letter color codes used in matplotlib format strings - All supported in GSP
    FMT_COLOR_LETTERS = {
        "b",  # blue
        "g",  # green
        "r",  # red
        "c",  # cyan
        "m",  # magenta
        "y",  # yellow
        "k",  # black
        "w",  # white
    }

    # =============================================================================
    # Conversion to GSP constants
    # =============================================================================

    @staticmethod
    def str_to_gsp_color(fmt_color: str) -> Color:
        """Convert a matplotlib color format to a GSP color format.

        Args:
            fmt_color (str): The color component from a matplotlib-style format string (e.g., 'r', 'C0', etc.).

        Returns:
            Color: The corresponding GSP color format.

        Raises:
            ValueError: If the color format is not recognized.
        """
        # Handle single-letter colors
        if fmt_color == "b":
            return Constants.Color.blue
        elif fmt_color == "g":
            return Constants.Color.green
        elif fmt_color == "r":
            return Constants.Color.red
        elif fmt_color == "c":
            return Constants.Color.cyan
        elif fmt_color == "m":
            return Constants.Color.magenta
        elif fmt_color == "y":
            return Constants.Color.yellow
        elif fmt_color == "k":
            return Constants.Color.black
        elif fmt_color == "w":
            return Constants.Color.white

        # Handle color cycle (C0, C1, C2, etc.)
        if fmt_color.startswith("C"):
            try:
                cycle_index = int(fmt_color[1:])
                # Cycle through the color list
                color_letter = _COLOR_CYCLE[cycle_index % len(_COLOR_CYCLE)]
                return FmtUtils.str_to_gsp_color(color_letter)
            except (ValueError, IndexError):
                pass

        raise ValueError(f"Unsupported plot() fmt color format: {fmt_color}")

    @staticmethod
    def str_to_gsp_marker(fmt_marker: str) -> MarkerShape:
        """Convert a matplotlib marker format to a GSP MarkerShape.

        Args:
            fmt_marker (str): The marker component from a matplotlib-style format string (e.g., 'o', 's', etc.).

        Returns:
            MarkerShape: The corresponding GSP MarkerShape, or None if the input is not recognized
        """
        if fmt_marker == "o":
            return MarkerShape.disc
        elif fmt_marker == "*":
            return MarkerShape.asterisk
        elif fmt_marker == "s":
            return MarkerShape.square
        elif fmt_marker == "v":
            return MarkerShape.triangle_down
        elif fmt_marker == "^":
            return MarkerShape.triangle_up
        elif fmt_marker == "<":
            return MarkerShape.triangle_left
        elif fmt_marker == ">":
            return MarkerShape.triangle_right
        elif fmt_marker == "X":
            return MarkerShape.cross
        elif fmt_marker == "D":
            return MarkerShape.diamond
        elif fmt_marker == "|":
            return MarkerShape.vbar
        elif fmt_marker == "_":
            return MarkerShape.hbar

        raise ValueError(f"Unsupported plot() fmt marker format: {fmt_marker}")

    # =============================================================================
    # Parsing of fmt string
    # =============================================================================

    @staticmethod
    def parse_fmt(fmt: str) -> ParsedFormat:
        """Parse a matplotlib-style format string.

        Args:
            fmt (str): The format string to parse (e.g., 'o', '-', 'C0', 'ro-', etc.).
                The format string can contain a marker, a line style, and a color, in any order.
                Examples: 'ro-' (red circles with line), 'b^' (blue triangles)

        Returns:
            ParsedFormat: Parsed format components (color, marker, linestyle).

        Raises:
            ValueError: If format contains duplicate specs, unrecognized characters, or
                unsupported line styles (only '-' solid line is supported).
        """
        color = None
        marker = None
        linestyle = None

        i = 0
        n = len(fmt)

        while i < n:
            # 1️⃣ Check line styles (longest first)
            matched = False
            for ls in FmtUtils.FMT_LINE_STYLES:
                if fmt.startswith(ls, i):
                    if linestyle is not None:
                        raise ValueError(f"Duplicate linestyle in fmt: {fmt}")
                    # Validate that only solid line style is supported
                    if ls != "-":
                        raise ValueError(
                            f"Unsupported line style '{ls}' in fmt '{fmt}'. "
                            f"Only solid line style '-' is supported. "
                            f"(Note: dashed '--', dash-dot '-.', and dotted ':' line styles are not supported by the datoviz backend)"
                        )
                    linestyle = ls
                    i += len(ls)
                    matched = True
                    break
            if matched:
                continue

            # 2️⃣ Check C-cycle color (e.g. C0, C1...)
            if fmt[i] == "C":
                match = re.match(r"C\d+", fmt[i:])
                if match:
                    if color is not None:
                        raise ValueError(f"Duplicate color in fmt: {fmt}")
                    color = match.group(0)
                    i += len(color)
                    continue

            ch = fmt[i]

            # 3️⃣ Single-letter color
            if ch in FmtUtils.FMT_COLOR_LETTERS:
                if color is not None:
                    raise ValueError(f"Duplicate color in fmt: {fmt}")
                color = ch
                i += 1
                continue

            # 4️⃣ Marker
            if ch in FmtUtils.FMT_MARKERS:
                if marker is not None:
                    raise ValueError(f"Duplicate marker in fmt: {fmt}")
                marker = ch
                i += 1
                continue

            raise ValueError(f"Unrecognized format character '{ch}' in fmt: {fmt}")

        return ParsedFormat(color=color, marker=marker, linestyle=linestyle)
