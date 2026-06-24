"""VisPy2 experimental producer API."""

from . import axes
from .plot.plot import plot
from .protocol import (
    Axes,
    Figure,
    imshow,
    markers,
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
    "imshow",
    "markers",
    "path",
    "plot",
    "scatter",
    "segments",
    "subplots",
    "text",
]
