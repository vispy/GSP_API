"""VisPy2 experimental producer API."""

from . import axes
from .plot.plot import plot
from .protocol import (
    Axes,
    Figure,
    color_scale,
    colorbar,
    imshow,
    markers,
    mesh,
    path,
    scatter,
    segments,
    subplots,
    text,
)

__all__ = [
    "Axes",
    "Figure",
    "axes",
    "color_scale",
    "colorbar",
    "imshow",
    "markers",
    "mesh",
    "path",
    "plot",
    "scatter",
    "segments",
    "subplots",
    "text",
]
