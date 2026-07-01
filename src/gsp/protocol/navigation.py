"""S035 View2D navigation action protocol support."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
import sys

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


class NavigationPointerEventKind(str, Enum):
    """Pointer events accepted by the optional S035 input adapter."""

    BUTTON_PRESS = "button-press"
    BUTTON_RELEASE = "button-release"
    MOUSE_MOVE = "mouse-move"
    WHEEL = "wheel"
    DOUBLE_CLICK = "double-click"


_DATOVIZ_PANZOOM_ZOOM_MIN_DEFAULT = 1e-3
_DATOVIZ_PANZOOM_ZOOM_MAX_DEFAULT = 1e4
_DATOVIZ_PANZOOM_APPLE_DRAG_COEF = 0.003
_DATOVIZ_PANZOOM_APPLE_WHEEL_COEF = 12.0
_DATOVIZ_PANZOOM_DEFAULT_DRAG_COEF = 0.002
_DATOVIZ_PANZOOM_DEFAULT_WHEEL_COEF = 120.0


@dataclass(frozen=True, slots=True)
class _DatovizPanzoomProfile:
    """Private Datoviz v0.4-dev panzoom constants used by the strict GSP adapter."""

    drag_coef: float
    wheel_coef: float
    zoom_min: float = _DATOVIZ_PANZOOM_ZOOM_MIN_DEFAULT
    zoom_max: float = _DATOVIZ_PANZOOM_ZOOM_MAX_DEFAULT

    @classmethod
    def for_platform(cls, platform: str | None = None) -> "_DatovizPanzoomProfile":
        """Return the profile matching Datoviz v0.4-dev panzoom.c for a platform."""
        effective_platform = sys.platform if platform is None else platform
        if effective_platform == "darwin":
            return cls(
                drag_coef=_DATOVIZ_PANZOOM_APPLE_DRAG_COEF,
                wheel_coef=_DATOVIZ_PANZOOM_APPLE_WHEEL_COEF,
            )
        return cls(
            drag_coef=_DATOVIZ_PANZOOM_DEFAULT_DRAG_COEF,
            wheel_coef=_DATOVIZ_PANZOOM_DEFAULT_WHEEL_COEF,
        )

    def clamp_zoom(self, value: float) -> float:
        """Clamp a Datoviz-style zoom factor to the v0.4-dev defaults."""
        if not math.isfinite(value) or value <= 0.0:
            return 1.0
        return min(max(value, self.zoom_min), self.zoom_max)

    def drag_zoom_factor(
        self, panel_rect: LogicalPixelRect, dx_px: float, dy_px: float
    ) -> tuple[float, float]:
        """Return Datoviz right-drag zoom factors for a GSP logical-pixel shift.

        GSP pointer y increases upward. Datoviz pointer y increases downward and
        then applies ``-2 * dy / h``. After coordinate conversion, the GSP
        vertical normalized shift is therefore ``+2 * dy / h``.
        """
        _validate_panel_rect(panel_rect)
        _validate_finite("dx_px", dx_px)
        _validate_finite("dy_px", dy_px)
        average_extent_px = 0.5 * (panel_rect.width + panel_rect.height)
        shift_x = 2.0 * dx_px / panel_rect.width
        shift_y = 2.0 * dy_px / panel_rect.height
        return (
            math.exp(self.drag_coef * average_extent_px * shift_x),
            math.exp(self.drag_coef * average_extent_px * shift_y),
        )

    def wheel_zoom_factor(
        self, panel_rect: LogicalPixelRect, scroll_steps: float
    ) -> tuple[float, float]:
        """Return Datoviz wheel zoom factors for a wheel direction value."""
        _validate_panel_rect(panel_rect)
        _validate_finite("scroll_steps", scroll_steps)
        d = scroll_steps / 4.0
        shift_x = self.wheel_coef * d
        shift_y = -(panel_rect.height / panel_rect.width) * shift_x
        average_extent_px = 0.5 * (panel_rect.width + panel_rect.height)
        normalized_x = 2.0 * shift_x / panel_rect.width
        normalized_y = -2.0 * shift_y / panel_rect.height
        return (
            math.exp(self.drag_coef * average_extent_px * normalized_x),
            math.exp(self.drag_coef * average_extent_px * normalized_y),
        )

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


NavigationAction = PanByAction | ZoomAboutAction | SetViewAction | ResetViewAction


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


@dataclass(frozen=True, slots=True)
class NavigationPointerEvent:
    """Backend-neutral pointer event resolved to target-panel logical pixels."""

    kind: NavigationPointerEventKind
    x_px: float
    y_px: float
    left_button: bool = False
    right_button: bool = False
    scroll_steps: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.kind, NavigationPointerEventKind):
            raise TypeError("kind must be a NavigationPointerEventKind")
        _validate_finite("x_px", self.x_px)
        _validate_finite("y_px", self.y_px)
        if not isinstance(self.left_button, bool):
            raise TypeError("left_button must be a bool")
        if not isinstance(self.right_button, bool):
            raise TypeError("right_button must be a bool")
        _validate_finite("scroll_steps", self.scroll_steps)


class View2DNavigationInputAdapter:
    """Convert resolved pointer events into deterministic S035 navigation actions."""

    __slots__ = (
        "_controller_id",
        "_drag_kind",
        "_drag_start_px",
        "_drag_start_zoom",
        "_drag_last_px",
        "_layout_snapshot_id",
        "_panel_rect",
        "_profile",
        "_view2d_revision",
        "_zoom",
    )

    def __init__(
        self,
        *,
        controller_id: str,
        view2d_revision: str,
        panel_rect: LogicalPixelRect,
        layout_snapshot_id: str | None = None,
    ) -> None:
        validate_id(controller_id)
        validate_id(view2d_revision)
        if layout_snapshot_id is not None:
            validate_id(layout_snapshot_id)
        _validate_panel_rect(panel_rect)
        self._controller_id = controller_id
        self._view2d_revision = view2d_revision
        self._layout_snapshot_id = layout_snapshot_id
        self._panel_rect = panel_rect
        self._profile = _DatovizPanzoomProfile.for_platform()
        self._zoom = (1.0, 1.0)
        self._drag_last_px: tuple[float, float] | None = None
        self._drag_start_px: tuple[float, float] | None = None
        self._drag_start_zoom: tuple[float, float] | None = None
        self._drag_kind: str | None = None

    @property
    def view2d_revision(self) -> str:
        """Return the revision token used for emitted actions."""
        return self._view2d_revision

    @property
    def panel_rect(self) -> LogicalPixelRect:
        """Return the current target-panel logical-pixel rectangle."""
        return self._panel_rect

    def set_panel_rect(self, panel_rect: LogicalPixelRect) -> None:
        """Update the resolved panel rectangle used by helper coordinate conversions."""
        _validate_panel_rect(panel_rect)
        self._panel_rect = panel_rect

    def update_view2d_revision(self, view2d_revision: str) -> None:
        """Update the revision token used by subsequent emitted actions."""
        validate_id(view2d_revision)
        self._view2d_revision = view2d_revision

    def accept_navigation_result(self, result: NavigationResult) -> None:
        """Advance the adapter revision after an accepted navigation result."""
        if result.controller_id != self._controller_id:
            raise ValueError("navigation result targets a different controller")
        if result.accepted and result.new_view2d_revision is not None:
            self.update_view2d_revision(result.new_view2d_revision)

    def handle_pointer_event(self, event: NavigationPointerEvent) -> NavigationAction | None:
        """Return a semantic navigation action for one pointer event, if any."""
        if event.kind is NavigationPointerEventKind.BUTTON_PRESS:
            if event.left_button:
                self._drag_last_px = (event.x_px, event.y_px)
                self._drag_start_px = (event.x_px, event.y_px)
                self._drag_start_zoom = self._zoom
                self._drag_kind = "pan"
            elif event.right_button:
                self._drag_last_px = (event.x_px, event.y_px)
                self._drag_start_px = (event.x_px, event.y_px)
                self._drag_start_zoom = self._zoom
                self._drag_kind = "zoom"
            else:
                self._clear_drag()
            return None
        if event.kind is NavigationPointerEventKind.BUTTON_RELEASE:
            self._clear_drag()
            return None
        if event.kind is NavigationPointerEventKind.MOUSE_MOVE:
            return self._handle_mouse_move(event)
        if event.kind is NavigationPointerEventKind.WHEEL:
            return self._handle_wheel(event)
        if event.kind is NavigationPointerEventKind.DOUBLE_CLICK:
            self._zoom = (1.0, 1.0)
            self._clear_drag()
            return ResetViewAction(
                controller_id=self._controller_id,
                view2d_revision=self._view2d_revision,
                layout_snapshot_id=self._layout_snapshot_id,
            )
        raise ValueError(f"unsupported pointer event kind: {event.kind!r}")

    def _handle_mouse_move(self, event: NavigationPointerEvent) -> NavigationAction | None:
        if self._drag_last_px is None:
            return None
        last_x, last_y = self._drag_last_px
        self._drag_last_px = (event.x_px, event.y_px)
        dx_px = event.x_px - last_x
        dy_px = event.y_px - last_y
        if dx_px == 0.0 and dy_px == 0.0:
            return None
        if self._drag_kind == "zoom":
            if self._drag_start_px is None or self._drag_start_zoom is None:
                return None
            start_x, start_y = self._drag_start_px
            start_zoom_x, start_zoom_y = self._drag_start_zoom
            absolute_factor_x, absolute_factor_y = self._profile.drag_zoom_factor(
                self._panel_rect,
                event.x_px - start_x,
                event.y_px - start_y,
            )
            target_zoom = (
                self._profile.clamp_zoom(start_zoom_x * absolute_factor_x),
                self._profile.clamp_zoom(start_zoom_y * absolute_factor_y),
            )
            factor_x, factor_y = self._relative_zoom_factors(target_zoom)
            if factor_x == 1.0 and factor_y == 1.0:
                return None
            self._zoom = target_zoom
            return ZoomAboutAction(
                controller_id=self._controller_id,
                view2d_revision=self._view2d_revision,
                anchor_px=self._drag_start_px,
                factor_x=factor_x,
                factor_y=factor_y,
                layout_snapshot_id=self._layout_snapshot_id,
            )
        return PanByAction(
            controller_id=self._controller_id,
            view2d_revision=self._view2d_revision,
            dx_px=dx_px,
            dy_px=dy_px,
            layout_snapshot_id=self._layout_snapshot_id,
        )

    def _handle_wheel(self, event: NavigationPointerEvent) -> ZoomAboutAction | None:
        if event.scroll_steps == 0.0:
            return None
        factor_x, factor_y = self._profile.wheel_zoom_factor(
            self._panel_rect, event.scroll_steps
        )
        target_zoom = (
            self._profile.clamp_zoom(self._zoom[0] * factor_x),
            self._profile.clamp_zoom(self._zoom[1] * factor_y),
        )
        factor_x, factor_y = self._relative_zoom_factors(target_zoom)
        if factor_x == 1.0 and factor_y == 1.0:
            return None
        self._zoom = target_zoom
        return ZoomAboutAction(
            controller_id=self._controller_id,
            view2d_revision=self._view2d_revision,
            anchor_px=(event.x_px, event.y_px),
            factor_x=factor_x,
            factor_y=factor_y,
            layout_snapshot_id=self._layout_snapshot_id,
        )

    def _relative_zoom_factors(
        self, target_zoom: tuple[float, float]
    ) -> tuple[float, float]:
        current_x, current_y = self._zoom
        if current_x <= 0.0 or current_y <= 0.0:
            self._zoom = (1.0, 1.0)
            current_x, current_y = self._zoom
        return target_zoom[0] / current_x, target_zoom[1] / current_y

    def _clear_drag(self) -> None:
        self._drag_last_px = None
        self._drag_start_px = None
        self._drag_start_zoom = None
        self._drag_kind = None


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


def navigation_pointer_event_from_ndc(
    *,
    kind: NavigationPointerEventKind,
    x_ndc: float,
    y_ndc: float,
    panel_rect: LogicalPixelRect,
    left_button: bool = False,
    right_button: bool = False,
    scroll_steps: float = 0.0,
) -> NavigationPointerEvent:
    """Create a pointer event from target-panel NDC coordinates."""
    _validate_panel_rect(panel_rect)
    _validate_finite("x_ndc", x_ndc)
    _validate_finite("y_ndc", y_ndc)
    return NavigationPointerEvent(
        kind=kind,
        x_px=panel_rect.x + (x_ndc + 1.0) * 0.5 * panel_rect.width,
        y_px=panel_rect.y + (y_ndc + 1.0) * 0.5 * panel_rect.height,
        left_button=left_button,
        right_button=right_button,
        scroll_steps=scroll_steps,
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
