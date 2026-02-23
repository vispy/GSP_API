"""Register the Matplotlib renderer and its associated components into GSP's RendererRegistry."""

# local imports
from .animator.animator_matplotlib import AnimatorMatplotlib
from .viewport_events.viewport_events_matplotlib import ViewportEventsMatplotlib
from .renderer import MatplotlibRenderer
from gsp.utils.renderer_registery import RendererRegistry


def register_renderer_matplotlib():
    """Register the Matplotlib renderer and its associated components into the RendererRegistry."""
    RendererRegistry.register_renderer(
        renderer_name="matplotlib",
        renderer_base_type=MatplotlibRenderer,
        viewport_event_base_type=ViewportEventsMatplotlib,
        animator_base_type=AnimatorMatplotlib,
    )
