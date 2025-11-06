# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class Canvas:
    def __init__(self, width: int, height: int, dpi: float):
        self._uuid: str = UuidUtils.generate_uuid()
        self._width: int = width
        self._height: int = height
        self._dpi: float = dpi
        self.userData: dict[str, Any] = {}

    def get_uuid(self) -> str:
        return self._uuid

    def get_width(self) -> int:
        return self._width

    def get_height(self) -> int:
        return self._height

    def get_dpi(self) -> float:
        return self._dpi
