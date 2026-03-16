"""Example demonstrating the AxesDisplay with pan and zoom functionality."""

# stdlib imports
import time

# pip imports
import numpy as np

# local imports
from gsp.core import Viewport, Camera
from gsp.constants import Constants
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType, VisualBase, TransBuf
from gsp.types.renderer_base import RendererBase
from gsp.utils.renderer_registery import RendererRegistry
from gsp.types.animator_base import AnimatorBase
from gsp_extra.misc.render_item import RenderItem
from vispy2.axes.axes_display import AxesDisplay
from vispy2.axes.axes_panzoom import AxesPanZoom


class AxesManaged:
    """Class to manage an axes display with pan and zoom functionality.

    Includes:
    - an axes display to show the axes
    - a pan zoom to handle pan and zoom
    - an animator for your event loop
    - a list of render items (visuals with model matrices and cameras) that will be display in the axes
    """

    def __init__(
        self,
        renderer_base: RendererBase,
        viewport_x: int,
        viewport_y: int,
        viewport_width: int,
        viewport_height: int,
        *,
        animator_base: AnimatorBase | None = None,
    ) -> None:
        """Initialize the AxesManaged instance.

        Args:
            renderer_base: The renderer base to use for rendering the axes and the render items.
            viewport_x: The x position (in pixels) for the **inner** viewport.
            viewport_y: The y position (in pixels) for the **inner** viewport.
            viewport_width: The width (in pixels) for the **inner** viewport.
            viewport_height: The height (in pixels) for the **inner** viewport.
            animator_base: Optional animator base to use for the animation loop. If None, a default animator will be created based on the renderer base.
        """
        self._renderer_base = renderer_base

        # Create a inner viewport for the axes display
        self._inner_viewport = Viewport(viewport_x, viewport_y, viewport_width, viewport_height, Constants.Color.transparent)

        # Create viewport events based on the renderer base and inner viewport
        self._viewport_events = RendererRegistry.create_viewport_events(renderer_base, self._inner_viewport)

        # Create an animator based on the renderer base
        if animator_base is not None:
            self._animator_base = animator_base
        else:
            self._animator_base = RendererRegistry.create_animator(renderer_base)

        # Create an AxesDisplay for the inner viewport
        self._axes_display = AxesDisplay(renderer_base.get_canvas(), self._inner_viewport)

        # Create an AxesPanZoom to handle pan and zoom for the axes display
        self._axes_pan_zoom = AxesPanZoom(self._viewport_events, base_scale=1.1, axes_display=self._axes_display)

        # Create a list to hold all render items associated with this axes display
        self._render_items: list[RenderItem] = []

        # =============================================================================
        # Init animator callback to handle rendering frequency
        # - on new limits event we set a flag to trigger rendering in the animator callback
        # - in the animator callback we check the flag and the time since last render to limit
        #   rendering frequency to avoid blinking during interaction
        # =============================================================================

        # define variables to control rendering frequency
        needs_render: bool = True
        last_render_time: float = 0.0
        max_delta_time_between_renders: float = 1.0 / 60.0  # seconds

        # Define the event handler for new limits for the axes display
        def on_new_limits():
            """Event handle to update points model matrices on axes limits change."""
            nonlocal needs_render
            needs_render = True

        # Subscribe to new limits event - thus updating axes visuals on zoom/pan
        self._axes_display.new_limits_event.subscribe(on_new_limits)

        @self._animator_base.event_listener
        def animator_callback(delta_time: float) -> list[VisualBase]:
            """Animator callback to handle rendering frequency."""
            nonlocal needs_render, last_render_time, max_delta_time_between_renders

            if needs_render and (time.time() - last_render_time) >= max_delta_time_between_renders:
                self.render()
                needs_render = False
                last_render_time = time.time()

            changed_visuals: list[VisualBase] = []
            return changed_visuals

    # =============================================================================
    #
    # =============================================================================

    def get_renderer(self) -> RendererBase:
        """Get the renderer base associated with this axes."""
        return self._renderer_base

    def get_viewport(self) -> Viewport:
        """Get the inner viewport associated with this axes."""
        return self._inner_viewport

    def get_animator(self) -> AnimatorBase:
        """Get the animator base associated with this axes."""
        return self._animator_base

    def get_axes_display(self) -> AxesDisplay:
        """Get the axes display associated with this axes."""
        return self._axes_display

    def get_axes_pan_zoom(self) -> AxesPanZoom:
        """Get the axes pan zoom associated with this axes."""
        return self._axes_pan_zoom

    def set_title(self, text: str | None) -> None:
        """Set the plot title. Pass None to remove it."""
        self._axes_display.set_title(text)

    def set_xlabel(self, text: str | None) -> None:
        """Set the x-axis label. Pass None to remove it."""
        self._axes_display.set_xlabel(text)

    def set_ylabel(self, text: str | None) -> None:
        """Set the y-axis label. Pass None to remove it."""
        self._axes_display.set_ylabel(text)

    def get_render_items(self) -> list[RenderItem]:
        """Get the render items associated with this axes."""
        return self._render_items

    # =============================================================================
    #
    # =============================================================================

    # FIXME this is not very clean

    def add_render_items(self, render_item: RenderItem) -> RenderItem:
        """Add a render item."""
        # sanity check -
        self._render_items.append(render_item)
        return render_item

    def remove_render_item(self, render_item: RenderItem) -> None:
        """Remove a render item."""
        self._render_items = [ri for ri in self._render_items if ri != render_item]

    def add_visual(self, visualBase: VisualBase, model_matrix: TransBuf | None = None, camera: Camera | None = None) -> RenderItem:
        """Add a visual to the axes display with an optional model matrix and camera."""
        if model_matrix is None:
            model_matrix = Bufferx.mat4_identity()
        if camera is None:
            camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        render_item = RenderItem(self._inner_viewport, visualBase, model_matrix, camera)
        self.add_render_items(render_item)
        return render_item

    def remove_visual(self, visualBase: VisualBase) -> None:
        """Remove a visual from the axes display."""
        # Find the first render_item for this visual
        render_item = None
        for ri in self._render_items:
            if ri.visual_base == visualBase:
                render_item = ri
                break

        if render_item is not None:
            self.remove_render_item(render_item)

    # =============================================================================
    #
    # =============================================================================

    def render(self) -> None:
        """Render all render items associated with this axes."""
        # Clone all render items to avoid modifying them during rendering
        render_items = self._render_items.copy()

        # Get the axes transform matrix
        axes_transform_numpy = self._axes_display.get_transform_matrix_numpy()

        # Update model matrices for all visuals - thus apply axes transform to all visuals in the axes display
        for render_item in render_items:
            model_matrix_numpy = np.eye(4, dtype=np.float32)
            model_matrix_numpy = axes_transform_numpy @ model_matrix_numpy
            render_item.model_matrix = Bufferx.from_numpy(np.array([model_matrix_numpy]), BufferType.mat4)

        # Collect all render items for the axes display
        render_items_axes = self._axes_display.get_render_items()

        # Combine all render items
        render_items_combined = render_items + render_items_axes

        # Render all render items
        self._renderer_base.render(
            [render_item.viewport for render_item in render_items_combined],
            [render_item.visual_base for render_item in render_items_combined],
            [render_item.model_matrix for render_item in render_items_combined],
            [render_item.camera for render_item in render_items_combined],
        )

    def start(self) -> None:
        """Start the animator."""
        self._animator_base.start()

    def stop(self) -> None:
        """Stop the animator."""
        self._animator_base.stop()
