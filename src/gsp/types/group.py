"""Group type definitions for GSP.

This module defines types used to represent groups of elements in various forms.
"""

from typing import Union

Groups = Union[int, list[int], list[list[int]]]
"""A type that can represent group IDs in various forms.

The Groups type supports three different formats:
    - int: Represents the size of a single group.
    - list[int]: Each int represents the size of each subgroup.
    - list[list[int]]: Each sublist represents element indices in a group.
        - len(groups) represents the number of groups.
        - groups[0] contains element indices of the first group.
        - groups[1] contains element indices of the second group.
"""
