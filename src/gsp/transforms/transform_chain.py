# local imports
from ..types import BufferType, Buffer
from .transform_link import TransformLink


# =============================================================================
# Transform
# =============================================================================
class TransformChain:
    """Chain of transformations to apply to data."""

    def __init__(self, buffer_count: int, buffer_type: BufferType | None) -> None:
        self.__links: list[TransformLink] = []
        """Ordered list of links defining the transform."""

        # sanity check
        if buffer_count < 0:
            assert buffer_count == -1, "TransformChain: buffer_count must be -1 (undefined) or >= 0"

        self.__buffer_count = buffer_count
        """Number of elements in the output Buffer. -1 if not defined yet."""

        self.__buffer_type = buffer_type
        """Type of the output Buffer. None if not defined yet."""

    # =============================================================================
    #
    # =============================================================================

    def is_fully_defined(self) -> bool:
        """Check if the TransformChain is fully defined (i.e., buffer_type is not None and buffer_count >= 0)."""
        if self.__buffer_type is None:
            return False
        if self.__buffer_count < 0:
            return False
        return True

    def get_buffer_count(self) -> int:
        """Get the number of elements in the output Buffer. use this only if .is_fully_defined() is True."""

        # sanity check - buffer_count MUST be defined
        assert self.__buffer_type is not None, "TransformChain.get_buffer_count: buffer_type is None. use .is_fully_defined() to check."
        assert self.__buffer_count >= 0, "TransformChain.get_buffer_count: buffer_count is negative. use .is_fully_defined() to check."

        # return the buffer count
        return self.__buffer_count

    def get_buffer_type(self) -> BufferType:
        """Get the type of the output Buffer. use this only if .is_fully_defined() is True."""

        # sanity check - buffer_type MUST be defined
        assert self.__buffer_type is not None, "TransformChain.get_buffer_type: buffer_type is None. use .is_fully_defined() to check."
        assert self.__buffer_count >= 0, "TransformChain.get_buffer_count: buffer_count is negative. use .is_fully_defined() to check."

        # return the buffer type
        return self.__buffer_type

    # =============================================================================
    # .add/.remove/.clear the links
    # =============================================================================

    def add(self, link: TransformLink) -> None:
        """Add a TransformLink to the chain."""
        self.__links.append(link)

    def remove(self, link: TransformLink) -> None:
        """Remove a TransformLink from the chain."""
        self.__links.remove(link)

    # =============================================================================
    # .run()
    # =============================================================================

    def run(self) -> Buffer:
        """Compute the transform and return a Buffer with the result."""

        # Create a new Buffer to hold the transformed data
        buffer = None

        # Apply each link in the chain
        for link in self.__links:
            buffer = link.apply(buffer)

        # Sanity check the output buffer
        assert buffer is not None, "TransformChain.to_buffer: No buffer produced by the transform chain."

        # Return the final buffer
        return buffer
