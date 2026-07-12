"""Independent experimental VisPy2 producer for GSP.

This package is not the official upstream VisPy 2.0 API or release.
"""

__version__ = "0.2.0"

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
from .session import (
    Display,
    Session,
    SessionDiagnostic,
    SessionExecutionError,
    SessionInspection,
    SessionLifecycleError,
    open_session,
)

__all__ = [
    "__version__",
    "Axes",
    "Figure",
    "Display",
    "Session",
    "SessionDiagnostic",
    "SessionExecutionError",
    "SessionInspection",
    "SessionLifecycleError",
    "affine2d",
    "axes",
    "color_scale",
    "colorbar",
    "imshow",
    "markers",
    "mesh",
    "open_session",
    "path",
    "plot",
    "scatter",
    "segments",
    "subplots",
    "text",
]
