"""Scatter visualization API supporting three rendering modes: Pixels, Points, and Markers.

This module provides a unified scatter() function to create scatter plots with different
rendering backends optimized for different point cloud sizes:

- **Pixels:** Fast rendering for large point clouds (2000+ points). Minimal features.
- **Points:** Balanced quality and customization (100-1000 points). Full styling control.
- **Markers:** Styled shapes with customizable sizes and colors (10-500 points).

Mode Selection:
    The function automatically infers the rendering mode based on provided arguments:
    - If `groups` is provided → Pixels mode
    - Else if `marker_shape` is provided → Markers mode
    - Else → Points mode (default)

    You can also explicitly specify mode with the `mode` parameter.

Examples:
    >>> import numpy as np
    >>> from vispy2 import scatter
    >>> positions = np.random.rand(100, 3)
    >>>
    >>> # Points mode (default, full customization)
    >>> visual = scatter(positions)
    >>>
    >>> # Markers mode (with custom shapes)
    >>> from gsp.types import MarkerShape
    >>> visual = scatter(positions, marker_shape=MarkerShape.circle)
    >>>
    >>> # Pixels mode (fast for many points)
    >>> visual = scatter(positions, groups=100)

References:
  - https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.scatter.html
"""

# stdlib imports
from typing import Literal

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
    *,
    mode: Literal["pixels", "points", "markers"] | None = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
    groups: Groups | None = None,
    marker_shape: MarkerShape | None = None,
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
    mode: Literal["pixels", "points", "markers"] | None = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
    groups: Groups | None = None,
    marker_shape: MarkerShape | None = None,
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
    mode: Literal["pixels", "points", "markers"] | None = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
    groups: Groups | None = None,
    marker_shape: MarkerShape | None = None,
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
    mode: Literal["pixels", "points", "markers"] | None = None,
    sizes: TransBuf | np.ndarray | None = None,
    colors: TransBuf | np.ndarray | None = None,
    face_colors: TransBuf | np.ndarray | None = None,
    edge_colors: TransBuf | np.ndarray | None = None,
    edge_widths: TransBuf | np.ndarray | None = None,
    groups: Groups | None = None,
    marker_shape: MarkerShape | None = None,
) -> VisualBase:
    """Create a scatter plot with Points, Pixels, or Markers visual.

    Provides a unified interface for creating different types of scatter visualizations,
    optimized for different point cloud sizes. The rendering mode is automatically inferred
    from provided arguments, but can be explicitly specified.

    Mode Selection & Performance:
        - **Pixels** (2000+ points): Fast, minimal features, group-based rendering
        - **Points** (100-1000 points): Balanced quality, full customization
        - **Markers** (10-500 points): Styled shapes, customizable sizes/colors

    Auto Mode Inference:
        If `mode` is not provided, infers based on arguments:
            1. If `groups` present → Pixels mode
            2. Else if `marker_shape` present → Markers mode
            3. Else → Points mode (default)

    Default Value Generation:
        If `positions` is a Buffer, auto-generates defaults for missing attributes:
            - sizes: Default to 40.0 (points/markers)
            - face_colors: Default to red (points/markers)
            - edge_colors: Default to blue (points/markers)
            - edge_widths: Default to 1.0 (points/markers)
            - colors: No default (pixels mode requires explicit colors)

    Args:
        positions (TransBuf | np.ndarray): Positions of points. Shape: (N, 3) for vec3 or
            (N,) for conversion. If numpy array, auto-converted to Buffer(vec3).
        mode (Literal["pixels", "points", "markers"] | None): Rendering mode.
            If None, auto-inferred from other arguments.
        sizes (TransBuf | np.ndarray | None): Point/marker sizes. Default: 40.0 (points/markers).
            Required for points/markers unless Buffer positions provided (uses default).
        colors (TransBuf | np.ndarray | None): Pixel colors (RGBA8). Required for pixels mode.
            Ignored in points/markers mode (use face_colors instead).
        face_colors (TransBuf | np.ndarray | None): Face colors of points/markers (RGBA8).
            Default: red (255, 0, 0, 255). Required for points/markers unless Buffer positions.
        edge_colors (TransBuf | np.ndarray | None): Edge colors of points/markers (RGBA8).
            Default: blue (0, 0, 255, 255). Required for points/markers unless Buffer positions.
        edge_widths (TransBuf | np.ndarray | None): Edge widths for points/markers (float32).
            Default: 1.0. Required for points/markers unless Buffer positions.
        groups (Groups | None): Group membership for pixels (optimization). Required for pixels mode.
            Determines how pixels are batched for rendering.
        marker_shape (MarkerShape | None): Shape of markers. Required for markers mode.
            Examples: MarkerShape.circle, MarkerShape.square, MarkerShape.diamond, etc.

    Returns:
        VisualBase: A Points, Pixels, or Markers visual object ready for rendering.

    Raises:
        ValueError: If required parameters for the selected mode are missing.

    Examples:
        >>> import numpy as np
        >>> from vispy2 import scatter
        >>> from gsp.types import MarkerShape
        >>> from gsp.constants import Constants
        >>>
        >>> positions = np.random.rand(100, 3)
        >>>
        >>> # Pixels mode (fastest, for large datasets)
        >>> colors = np.full((100, 4), [255, 0, 0, 255], dtype=np.uint8)
        >>> visual = scatter(positions, colors=colors, groups=100)
        >>>
        >>> # Points mode (default, most flexible)
        >>> visual = scatter(positions)  # Uses all defaults
        >>>
        >>> # Markers mode (with custom shapes)
        >>> visual = scatter(positions, marker_shape=MarkerShape.square)
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
        visual_pixels = _scatter_pixels(positions, mode=mode, colors=colors, groups=groups)
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
