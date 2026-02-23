"""Renderer registry to manage different renderers in the GSP API."""

# stdlib imports
from dataclasses import dataclass
from typing import Type

# local imports
from gsp.core import Canvas, Viewport
from gsp.types.renderer_base import RendererBase
from gsp.types.viewport_events_base import ViewportEventsBase
from gsp.types.animator_base import AnimatorBase


@dataclass(frozen=True)
class RendererRegistryItem:
    """Data class to hold renderer-related information for registration."""

    renderer_name: str
    renderer_base_type: Type[RendererBase]
    viewport_event_base_type: Type[ViewportEventsBase]
    animator_base_type: Type[AnimatorBase]


class RendererRegistry:
    """Registry for renderers."""

    _registry: dict[str, RendererRegistryItem] = {}

    @staticmethod
    def register_renderer(
        renderer_name: str, renderer_base_type: Type[RendererBase], viewport_event_base_type: Type[ViewportEventsBase], animator_base_type: Type[AnimatorBase]
    ) -> None:
        """Register a renderer with its associated components."""
        renderer_item = RendererRegistryItem(
            renderer_name=renderer_name,
            renderer_base_type=renderer_base_type,
            viewport_event_base_type=viewport_event_base_type,
            animator_base_type=animator_base_type,
        )
        RendererRegistry._registry[renderer_name] = renderer_item

    # =============================================================================
    # Creator functions to create renderers, viewport events, and animators based on renderer name
    # =============================================================================

    @staticmethod
    def create_renderer(renderer_name: str, canvas: Canvas) -> RendererBase:
        """Create a renderer instance by name."""
        # Get the renderer registry item for the given renderer name
        renderer_registery_item = RendererRegistry._get_item_by_name(renderer_name)

        # Instantiate the renderer base
        renderer_base = renderer_registery_item.renderer_base_type(canvas)

        # Return the created renderer instance
        return renderer_base

    @staticmethod
    def create_viewport_events(renderer_base: RendererBase, inner_viewport: Viewport) -> ViewportEventsBase:
        """Create a viewport events instance by renderer name."""
        # Get the renderer registry item based on renderer base type
        renderer_registery_item = RendererRegistry._get_item_by_renderer_base(renderer_base)

        # Instantiate the viewport events base
        viewport_events_base = renderer_registery_item.viewport_event_base_type(renderer_base, inner_viewport)

        # Return the created viewport events instance
        return viewport_events_base

    @staticmethod
    def create_animator(renderer_base: RendererBase) -> AnimatorBase:
        """Create an animator instance by renderer name."""
        # Get the renderer registry item based on renderer base type
        renderer_registery_item = RendererRegistry._get_item_by_renderer_base(renderer_base)

        # Instantiate the animator base
        animator_base = renderer_registery_item.animator_base_type(renderer_base)

        # Return the created animator instance
        return animator_base

    # =============================================================================
    # Private functions
    # =============================================================================

    @staticmethod
    def _get_item_by_name(renderer_name: str) -> RendererRegistryItem:
        """Get the renderer registry item for a given renderer name."""
        if renderer_name not in RendererRegistry._registry:
            raise ValueError(f"Renderer '{renderer_name}' not found in the registry.")
        return RendererRegistry._registry[renderer_name]

    @staticmethod
    def _get_item_by_renderer_base(renderer_base: RendererBase) -> RendererRegistryItem:
        """Get the renderer registry item for a given renderer base instance."""
        for item in RendererRegistry._registry.values():
            if isinstance(renderer_base, item.renderer_base_type):
                return item
        raise ValueError(f"Renderer base of type '{type(renderer_base)}' not found in the registry.")
