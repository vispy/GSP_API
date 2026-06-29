"""S026 color mapping and colorbar protocol models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import numpy.typing as npt

from .ids import validate_id


ScalarArray = npt.NDArray[np.float32] | npt.NDArray[np.float64]


class ColorMapKind(str, Enum):
    """Color map reference kind."""

    NAMED = "named"


class ColorMapId(str, Enum):
    """Canonical S026 named colormaps."""

    GRAY = "gray"
    VIRIDIS = "viridis"
    MAGMA = "magma"
    PLASMA = "plasma"
    INFERNO = "inferno"
    CIVIDIS = "cividis"


class NormalizeKind(str, Enum):
    """S026 normalization kind."""

    LINEAR = "linear"


class ScalarColorSlot(str, Enum):
    """Visual color slots that may carry scalar color encodings."""

    IMAGE = "image"
    COLOR = "color"
    FILL = "fill"
    FACE_COLOR = "face_color"


class ScalarColorDomain(str, Enum):
    """Item domain for scalar color values."""

    TEXEL = "texel"
    ITEM = "item"
    FACE = "face"


class ColorbarOrientation(str, Enum):
    """Semantic colorbar orientation."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class ColorbarPlacement(str, Enum):
    """Semantic colorbar placement side."""

    RIGHT = "right"
    LEFT = "left"
    BOTTOM = "bottom"
    TOP = "top"


class ScalarRangeClass(str, Enum):
    """Scalar range class after linear normalization."""

    UNDER = "under"
    IN_RANGE = "in_range"
    OVER = "over"


@dataclass(frozen=True, slots=True)
class ColorMapRef:
    """Reference to a canonical GSP colormap."""

    id: ColorMapId
    kind: ColorMapKind = ColorMapKind.NAMED

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ColorMapKind):
            raise TypeError("kind must be a ColorMapKind")
        if self.kind is not ColorMapKind.NAMED:
            raise ValueError("S026 accepts named colormaps only")
        if not isinstance(self.id, ColorMapId):
            raise TypeError("id must be a ColorMapId")


@dataclass(frozen=True, slots=True)
class LinearNormalize:
    """Explicit linear scalar normalization with clipping."""

    vmin: float
    vmax: float
    clip: bool = True
    kind: NormalizeKind = NormalizeKind.LINEAR

    def __post_init__(self) -> None:
        if not isinstance(self.kind, NormalizeKind):
            raise TypeError("kind must be a NormalizeKind")
        if self.kind is not NormalizeKind.LINEAR:
            raise ValueError("S026 accepts linear normalization only")
        if not np.isfinite(self.vmin) or not np.isfinite(self.vmax):
            raise ValueError("vmin and vmax must be finite")
        if self.vmin >= self.vmax:
            raise ValueError("vmin must be less than vmax")
        if self.clip is not True:
            raise ValueError("S026 linear normalization requires clip=True")


@dataclass(frozen=True, slots=True)
class ColorScale:
    """Shared scalar-to-color mapping resource."""

    id: str
    colormap: ColorMapRef
    normalize: LinearNormalize
    description: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        if not isinstance(self.colormap, ColorMapRef):
            raise TypeError("colormap must be a ColorMapRef")
        if not isinstance(self.normalize, LinearNormalize):
            raise TypeError("normalize must be a LinearNormalize")
        if self.description is not None and not isinstance(self.description, str):
            raise TypeError("description must be a string")


@dataclass(frozen=True, slots=True)
class ScalarColorEncoding:
    """Slot-specific scalar values linked to a color scale."""

    slot: ScalarColorSlot
    values: ScalarArray
    color_scale_id: str
    alpha: float = 1.0
    domain: ScalarColorDomain | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.slot, ScalarColorSlot):
            raise TypeError("slot must be a ScalarColorSlot")
        validate_id(self.color_scale_id)
        _validate_scalar_values(self.values, field_name="values")
        if not np.isfinite(self.alpha):
            raise ValueError("alpha must be finite")
        if self.alpha < 0.0 or self.alpha > 1.0:
            raise ValueError("alpha must be in [0, 1]")
        if self.domain is not None and not isinstance(self.domain, ScalarColorDomain):
            raise TypeError("domain must be a ScalarColorDomain")


