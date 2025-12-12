from typing import Union

Groups = Union[int, list[int], list[list[int]]]
"""A type that can represent group IDs in various forms.

- if an int, it represents the size of the group
- if a list of int, each int represents the size of each subgroup
- if a list of list of int, each sublist represents a list of element index which are part of this group
  - len(groups) represents the number of groups
  - groups[0] represent the element indices of the first group
    - groups[1] represent the element indices of the second group

"""
