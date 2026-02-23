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

# =============================================================================
# Private scatter() function for pixels
# =============================================================================


def _scatter_pixels(
    positions: TransBuf,
    colors: TransBuf | np.ndarray | None = None,
    groups: Groups | None = None,
) -> VisualBase:
    """Helper function to create a Pixels visual."""
    # If positions is a Buffer, we can infer the count and create default buffers for any missing attributes
    if isinstance(positions, Buffer):
        position_count = positions.get_count()

        if colors is None:
            colors = Buffer(position_count, BufferType.rgba8)
            colors.set_data(bytearray([255, 0, 0, 255]) * position_count, 0, position_count)
        elif isinstance(colors, np.ndarray):
            colors = Bufferx.from_numpy(colors, BufferType.rgba8)
        if groups is None:
            groups = position_count  # all points belong to the same group

    # Raise errors if required attributes are missing
    if colors is None:
        raise ValueError("'colors' is required for pixels mode")
    if groups is None:
        raise ValueError("'groups' is required for pixels mode")

    # sanity check - workaround static type checkers since we know these are the right types after the above logic
    assert isinstance(colors, TransBuf), f"Expected 'colors' to be a TransBuf, got {type(colors)}"
    assert groups is not None, "'groups' should not be None at this point"

    # Now actually create the Pixels visual
    visual = Pixels(positions, colors, groups)
    return visual


# =============================================================================
# Private scatter() function for points
# =============================================================================


def _scatter_points(
    positions: TransBuf,
    *,
    mode: Optional[Union[Literal["pixels"], Literal["points"], Literal["markers"]]] = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
    groups: Optional[Groups] = None,
    marker_shape: Optional[MarkerShape] = None,
) -> VisualBase:
    """Helper function to create a Points visual with default attributes if positions is a Buffer."""
    # If positions is a Buffer, we can infer the count and create default buffers for any missing attributes
    if isinstance(positions, Buffer):
        position_count = positions.get_count()

        if sizes is None:
            sizes_numpy = np.array([40] * position_count, dtype=np.float32)
            sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)
        elif isinstance(sizes, np.ndarray):
            sizes = Bufferx.from_numpy(sizes, BufferType.float32)

        if face_colors is None:
            face_colors = Buffer(position_count, BufferType.rgba8)
            face_colors.set_data(bytearray([255, 0, 0, 255]) * position_count, 0, position_count)
        elif isinstance(face_colors, np.ndarray):
            face_colors = Bufferx.from_numpy(face_colors, BufferType.rgba8)

        if edge_colors is None:
            edge_colors = Buffer(position_count, BufferType.rgba8)
            edge_colors.set_data(bytearray([0, 0, 255, 255]) * position_count, 0, position_count)
        elif isinstance(edge_colors, np.ndarray):
            edge_colors = Bufferx.from_numpy(edge_colors, BufferType.rgba8)

        if edge_widths is None:
            edge_widths_numpy = np.array([1.0] * position_count, dtype=np.float32)
            edge_widths = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)
        elif isinstance(edge_widths, np.ndarray):
            edge_widths = Bufferx.from_numpy(edge_widths, BufferType.float32)

    # Raise errors if required attributes are missing
    if isinstance(sizes, TransBuf) is False:
        raise ValueError("'sizes' is required for points mode")
    if face_colors is None:
        raise ValueError("'face_colors' is required for points mode")
    if edge_colors is None:
        raise ValueError("'edge_colors' is required for points mode")
    if edge_widths is None:
        raise ValueError("'edge_widths' is required for points mode")

    # sanity check - workaround static type checkers since we know these are the right types after the above logic
    assert isinstance(sizes, TransBuf), f"Expected 'sizes' to be a TransBuf, got {type(sizes)}"
    assert isinstance(face_colors, TransBuf), f"Expected 'face_colors' to be a TransBuf, got {type(face_colors)}"
    assert isinstance(edge_colors, TransBuf), f"Expected 'edge_colors' to be a TransBuf, got {type(edge_colors)}"
    assert isinstance(edge_widths, TransBuf), f"Expected 'edge_widths' to be a TransBuf, got {type(edge_widths)}"

    # Now actually create the Points visual
    visual = Points(positions, sizes, face_colors, edge_colors, edge_widths)
    return visual


# =============================================================================
# Private scatter() function for markers
# =============================================================================


