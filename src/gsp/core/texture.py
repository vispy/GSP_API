"""Texture module for the GSP library."""

# stdlib imports
from typing import Any

# local imports
from ..types.buffer import Buffer
from ..utils.uuid_utils import UuidUtils


class Texture:
    """Texture class holding pixel data and its dimensions."""

    __slots__ = ["_uuid", "_buffer", "_width", "_height", "userData"]

    def __init__(self, buffer: Buffer, width: int, height: int):
        """Create a new Texture from a buffer and its dimensions.

        Args:
            buffer (Buffer): Pixel data stored in a Buffer instance.
            width (int): Texture width in pixels.
            height (int): Texture height in pixels.
        """
        assert width > 0 and height > 0, "Texture dimensions must be positive"

        self._uuid: str = UuidUtils.generate_uuid()
        self._buffer: Buffer = buffer
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

    def get_buffer(self) -> Buffer:
        """Get the buffer containing the texture pixel data."""
        return self._buffer

    def set_buffer(self, buffer: Buffer) -> None:
        """Replace the buffer storing the texture pixel data."""
        self._buffer = buffer

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

