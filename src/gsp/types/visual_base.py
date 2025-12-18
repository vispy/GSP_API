"""Base class for visual objects in GSP.

This module provides the foundational VisualBase class that all visual
objects inherit from, providing common functionality like UUID generation
and user data storage.
"""
# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class VisualBase:
    """Base class for all visual objects in the GSP library.

    This class provides fundamental functionality for visual objects including
    automatic UUID generation and a userData dictionary for storing custom
    metadata.
    """
    __slots__ = ["_uuid", "userData"]

    def __init__(self):
        """Initialize a new VisualBase instance.

        Creates a new visual object with a unique identifier and an empty
        userData dictionary.
        """
        self._uuid: str = UuidUtils.generate_uuid()
        self.userData: dict[str, Any] = {}

    def get_uuid(self) -> str:
        """Get the unique identifier of the visual object.

        Returns:
            str: The unique identifier.
        """
        return self._uuid
