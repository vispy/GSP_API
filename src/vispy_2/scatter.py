"""Unified scatter API to create Points, Pixels or Markers visuals."""

# stdlib imports
from typing import Optional, Union, Literal

# local imports
from gsp.types.transbuf import TransBuf
from gsp.types.group import Groups
from gsp.types.marker_shape import MarkerShape
from gsp.visuals.points import Points
from gsp.visuals.pixels import Pixels
from gsp.visuals.markers import Markers
from gsp.types.visual_base import VisualBase


def scatter(
    positions: TransBuf,
    *,
    mode: Optional[Union[Literal["points"], Literal["pixels"], Literal["markers"]]] = None,
    sizes: Optional[TransBuf] = None,
    colors: Optional[TransBuf] = None,
    face_colors: Optional[TransBuf] = None,
    edge_colors: Optional[TransBuf] = None,
    edge_widths: Optional[TransBuf] = None,
    groups: Optional[Groups] = None,
    marker_shape: Optional[MarkerShape] = None,
) -> VisualBase:
    """Create a Points, Pixels or Markers visual based on arguments.

    Selection rules:
    - If `mode` is provided it must be one of: 'points', 'pixels', 'markers'.
    - If `mode` is not provided the function will infer:
      - if `groups` is given -> `Pixels`
      - elif `marker_shape` is given -> `Markers`
      - else -> `Points`

    The arguments required for each mode are:
    - Pixels: `positions`, `colors`, `groups`
    - Points: `positions`, `sizes`, `face_colors`, `edge_colors`, `edge_widths`
    - Markers: `marker_shape`, `positions`, `sizes`, `face_colors`, `edge_colors`, `edge_widths`

    The function does not perform deep sanity checks; it delegates to the
    underlying visual constructors which will validate attributes.
    """
    # Sanity check - ensure mode is valid if provided
    if mode is not None and mode not in ("points", "pixels", "markers"):
        raise ValueError("mode must be one of 'points', 'pixels' or 'markers'")

    # Infer mode if not provided
    if mode is None:
        if groups is not None:
            mode = "pixels"
        elif marker_shape is not None:
            mode = "markers"
        else:
            mode = "points"

    # =============================================================================
    # Create the appropriate visual based on mode
    # =============================================================================
    if mode == "pixels":
        if colors is None:
            raise ValueError("'colors' is required for pixels mode")
        if groups is None:
            raise ValueError("'groups' is required for pixels mode")
        visual = Pixels(positions, colors, groups)
        return visual
    elif mode == "markers":
        if marker_shape is None:
            raise ValueError("'marker_shape' is required for markers mode")
        if sizes is None:
            raise ValueError("'sizes' is required for markers mode")
        if face_colors is None:
            raise ValueError("'face_colors' is required for markers mode")
        if edge_colors is None:
            raise ValueError("'edge_colors' is required for markers mode")
        if edge_widths is None:
            raise ValueError("'edge_widths' is required for markers mode")
        # Markers expect sizes, face_colors, edge_colors, edge_widths
        visual = Markers(marker_shape, positions, sizes, face_colors, edge_colors, edge_widths)
        return visual
    elif mode == "points":
        if sizes is None:
            raise ValueError("'sizes' is required for points mode")
        if face_colors is None:
            raise ValueError("'face_colors' is required for points mode")
        if edge_colors is None:
            raise ValueError("'edge_colors' is required for points mode")
        if edge_widths is None:
            raise ValueError("'edge_widths' is required for points mode")
        # Points expect sizes, face_colors, edge_colors, edge_widths
        visual = Points(positions, sizes, face_colors, edge_colors, edge_widths)
        return visual
    else:
        raise ValueError(f"Unsupported mode: {mode}")
