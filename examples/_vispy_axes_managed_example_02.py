"""Example demonstrating the AxesDisplay with pan and zoom functionality."""

# stdlib imports
import time

# pip imports
import numpy as np

# local imports
from common.example_helper import ExampleHelper
from gsp.core import Canvas, Viewport
from gsp.core.camera import Camera
from gsp.types.animator_base import AnimatorBase
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx
from gsp.types import BufferType, VisualBase
from gsp.types.renderer_base import RendererBase
from gsp.types.viewport_events_base import ViewportEventsBase
from gsp.types import Buffer
from gsp.constants import Constants
from gsp.utils.unit_utils import UnitUtils
from gsp_extra.misc.render_item import RenderItem
from vispy2.axes.axes_display import AxesDisplay
from vispy2.axes.axes_panzoom import AxesPanZoom

# =============================================================================
# Register this renderer into gsp renderer_registery
# =============================================================================

from gsp_matplotlib.animator.animator_matplotlib import AnimatorMatplotlib
from gsp_matplotlib.viewport_events.viewport_events_matplotlib import ViewportEventsMatplotlib
from gsp_matplotlib.renderer import MatplotlibRenderer
from gsp.utils.renderer_registery import RendererRegistry

RendererRegistry.register_renderer(
    renderer_name="matplotlib",
    renderer_base_type=MatplotlibRenderer,
    viewport_event_base_type=ViewportEventsMatplotlib,
    animator_base_type=AnimatorMatplotlib,
)


class AxesManaged:
    """Handle one axe in a canvas."""

    def __init__(
        self,
        renderer_base: RendererBase,
        viewport_x: int,
        viewport_y: int,
        viewport_width: int,
        viewport_height: int,
    ):
        self._renderer_base = renderer_base

        # Create a inner viewport for the axes display
        self._inner_viewport = Viewport(viewport_x, viewport_y, viewport_width, viewport_height)

        # Create viewport events based on the renderer base and inner viewport
        self._viewport_events = RendererRegistry.create_viewport_events(renderer_base, self._inner_viewport)

        # Create an animator based on the renderer base
        self._animator = RendererRegistry.create_animator(renderer_base)

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
        needs_render: bool = False
        last_render_time: float = 0.0
        max_delta_time_between_renders: float = 1.0 / 60.0  # seconds

        # Define the event handler for new limits for the axes display
        def on_new_limits():
            """Event handle to update points model matrices on axes limits change."""
            nonlocal needs_render
            needs_render = True

        # Subscribe to new limits event - thus updating axes visuals on zoom/pan
        self._axes_display.new_limits_event.subscribe(on_new_limits)

        @self._animator.event_listener
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
        return self._renderer_base

    def get_viewport(self) -> Viewport:
        return self._inner_viewport

    def get_axes_display(self) -> AxesDisplay:
        return self._axes_display

    def get_axes_pan_zoom(self) -> AxesPanZoom:
        return self._axes_pan_zoom

    def get_render_items(self) -> list[RenderItem]:
        return self._render_items

    # =============================================================================
    #
    # =============================================================================

    def add_render_items(self, render_item: RenderItem) -> None:
        """Add a render item."""
        self._render_items.append(render_item)

    def remove_render_item(self, render_item: RenderItem) -> None:
        """Remove a render item."""
        self._render_items = [ri for ri in self._render_items if ri != render_item]

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

    def start(self):
        self.render()
        self._animator.start([], [], [], [])

    def stop(self):
        self._animator.stop()


def main():
    """Main function to run the example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(width=400, height=400, dpi=127)

    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # =============================================================================
    #
    # =============================================================================

    # Create an AxesManaged instance for the canvas with a viewport that takes 80% of the canvas size and is centered
    viewport_x = int(canvas.get_width() * 0.1)
    viewport_y = int(canvas.get_height() * 0.1)
    viewport_width = int(canvas.get_width() * 0.8)
    viewport_height = int(canvas.get_height() * 0.8)

    axes_managed = AxesManaged(renderer_base, viewport_x, viewport_y, viewport_width, viewport_height)

    # =============================================================================
    #
    # =============================================================================

    def generate_visual_points(point_count: int, viewport: Viewport) -> RenderItem:
        # Generate a sinusoidal distribution of points
        sin_scale = 3.0
        x_values = np.linspace(-1.0, +1.0, point_count, dtype=np.float32)
        y_values = np.sin(x_values * np.pi * sin_scale).astype(np.float32)
        z_values = np.zeros(point_count, dtype=np.float32)
        positions_numpy = np.vstack((x_values, y_values, z_values)).T.astype(np.float32)

        # positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
        positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

        # Sizes - Create buffer and set data with numpy array
        sizes_numpy = np.array([10] * point_count, dtype=np.float32)
        sizes_buffer = Bufferx.from_numpy(sizes_numpy, BufferType.float32)

        # all pixels red - Create buffer and fill it with a constant
        face_colors_buffer = Buffer(point_count, BufferType.rgba8)
        face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * point_count, 0, point_count)

        # Edge colors - Create buffer and fill it with a constant
        edge_colors_buffer = Buffer(point_count, BufferType.rgba8)
        edge_colors_buffer.set_data(Constants.Color.blue * point_count, 0, point_count)

        # Edge widths - Create buffer and fill it with a constant
        edge_widths_numpy = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * point_count, dtype=np.float32)
        edge_widths_buffer = Bufferx.from_numpy(edge_widths_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

        # Create model matrix to transform points into axes data space
        model_matrix = Bufferx.mat4_identity()

        camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

        render_item = RenderItem(viewport, points, model_matrix, camera)
        return render_item

    render_item_points = generate_visual_points(100, axes_managed.get_viewport())

    axes_managed.add_render_items(render_item_points)

    # =============================================================================
    #
    # =============================================================================

    # start the animation loop
    axes_managed.start()


if __name__ == "__main__":
    main()
