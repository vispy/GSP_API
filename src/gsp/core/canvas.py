"""Canvas module for the GSP library."""
# stdlib imports
from typing import Any

# local imports
from ..types.color import Color
from ..utils.uuid_utils import UuidUtils


class Canvas:
    """Canvas class representing a drawing surface with specific dimensions and DPI."""

    __slots__ = ["_uuid", "_width", "_height", "_dpi", "_background_color", "userData"]

    def __init__(self, width: int, height: int, dpi: float, background_color: Color):
        """Create a new Canvas object with the given width, height, and dpi.

        Args:
            width (int): Width of the canvas in pixels.
            height (int): Height of the canvas in pixels.
            dpi (float): Dots per inch (DPI) of the canvas. If set to the screen PPI, the 'inch' unit in will correspond to one physical inch on the screen.
            background_color (Color): Background color of the canvas.
        """
        self._uuid: str = UuidUtils.generate_uuid()
        self._width: int = width
        self._height: int = height
        self._dpi: float = dpi
        self._background_color: Color = background_color
        self.userData: dict[str, Any] = {}

    def __repr__(self) -> str:
        """Return string representation of the Canvas instance."""
        return f"Canvas(width={self._width}, height={self._height}, dpi={self._dpi}, background_color={self._background_color})"

    def get_uuid(self) -> str:
        """Get the UUID of the Canvas instance.

        Returns:
            str: The UUID of the Canvas.
        """
        return self._uuid

    def get_width(self) -> int:
        """Get the width of the canvas in pixels."""
        return self._width

    def set_width(self, width: int) -> None:
        """Set the width of the canvas in pixels.

        Args:
            width (int): The new width in pixels.
        """
        self._width = width

    def get_height(self) -> int:
        """Get the height of the canvas in pixels."""
        return self._height

    def set_height(self, height: int) -> None:
        """Set the height of the canvas in pixels.

        Args:
            height (int): The new height in pixels.
        """
        self._height = height

    def get_dpi(self) -> float:
        """Get the DPI of the canvas."""
        return self._dpi

    def set_dpi(self, dpi: float) -> None:
        """Set the DPI of the canvas.

        Args:
            dpi (float): The new DPI value.
        """
        self._dpi = dpi

    def get_background_color(self) -> Color:
        """Get the background color of the canvas.

        Returns:
            Color: The background color.
        """
        return self._background_color

    def set_background_color(self, background_color: Color) -> None:
        """Set the background color of the canvas.

        Args:
            background_color (Color): The new background color.
        """
        self._background_color = background_color
