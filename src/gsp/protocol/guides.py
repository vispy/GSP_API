"""Semantic guide protocol models for axes and panel text."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math

from .ids import validate_id


class AxisDimension(str, Enum):
    """Supported 2D axis dimensions."""

    X = "x"
    Y = "y"


class AxisSide(str, Enum):
    """Supported 2D axis sides for the first guide slice."""

    BOTTOM = "bottom"
    LEFT = "left"


class TickSpecKind(str, Enum):
    """Tick authority for an axis guide."""

    NONE = "none"
    EXPLICIT = "explicit"
    AUTO_LINEAR_NICE_V0 = "auto-linear-nice-v0"
    BACKEND_ADAPTED = "backend-adapted"


class GuideQueryPolicy(str, Enum):
    """Whether guide contributions participate in guide-scoped queries."""

    NON_QUERYABLE = "non-queryable"
    QUERYABLE = "queryable"


class PanelTextRole(str, Enum):
    """Panel-level text guide roles."""

    TITLE = "title"
    SUBTITLE = "subtitle"


@dataclass(frozen=True, slots=True)
class AxisGuideStyle:
    """Logical-pixel style hints for axis guides."""

    axis_label_font_size_px: float | None = None
    tick_label_font_size_px: float | None = None
    tick_length_px: float | None = None
    tick_width_px: float | None = None
    tick_label_padding_px: float | None = None
    axis_label_padding_px: float | None = None
    grid_width_px: float | None = None
    guide_margin_px: float | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "axis_label_font_size_px",
            "tick_label_font_size_px",
            "tick_length_px",
            "tick_width_px",
            "tick_label_padding_px",
            "axis_label_padding_px",
            "grid_width_px",
            "guide_margin_px",
        ):
            _validate_optional_nonnegative(field_name, getattr(self, field_name))


@dataclass(frozen=True, slots=True)
class PanelTextGuideStyle:
    """Logical-pixel style hints for panel text guides."""

    title_font_size_px: float | None = None
    guide_margin_px: float | None = None

    def __post_init__(self) -> None:
        _validate_optional_nonnegative("title_font_size_px", self.title_font_size_px)
        _validate_optional_nonnegative("guide_margin_px", self.guide_margin_px)


@dataclass(frozen=True, slots=True)
class TickSpec:
    """Semantic tick specification for an axis guide."""

    kind: TickSpecKind = TickSpecKind.AUTO_LINEAR_NICE_V0
    explicit_values: tuple[float, ...] = ()
    explicit_labels: tuple[str, ...] | None = None
    target_count: int | None = 7

    def __post_init__(self) -> None:
        if self.kind == TickSpecKind.EXPLICIT:
            if not self.explicit_values:
                raise ValueError("explicit TickSpec requires explicit_values")
            if self.explicit_labels is not None and len(self.explicit_labels) != len(self.explicit_values):
                raise ValueError("explicit tick labels must match explicit tick values")
        if self.target_count is not None and self.target_count <= 0:
            raise ValueError("target_count must be positive")


@dataclass(frozen=True, slots=True)
class AxisGuide:
    """Semantic axis guide intent attached to a View2D."""

    id: str
    view_id: str
    dimension: AxisDimension
    side: AxisSide
    visible: bool = True
    label_text: str | None = None
    spine_visible: bool = True
    grid_visible: bool = False
    tick_spec: TickSpec = field(default_factory=TickSpec)
    query_policy: GuideQueryPolicy = GuideQueryPolicy.NON_QUERYABLE
    style: AxisGuideStyle = field(default_factory=AxisGuideStyle)

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.view_id)
        if not isinstance(self.style, AxisGuideStyle):
            raise TypeError("AxisGuide style must be an AxisGuideStyle")
        if self.dimension == AxisDimension.X and self.side != AxisSide.BOTTOM:
            raise ValueError("the first axis guide slice supports x guides on the bottom side only")
        if self.dimension == AxisDimension.Y and self.side != AxisSide.LEFT:
            raise ValueError("the first axis guide slice supports y guides on the left side only")


@dataclass(frozen=True, slots=True)
class PanelTextGuide:
    """Semantic panel-level text guide such as a title."""

    id: str
    panel_id: str
    role: PanelTextRole
    text: str
    query_policy: GuideQueryPolicy = GuideQueryPolicy.NON_QUERYABLE
    style: PanelTextGuideStyle = field(default_factory=PanelTextGuideStyle)

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        if not isinstance(self.style, PanelTextGuideStyle):
            raise TypeError("PanelTextGuide style must be a PanelTextGuideStyle")
        if not self.text:
            raise ValueError("panel text guide text must not be empty")


def _validate_optional_nonnegative(field_name: str, value: float | None) -> None:
    if value is None:
        return
    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")
    if value < 0.0:
        raise ValueError(f"{field_name} must be non-negative")
