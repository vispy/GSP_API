"""First-slice protocol visual models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import numpy.typing as npt

from .ids import validate_id


class CoordinateSpace(str, Enum):
    """Coordinate space for first-slice visual placement."""

    NDC = "ndc"
    DATA = "data"


class ImageInterpolation(str, Enum):
    """Image sampling mode."""

    NEAREST = "nearest"
    LINEAR = "linear"


class ImageOrigin(str, Enum):
    """Array row origin for image display."""

    UPPER = "upper"
    LOWER = "lower"


class MarkerShape(str, Enum):
    """Conservative v1 marker shape vocabulary."""

    DISC = "disc"
    SQUARE = "square"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    CROSS = "cross"


class StrokeCap(str, Enum):
    """Conservative v1 screen-stroked segment cap vocabulary."""

    BUTT = "butt"
    ROUND = "round"
    SQUARE = "square"


FloatArray = npt.NDArray[np.float32] | npt.NDArray[np.float64]
ColorArray = npt.NDArray[np.uint8] | npt.NDArray[np.float32] | npt.NDArray[np.float64]
ImageArray = npt.NDArray[np.uint8] | npt.NDArray[np.float32] | npt.NDArray[np.float64]
MarkerShapeTuple = tuple[MarkerShape, ...]


@dataclass(frozen=True, slots=True)
class PointVisual:
    """Semantic point visual model for the protocol reference slice.

    ``sizes`` are rendered screen-pixel diameters, not backend marker-area units.
    """

    id: str
    positions: FloatArray
    colors: ColorArray
    sizes: FloatArray | float
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC

    def __post_init__(self) -> None:
        validate_id(self.id)
        if self.positions.ndim != 2 or self.positions.shape[1] not in (2, 3):
            raise ValueError("positions must have shape (N, 2) or (N, 3)")
        if self.positions.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError("positions must be float32 or float64")
        if not np.all(np.isfinite(self.positions)):
            raise ValueError("positions must be finite")
        point_count = self.positions.shape[0]

        if isinstance(self.sizes, np.ndarray):
            if self.sizes.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
                raise TypeError("sizes must be float32 or float64")
            if self.sizes.ndim > 1:
                raise ValueError("sizes must be scalar or shape (N,)")
            if self.sizes.shape[0] != point_count:
                raise ValueError("sizes length must match positions")
            if not np.all(np.isfinite(self.sizes)):
                raise ValueError("sizes must be finite")
            if np.any(self.sizes < 0):
                raise ValueError("sizes must be non-negative")
        else:
            if not np.isfinite(self.sizes):
                raise ValueError("sizes must be finite")
            if self.sizes < 0:
                raise ValueError("sizes must be non-negative")

        if self.colors.ndim != 2 or self.colors.shape[1] != 4:
            raise ValueError("colors must have shape (N, 4)")
        if self.colors.shape[0] != point_count:
            raise ValueError("colors length must match positions")
        if self.colors.dtype == np.dtype(np.uint8):
            return
        if self.colors.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError("colors must be rgba8, float32, or float64")
        if not np.all(np.isfinite(self.colors)):
            raise ValueError("floating point colors must be finite")
        if np.any((self.colors < 0.0) | (self.colors > 1.0)):
            raise ValueError("floating point colors must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class MarkerVisual:
    """Semantic shaped marker visual model.

    ``sizes`` are rendered screen-pixel diameters. ``angle`` values are radians.
    """

    id: str
    positions: FloatArray
    shape: MarkerShape | MarkerShapeTuple
    fill_colors: ColorArray
    sizes: FloatArray | float
    angle: FloatArray | float = 0.0
    stroke_color: ColorArray = field(
        default_factory=lambda: np.array([0, 0, 0, 255], dtype=np.uint8)
    )
    stroke_width: float = 0.0
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC

    def __post_init__(self) -> None:
        validate_id(self.id)
        point_count = _validate_positions(self.positions)
        _validate_shapes(self.shape, point_count)
        _validate_sizes(self.sizes, point_count)
        _validate_angles(self.angle, point_count)
        _validate_rgba_array(
            self.fill_colors, shape=(point_count, 4), field_name="fill_colors"
        )
        _validate_rgba_array(self.stroke_color, shape=(4,), field_name="stroke_color")
        if not np.isfinite(self.stroke_width):
            raise ValueError("stroke_width must be finite")
        if self.stroke_width < 0:
            raise ValueError("stroke_width must be non-negative")

    def shape_values(self) -> MarkerShapeTuple:
        """Return one shape per marker."""
        if isinstance(self.shape, MarkerShape):
            return (self.shape,) * int(self.positions.shape[0])
        return self.shape

    def angle_values(self) -> npt.NDArray[np.float32]:
        """Return one angle in radians per marker."""
        if isinstance(self.angle, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.angle, dtype=np.float32).reshape(-1)
            )
        return np.full((self.positions.shape[0],), float(self.angle), dtype=np.float32)


@dataclass(frozen=True, slots=True)
class SegmentVisual:
    """Semantic independent line segment visual model.

    ``widths`` are rendered screen-pixel stroke widths. ``cap`` applies to both ends.
    """

    id: str
    start_positions: FloatArray
    end_positions: FloatArray
    colors: ColorArray
    widths: FloatArray | float
    cap: StrokeCap = StrokeCap.BUTT
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC

    def __post_init__(self) -> None:
        validate_id(self.id)
        segment_count = _validate_positions(self.start_positions)
        if _validate_positions(self.end_positions) != segment_count:
            raise ValueError("end_positions length must match start_positions")
        if self.end_positions.shape[1] != self.start_positions.shape[1]:
            raise ValueError("end_positions dimensionality must match start_positions")
        _validate_rgba_array(self.colors, shape=(segment_count, 4), field_name="colors")
        _validate_sizes(self.widths, segment_count, field_name="widths")

    def width_values(self) -> npt.NDArray[np.float32]:
        """Return one pixel stroke width per segment."""
        if isinstance(self.widths, np.ndarray):
            return np.ascontiguousarray(
                np.asarray(self.widths, dtype=np.float32).reshape(-1)
            )
        return np.full(
            (self.start_positions.shape[0],), float(self.widths), dtype=np.float32
        )


@dataclass(frozen=True, slots=True)
class ImageVisual:
    """Semantic image visual model for the protocol reference slice."""

    id: str
    image: ImageArray
    extent: tuple[float, float, float, float]
    coordinate_space: CoordinateSpace = CoordinateSpace.NDC
    interpolation: ImageInterpolation = ImageInterpolation.NEAREST
    origin: ImageOrigin = ImageOrigin.UPPER

    def __post_init__(self) -> None:
        validate_id(self.id)
        if self.image.ndim not in (2, 3):
            raise ValueError("image must have shape (H, W), (H, W, 3), or (H, W, 4)")
        if self.image.ndim == 3 and self.image.shape[2] not in (3, 4):
            raise ValueError("image channel dimension must be 3 or 4")
        if self.image.shape[0] <= 0 or self.image.shape[1] <= 0:
            raise ValueError("image dimensions must be positive")
        if self.image.dtype == np.dtype(np.uint8):
            return
        if self.image.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError("image must be uint8, float32, or float64")
        if np.any((self.image < 0.0) | (self.image > 1.0)):
            raise ValueError("floating point image values must be in [0, 1]")


def _validate_positions(positions: FloatArray) -> int:
    if positions.ndim != 2 or positions.shape[1] not in (2, 3):
        raise ValueError("positions must have shape (N, 2) or (N, 3)")
    if positions.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("positions must be float32 or float64")
    if not np.all(np.isfinite(positions)):
        raise ValueError("positions must be finite")
    return int(positions.shape[0])


def _validate_shapes(shape: MarkerShape | MarkerShapeTuple, count: int) -> None:
    if isinstance(shape, MarkerShape):
        return
    if not shape:
        raise ValueError("shape tuple must not be empty")
    if len(shape) != count:
        raise ValueError("shape length must match positions")
    if any(not isinstance(value, MarkerShape) for value in shape):
        raise TypeError("shape entries must be MarkerShape values")


def _validate_sizes(
    sizes: FloatArray | float, count: int, *, field_name: str = "sizes"
) -> None:
    if isinstance(sizes, np.ndarray):
        if sizes.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError(f"{field_name} must be float32 or float64")
        if sizes.ndim != 1:
            raise ValueError(f"{field_name} must be scalar or shape (N,)")
        if sizes.shape[0] != count:
            raise ValueError(f"{field_name} length must match positions")
        if not np.all(np.isfinite(sizes)):
            raise ValueError(f"{field_name} must be finite")
        if np.any(sizes < 0):
            raise ValueError(f"{field_name} must be non-negative")
        return
    if not np.isfinite(sizes):
        raise ValueError(f"{field_name} must be finite")
    if sizes < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _validate_angles(angle: FloatArray | float, count: int) -> None:
    if isinstance(angle, np.ndarray):
        if angle.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
            raise TypeError("angle must be float32 or float64")
        if angle.ndim != 1:
            raise ValueError("angle must be scalar or shape (N,)")
        if angle.shape[0] != count:
            raise ValueError("angle length must match positions")
        if not np.all(np.isfinite(angle)):
            raise ValueError("angle must be finite")
        return
    if not np.isfinite(angle):
        raise ValueError("angle must be finite")


def _validate_rgba_array(
    colors: ColorArray, *, shape: tuple[int, ...], field_name: str
) -> None:
    if colors.shape != shape:
        raise ValueError(f"{field_name} must have shape {shape}")
    if colors.dtype == np.dtype(np.uint8):
        return
    if colors.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError(f"{field_name} must be rgba8, float32, or float64")
    if not np.all(np.isfinite(colors)):
        raise ValueError(f"floating point {field_name} must be finite")
    if np.any((colors < 0.0) | (colors > 1.0)):
        raise ValueError(f"floating point {field_name} must be in [0, 1]")
