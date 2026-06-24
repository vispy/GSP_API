"""VisPy2 experimental producer API."""

from . import axes
from .plot.plot import plot
from .protocol import Axes, Figure, imshow, markers, scatter, segments, subplots

__all__ = [
    "Axes",
    "Figure",
    "axes",
    "imshow",
    "markers",
    "plot",
    "scatter",
    "segments",
    "subplots",
]
