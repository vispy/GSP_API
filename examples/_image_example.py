"""Example showing how to use the Pixels visual to render a set of points."""

# stdlib imports
import os
import pathlib

# pip imports
import numpy as np
import matplotlib.pyplot

# local imports
from gsp.core import Canvas, Viewport
from gsp.core.texture import Texture
from gsp.visuals import Image
from gsp.types import Buffer, BufferType
from gsp.core import Camera
from gsp_extra.bufferx import Bufferx
from gsp.utils.group_utils import GroupUtils
from common.example_helper import ExampleHelper


def main():
    """Main function for the pixels example."""
    # fix random seed for reproducibility
    np.random.seed(0)

    # Create a canvas
    canvas = Canvas(100, 100, 72.0)

    # Create a viewport and add it to the canvas
    viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

    # =============================================================================
    # Read image and create texture
    # =============================================================================

    image_path = pathlib.Path(__file__).parent / "images" / "image.png"
    texture_numpy = matplotlib.pyplot.imread(image_path)
    # get image dimensions
    image_height, image_width, image_channels = texture_numpy.shape
    print(f"Loaded image with dimensions: {image_width}x{image_height}, channels: {image_channels}")
    # ensure texture_numpy is uint8
    texture_numpy = (texture_numpy * 255).astype(np.uint8) if texture_numpy.dtype == np.float32 else texture_numpy
    # add alpha channel if needed
    if image_channels == 3:
        alpha_channel = np.full((image_height, image_width, 1), 255, dtype=np.uint8)
        texture_numpy = np.concatenate((texture_numpy, alpha_channel), axis=2)
    # linearize the texture data, thus we can do a buffer out of it
    texture_numpy = texture_numpy.reshape((image_width * image_height, 4))
    texture_buffer = Bufferx.from_numpy(texture_numpy, BufferType.rgba8)
    texture = Texture(texture_buffer, image_width, image_height)

    # =============================================================================
    # Create a image visual
    # =============================================================================

    # Define image position (4 vertices for a quad)
    positions_numpy = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
    positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

    # Define image extent (left, right, bottom, top)
    image_extent = (-0.5, 0.5, -0.5, 0.5)

    # Create the Image visual and add it to the viewport
    image = Image(texture, positions_buffer, image_extent)

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
