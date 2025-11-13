# pip imports
import matplotlib.cm
import numpy as np


class CmapUtils:

    @staticmethod
    def has_color_map(colormap_name: str) -> bool:
        try:
            matplotlib.cm.get_cmap(colormap_name)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_color_map(colormap_name: str, values: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
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

        normalized_values = (values - vmin) / (vmax - vmin)
        normalized_values = np.clip(normalized_values, 0.0, 1.0)
        color_mapped = color_map(normalized_values)  # normalize values to [0, 1]

        return color_mapped


if __name__ == "__main__":
    # simple test
    import numpy as np
    import matplotlib.pyplot

    values = np.linspace(0.0, 1.0, 100)
    cmap_name = "plasma"
    colors = CmapUtils.get_color_map(cmap_name, values, values.min(), values.max())

    matplotlib.pyplot.scatter(values, np.zeros_like(values), c=colors, s=100, marker="s")
    matplotlib.pyplot.title(f"Colormap: {cmap_name}")
    matplotlib.pyplot.show()
