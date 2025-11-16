# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class Viewport:
    __slots__ = ["_uuid", "_x", "_y", "_width", "_height", "userData"]

    def __init__(self, x: int, y: int, width: int, height: int):
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
        return self._x

    def get_y(self) -> int:
        return self._y

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height
