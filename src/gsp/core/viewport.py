"""Viewport class representing a rectangular area on the canvas."""

# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class Viewport:
    """Viewport class representing a rectangular area on the canvas."""

    __slots__ = ["_uuid", "_x", "_y", "_width", "_height", "userData"]

    def __init__(self, x: int, y: int, width: int, height: int):
        """Create a viewport.

        Args:
            x (int): The x offset (in pixels from left) of the viewport.
            y (int): The y offset (in pixels from bottom) of the viewport.
            width (int): The width (in pixels) of the viewport.
            height (int): The height (in pixels) of the viewport.
        """
        self._uuid: str = UuidUtils.generate_uuid()
        self._x: int = x
        self._y: int = y
        self._width: int = width
        self._height: int = height
        self.userData: dict[str, Any] = {}

    def __repr__(self) -> str:
        """Return string representation of the Viewport instance."""
        return f"Viewport(x={self._x}, y={self._y}, width={self._width}, height={self._height})"

    def get_uuid(self) -> str:
        """Get the unique identifier of the viewport.

        Returns:
            str: The unique identifier.
        """
        return self._uuid

    def get_x(self) -> int:
        """Get the x offset (in pixels from left) of the viewport.

        Returns:
            int: The x offset.
        """
        return self._x

    def set_x(self, x: int) -> None:
        """Set the x offset (in pixels from left) of the viewport.

        Args:
            x (int): The new x offset.
        """
        self._x = x

    def get_y(self) -> int:
        """Get the y offset (in pixels from bottom) of the viewport.

        Returns:
            int: The y offset.
        """
        return self._y

    def set_y(self, y: int) -> None:
        """Set the y offset (in pixels from bottom) of the viewport.

        Args:
            y (int): The new y offset.
        """
        self._y = y

    def get_width(self) -> int:
        """Get the width (in pixels) of the viewport.

        Returns:
            int: The width.
        """
        return self._width

    def set_width(self, width: int) -> None:
        """Set the width (in pixels) of the viewport.

        Args:
            width (int): The new width.
        """
        self._width = width

    def get_height(self) -> int:
        """Get the height (in pixels) of the viewport.

        Returns:
            int: The height.
        """
        return self._height

    def set_height(self, height: int) -> None:
        """Set the height (in pixels) of the viewport.

        Args:
            height (int): The new height.
        """
        self._height = height
