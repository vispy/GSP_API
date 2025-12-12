# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class VisualBase:
    __slots__ = ["_uuid", "userData"]

    def __init__(self):
        self._uuid: str = UuidUtils.generate_uuid()
        self.userData: dict[str, Any] = {}

    def get_uuid(self) -> str:
        """Get the unique identifier of the visual object.

        Returns:
            The unique identifier.
        """
        return self._uuid
