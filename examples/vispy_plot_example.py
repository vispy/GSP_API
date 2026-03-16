"""Plot example with different marker and line styles.

Creates a 2x2 grid of sine wave plots using matplotlib-style format strings
to demonstrate color and marker customization options.

Format strings: [marker_style][color] (e.g., 'bo' = blue circles, 'rs' = red squares)
"""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Camera, Viewport
from gsp.types import BufferType, VisualBase
from gsp_extra.bufferx import Bufferx
from common.example_helper import ExampleHelper
from gsp_extra.misc.render_item import RenderItem
import vispy2 as Vispy2


def main():
    """Main function."""
    # Configuration
    CANVAS_WIDTH = 400
    CANVAS_HEIGHT = 400
    CANVAS_DPI = 72.0
    POINT_COUNT = 40
    X_AMPLITUDE = 0.9  # Range: [-0.9, 0.9]
    Y_AMPLITUDE = 0.9

    # Fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT, CANVAS_DPI)

    # viewport size
    half_width = int(canvas.get_width() / 2)
    half_height = int(canvas.get_height() / 2)

    # Create viewports
    viewport_1 = Viewport(0, 0, half_width, half_height)
    viewport_2 = Viewport(half_width, 0, half_width, half_height)
    viewport_3 = Viewport(0, half_height, half_width, half_height)
    viewport_4 = Viewport(half_width, half_height, half_width, half_height)

    # =============================================================================
    # Create sine wave plots with different styles
    # =============================================================================

    def create_sine_wave_visual(fmt: str) -> list[VisualBase]:
        """Create a sine wave visualization with matplotlib-style format string.

        Args:
            fmt: Format string (e.g., 'bo' for blue circles, 'r-' for red line)
                 Format: [marker_style][color]
                 - Marker: 'o' (circle), 's' (square), '^' (triangle), 'X' (cross), 'D' (diamond)
                 - Color: 'r' (red), 'g' (green), 'b' (blue), 'c' (cyan), etc.
                 - Line style: '-' (solid line). Omit for markers only.

        Returns:
            List of visual objects to render
        """
        # Generate x coordinates: evenly spaced points from -0.9 to 0.9
        x_numpy = np.linspace(-X_AMPLITUDE, X_AMPLITUDE, POINT_COUNT, dtype=np.float32).reshape(POINT_COUNT, 1)
        x_buffer = Bufferx.from_numpy(x_numpy, BufferType.float32)

        # Generate y coordinates: one complete sine wave cycle (2π radians)
        # sin(x * 2π) creates one full oscillation across the x range
        y_numpy = (np.sin(x_numpy * 2 * np.pi) * Y_AMPLITUDE).astype(np.float32)
        y_buffer = Bufferx.from_numpy(y_numpy, BufferType.float32)

        # Create visualization using the plot() function with matplotlib-style formatting
        visuals = Vispy2.plot(x_buffer, y_buffer, fmt=fmt)
        return visuals

    # Create sine wave plots with different matplotlib-style format strings
    # Format: [marker_style][color]
    visuals_1 = create_sine_wave_visual("bo")  # 'b'=blue, 'o'=circle markers
    visuals_2 = create_sine_wave_visual("rs")  # 'r'=red, 's'=square markers
    visuals_3 = create_sine_wave_visual("gX")  # 'g'=green, 'X'=cross markers
    visuals_4 = create_sine_wave_visual("cD")  # 'c'=cyan, 'D'=diamond markers

    render_items: list[RenderItem] = []
    for visuals, viewport in zip([visuals_1, visuals_2, visuals_3, visuals_4], [viewport_1, viewport_2, viewport_3, viewport_4]):
        for visual in visuals:
            model_matrix = Bufferx.mat4_identity()
            camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())
            render_item = RenderItem(viewport, visual, model_matrix, camera)
            render_items.append(render_item)

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # Render all render items
    rendered_image = renderer_base.render(
        [render_item.viewport for render_item in render_items],
        [render_item.visual_base for render_item in render_items],
        [render_item.model_matrix for render_item in render_items],
        [render_item.camera for render_item in render_items],
    )

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
