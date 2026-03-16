"""Scatter example demonstrating the use of the scatter function to create different types of visuals.

- Left: Pixels visual with random positions and red color.
- Right: Markers visual with random positions, varying sizes and colors.
"""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.constants import Constants

from gsp_extra.misc.render_item import RenderItem
from common.example_helper import ExampleHelper

# from vispy_2 import scatter
import vispy2 as Vispy2


def main():
    """Main function for the scatter example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(400, 400, 72.0, Constants.Color.white)

    # Create viewports
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height(), Constants.Color.transparent)

    # =============================================================================
    # Add random points
    # - various ways to create Buffers
    # =============================================================================

    imageData = np.random.rand(400, 400).astype(np.float32)
    imshowImage = Vispy2.imshow(imageData, cmap="viridis")
    visualImage = imshowImage.to_visual_image()

    # declare array of render items
    render_items: list[RenderItem] = []
    render_items.append(RenderItem(viewport, visualImage, Bufferx.mat4_identity(), Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())))

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
