"""Texture module for the GSP library."""

# stdlib imports
from typing import Any

# local imports
from ..types.transbuf import TransBuf
from ..utils.uuid_utils import UuidUtils


class Texture:
    """Texture class holding pixel data and its dimensions."""

    __slots__ = ["_uuid", "_data", "_width", "_height", "userData"]

    def __init__(self, data: TransBuf, width: int, height: int):
        """Create a new Texture from a buffer and its dimensions.

        Args:
            data (TransBuf): Pixel data stored in a TransBuf instance.
            width (int): Texture width in pixels.
            height (int): Texture height in pixels.
        """
        assert width > 0 and height > 0, "Texture dimensions must be positive"

        # TODO validate that buffer size matches width * height * pixel_size
        # TODO create a sanity check method for texture

        self._uuid: str = UuidUtils.generate_uuid()
        self._data: TransBuf = data
        self._width: int = width
        self._height: int = height
        self.userData: dict[str, Any] = {}
        """Container for user-defined metadata."""

    def __repr__(self) -> str:
        """Return string representation of the Texture instance."""
        return f"Texture(width={self._width}, height={self._height})"

    def get_uuid(self) -> str:
        """Get the UUID of the texture."""
        return self._uuid

    def get_data(self) -> TransBuf:
        """Get the pixel data of the texture."""
        return self._data

    def set_data(self, data: TransBuf) -> None:
        """Set the pixel data of the texture."""
        self._data = data

    def get_width(self) -> int:
        """Get the width of the texture in pixels."""
        return self._width

    def set_width(self, width: int) -> None:
        """Set the width of the texture in pixels."""
        assert width > 0, "Texture width must be positive"
        self._width = width

    def get_height(self) -> int:
        """Get the height of the texture in pixels."""
        return self._height

    def set_height(self, height: int) -> None:
        """Set the height of the texture in pixels."""
        assert height > 0, "Texture height must be positive"
        self._height = height
