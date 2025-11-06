# stdlib imports
from typing import Any

# local imports
from ..utils.uuid_utils import UuidUtils


class VisualBase:
    def __init__(self):
        self._uuid: str = UuidUtils.generate_uuid()
        self.userData: dict[str, Any] = {}

    def get_uuid(self) -> str:
        return self._uuid
