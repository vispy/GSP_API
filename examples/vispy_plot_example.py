"""Scatter example demonstrating the use of the scatter function to create different types of visuals.

- Left: Pixels visual with random positions and red color.
- Right: Markers visual with random positions, varying sizes and colors.
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
    """Main function for the scatter example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(400, 400, 72.0)

    # viewport size
    half_width = int(canvas.get_width() / 2)
    half_height = int(canvas.get_height() / 2)

    # Create viewports
    viewport_1 = Viewport(0, 0, half_width, half_height)
    viewport_2 = Viewport(half_width, 0, half_width, half_height)
    viewport_3 = Viewport(0, half_height, half_width, half_height)
    viewport_4 = Viewport(half_width, half_height, half_width, half_height)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    def createVisualPoints(fmt: str) -> list[VisualBase]:
        point_count = 40

        # Create Buffers
        x_numpy = np.linspace(-1 * 0.9, 1 * 0.9, point_count, dtype=np.float32).reshape(point_count, 1)
        x_buffer = Bufferx.from_numpy(x_numpy, BufferType.float32)

        y_numpy = np.sin(x_numpy * 2 * np.pi).astype(np.float32) * 0.9
        y_buffer = Bufferx.from_numpy(y_numpy, BufferType.float32)

        # Create the Points visual and add it to the viewport
        visuals = Vispy2.plot(
            x_buffer,
            y_buffer,
            fmt=fmt,
        )
        return visuals

    visuals_1 = createVisualPoints("bo")
    visuals_2 = createVisualPoints("rs")
    visuals_3 = createVisualPoints("gs")
    visuals_4 = createVisualPoints("yo")

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
