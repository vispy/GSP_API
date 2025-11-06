import numpy as np
from ..types.buffer import Buffer as Buffer

class MathUtils:
    @staticmethod
    def apply_mvp_to_vertices(vertices: np.ndarray, model_matrix: np.ndarray, view_matrix: np.ndarray, projection_matrix: np.ndarray) -> np.ndarray: ...
