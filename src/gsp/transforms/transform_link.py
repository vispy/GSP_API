# stdlib imports
from abc import ABC, abstractmethod

# local imports
from ..types import BufferType, Buffer


# =============================================================================
# TransformLink
# =============================================================================
class TransformLink(ABC):
    """Base class for a link in a Transform chain."""

    @abstractmethod
    def apply(self, buffer_src: Buffer | None) -> Buffer:
        """Apply the transformation to the given buffer and return a new buffer."""
        pass
