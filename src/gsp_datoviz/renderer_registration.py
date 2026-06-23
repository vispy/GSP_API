"""Register the legacy Datoviz renderer into GSP's RendererRegistry."""

# local imports
from .animator.animator_datoviz import AnimatorDatoviz
from .viewport_events.viewport_events_datoviz import ViewportEventsDatoviz
from .renderer import DatovizRenderer
from gsp.utils.renderer_registery import RendererRegistry


def register_renderer_datoviz() -> None:
    """Register the legacy Datoviz v0.3 renderer."""
    RendererRegistry.register_renderer(
        renderer_name="datoviz-v03",
        renderer_base_type=DatovizRenderer,
        viewport_event_base_type=ViewportEventsDatoviz,
        animator_base_type=AnimatorDatoviz,
    )


def register_renderer_datoviz_v03() -> None:
    """Register the legacy Datoviz v0.3 renderer."""
    register_renderer_datoviz()
