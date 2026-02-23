"""Register the Datoviz renderer and its associated components into GSP's RendererRegistry."""

# local imports
from .animator.animator_datoviz import AnimatorDatoviz
from .viewport_events.viewport_events_datoviz import ViewportEventsDatoviz
from .renderer import DatovizRenderer
from gsp.utils.renderer_registery import RendererRegistry


def register_renderer_datoviz():
    """Register the Datoviz renderer and its associated components into the RendererRegistry."""
    RendererRegistry.register_renderer(
        renderer_name="datoviz",
        renderer_base_type=DatovizRenderer,
        viewport_event_base_type=ViewportEventsDatoviz,
        animator_base_type=AnimatorDatoviz,
    )
