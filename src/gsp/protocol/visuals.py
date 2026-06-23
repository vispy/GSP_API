"""First-slice protocol visual models."""

from __future__ import annotations

from dataclasses import dataclass
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


FloatArray = npt.NDArray[np.float32] | npt.NDArray[np.float64]
ColorArray = npt.NDArray[np.uint8] | npt.NDArray[np.float32] | npt.NDArray[np.float64]
ImageArray = npt.NDArray[np.uint8] | npt.NDArray[np.float32] | npt.NDArray[np.float64]


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
