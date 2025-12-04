# stdlib imports
import sys

# pip imports
import numpy as np

# ## Glossary:
# - Point is a typographic unit of length — used for font sizes and layout.
# - dpi is dots per inch, a measure of spatial printing or video dot density.
#   - Dot refers to a physical pixel or ink droplet on a display or printer.


class UnitUtils:

    @staticmethod
    def in_to_cm(inches: float) -> float:
        """Convert inches to centimeters.

        Args:
            inches (float): Length in inches.

        Returns:
            float: Length in centimeters.
        """
        return inches * 2.54

    @staticmethod
    def cm_to_in(cm: float) -> float:
        """Convert centimeters to inches.

        Args:
            cm (float): Length in centimeters.

        Returns:
            float: Length in inches.
        """
        return cm / 2.54

    @staticmethod
    def device_pixel_ratio() -> float:
        """Get the device pixel ratio for high-DPI displays.

        Returns:
            float: Device pixel ratio (typically 1.0 for standard displays, >1.0 for high-DPI).
        """
        # detect if running on a macOS retina display or other high-DPI display
        # This is a placeholder implementation; actual detection may vary based on the GUI framework used.
        is_macosx = "darwin" in sys.platform
        if is_macosx:
            return 2.0  # Common value for retina displays
        return 1.0

    @staticmethod
    def pixel_to_point(pixel_size: float, dpi: float) -> float:
        """Convert pixel size to typographic point size based on DPI.

        Args:
            pixel_size (float): Size in pixels.
            dpi (float): Dots per inch of the display.

        Returns:
            float: Size in points.
        """
        inches_per_pixel = 1.0 / dpi
        points_per_inch = 72.0
        point_size = pixel_size * inches_per_pixel * points_per_inch
        return point_size

    @staticmethod
    def point_to_pixel(point_size: float, dpi: float) -> float:
        """Convert point size to pixel size based on DPI.

        Args:
            point_size (float): Size in points.
            dpi (float): Dots per inch of the display.

        Returns:
            float: Size in pixels.
        """
        inches_per_point = 1.0 / 72.0
        pixels_per_inch = dpi
        pixel_size = point_size * inches_per_point * pixels_per_inch
        return pixel_size

    # =============================================================================
    # numpy array versions
    # =============================================================================

    @staticmethod
    def pixel_to_point_numpy(pixel_sizes: np.ndarray, dpi: float) -> np.ndarray:
        """Convert an array of pixel sizes to point sizes based on DPI.
        Args:
            pixel_sizes (np.ndarray): Array of sizes in pixels.
            dpi (float): Dots per inch of the display.
        Returns:
            np.ndarray: Array of sizes in points.
        """
        inches_per_pixel = 1.0 / dpi
        points_per_inch = 72.0
        point_sizes = pixel_sizes * inches_per_pixel * points_per_inch
        return point_sizes

    @staticmethod
    def point_to_pixel_numpy(point_sizes: np.ndarray, dpi: float) -> np.ndarray:
        """Convert an array of point sizes to pixel sizes based on DPI.

        Args:
            point_sizes (np.ndarray): Array of sizes in points.
            dpi (float): Dots per inch of the display.

        Returns:
            np.ndarray: Array of sizes in pixels.
        """
        inches_per_point = 1.0 / 72.0
        pixels_per_inch = dpi
        pixel_sizes = point_sizes * inches_per_point * pixels_per_inch
        return pixel_sizes
