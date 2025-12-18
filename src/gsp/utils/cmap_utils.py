"""Colormap utilities for mapping values to colors using matplotlib colormaps."""

# pip imports
import matplotlib.cm
import numpy as np

# local imports
from gsp.types import Buffer, BufferType


class CmapUtils:
    """Utility class for colormap operations. Leverage [matplotlib colormaps](https://matplotlib.org/stable/tutorials/colors/colormaps.html)."""

    @staticmethod
    def has_color_map(colormap_name: str) -> bool:
        """Check if the given colormap name is recognized by matplotlib.

        Args:
            colormap_name (str): Name of the colormap to check.

        Returns:
            bool: True if the colormap exists, False otherwise.
        """
        try:
            matplotlib.cm.get_cmap(colormap_name)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_color_map(colormap_name: str, values: np.ndarray, vmin: float | None = None, vmax: float | None = None) -> Buffer:
        """Get colors from a colormap for the given values.

        Args:
            colormap_name (str): Name of the colormap (e.g., 'plasma', 'viridis', etc.).
            values (np.ndarray): Array of input values to map to colors.
            vmin (float|None): Minimum value for values normalization. if None, use min of values.
            vmax (float|None): Maximum value for values normalization. if None, use max of values.

        Returns:
            Buffer: A Buffer containing the RGBA8 colors mapped from the input values.
        """
        # Handle default parameters
        vmin = vmin if vmin is not None else values.min()
        vmax = vmax if vmax is not None else values.max()

        # sanity check
        assert CmapUtils.has_color_map(colormap_name), f"Colormap '{colormap_name}' is not recognized."

        mpl_color_map = matplotlib.cm.get_cmap(colormap_name)

        # sanity check
        assert vmin is not None, "vmin should not be None"
        assert vmax is not None, "vmax should not be None"

        normalized_values = (values - vmin) / (vmax - vmin)
        normalized_values = np.clip(normalized_values, 0.0, 1.0)
        color_mapped_normalized = mpl_color_map(normalized_values)  # normalized values to [0, 1]
        color_mapped_255 = (color_mapped_normalized * 255).astype(np.uint8)

        # Create a Buffer
        color_buffer = Buffer(color_mapped_255.__len__(), buffer_type=BufferType.rgba8)
        color_buffer.set_data(bytearray(color_mapped_255.tobytes()), 0, color_mapped_255.__len__())

        # Return the color buffer
        return color_buffer
