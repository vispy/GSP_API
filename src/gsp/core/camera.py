# stdlib imports
from typing import Any

# local imports
from ..types.transbuf import TransBuf
from ..utils.uuid_utils import UuidUtils


class Camera:
    def __init__(self, view_matrix: TransBuf, projection_matrix: TransBuf):
        self._uuid: str = UuidUtils.generate_uuid()
        self._view_matrix: TransBuf = view_matrix
        self._projection_matrix: TransBuf = projection_matrix
        self.userData: dict[str, Any] = {}

    def get_uuid(self) -> str:
        return self._uuid

    def set_view_matrix(self, view_matrix: TransBuf):
        self._view_matrix = view_matrix

    def get_view_matrix(self) -> TransBuf:
        return self._view_matrix

    def set_projection_matrix(self, projection_matrix: TransBuf):
        self._projection_matrix = projection_matrix

    def get_projection_matrix(self) -> TransBuf:
        return self._projection_matrix
