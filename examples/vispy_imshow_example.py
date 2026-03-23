"""Scatter example demonstrating the use of the scatter function to create different types of visuals.

- Left: Pixels visual with random positions and red color.
- Right: Markers visual with random positions, varying sizes and colors.
"""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas
from gsp.constants import Constants

from gsp_extra.misc.render_item import RenderItem
from common.example_helper import ExampleHelper
from gsp.core.texture import Texture
from gsp_extra.misc.texture_utils import TextureUtils


# from vispy_2 import scatter
import vispy2 as Vispy2


def main():
    """Main function for the scatter example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(400, 400, 72.0, Constants.Color.white)

    # Create a renderer
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)

    # Create an AxesManaged instance for the canvas
    axes_managed = Vispy2.axes.AxesManaged(renderer_base, 40, 40, 320, 320)
    axes_managed.set_title("Vispy2 imshow Example")

    # =============================================================================
    # Read image and create texture
    # =============================================================================

    image_path = pathlib.Path(__file__).parent / "images" / "image.png"
    texture = TextureUtils.load_image(str(image_path))

    imshowImage = Vispy2.imshow(texture, cmap="viridis", origin="upper")
    visualImage = imshowImage.to_visual_image()

    axes_managed.add_visual(visualImage)

    # =============================================================================
    # Render
    # =============================================================================

    # start the animation loop
    axes_managed.start()


if __name__ == "__main__":
    main()
