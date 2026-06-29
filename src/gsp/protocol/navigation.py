"""S035 View2D navigation action protocol support."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from .ids import validate_id
from .layout import LogicalPixelRect
from .panels import View2D


class NavigationActionKind(str, Enum):
    """Accepted S035 semantic navigation actions."""

    PAN_BY = "pan-by"
    ZOOM_ABOUT = "zoom-about"
    SET_VIEW = "set-view"
    RESET_VIEW = "reset-view"


class NavigationPlacement(str, Enum):
    """Where a backend applies accepted navigation updates."""

    RETAINED_GPU_STATE = "retained-gpu-state"
    CPU_REMAP = "cpu-remap"
    SERVER_SIDE = "server-side"
    CLIENT_SIDE = "client-side"
    MIXED = "mixed"
    UNSUPPORTED = "unsupported"


class NavigationDiagnosticCode(str, Enum):
    """Structured S035 navigation diagnostic vocabulary."""

    NAVIGATION_UNSUPPORTED = "GSP_NAVIGATION_UNSUPPORTED"
    NAVIGATION_DISABLED = "GSP_NAVIGATION_DISABLED"
    NAVIGATION_STALE_VIEW = "GSP_NAVIGATION_STALE_VIEW"
    NAVIGATION_STALE_LAYOUT = "GSP_NAVIGATION_STALE_LAYOUT"
    NAVIGATION_NONFINITE = "GSP_NAVIGATION_NONFINITE"
    NAVIGATION_INVALID_ZOOM_FACTOR = "GSP_NAVIGATION_INVALID_ZOOM_FACTOR"
    NAVIGATION_INVALID_PANEL_RECT = "GSP_NAVIGATION_INVALID_PANEL_RECT"
    NAVIGATION_RESET_UNAVAILABLE = "GSP_NAVIGATION_RESET_UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class View2DNavigationController:
    """Controller metadata for one target panel/view pair."""

    id: str
    panel_id: str
    view_id: str
    current_view2d_revision: str
    enabled: bool = True
    home_view: View2D | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        validate_id(self.view_id)
        validate_id(self.current_view2d_revision)
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a bool")
        if self.home_view is not None:
            if not isinstance(self.home_view, View2D):
                raise TypeError("home_view must be a View2D")
            if self.home_view.id != self.view_id:
                raise ValueError("home_view id must match controller view_id")
            if self.home_view.panel_id != self.panel_id:
                raise ValueError("home_view panel_id must match controller panel_id")


@dataclass(frozen=True, slots=True)
class PanByAction:
    """Pan a target View2D by a resolved logical-pixel delta."""

    controller_id: str
    view2d_revision: str
    dx_px: float
    dy_px: float
    layout_snapshot_id: str | None = None
    kind: NavigationActionKind = NavigationActionKind.PAN_BY

    def __post_init__(self) -> None:
        _validate_action_header(self.controller_id, self.view2d_revision, self.layout_snapshot_id)
        _validate_kind(self.kind, NavigationActionKind.PAN_BY)
        _validate_finite("dx_px", self.dx_px)
        _validate_finite("dy_px", self.dy_px)


@dataclass(frozen=True, slots=True)
class ZoomAboutAction:
    """Zoom a target View2D around a resolved logical-pixel anchor."""

    controller_id: str
    view2d_revision: str
    anchor_px: tuple[float, float]
    factor_x: float
    factor_y: float
    layout_snapshot_id: str | None = None
    kind: NavigationActionKind = NavigationActionKind.ZOOM_ABOUT

    def __post_init__(self) -> None:
        _validate_action_header(self.controller_id, self.view2d_revision, self.layout_snapshot_id)
        _validate_kind(self.kind, NavigationActionKind.ZOOM_ABOUT)
        _validate_pair("anchor_px", self.anchor_px)
        _validate_zoom_factor("factor_x", self.factor_x)
        _validate_zoom_factor("factor_y", self.factor_y)


@dataclass(frozen=True, slots=True)
class SetViewAction:
    """Replace the target View2D with explicit validated state."""

    controller_id: str
    view2d_revision: str
    view: View2D
    layout_snapshot_id: str | None = None
    kind: NavigationActionKind = NavigationActionKind.SET_VIEW

    def __post_init__(self) -> None:
        _validate_action_header(self.controller_id, self.view2d_revision, self.layout_snapshot_id)
        _validate_kind(self.kind, NavigationActionKind.SET_VIEW)
        if not isinstance(self.view, View2D):
            raise TypeError("view must be a View2D")


@dataclass(frozen=True, slots=True)
class ResetViewAction:
    """Restore the target View2D to the controller home view."""

    controller_id: str
    view2d_revision: str
    layout_snapshot_id: str | None = None
    kind: NavigationActionKind = NavigationActionKind.RESET_VIEW

    def __post_init__(self) -> None:
        _validate_action_header(self.controller_id, self.view2d_revision, self.layout_snapshot_id)
        _validate_kind(self.kind, NavigationActionKind.RESET_VIEW)


@dataclass(frozen=True, slots=True)
class NavigationResult:
    """Result of applying a semantic navigation action."""

    accepted: bool
    controller_id: str
    old_view2d_revision: str
    diagnostics: tuple[str, ...] = ()
    new_view2d_revision: str | None = None
    view: View2D | None = None
    view_snapshot_id: str | None = None
    layout_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool")
        validate_id(self.controller_id)
        validate_id(self.old_view2d_revision)
        if self.new_view2d_revision is not None:
            validate_id(self.new_view2d_revision)
        if self.view_snapshot_id is not None:
            validate_id(self.view_snapshot_id)
        if self.layout_snapshot_id is not None:
            validate_id(self.layout_snapshot_id)
        for diagnostic in self.diagnostics:
            if not diagnostic:
                raise ValueError("navigation diagnostics must not contain empty strings")
        if self.accepted:
            if self.new_view2d_revision is None or self.view is None:
                raise ValueError("accepted navigation results require new revision and view")
            if not isinstance(self.view, View2D):
                raise TypeError("view must be a View2D")
        elif not self.diagnostics:
            raise ValueError("rejected navigation results require diagnostics")


def pan_view2d(view: View2D, panel_rect: LogicalPixelRect, dx_px: float, dy_px: float) -> View2D:
    """Return the View2D produced by panning in resolved logical pixels."""
    _validate_panel_rect(panel_rect)
    _validate_finite("dx_px", dx_px)
    _validate_finite("dy_px", dy_px)
    x0, x1 = view.x_range
    y0, y1 = view.y_range
    data_dx = -dx_px / panel_rect.width * (x1 - x0)
    data_dy = -dy_px / panel_rect.height * (y1 - y0)
    return View2D(
        id=view.id,
        panel_id=view.panel_id,
        x_range=(x0 + data_dx, x1 + data_dx),
        y_range=(y0 + data_dy, y1 + data_dy),
        aspect_policy=view.aspect_policy,
        kind=view.kind,
        clip=view.clip,
    )


def zoom_view2d_about(
    view: View2D,
    panel_rect: LogicalPixelRect,
    anchor_px: tuple[float, float],
    factor_x: float,
    factor_y: float,
) -> View2D:
    """Return the View2D produced by zooming about a resolved logical-pixel anchor."""
    _validate_panel_rect(panel_rect)
    _validate_pair("anchor_px", anchor_px)
    _validate_zoom_factor("factor_x", factor_x)
    _validate_zoom_factor("factor_y", factor_y)
    tx = (anchor_px[0] - panel_rect.x) / panel_rect.width
    ty = (anchor_px[1] - panel_rect.y) / panel_rect.height
    x0, x1 = view.x_range
    y0, y1 = view.y_range
    anchor_data_x = x0 + tx * (x1 - x0)
    anchor_data_y = y0 + ty * (y1 - y0)
    new_span_x = (x1 - x0) / factor_x
    new_span_y = (y1 - y0) / factor_y
    return View2D(
        id=view.id,
        panel_id=view.panel_id,
        x_range=(anchor_data_x - tx * new_span_x, anchor_data_x + (1.0 - tx) * new_span_x),
        y_range=(anchor_data_y - ty * new_span_y, anchor_data_y + (1.0 - ty) * new_span_y),
        aspect_policy=view.aspect_policy,
        kind=view.kind,
        clip=view.clip,
    )


def _validate_action_header(
    controller_id: str, view2d_revision: str, layout_snapshot_id: str | None
) -> None:
    validate_id(controller_id)
    validate_id(view2d_revision)
    if layout_snapshot_id is not None:
        validate_id(layout_snapshot_id)


def _validate_kind(actual: NavigationActionKind, expected: NavigationActionKind) -> None:
    if actual is not expected:
        raise ValueError(f"navigation action kind must be {expected.value!r}")


def _validate_panel_rect(panel_rect: LogicalPixelRect) -> None:
    if not isinstance(panel_rect, LogicalPixelRect):
        raise TypeError("panel_rect must be a LogicalPixelRect")
    if panel_rect.width <= 0.0 or panel_rect.height <= 0.0:
        raise ValueError(
            f"{NavigationDiagnosticCode.NAVIGATION_INVALID_PANEL_RECT.value}: "
            "panel rectangle width and height must be positive"
        )


def _validate_pair(field_name: str, value: tuple[float, float]) -> None:
    if len(value) != 2:
        raise ValueError(f"{field_name} must contain two values")
    _validate_finite(f"{field_name}[0]", value[0])
    _validate_finite(f"{field_name}[1]", value[1])


def _validate_zoom_factor(field_name: str, value: float) -> None:
    _validate_finite(field_name, value)
    if value <= 0.0:
        raise ValueError(
            f"{NavigationDiagnosticCode.NAVIGATION_INVALID_ZOOM_FACTOR.value}: "
            f"{field_name} must be positive"
        )


def _validate_finite(field_name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(
            f"{NavigationDiagnosticCode.NAVIGATION_NONFINITE.value}: {field_name} must be finite"
        )
