# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class Viewport:
    __slots__ = ["_uuid", "_x", "_y", "_width", "_height", "userData"]

    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Create a viewport.

        :param x: offset from left in pixels
        :type x: int
        :param y: offset from bottom in pixels
        :type y: int
        :param width: width in pixels
        :type width: int
        :param height: height in pixels
        :type height: int
        """
        self._uuid: str = UuidUtils.generate_uuid()
        self._x: int = x
        self._y: int = y
        self._width: int = width
        self._height: int = height
        self.userData: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"Viewport(x={self._x}, y={self._y}, width={self._width}, height={self._height})"

    def get_uuid(self) -> str:
        return self._uuid

    def get_x(self) -> int:
        """
        Get the x offset (in pixels from left) of the viewport.
        """
        return self._x

    def get_y(self) -> int:
        """
        Get the y offset (in pixels from bottom) of the viewport.
        """
        return self._y

    def get_width(self) -> int:
        """
        Get the width (in pixels) of the viewport.
        """
        return self._width

    def get_height(self) -> int:
        """
        Get the height (in pixels) of the viewport.
        """
        return self._height
