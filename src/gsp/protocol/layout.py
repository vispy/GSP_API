"""Resolved layout protocol models for GSP guide geometry."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Literal

from .ids import validate_id


class ConformanceTier(str, Enum):
    """Tiered conformance target for guide/layout review."""

    SEMANTIC_STRICT = "semantic_strict"
    LAYOUT_STRICT = "layout_strict"
    RASTER_TOLERANT = "raster_tolerant"
    PIXEL_PARITY = "pixel_parity"


class PixelOrigin(str, Enum):
    """Pixel origin for logical screen coordinates."""

    TOP_LEFT = "top-left"
    BOTTOM_LEFT = "bottom-left"


class LayoutResolveStatus(str, Enum):
    """Outcome of resolving layout for a render target."""

    RESOLVED = "resolved"
    ADAPTED = "adapted"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"


class LayoutDiagnosticStatus(str, Enum):
    """Standard statuses for layout and guide adaptation diagnostics."""

    NATIVE = "native"
    RESOLVED = "resolved"
    ADAPTED = "adapted"
    DEGRADED = "degraded"
    UNSUPPORTED = "unsupported"
    MISSING = "missing"
    BACKEND_DEFAULT_USED = "backend_default_used"
    FONT_SUBSTITUTED = "font_substituted"
    LAYOUT_SNAPSHOT_NOT_USED = "layout_snapshot_not_used"
    QUERY_SEMANTICS_MISSING = "query_semantics_missing"
    GRID_CLIP_NOT_ENFORCED = "grid_clip_not_enforced"


GuideBoxKind = Literal[
    "axis",
    "axis_label",
    "tick_label",
    "title",
    "legend",
    "colorbar",
    "grid",
    "panel_text",
]


@dataclass(frozen=True, slots=True)
class LogicalPixelRect:
    """Rectangle in logical pixels."""

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        _validate_finite("x", self.x)
        _validate_finite("y", self.y)
        _validate_finite("width", self.width)
        _validate_finite("height", self.height)
        if self.width < 0.0 or self.height < 0.0:
            raise ValueError("logical pixel rectangle width/height must be non-negative")


@dataclass(frozen=True, slots=True)
class LayoutAnchor:
    """Anchor point in logical pixels."""

    x: float
    y: float

    def __post_init__(self) -> None:
        _validate_finite("x", self.x)
        _validate_finite("y", self.y)


@dataclass(frozen=True, slots=True)
class RenderTarget:
    """Logical render target used to resolve layout."""

    logical_width_px: float
    logical_height_px: float
    device_scale: float = 1.0
    dpi: float | None = None
    pixel_origin: PixelOrigin = PixelOrigin.TOP_LEFT
    query_coordinate_space: str = "panel"

    def __post_init__(self) -> None:
        _validate_positive("logical_width_px", self.logical_width_px)
        _validate_positive("logical_height_px", self.logical_height_px)
        _validate_positive("device_scale", self.device_scale)
        if self.dpi is not None:
            _validate_positive("dpi", self.dpi)
        if not self.query_coordinate_space:
            raise ValueError("query_coordinate_space must not be empty")

    @property
    def framebuffer_width_px(self) -> int:
        """Physical framebuffer width implied by logical size and device scale."""
        return int(round(self.logical_width_px * self.device_scale))

    @property
    def framebuffer_height_px(self) -> int:
        """Physical framebuffer height implied by logical size and device scale."""
        return int(round(self.logical_height_px * self.device_scale))


@dataclass(frozen=True, slots=True)
class LayoutDiagnostic:
    """Diagnostic for layout support, adaptation, or fallback behavior."""

    code: str
    status: LayoutDiagnosticStatus
    message: str | None = None

    def __post_init__(self) -> None:
        if not self.code:
            raise ValueError("layout diagnostic code must not be empty")
        if self.message is not None and not self.message:
            raise ValueError("layout diagnostic message must not be empty")


@dataclass(frozen=True, slots=True)
class ResolvedGuideBox:
    """Resolved box for one guide contribution."""

    guide_id: str
    kind: GuideBoxKind
    rect_px: LogicalPixelRect
    anchor_px: LayoutAnchor | None = None
    role: str | None = None
    layer: str | None = None
    diagnostics: tuple[LayoutDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        validate_id(self.guide_id)
        if not self.kind:
            raise ValueError("guide box kind must not be empty")
        if self.role is not None and not self.role:
            raise ValueError("guide box role must not be empty")
        if self.layer is not None and not self.layer:
            raise ValueError("guide box layer must not be empty")


@dataclass(frozen=True, slots=True)
class LayoutLayer:
    """Layer assignment for a resolved scene object."""

    object_id: str
    layer: str
    z_order: float = 0.0

    def __post_init__(self) -> None:
        validate_id(self.object_id)
        if not self.layer:
            raise ValueError("layout layer name must not be empty")
        _validate_finite("z_order", self.z_order)


@dataclass(frozen=True, slots=True)
class ResolvedLayoutSnapshot:
    """Derived layout state for one scene/view/render target."""

    snapshot_id: str
    render_target: RenderTarget
    panel_rect_px: LogicalPixelRect
    plot_rect_px: LogicalPixelRect
    view_id: str | None = None
    data_to_screen_transform: tuple[float, ...] = (
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
    )
    guide_boxes: tuple[ResolvedGuideBox, ...] = ()
    guide_anchors: tuple[ResolvedGuideBox, ...] = ()
    tick_label_boxes: tuple[ResolvedGuideBox, ...] = ()
    axis_label_boxes: tuple[ResolvedGuideBox, ...] = ()
    title_boxes: tuple[ResolvedGuideBox, ...] = ()
    legend_boxes: tuple[ResolvedGuideBox, ...] = ()
    colorbar_boxes: tuple[ResolvedGuideBox, ...] = ()
    grid_clip_rect_px: LogicalPixelRect | None = None
    z_layers: tuple[LayoutLayer, ...] = ()
    diagnostics: tuple[LayoutDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        validate_id(self.snapshot_id)
        if self.view_id is not None:
            validate_id(self.view_id)
        if len(self.data_to_screen_transform) not in (6, 9):
            raise ValueError("data_to_screen_transform must contain 6 or 9 finite values")
        for value in self.data_to_screen_transform:
            _validate_finite("data_to_screen_transform", value)


@dataclass(frozen=True, slots=True)
class LayoutResolveRequest:
    """Request to resolve layout for a scene and render target."""

    request_id: str
    scene_id: str
    render_target: RenderTarget
    requested_tier: ConformanceTier = ConformanceTier.LAYOUT_STRICT

    def __post_init__(self) -> None:
        validate_id(self.request_id)
        validate_id(self.scene_id)


@dataclass(frozen=True, slots=True)
class LayoutResolveResult:
    """Result of a layout resolve/get operation."""

    request_id: str
    status: LayoutResolveStatus
    snapshot: ResolvedLayoutSnapshot | None = None
    diagnostics: tuple[LayoutDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        validate_id(self.request_id)
        if self.status == LayoutResolveStatus.RESOLVED and self.snapshot is None:
            raise ValueError("resolved layout results require a snapshot")
        if self.status != LayoutResolveStatus.RESOLVED and not self.diagnostics:
            raise ValueError("non-resolved layout results require diagnostics")


def logical_px_to_points(logical_px: float, dpi: float) -> float:
    """Convert logical pixels to typographic points for a DPI-bound backend."""
    _validate_finite("logical_px", logical_px)
    _validate_positive("dpi", dpi)
    return logical_px * 72.0 / dpi


def _validate_finite(field_name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _validate_positive(field_name: str, value: float) -> None:
    _validate_finite(field_name, value)
    if value <= 0.0:
        raise ValueError(f"{field_name} must be positive")
