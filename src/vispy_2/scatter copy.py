"""Unified scatter API to create Points, Pixels or Markers visuals."""

# stdlib imports
from typing import Optional, Union, Literal

# pip imports
import numpy as np

# local imports
from gsp.types import TransBuf, Buffer, BufferType
from gsp.types.group import Groups
from gsp.types.marker_shape import MarkerShape
from gsp.visuals.points import Points
from gsp.visuals.pixels import Pixels
from gsp.visuals.markers import Markers
from gsp.types.visual_base import VisualBase
from gsp_extra.bufferx import Bufferx


def _scatter_points(
    positions: TransBuf,
    *,
    mode: Optional[Union[Literal["pixels"], Literal["points"], Literal["markers"]]] = None,
    sizes: Optional[TransBuf] = None,
    colors: Optional[TransBuf] = None,
    face_colors: Optional[TransBuf] = None,
    edge_colors: Optional[TransBuf] = None,
    edge_widths: Optional[TransBuf] = None,
    groups: Optional[Groups] = None,
    marker_shape: Optional[MarkerShape] = None,
) -> VisualBase:
    """Helper function to create a Points visual with default attributes if positions is a Buffer."""
    if isinstance(positions, Buffer):
        position_count = positions.get_count()
        if sizes is None:
            sizes_numpy = np.array([40] * position_count, dtype=np.float32)
            sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)
        if face_colors is None:
            face_colors = Buffer(position_count, BufferType.rgba8)
            face_colors.set_data(bytearray([255, 0, 0, 255]) * position_count, 0, position_count)
        if edge_colors is None:
            edge_colors = Buffer(position_count, BufferType.rgba8)
            edge_colors.set_data(bytearray([0, 0, 255, 255]) * position_count, 0, position_count)
        if edge_widths is None:
            edge_widths_numpy = np.array([1.0] * position_count, dtype=np.float32)
            edge_widths = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

    # Raise errors if required attributes are missing for points mode
    if sizes is None:
        raise ValueError("'sizes' is required for points mode")
    if face_colors is None:
        raise ValueError("'face_colors' is required for points mode")
    if edge_colors is None:
        raise ValueError("'edge_colors' is required for points mode")
    if edge_widths is None:
        raise ValueError("'edge_widths' is required for points mode")

    # Now actually create the Points visual
    visual = Points(positions, sizes, face_colors, edge_colors, edge_widths)
    return visual


def scatter(
    positions: TransBuf,
    *,
    mode: Optional[Union[Literal["pixels"], Literal["points"], Literal["markers"]]] = None,
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
    elif mode == "points":
        # Guess missing attributes for points mode if positions is a Buffer
        if isinstance(positions, Buffer):
            position_count = positions.get_count()
            if sizes is None:
                sizes_numpy = np.array([40] * position_count, dtype=np.float32)
                sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)
            if face_colors is None:
                face_colors = Buffer(position_count, BufferType.rgba8)
                face_colors.set_data(bytearray([255, 0, 0, 255]) * position_count, 0, position_count)
            if edge_colors is None:
                edge_colors = Buffer(position_count, BufferType.rgba8)
                edge_colors.set_data(bytearray([0, 0, 255, 255]) * position_count, 0, position_count)
            if edge_widths is None:
                edge_widths_numpy = np.array([1.0] * position_count, dtype=np.float32)
                edge_widths = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Raise errors if required attributes are missing for points mode
        if sizes is None:
            raise ValueError("'sizes' is required for points mode")
        if face_colors is None:
            raise ValueError("'face_colors' is required for points mode")
        if edge_colors is None:
            raise ValueError("'edge_colors' is required for points mode")
        if edge_widths is None:
            raise ValueError("'edge_widths' is required for points mode")

        # Now actually create the Points visual
        visual = Points(positions, sizes, face_colors, edge_colors, edge_widths)
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

        # Now actually create the Markers visual
        visual = Markers(marker_shape, positions, sizes, face_colors, edge_colors, edge_widths)
        return visual
    else:
        raise ValueError(f"Unsupported mode: {mode}")
