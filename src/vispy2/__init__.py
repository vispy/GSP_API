"""VisPy2 experimental producer API."""

from . import axes
from .plot.plot import plot
from .protocol import (
    Axes,
    Figure,
    affine2d,
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
    "affine2d",
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
