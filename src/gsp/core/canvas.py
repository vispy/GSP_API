# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class Canvas:
    __slots__ = ["_uuid", "_width", "_height", "_dpi", "userData"]

    def __init__(self, width: int, height: int, dpi: float):
        """Create a new Canvas object with the given width, height, and dpi.

        Args:
            width (int): Width of the canvas in pixels.
            height (int): Height of the canvas in pixels.
            dpi (float): Dots per inch (DPI) of the canvas. If set to the screen PPI, the 'inch' unit in will correspond to one physical inch on the screen.
        """
        self._uuid: str = UuidUtils.generate_uuid()
        self._width: int = width
        self._height: int = height
        self._dpi: float = dpi
        self.userData: dict[str, Any] = {}

    def __repr__(self) -> str:
        return f"Canvas(width={self._width}, height={self._height}, dpi={self._dpi})"

    def get_uuid(self) -> str:
        return self._uuid

    def get_width(self) -> int:
        return self._width

    def set_width(self, width: int) -> None:
        self._width = width

    def get_height(self) -> int:
        return self._height

    def set_height(self, height: int) -> None:
        self._height = height

    def get_dpi(self) -> float:
        return self._dpi

    def set_dpi(self, dpi: float) -> None:
        self._dpi = dpi