@dataclass(frozen=True, slots=True)
class ColorbarGuideStyle:
    """Canvas-pixel colorbar style hints shared by backend lowerings."""

    ramp_width_px: float = 36.0
    tick_length_px: float = 6.0
    label_gap_px: float = 6.0
    min_length_px: float = 160.0
    length_fraction: float = 0.62

    def __post_init__(self) -> None:
        _validate_positive_finite("ramp_width_px", self.ramp_width_px)
        _validate_positive_finite("tick_length_px", self.tick_length_px)
        _validate_positive_finite("label_gap_px", self.label_gap_px)
        _validate_positive_finite("min_length_px", self.min_length_px)
        _validate_positive_finite("length_fraction", self.length_fraction)
        if self.length_fraction > 1.0:
            raise ValueError("length_fraction must be <= 1")


@dataclass(frozen=True, slots=True)
class ColorbarGuide:
    """Semantic guide representing a color scale in a panel."""

    id: str
    panel_id: str
    color_scale_id: str
    linked_visual_ids: tuple[str, ...] = ()
    orientation: ColorbarOrientation = ColorbarOrientation.VERTICAL
    placement: ColorbarPlacement | None = None
    label: str = ""
    ticks: tuple[float, ...] = ()
    tick_labels: tuple[str, ...] | None = None
    style: ColorbarGuideStyle = field(default_factory=ColorbarGuideStyle)

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        validate_id(self.color_scale_id)
        for visual_id in self.linked_visual_ids:
            validate_id(visual_id)
        if not isinstance(self.orientation, ColorbarOrientation):
            raise TypeError("orientation must be a ColorbarOrientation")
        placement = self.placement or _default_colorbar_placement(self.orientation)
        if not isinstance(placement, ColorbarPlacement):
            raise TypeError("placement must be a ColorbarPlacement")
        _validate_colorbar_placement(self.orientation, placement)
        object.__setattr__(self, "placement", placement)
        if not isinstance(self.label, str):
            raise TypeError("label must be a string")
        if not isinstance(self.style, ColorbarGuideStyle):
            raise TypeError("style must be a ColorbarGuideStyle")
        if any(not np.isfinite(tick) for tick in self.ticks):
            raise ValueError("ticks must be finite")
        if self.tick_labels is not None:
            if len(self.tick_labels) != len(self.ticks):
                raise ValueError("tick_labels length must match ticks")
            if any(not isinstance(label, str) for label in self.tick_labels):
                raise TypeError("tick_labels entries must be strings")


def _validate_scalar_values(values: ScalarArray, *, field_name: str) -> None:
    if values.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError(f"{field_name} must be float32 or float64")
    if values.ndim < 1:
        raise ValueError(f"{field_name} must have at least one dimension")
    if values.size == 0:
        raise ValueError(f"{field_name} must not be empty")
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{field_name} must be finite")


def _validate_positive_finite(field_name: str, value: float) -> None:
    if not np.isfinite(value) or value <= 0.0:
        raise ValueError(f"{field_name} must be positive and finite")


def _default_colorbar_placement(
    orientation: ColorbarOrientation,
) -> ColorbarPlacement:
    if orientation is ColorbarOrientation.VERTICAL:
        return ColorbarPlacement.RIGHT
    return ColorbarPlacement.BOTTOM


def _validate_colorbar_placement(
    orientation: ColorbarOrientation, placement: ColorbarPlacement
) -> None:
    if orientation is ColorbarOrientation.VERTICAL and placement not in (
        ColorbarPlacement.RIGHT,
        ColorbarPlacement.LEFT,
    ):
        raise ValueError("vertical colorbars must be placed right or left")
    if orientation is ColorbarOrientation.HORIZONTAL and placement not in (
        ColorbarPlacement.BOTTOM,
        ColorbarPlacement.TOP,
    ):
        raise ValueError("horizontal colorbars must be placed bottom or top")


def validate_scalar_encoding_shape(
    encoding: ScalarColorEncoding,
    *,
    slot: ScalarColorSlot,
    shape: tuple[int, ...],
    domain: ScalarColorDomain,
) -> None:
    """Validate a scalar color encoding against a visual slot and item shape."""
    if encoding.slot is not slot:
        raise ValueError(f"scalar encoding slot must be {slot.value}")
    if encoding.values.shape != shape:
        raise ValueError(f"scalar encoding values must have shape {shape}")
    if encoding.domain is not None and encoding.domain is not domain:
        raise ValueError(f"scalar encoding domain must be {domain.value}")
