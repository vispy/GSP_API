# stdlib imports
import warnings

# pip imports
import matplotlib.cm
import numpy as np

# local imports
from gsp.types import Buffer, BufferType


class CmapUtils:

    @staticmethod
    def has_color_map(colormap_name: str) -> bool:
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
            values (np.ndarray): Array of values to map to colors.
            vmin (float|None): Minimum value for values normalization. if None, use min of values.
            vmax (float|None): Maximum value for values normalization. if None, use max of values.
        """

        # Handle default parameters
        if vmin is None:
            vmin = values.min()
        if vmax is None:
            vmax = values.max()

        # sanity check
        assert CmapUtils.has_color_map(colormap_name), f"Colormap '{colormap_name}' is not recognized."

        color_map = matplotlib.cm.get_cmap(colormap_name)

        assert vmin is not None, "vmin should not be None"
        assert vmax is not None, "vmax should not be None"

        normalized_values = (values - vmin) / (vmax - vmin)
        normalized_values = np.clip(normalized_values, 0.0, 1.0)
        color_mapped_normalized = color_map(normalized_values)  # normalize values to [0, 1]
        color_mapped_255 = (color_mapped_normalized * 255).astype(np.uint8)

        # Create a Buffer
        color_buffer = Buffer(color_mapped_255.__len__(), buffer_type=BufferType.rgba8)
        color_buffer.set_data(bytearray(color_mapped_255.tobytes()), 0, color_mapped_255.__len__())

        return color_buffer

    @staticmethod
    @warnings.deprecated("Use get_color_map() instead")
    def get_color_map_numpy(colormap_name: str, values: np.ndarray, vmin: float | None = None, vmax: float | None = None) -> np.ndarray:
        """Get colors from a colormap for the given values.
        Args:
            colormap_name (str): Name of the colormap (e.g., 'plasma', 'viridis', etc.).
            values (np.ndarray): Array of values to map to colors.
            vmin (float): Minimum value for values normalization.
            vmax (float): Maximum value for values normalization.

        TODO: this depends on numpy and matplotlib, which is not ideal.
        TODO: return a Buffer with rgba8 ?

        """
        # sanity check
        assert CmapUtils.has_color_map(colormap_name), f"Colormap '{colormap_name}' is not recognized."

        color_map = matplotlib.cm.get_cmap(colormap_name)

        if vmin is None:
            vmin = values.min()
        if vmax is None:
            vmax = values.max()

        assert vmin is not None, "vmin should not be None"
        assert vmax is not None, "vmax should not be None"

        normalized_values = (values - vmin) / (vmax - vmin)
        normalized_values = np.clip(normalized_values, 0.0, 1.0)
        color_mapped_normalized = color_map(normalized_values)  # normalize values to [0, 1]
        color_mapped_255 = (color_mapped_normalized * 255).astype(np.uint8)

        return color_mapped_255


# =============================================================================
#
# =============================================================================
if __name__ == "__main__":
    # simple test
    import numpy as np
    import matplotlib.pyplot

    values = np.linspace(0.0, 1.0, 100)
    cmap_name = "plasma"
    colors = CmapUtils.get_color_map_numpy(cmap_name, values)

    matplotlib.pyplot.scatter(values, np.zeros_like(values), c=colors, s=100, marker="s")
    matplotlib.pyplot.title(f"Colormap: {cmap_name}")
    matplotlib.pyplot.show()