def _scatter_markers(
    positions: TransBuf,
    *,
    mode: Optional[Union[Literal["pixels"], Literal["points"], Literal["markers"]]] = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
    groups: Optional[Groups] = None,
    marker_shape: Optional[MarkerShape] = None,
) -> VisualBase:
    # If positions is a Buffer, we can infer the count and create default buffers for any missing attributes
    if isinstance(positions, Buffer):
        position_count = positions.get_count()

        if sizes is None:
            sizes_numpy = np.array([40] * position_count, dtype=np.float32)
            sizes = Bufferx.from_numpy(sizes_numpy, BufferType.float32)
        elif isinstance(sizes, np.ndarray):
            sizes = Bufferx.from_numpy(sizes, BufferType.float32)

        if face_colors is None:
            face_colors = Buffer(position_count, BufferType.rgba8)
            face_colors.set_data(bytearray([255, 0, 0, 255]) * position_count, 0, position_count)
        elif isinstance(face_colors, np.ndarray):
            face_colors = Bufferx.from_numpy(face_colors, BufferType.rgba8)

        if edge_colors is None:
            edge_colors = Buffer(position_count, BufferType.rgba8)
            edge_colors.set_data(bytearray([0, 0, 255, 255]) * position_count, 0, position_count)
        elif isinstance(edge_colors, np.ndarray):
            edge_colors = Bufferx.from_numpy(edge_colors, BufferType.rgba8)

        if edge_widths is None:
            edge_widths_numpy = np.array([1.0] * position_count, dtype=np.float32)
            edge_widths = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)
        elif isinstance(edge_widths, np.ndarray):
            edge_widths = Bufferx.from_numpy(edge_widths, BufferType.float32)

    # Raise errors if required attributes are missing
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

    # sanity check - workaround static type checkers since we know these are the right types after the above logic
    assert isinstance(sizes, TransBuf), f"Expected 'sizes' to be a TransBuf, got {type(sizes)}"
    assert isinstance(face_colors, TransBuf), f"Expected 'face_colors' to be a TransBuf, got {type(face_colors)}"
    assert isinstance(edge_colors, TransBuf), f"Expected 'edge_colors' to be a TransBuf, got {type(edge_colors)}"
    assert isinstance(edge_widths, TransBuf), f"Expected 'edge_widths' to be a TransBuf, got {type(edge_widths)}"

    # Now actually create the Markers visual
    visual_markers = Markers(marker_shape, positions, sizes, face_colors, edge_colors, edge_widths)
    return visual_markers


# =============================================================================
# Public scatter() function
# =============================================================================


def scatter(
    positions: TransBuf | np.ndarray,
    *,
    mode: Optional[Union[Literal["pixels"], Literal["points"], Literal["markers"]]] = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
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

    If they are not provided, the function will attempt to create default buffers for any missing attributes based on the count of `positions` if it is a
    Buffer. For example, if `positions` is a Buffer and `sizes` is not provided for points mode, it will create a default `sizes` buffer with
    all values set to 40.

    The function does not perform deep sanity checks; it delegates to the
    underlying visual constructors which will validate attributes.
    """
    # Infer mode if not provided
    if mode is None:
        if groups is not None:
            mode = "pixels"
        elif marker_shape is not None:
            mode = "markers"
        else:
            mode = "points"

    # If positions is a numpy array, convert it to a Buffer
    if isinstance(positions, np.ndarray):
        positions = Bufferx.from_numpy(positions, BufferType.vec3)

    # =============================================================================
    # Create the appropriate visual based on mode
    # =============================================================================
    if mode == "pixels":
        visual_pixels = _scatter_pixels(positions, colors, groups)
        return visual_pixels
    elif mode == "points":
        visual_points = _scatter_points(positions, mode=mode, sizes=sizes, face_colors=face_colors, edge_colors=edge_colors, edge_widths=edge_widths)
        return visual_points
    elif mode == "markers":
        # Now actually create the Markers visual
        visual_markers = _scatter_markers(
            positions,
            mode=mode,
            sizes=sizes,
            face_colors=face_colors,
            edge_colors=edge_colors,
            edge_widths=edge_widths,
            marker_shape=marker_shape,
        )
        return visual_markers
    else:
        raise ValueError(f"Unsupported mode: {mode}")
