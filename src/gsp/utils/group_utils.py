# stdlib imports
from typing import Literal
import typing

# local imports
from ..types.group import Groups


class GroupUtils:

    @staticmethod
    def get_group_count(groups: Groups) -> int:
        """Return the number of groups from the groups object."""

        groups_format = GroupUtils._groups_format(groups)
        if groups_format == GroupUtils.FORMAT_INT:
            groups_typed = typing.cast(int, groups)
            group_count = groups_typed
        elif groups_format == GroupUtils.FORMAT_LIST_INT:
            groups_typed = typing.cast(list[int], groups)
            group_count = len(groups_typed)
        elif groups_format == GroupUtils.FORMAT_LIST_LIST_INT:
            groups_typed = typing.cast(list[list[int]], groups)
            group_count = len(groups_typed)
        else:
            raise NotImplementedError(f"Group buffer shape not supported: {type(groups)}")

        return group_count

    # =============================================================================
    # is_instance_of_groups
    # =============================================================================

    @staticmethod
    def is_instance_of_groups(groups: Groups) -> bool:
        """Check if the type  of groups.
        - Deep check where all elements are checked.
        - Dont check the values themselves, only the types

        groups can be:
        - int
        - list[int]
        - list[list[int]]
        """

        if isinstance(groups, int):
            return True
        elif isinstance(groups, list) and all(isinstance(int_value, int) for int_value in groups):
            return True
        elif isinstance(groups, list) and all(isinstance(group, list) for group in groups) and all(isinstance(int_value, int) for int_list in groups for int_value in int_list):  # type: ignore[union-attr]
            return True
        else:
            return False

    # =============================================================================
    # ._groups_format()
    # =============================================================================

    FORMAT_INT = "format_int"
    FORMAT_LIST_INT = "format_list_int"
    FORMAT_LIST_LIST_INT = "format_list_list_int"

    @staticmethod
    def _groups_format(groups: Groups) -> Literal["format_int", "format_list_int", "format_list_list_int"]:
        """Return the format of the groups object as a string.
        No check is done

        Returns:
            str: "format_int", "format_list_int", "format_list_list_int"
        """

        if isinstance(groups, int):
            return GroupUtils.FORMAT_INT
        elif isinstance(groups, list) and groups.__len__() > 0 and isinstance(groups[0], int):
            return GroupUtils.FORMAT_LIST_INT
        elif isinstance(groups, list) and groups.__len__() > 0 and isinstance(groups[0], list) and groups[0].__len__() > 0 and isinstance(groups[0][0], int):
            return GroupUtils.FORMAT_LIST_LIST_INT
        else:
            raise ValueError(f"Groups object is not valid: {type(groups)}")

    # =============================================================================
    # Sanity Checks
    # =============================================================================

    @staticmethod
    def sanity_check(vertex_count: int, groups: Groups) -> None:
        """Perform sanity checks on the groups object, raising exceptions if not valid.

        Raise:
            ValueError: if the groups object is not valid.
        """

        if not GroupUtils.is_instance_of_groups(groups):
            raise ValueError(f"Groups object is not valid: {type(groups)}")

        groups_mode = GroupUtils._groups_format(groups)

        if groups_mode == GroupUtils.FORMAT_INT:
            groups_int = typing.cast(int, groups)
            if groups_int <= 0:
                raise ValueError(f"Groups as int must be positive, got {groups_int}")
            if groups_int > vertex_count:
                raise ValueError(f"Groups as int must be less than or equal to vertex_count, got groups={groups_int}, vertex_count={vertex_count}")
        elif groups_mode == GroupUtils.FORMAT_LIST_INT:
            groups_list_int = typing.cast(list[int], groups)
            if any(group_size <= 0 for group_size in groups_list_int):
                raise ValueError(f"Groups as list[int], group sizes must be all positive, got {groups_list_int}")
            if sum(groups_list_int) != vertex_count:
                raise ValueError(
                    f"Sum of groups size as list[int] must equal vertex_count, got sum(groups)={sum(groups_list_int)}, vertex_count={vertex_count}"
                )
        elif groups_mode == GroupUtils.FORMAT_LIST_LIST_INT:
            groups_list_list_int = typing.cast(list[list[int]], groups)
            all_indices = [index for group in groups_list_list_int for index in group]
            if any(index < 0 or index >= vertex_count for index in all_indices):
                raise ValueError(f"Groups as list[list[int]], all indices must be in range [0, {vertex_count-1}], got indices={all_indices}")
            if len(set(all_indices)) != len(all_indices):
                raise ValueError(f"Groups as list[list[int]], all indices must be unique, got indices={all_indices}")

        # TODO check that the list matches the vertex count where needed
        # TODO check that no list is empty

    @staticmethod
    def sanity_check_safe(vertex_count: int, groups: Groups) -> bool:
        """Perform sanity checks on the groups object.
        same as .sanity_check_groups() but dont raise exceptions if not valid

        Returns:
            bool: True if the groups object is valid, False otherwise.
        """

        try:
            GroupUtils.sanity_check(vertex_count, groups)
            return True
        except ValueError:
            return False

    # =============================================================================
    # .compute_indices_per_group
    # =============================================================================

    @staticmethod
    def compute_indices_per_group(vertex_count: int, groups: Groups) -> list[list[int]]:
        """Compute indices_per_group for groups depending on the type of groups

        Returns:
            group_count (int): number of groups
            indices_per_group (list[list[int]]): list of vertex indices per group
        """

        # sanity check
        assert GroupUtils.sanity_check_safe(vertex_count, groups), "groups failed sanity check"

        groups_format = GroupUtils._groups_format(groups)
        if groups_format == GroupUtils.FORMAT_INT:
            groups_typed = typing.cast(int, groups)
            indices_per_group = GroupUtils._compute_indices_per_group_int(vertex_count, groups_typed)
        elif groups_format == GroupUtils.FORMAT_LIST_INT:
            groups_typed = typing.cast(list[int], groups)
            indices_per_group = GroupUtils._compute_indices_per_group_list_int(vertex_count, groups_typed)
        elif groups_format == GroupUtils.FORMAT_LIST_LIST_INT:
            groups_typed = typing.cast(list[list[int]], groups)
            indices_per_group = GroupUtils._compute_indices_per_group_list_list_int(vertex_count, groups_typed)
        else:
            raise NotImplementedError(f"Group buffer shape not supported: {type(groups)}")

        return indices_per_group

    # =============================================================================
    # ._compute_indices_per_group_*() for each format
    # =============================================================================

    @staticmethod
    def _compute_indices_per_group_int(vertex_count: int, groups: int) -> list[list[int]]:
        """Compute indices_per_group for groups as int.
        The int represents the number of groups.

        group_count = groups
        indices_per_group = list[list[int]]

        Examples:
        - vertex_count = 6, groups = 3 - divisible - all groups are vertex_count // groups long
          - indices_per_group = [[0, 1], [2, 3], [4, 5]]
        - vertex_count = 7, groups = 4 - non divisible - all groups are vertex_count // (groups-1) long, except the last group takes the remainder
          - indices_per_group = [[0, 1], [2, 3], [4, 5], [6]]

        Returns:
            group_count (int): number of groups
            indices_per_group (list[list[int]]): list of vertex indices per group
        """

        # Initialize output variables
        group_count: int = groups
        indices_per_group: list[list[int]] = []

        # Create the indices per group for this case
        element_count_per_group = (vertex_count // group_count) if (vertex_count % group_count == 0) else (vertex_count // (group_count - 1))

        for group_index in range(group_count):
            is_last_group = group_index == group_count - 1
            start_index = element_count_per_group * group_index
            end_index = (start_index + element_count_per_group) if is_last_group is False else vertex_count

            # Fill the indices for this group
            indices_per_group.append(list(range(start_index, end_index)))

        return indices_per_group

    @staticmethod
    def _compute_indices_per_group_list_int(vertex_count: int, groups: list[int]) -> list[list[int]]:
        """Compute indices_per_group for groups as list[int].
        In this case, each int represents the size of each group.

        group_count = len(groups)
        indices_per_group = list[list[int]]

        Returns:
            group_count (int): number of groups
            indices_per_group (list[list[int]]): list of vertex indices per group
        """

        # Initialize output variables
        indices_per_group: list[list[int]] = []

        # Create the indices per group for this case
        current_index = 0
        for group_size in groups:
            # Fill the indices for this group
            group_indices = list(range(current_index, current_index + group_size))
            indices_per_group.append(group_indices)

            # Update the current index
            current_index += group_size

        return indices_per_group

    @staticmethod
    def _compute_indices_per_group_list_list_int(vertex_count: int, groups: list[list[int]]) -> list[list[int]]:
        """Compute indices_per_group for groups as list[list[int]].
        In this case, the groups are directly the indices per group themselves.

        group_count = len(groups)
        indices_per_group = list[list[int]]

        Returns:
            group_count (int): number of groups
            indices_per_group (list[list[int]]): list of vertex indices per group
        """

        # Initialize output variables
        indices_per_group: list[list[int]] = groups

        return indices_per_group
