"""Utility functions for texture handling."""

# stdlib imports
import imageio

# import matplotlib.pyplot
import numpy as np

# local imports
from gsp.core.texture import Texture
from gsp.types import BufferType
from gsp_extra.bufferx import Bufferx


class TextureUtils:
    """Utility functions for texture handling."""

    @staticmethod
    def load_image(image_path: str) -> Texture:
        """Load an image from the given path and create a Texture instance.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Texture: The created Texture instance.
        """
        # read image using imageio
        texture_numpy = imageio.v3.imread(image_path)

        # get image dimensions
        image_height, image_width, image_channels = texture_numpy.shape
        # print(f"Loaded image with dimensions: {image_width}x{image_height}, channels: {image_channels}")

        # ensure texture_numpy is uint8
        texture_numpy = (texture_numpy * 255).astype(np.uint8) if texture_numpy.dtype == np.float32 else texture_numpy

        # add alpha channel if needed
        if image_channels == 3:
            alpha_channel = np.full((image_height, image_width, 1), 255, dtype=np.uint8)
            texture_numpy = np.concatenate((texture_numpy, alpha_channel), axis=2)

        # linearize the texture data, thus we can do a buffer out of it
        texture_numpy = texture_numpy.reshape((image_width * image_height, 4))

        # create buffer and texture
        texture_buffer = Bufferx.from_numpy(texture_numpy, BufferType.rgba8)
        texture = Texture(texture_buffer, image_width, image_height)

        # return the texture
        return texture
