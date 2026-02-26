"""Helper class to parse matplotlib-style format strings for plotting.

- https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
"""

# stdlib imports
from typing import Optional, Union, Literal
from dataclasses import dataclass
import re

# local imports
from gsp.constants import Constants
from gsp.types.marker_shape import MarkerShape
from gsp.types.color import Color


@dataclass
class ParsedFormat:
    """Represents the parsed components of a matplotlib-style format string."""

    color: Optional[str] = None
    marker: Optional[str] = None
    linestyle: Optional[str] = None


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
            Optional[str]: The corresponding GSP color format, or None if the input is not recognized.
        """
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
        elif fmt_marker == "s":
            return MarkerShape.square

        raise ValueError(f"Unsupported plot() fmt marker format: {fmt_marker}")

    # =============================================================================
    # Parsing of fmt string
    # =============================================================================

    @staticmethod
    def parse_fmt(fmt: str) -> ParsedFormat:
        """Parse a matplotlib-style format string.

        Args:
            fmt (str): The format string to parse (e.g., 'o', '--', 'C0', 'ro-', etc.). The format string can contain a marker, a line style, and a color, in any order. For example:
                - 'ro-' means red color

        Returns:
            ParsedFormat(color=..., marker=..., linestyle=...)
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
