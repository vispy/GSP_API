from ..core.visual_base import VisualBase
from ..types.transbuf import TransBuf
from ..types.buffer import Buffer
from ..transforms.transform_chain import TransformChain
from ..types.group import Groups
from ..utils.group_utils import GroupUtils


class Pixels(VisualBase):
    def __init__(self, positions: TransBuf, colors: TransBuf, groups: Groups):
        super().__init__()

        self.__positions: TransBuf = positions
        self.__colors: TransBuf = colors
        self.__groups: Groups = groups

        self.check_attributes()

    # =============================================================================
    # get/set attributes
    # =============================================================================

    def get_positions(self) -> TransBuf:
        return self.__positions

    def set_positions(self, positions: TransBuf) -> None:
        self.__positions = positions
        self.check_attributes()

    def get_colors(self) -> TransBuf:
        return self.__colors

    def set_colors(self, colors: TransBuf) -> None:
        self.__colors = colors
        self.check_attributes()

    def get_groups(self) -> Groups:
        return self.__groups

    def set_groups(self, groups: Groups) -> None:
        self.__groups = groups
        self.check_attributes()

    def set_attributes(self, positions: TransBuf | None = None, colors: TransBuf | None = None, groups: Groups | None = None) -> None:
        """Set multiple attributes at once and then check their validity."""
        if positions is not None:
            self.__positions = positions
        if colors is not None:
            self.__colors = colors
        if groups is not None:
            self.__groups = groups
        self.check_attributes()

    # =============================================================================
    # Sanity check functions
    # =============================================================================

    def check_attributes(self) -> None:
        """Check that the attributes are valid and consistent."""
        self.sanity_check_attributes(self.__positions, self.__colors, self.__groups)

    @staticmethod
    def sanity_check_attribute_buffers(positions: Buffer, colors: Buffer, groups: Groups):
        """same as .sanity_check_attributes() but accept only Buffers.

        - It is meant to be used after converting TransBuf to Buffer.
        """
        # sanity check - each attribute must be a Buffer (not a transform chain)
        assert isinstance(positions, Buffer), "Positions must be a Buffer"
        assert isinstance(colors, Buffer), "Colors must be a Buffer"

        Pixels.sanity_check_attributes(positions, colors, groups)

    @staticmethod
    def sanity_check_attributes(positions: TransBuf, colors: TransBuf, groups: Groups):

        # =============================================================================
        # if any of the attributes is a TransformChain not fully defined, skip the sanity check
        # =============================================================================

        if isinstance(positions, TransformChain) and not positions.is_fully_defined():
            return
        if isinstance(colors, TransformChain) and not colors.is_fully_defined():
            return

        # =============================================================================
        # Check groups
        # =============================================================================

        # get position_count and group_count
        position_count = positions.get_count() if isinstance(positions, Buffer) else positions.get_buffer_count()
        group_count = GroupUtils.get_group_count(groups)

        # Check groups matches position count
        GroupUtils.sanity_check(position_count, groups)

        # =============================================================================
        # Check each attributes
        # =============================================================================

        # Check colors attribute
        color_count = colors.get_count() if isinstance(colors, Buffer) else colors.get_buffer_count()
        assert color_count == group_count, f"Colors count {color_count} must match group count {group_count}"
