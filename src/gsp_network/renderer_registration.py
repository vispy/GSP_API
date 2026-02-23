"""Register the Network renderer and its associated components into GSP's RendererRegistry."""

# local imports
from .animator.animator_network import AnimatorNetwork
from .viewport_events.viewport_events_network import ViewportEventsNetwork
from .renderer import NetworkRenderer
from gsp.utils.renderer_registery import RendererRegistry


def register_renderer_network():
    """Register the Network renderer and its associated components into the RendererRegistry."""
    RendererRegistry.register_renderer(
        renderer_name="network",
        renderer_base_type=NetworkRenderer,
        viewport_event_base_type=ViewportEventsNetwork,
        animator_base_type=AnimatorNetwork,
    )
