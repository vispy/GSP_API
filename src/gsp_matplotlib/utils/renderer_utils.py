# pip imports
import matplotlib.artist
import numpy as np

# local imports
from gsp.constants import Constants


class RendererUtils:
    """Utility functions for matplotlib rendering in GSP."""

    @staticmethod
    def compute_faces_visible(faces_vertices_2d: np.ndarray, face_culling: Constants.FaceCulling) -> np.ndarray:
        """Compute which faces are visible based on their normals and the camera position.

        Returns:
            np.ndarray: A boolean array indicating which faces are visible.
        """
        # For each face, compute the cross product of the edges in 2D (NDC, y is up).
        # - cross_z > 0  → CCW in screen space → FrontSide (OpenGL / glTF convention)
        # - cross_z < 0  → CW  in screen space → BackSide
        # - cross_z == 0 → degenerate (line or point)
        faces_edges_2d_a = faces_vertices_2d[:, 1] - faces_vertices_2d[:, 0]
        faces_edges_2d_b = faces_vertices_2d[:, 2] - faces_vertices_2d[:, 0]
        faces_cross_z = faces_edges_2d_a[:, 0] * faces_edges_2d_b[:, 1] - faces_edges_2d_a[:, 1] * faces_edges_2d_b[:, 0]
        # this is the threshold below which a face is considered degenerated and trigger exception when inverting matrix
        faces_cross_threshold = 1e-6
        if face_culling == Constants.FaceCulling.FrontSide:
            faces_visible = faces_cross_z >= faces_cross_threshold
        elif face_culling == Constants.FaceCulling.BackSide:
            faces_visible = faces_cross_z <= -faces_cross_threshold
        elif face_culling == Constants.FaceCulling.BothSides:
            # If the face is degenerated (line or point), it is not visible
            faces_visible = np.abs(faces_cross_z) > faces_cross_threshold
        else:
            raise ValueError(f"Unknown face culling mode: {face_culling}")

        # print(f"faces_visible: {faces_visible.sum()}/{len(faces_visible)}")
        return faces_visible
