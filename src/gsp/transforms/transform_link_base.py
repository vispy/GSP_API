# stdlib imports
from abc import ABC, abstractmethod
from typing import Any

# local imports
from ..types import BufferType, Buffer


# =============================================================================
# TransformLink
# =============================================================================
class TransformLinkBase(ABC):
    """Base class for a link in a Transform chain."""

    @abstractmethod
    def apply(self, buffer_src: Buffer | None) -> Buffer:
        """Apply the transformation to the given buffer and return a new buffer."""
        pass

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def deserialize(data: dict[str, Any]) -> "TransformLinkBase":
        pass
