"""Panel and View2D protocol models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ids import validate_id


class AspectPolicy(str, Enum):
    """2D view aspect policy."""

    AUTO = "auto"
    EQUAL = "equal"


class VisualCoordinateSpace(str, Enum):
    """Coordinate space used by a visual attachment."""

    DATA = "data"
    VIEW = "view"
    PANEL = "panel"


@dataclass(frozen=True, slots=True)
class Panel:
    """Semantic plot panel with a stable protocol identity."""

    id: str
    figure_id: str
    viewport_rect: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.figure_id)
        x, y, width, height = self.viewport_rect
        if width <= 0 or height <= 0:
            raise ValueError("panel viewport width and height must be positive")
        if x < 0 or y < 0:
            raise ValueError("panel viewport origin must be non-negative")


@dataclass(frozen=True, slots=True)
class View2D:
    """Semantic 2D Cartesian view attached to a panel."""

    id: str
    panel_id: str
    x_range: tuple[float, float] = (-1.0, 1.0)
    y_range: tuple[float, float] = (-1.0, 1.0)
    aspect_policy: AspectPolicy = AspectPolicy.AUTO

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        _validate_range("x_range", self.x_range)
        _validate_range("y_range", self.y_range)


@dataclass(frozen=True, slots=True)
class VisualAttachment:
    """Attach a data visual to a panel/view without making axes part of the visual stream."""

    visual_id: str
    panel_id: str
    view_id: str
    coordinate_space: VisualCoordinateSpace = VisualCoordinateSpace.DATA
    z_order: int = 0

    def __post_init__(self) -> None:
        validate_id(self.visual_id)
        validate_id(self.panel_id)
        validate_id(self.view_id)


def _validate_range(name: str, value: tuple[float, float]) -> None:
    low, high = value
    if low >= high:
        raise ValueError(f"{name} minimum must be less than maximum")
