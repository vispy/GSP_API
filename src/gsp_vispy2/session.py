"""Experimental explicit backend-session preview for the VisPy2 producer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal, cast

from gsp.protocol import (
    AxisDimension,
    CapabilitySnapshot,
    ImageVisual,
    MarkerVisual,
    MeshVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    TextVisual,
    TickSpecKind,
)
from gsp_datoviz.capabilities import datoviz_v04_capability_snapshot
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    import_datoviz_v04,
)

from .protocol import Figure


class SessionLifecycleError(RuntimeError):
    """Raised when an operation targets a closed session or display."""


class SessionExecutionError(RuntimeError):
    """Raised when inspection or backend execution cannot proceed."""


@dataclass(frozen=True, slots=True)
class SessionDiagnostic:
    """Immutable structured diagnostic emitted by the session preview."""

    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "error"


@dataclass(frozen=True, slots=True)
class SessionInspection:
    """Immutable pre-execution plan for one producer operation."""

    backend: str
    operation: str
    capabilities: CapabilitySnapshot
    diagnostics: tuple[SessionDiagnostic, ...] = ()

    @property
    def executable(self) -> bool:
        """Return whether inspection found no error diagnostics."""
        return not any(item.severity == "error" for item in self.diagnostics)

    def require_executable(self) -> None:
        """Reject a plan carrying unsupported or invalid producer state."""
        if not self.executable:
            detail = "; ".join(item.message for item in self.diagnostics)
            raise SessionExecutionError(detail)


class Display:
    """Opaque display token owned by an explicit session."""

    def __init__(
        self,
        *,
        session: "Session",
        renderer: DatovizV04ProtocolRenderer,
        blocking: bool,
        diagnostics: tuple[SessionDiagnostic, ...],
    ) -> None:
        self._session = session
        self._renderer = renderer
        self._blocking = blocking
        self._diagnostics = diagnostics
        self._closed = False

    @property
    def backend(self) -> str:
        """Return the selected backend name without exposing native handles."""
        return "datoviz"

    @property
    def blocking(self) -> bool:
        """Return whether the display was opened through blocking execution."""
        return self._blocking

    @property
    def closed(self) -> bool:
        """Return whether deterministic display cleanup has completed."""
        return self._closed

    @property
    def diagnostics(self) -> tuple[SessionDiagnostic, ...]:
        """Return the immutable diagnostic snapshot for this display."""
        return self._diagnostics

    def _require_open(self) -> None:
        if self._closed:
            raise SessionLifecycleError("display is closed")

    def _close(self) -> None:
        if self._closed:
            return
        self._renderer.close()
        self._closed = True


_RendererFactory = Callable[..., DatovizV04ProtocolRenderer]
_renderer_factory: _RendererFactory = DatovizV04ProtocolRenderer


def _load_capabilities() -> CapabilitySnapshot:
    return datoviz_v04_capability_snapshot(import_datoviz_v04())


_capability_loader: Callable[[], CapabilitySnapshot] = _load_capabilities


class Session:
    """Explicit owner of experimental Datoviz execution resources."""

    def __init__(self, backend: str) -> None:
        if backend != "datoviz":
            raise ValueError("experimental sessions currently support only 'datoviz'")
        self._backend = backend
        self._capabilities: CapabilitySnapshot | None = None
        self._displays: list[Display] = []
        self._diagnostics: list[SessionDiagnostic] = []
        self._closed = False

    @property
    def backend(self) -> str:
        return self._backend

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def capabilities(self) -> CapabilitySnapshot:
        """Return the immutable backend capability snapshot."""
        self._require_open()
        if self._capabilities is None:
            self._capabilities = _capability_loader()
        return self._capabilities

    @property
    def diagnostics(self) -> tuple[SessionDiagnostic, ...]:
        """Return immutable diagnostics accumulated by this session."""
        return tuple(self._diagnostics)

    def inspect(self, figure: Figure, *, operation: str = "display") -> SessionInspection:
        """Inspect a figure without creating window or renderer resources."""
        self._require_open()
        if operation != "display":
            raise ValueError("the experimental preview supports only operation='display'")
        diagnostics: list[SessionDiagnostic] = []
        if not isinstance(figure, Figure):
            raise TypeError("inspect() requires a gsp_vispy2.Figure")
        if len(figure.axes) > 1:
            diagnostics.append(SessionDiagnostic(
                "session.figure.multiple_axes_unsupported",
                "the experimental Datoviz session supports at most one axes",
            ))
        if figure.panel_text_guides():
            diagnostics.append(SessionDiagnostic(
                "session.guide.panel_text_unsupported",
                "panel text guides are not yet supported by the session preview",
            ))
        inspection = SessionInspection(
            backend=self.backend,
            operation=operation,
            capabilities=self.capabilities,
            diagnostics=tuple(diagnostics),
        )
        self._diagnostics.extend(diagnostics)
        return inspection

    def show(
        self,
        figure: Figure,
        *,
        block: bool = True,
        frame_count: int = 1,
    ) -> Display:
        """Create a display and optionally execute a bounded blocking run.

        ``frame_count`` must be positive. Polled use passes ``block=False`` and
        advances exactly one frame through :meth:`poll`.
        """
        self._require_open()
        if frame_count < 1:
            raise ValueError("frame_count must be positive for bounded display")
        inspection = self.inspect(figure, operation="display")
        inspection.require_executable()
        try:
            renderer = self._build_renderer(figure)
        except Exception as exc:
            diagnostic = SessionDiagnostic(
                "session.backend.preparation_failed", str(exc)
            )
            self._diagnostics.append(diagnostic)
            raise SessionExecutionError(str(exc)) from exc
        display = Display(
            session=self,
            renderer=renderer,
            blocking=block,
            diagnostics=inspection.diagnostics,
        )
        self._displays.append(display)
        if block:
            try:
                renderer.show(frame_count=frame_count)
            except Exception as exc:
                display._close()
                diagnostic = SessionDiagnostic(
                    "session.backend.execution_failed", str(exc)
                )
                self._diagnostics.append(diagnostic)
                raise SessionExecutionError(str(exc)) from exc
        return display

    def poll(self, display: Display) -> None:
        """Advance one frame for a display owned explicitly by this session."""
        self._require_open()
        if not isinstance(display, Display) or display._session is not self:
            raise ValueError("display is not owned by this session")
        display._require_open()
        if display.blocking:
            raise ValueError("poll() requires a display created with block=False")
        try:
            display._renderer.show(frame_count=1)
        except Exception as exc:
            diagnostic = SessionDiagnostic("session.backend.poll_failed", str(exc))
            self._diagnostics.append(diagnostic)
            raise SessionExecutionError(str(exc)) from exc

    def close(self) -> None:
        """Close all owned displays deterministically; repeated calls are safe."""
        if self._closed:
            return
        for display in reversed(self._displays):
            display._close()
        self._closed = True

    def __enter__(self) -> "Session":
        self._require_open()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def _require_open(self) -> None:
        if self._closed:
            raise SessionLifecycleError("session is closed")

    def _build_renderer(self, figure: Figure) -> DatovizV04ProtocolRenderer:
        axes = figure.axes[0] if figure.axes else None
        renderer = _renderer_factory(
            color_scales={scale.id: scale for scale in figure.color_scales()},
            view=None if axes is not None and axes.axis_guides else (
                axes.view if axes is not None else None
            ),
        )
        try:
            if axes is not None and axes.axis_guides:
                x_guide = next(
                    guide for guide in axes.axis_guides
                    if guide.dimension is AxisDimension.X
                )
                y_guide = next(
                    guide for guide in axes.axis_guides
                    if guide.dimension is AxisDimension.Y
                )
                explicit = (
                    x_guide.tick_spec.kind is TickSpecKind.EXPLICIT
                    or y_guide.tick_spec.kind is TickSpecKind.EXPLICIT
                )
                renderer.configure_view2d_axes(
                    axes.view,
                    x_label=x_guide.label_text,
                    y_label=y_guide.label_text,
                    grid=x_guide.grid_visible or y_guide.grid_visible,
                    backend_auto_ticks=not explicit,
                    x_tick_values=x_guide.tick_spec.explicit_values,
                    x_tick_labels=x_guide.tick_spec.explicit_labels,
                    y_tick_values=y_guide.tick_spec.explicit_values,
                    y_tick_labels=y_guide.tick_spec.explicit_labels,
                )
            for visual in figure.visuals():
                _add_visual(renderer, visual)
            for guide in figure.colorbar_guides():
                renderer.add_colorbar_guide(guide)
        except Exception:
            renderer.close()
            raise
        return renderer


def open_session(backend: str) -> Session:
    """Open an explicit experimental backend session."""
    return Session(backend)


def _add_visual(renderer: DatovizV04ProtocolRenderer, visual: object) -> None:
    if isinstance(visual, PointVisual):
        renderer.add_point_visual(visual)
    elif isinstance(visual, MarkerVisual):
        renderer.add_marker_visual(visual)
    elif isinstance(visual, SegmentVisual):
        renderer.add_segment_visual(visual)
    elif isinstance(visual, PathVisual):
        renderer.add_path_visual(visual)
    elif isinstance(visual, ImageVisual):
        renderer.add_image_visual(visual)
    elif isinstance(visual, TextVisual):
        renderer.add_text_visual(visual)
    elif isinstance(visual, MeshVisual):
        renderer.add_mesh_visual(visual)
    else:
        raise TypeError(f"unsupported protocol visual: {type(visual).__name__}")
