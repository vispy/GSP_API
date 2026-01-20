"""Example showing how to use the Pixels visual to render a set of points."""

# stdlib imports
import pathlib

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas, Viewport
from gsp.types.image_interpolation import ImageInterpolation
from gsp.visuals import Image
from gsp.types import BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from common.example_helper import ExampleHelper
from gsp_extra.misc.texture_utils import TextureUtils


def main():
    """Main function for the pixels example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(512, 512, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Read image and create texture
    # =============================================================================

    image_path = pathlib.Path(__file__).parent / "images" / "image.png"
    texture = TextureUtils.load_image(str(image_path))

    # =============================================================================
    # Create a image visual
    # =============================================================================

    # Define image position (4 vertices for a quad)
    positions_numpy = np.array([[0.0, 0.5, 0.0]], dtype=np.float32)
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Define image extent (left, right, bottom, top)
    image_extent = (-0.5, 0.5, -0.5, 0.5)

    # Create the Image visual and add it to the viewport
    image = Image(texture, positions_buffer, image_extent, ImageInterpolation.NEAREST)

    # =============================================================================
    # Render the canvas
    # =============================================================================

    # Model matrix
    model_matrix = Bufferx.mat4_identity()

    # Create a camera
    camera = Camera(Bufferx.mat4_identity(), Bufferx.mat4_identity())

    # =============================================================================
    # Render
    # =============================================================================

    # Create renderer and render
    renderer_name = ExampleHelper.get_renderer_name()
    renderer_base = ExampleHelper.create_renderer(renderer_name, canvas)
    rendered_image = renderer_base.render([viewport], [image], [model_matrix], [camera])

    # Save to file
    ExampleHelper.save_output_image(rendered_image, f"{pathlib.Path(__file__).stem}_{renderer_name}.png")

    # Show the renderer
    renderer_base.show()


if __name__ == "__main__":
    main()
