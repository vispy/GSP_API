# ## Glossary:
# - Point is a typographic unit of length — used for font sizes and layout.
# - dpi is dots per inch, a measure of spatial printing or video dot density.
#   - Dot refers to a physical pixel or ink droplet on a display or printer.


class UnitUtils:
    @staticmethod
    def pixel_to_point(pixel_size: float, dpi: float) -> float:
        """Convert pixel size to point size based on DPI.

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
