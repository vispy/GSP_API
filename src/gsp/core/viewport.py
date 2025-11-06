# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class Viewport:
    def __init__(self, origin_x: int, origin_y: int, width: int, height: int):
        self._uuid: str = UuidUtils.generate_uuid()
        self._origin_x: int = origin_x
        self._origin_y: int = origin_y
        self._width: int = width
        self._height: int = height
        self.userData: dict[str, Any] = {}

    def get_uuid(self) -> str:
        return self._uuid

    def get_origin_x(self) -> int:
        return self._origin_x

    def get_origin_y(self) -> int:
        return self._origin_y

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height
