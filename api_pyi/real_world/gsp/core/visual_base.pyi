from ..utils.uuid_utils import UuidUtils as UuidUtils
from typing import Any

class VisualBase:
    userData: dict[str, Any]
    def __init__(self) -> None: ...
    def get_uuid(self) -> str: ...
