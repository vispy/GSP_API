"""Canvas size policy and resolved canvas metrics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math


DEFAULT_REFERENCE_DPI = 96.0
MM_PER_INCH = 25.4


class CanvasSizePolicy(str, Enum):
    """Policy used to interpret a requested canvas size."""

    PIXEL_EXACT = "pixel_exact"
    HOST_LOGICAL_PX = "host_logical_px"
    REFERENCE_PX = "reference_px"
    PHYSICAL_MM = "physical_mm"


class CanvasMetricsSource(str, Enum):
    """Source of host/device/physical metrics used during resolution."""

    EXPLICIT = "explicit"
    BACKEND_DEFAULT = "backend_default"
    BACKEND_REPORTED = "backend_reported"
    ESTIMATED = "estimated"


class CanvasResolveExactness(str, Enum):
    """Exactness of resolved canvas metrics."""

    EXACT = "exact"
    APPROXIMATE = "approximate"
    ADAPTED = "adapted"


@dataclass(frozen=True, slots=True)
class CanvasSize:
    """User-authored canvas size request.

    Width and height are interpreted according to ``policy``. Visual protocol
    fields ending in ``_px`` are authored in the resolved canvas/reference pixel
    space, not necessarily in host logical pixels or framebuffer pixels.
    """

    policy: CanvasSizePolicy
    width: float
    height: float
    reference_dpi: float = DEFAULT_REFERENCE_DPI
    requested_device_scale: float | None = None
    monitor_dpi_override: float | None = None
    strict_framebuffer_size: bool = False

    def __post_init__(self) -> None:
        _validate_positive("width", self.width)
        _validate_positive("height", self.height)
        _validate_positive("reference_dpi", self.reference_dpi)
        if self.requested_device_scale is not None:
            _validate_positive("requested_device_scale", self.requested_device_scale)
        if self.monitor_dpi_override is not None:
            _validate_positive("monitor_dpi_override", self.monitor_dpi_override)

    @classmethod
    def pixel_exact(cls, width_px: float, height_px: float) -> "CanvasSize":
        """Request deterministic framebuffer/output pixels."""
        return cls(CanvasSizePolicy.PIXEL_EXACT, width_px, height_px)

    @classmethod
    def host_logical_px(cls, width: float, height: float) -> "CanvasSize":
        """Request backend/window-system logical pixels directly."""
        return cls(CanvasSizePolicy.HOST_LOGICAL_PX, width, height)

    @classmethod
    def reference_px(
        cls,
        width_px: float,
        height_px: float,
        *,
        reference_dpi: float = DEFAULT_REFERENCE_DPI,
    ) -> "CanvasSize":
        """Request CSS-like reference pixels at ``reference_dpi``."""
        return cls(
            CanvasSizePolicy.REFERENCE_PX,
            width_px,
            height_px,
            reference_dpi=reference_dpi,
        )

    @classmethod
    def physical_mm(
        cls,
        width_mm: float,
        height_mm: float,
        *,
        reference_dpi: float = DEFAULT_REFERENCE_DPI,
    ) -> "CanvasSize":
        """Request a physical target size in millimetres."""
        return cls(
            CanvasSizePolicy.PHYSICAL_MM,
            width_mm,
            height_mm,
            reference_dpi=reference_dpi,
        )

    def with_requested_device_scale(self, scale: float) -> "CanvasSize":
        """Return a copy with an explicit device scale override."""
        return CanvasSize(
            self.policy,
            self.width,
            self.height,
            reference_dpi=self.reference_dpi,
            requested_device_scale=scale,
            monitor_dpi_override=self.monitor_dpi_override,
            strict_framebuffer_size=self.strict_framebuffer_size,
        )

    def with_monitor_dpi_override(self, dpi: float) -> "CanvasSize":
        """Return a copy with an explicit physical monitor DPI override."""
        return CanvasSize(
            self.policy,
            self.width,
            self.height,
            reference_dpi=self.reference_dpi,
            requested_device_scale=self.requested_device_scale,
            monitor_dpi_override=dpi,
            strict_framebuffer_size=self.strict_framebuffer_size,
        )

    def resolve(
        self,
        *,
        output_dpi: float | None = None,
        device_scale: float | None = None,
        host_content_scale: float | None = None,
        metrics_source: CanvasMetricsSource = CanvasMetricsSource.BACKEND_DEFAULT,
    ) -> "ResolvedCanvas":
        """Resolve this request with explicit or backend-provided metrics."""
        scale = self.requested_device_scale
        if scale is None:
            scale = device_scale if device_scale is not None else 1.0
        _validate_positive("device_scale", scale)
        if host_content_scale is not None:
            _validate_positive("host_content_scale", host_content_scale)
        content_scale = host_content_scale if host_content_scale is not None else scale

        if output_dpi is not None:
            _validate_positive("output_dpi", output_dpi)
        raster_dpi = output_dpi if output_dpi is not None else self.reference_dpi

        if self.policy == CanvasSizePolicy.PIXEL_EXACT:
            canvas_width = self.width
            canvas_height = self.height
            framebuffer_width = int(round(self.width))
            framebuffer_height = int(round(self.height))
            host_width = max(1, int(round(framebuffer_width / content_scale)))
            host_height = max(1, int(round(framebuffer_height / content_scale)))
            target_width_mm = canvas_width / self.reference_dpi * MM_PER_INCH
            target_height_mm = canvas_height / self.reference_dpi * MM_PER_INCH
            exactness = CanvasResolveExactness.EXACT
        elif self.policy == CanvasSizePolicy.HOST_LOGICAL_PX:
            canvas_width = self.width
            canvas_height = self.height
            host_width = int(round(self.width))
            host_height = int(round(self.height))
            framebuffer_width = int(round(host_width * content_scale))
            framebuffer_height = int(round(host_height * content_scale))
            target_width_mm = host_width / self.reference_dpi * MM_PER_INCH
            target_height_mm = host_height / self.reference_dpi * MM_PER_INCH
            exactness = CanvasResolveExactness.APPROXIMATE
        elif self.policy == CanvasSizePolicy.REFERENCE_PX:
            canvas_width = self.width
            canvas_height = self.height
            target_width_mm = canvas_width / self.reference_dpi * MM_PER_INCH
            target_height_mm = canvas_height / self.reference_dpi * MM_PER_INCH
            framebuffer_width = int(
                round(canvas_width * raster_dpi / self.reference_dpi)
            )
            framebuffer_height = int(
                round(canvas_height * raster_dpi / self.reference_dpi)
            )
            host_width = max(1, int(round(framebuffer_width / content_scale)))
            host_height = max(1, int(round(framebuffer_height / content_scale)))
            exactness = CanvasResolveExactness.APPROXIMATE
        elif self.policy == CanvasSizePolicy.PHYSICAL_MM:
            target_width_mm = self.width
            target_height_mm = self.height
            canvas_width = target_width_mm / MM_PER_INCH * self.reference_dpi
            canvas_height = target_height_mm / MM_PER_INCH * self.reference_dpi
            framebuffer_width = int(
                round(canvas_width * raster_dpi / self.reference_dpi)
            )
            framebuffer_height = int(
                round(canvas_height * raster_dpi / self.reference_dpi)
            )
            host_width = max(1, int(round(framebuffer_width / content_scale)))
            host_height = max(1, int(round(framebuffer_height / content_scale)))
            exactness = CanvasResolveExactness.APPROXIMATE
        else:  # pragma: no cover - Enum exhaustiveness guard.
            raise ValueError(f"unsupported canvas size policy: {self.policy!r}")

        return ResolvedCanvas(
            requested_size=self,
            canvas_width_px=float(canvas_width),
            canvas_height_px=float(canvas_height),
            host_logical_width=int(host_width),
            host_logical_height=int(host_height),
            framebuffer_width=int(framebuffer_width),
            framebuffer_height=int(framebuffer_height),
            device_scale_x=float(scale),
            device_scale_y=float(scale),
            canvas_to_host_scale_x=float(host_width) / float(canvas_width),
            canvas_to_host_scale_y=float(host_height) / float(canvas_height),
            framebuffer_per_canvas_px_x=float(framebuffer_width) / float(canvas_width),
            framebuffer_per_canvas_px_y=float(framebuffer_height)
            / float(canvas_height),
            target_width_mm=float(target_width_mm),
            target_height_mm=float(target_height_mm),
            estimated_width_mm=float(target_width_mm),
            estimated_height_mm=float(target_height_mm),
            output_dpi=float(raster_dpi),
            metrics_source=metrics_source,
            exactness=exactness,
            strict_framebuffer_size=bool(self.strict_framebuffer_size),
        )


@dataclass(frozen=True, slots=True)
class ResolvedCanvas:
    """Resolved canvas metrics used by backends and query/debug results."""

    requested_size: CanvasSize
    canvas_width_px: float
    canvas_height_px: float
    host_logical_width: int
    host_logical_height: int
    framebuffer_width: int
    framebuffer_height: int
    device_scale_x: float
    device_scale_y: float
    canvas_to_host_scale_x: float
    canvas_to_host_scale_y: float
    framebuffer_per_canvas_px_x: float
    framebuffer_per_canvas_px_y: float
    target_width_mm: float
    target_height_mm: float
    estimated_width_mm: float
    estimated_height_mm: float
    output_dpi: float
    metrics_source: CanvasMetricsSource
    exactness: CanvasResolveExactness
    strict_framebuffer_size: bool = False
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_positive("canvas_width_px", self.canvas_width_px)
        _validate_positive("canvas_height_px", self.canvas_height_px)
        _validate_positive("host_logical_width", float(self.host_logical_width))
        _validate_positive("host_logical_height", float(self.host_logical_height))
        _validate_positive("framebuffer_width", float(self.framebuffer_width))
        _validate_positive("framebuffer_height", float(self.framebuffer_height))
        _validate_positive("device_scale_x", self.device_scale_x)
        _validate_positive("device_scale_y", self.device_scale_y)
        _validate_positive("canvas_to_host_scale_x", self.canvas_to_host_scale_x)
        _validate_positive("canvas_to_host_scale_y", self.canvas_to_host_scale_y)
        _validate_positive(
            "framebuffer_per_canvas_px_x", self.framebuffer_per_canvas_px_x
        )
        _validate_positive(
            "framebuffer_per_canvas_px_y", self.framebuffer_per_canvas_px_y
        )
        _validate_positive("target_width_mm", self.target_width_mm)
        _validate_positive("target_height_mm", self.target_height_mm)
        _validate_positive("estimated_width_mm", self.estimated_width_mm)
        _validate_positive("estimated_height_mm", self.estimated_height_mm)
        _validate_positive("output_dpi", self.output_dpi)

    @property
    def framebuffer_per_canvas_px(self) -> float:
        """Average scalar framebuffer-per-canvas scale for isotropic visual sizes."""
        return 0.5 * (
            self.framebuffer_per_canvas_px_x + self.framebuffer_per_canvas_px_y
        )

    def canvas_px_to_points(self, value_px: float) -> float:
        """Convert canvas/reference pixels to Matplotlib point units."""
        _validate_finite("value_px", value_px)
        return value_px * self.framebuffer_per_canvas_px * 72.0 / self.output_dpi


def _validate_finite(field_name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{field_name} must be finite")


def _validate_positive(field_name: str, value: float) -> None:
    _validate_finite(field_name, value)
    if value <= 0.0:
        raise ValueError(f"{field_name} must be positive")
