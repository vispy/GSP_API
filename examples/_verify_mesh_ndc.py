"""Verify NDC z-sign and Y-orientation conventions of the matplotlib mesh renderer.

Plan A from https://github.com/vispy/GSP_API/issues/21 (follow-up to #20).

For each projection (perspective + ortho), this script feeds known probe points
through the same MVP pipeline used by the renderer and prints a verdict for:

    Bug 7 — painter's algorithm sort direction (descending vs ascending on NDC z)
    Bug 8 — FrontSide culling sign (depends on NDC y direction)

It does NOT change renderer code. The output decides what the follow-up fix
plans look like.
"""

import numpy as np

from gsp.utils.math_utils import MathUtils
from gsp_extra.mpl3d import glm


CROSS_THRESHOLD = 1e-6  # mirrors renderer_utils.py:60


def screen_cross_z(face_vertices_2d: np.ndarray) -> float:
        """Replicates the cross-product expression at renderer_utils.py:59.

        Args:
                face_vertices_2d: shape (3, 2) — three 2D vertices of one triangle.

        Returns:
                The signed z component of the 2D edge cross product.
        """
        a = face_vertices_2d[1] - face_vertices_2d[0]
        b = face_vertices_2d[2] - face_vertices_2d[0]
        return float(a[0] * b[1] - a[1] * b[0])


def probe(projection_name: str, projection_matrix: np.ndarray) -> None:
        """Run all four probes against a single projection matrix and print a verdict."""

        model_matrix = np.eye(4, dtype=np.float32)
        view_matrix = glm.lookat(eye=(0, 0, 4), center=(0, 0, 0), up=(0, 1, 0))
        mvp_matrix = MathUtils.compute_mvp_matrix(model_matrix, view_matrix, projection_matrix)

        # Probe 2 — NDC z sign (Bug 7).
        # p_near is closer to the camera (camera at z=4 looking toward origin),
        # p_far is on the opposite side.
        z_probes = np.array([
                [0.0, 0.0,  3.9],   # near
                [0.0, 0.0, -3.9],   # far
        ], dtype=np.float32)
        _, z_ndc = MathUtils.apply_transform_matrix(z_probes, mvp_matrix)
        near_ndc_z = float(z_ndc[0, 2])
        far_ndc_z = float(z_ndc[1, 2])
        far_is_more_positive = far_ndc_z > near_ndc_z
        # Painter's algorithm: draw farthest first. So sort key for "far first" is
        # the value that's larger for far points → np.argsort(-key) (descending).
        sort_should_be = 'descending' if far_is_more_positive else 'ascending'
        sort_current_is_descending = True  # see matplotlib_renderer_mesh.py:151
        sort_status = 'OK' if sort_should_be == ('descending' if sort_current_is_descending else 'ascending') else 'INVERTED'

        # Probe 3 — NDC y direction (Bug 8 part 1).
        y_probe = np.array([[0.0, 0.5, 0.0]], dtype=np.float32)
        _, y_ndc = MathUtils.apply_transform_matrix(y_probe, mvp_matrix)
        ndc_y_value = float(y_ndc[0, 1])
        ndc_y_is_up = ndc_y_value > 0
        ndc_y_label = 'up' if ndc_y_is_up else 'down'

        # Probe 4 — winding (Bug 8 part 2). CCW from camera looking down -z.
        triangle = np.array([
                [-0.5, -0.5, 0.0],
                [ 0.5, -0.5, 0.0],
                [ 0.0,  0.5, 0.0],
        ], dtype=np.float32)
        _, tri_ndc = MathUtils.apply_transform_matrix(triangle, mvp_matrix)
        tri_2d = tri_ndc[:, :2]
        cross_z = screen_cross_z(tri_2d)
        # Current code (renderer_utils.py:62-63): FrontSide is visible when
        # cross_z <= -threshold. A camera-facing CCW triangle SHOULD be visible
        # under FrontSide, so we expect cross_z to be negative.
        front_side_correct = cross_z <= -CROSS_THRESHOLD
        if abs(cross_z) < CROSS_THRESHOLD:
                front_status = 'DEGENERATE'
        else:
                front_status = 'OK' if front_side_correct else 'INVERTED'

        # Detail lines.
        print(f'--- {projection_name} ---')
        print(f'  near_ndc_z = {near_ndc_z:+.4f}    far_ndc_z = {far_ndc_z:+.4f}'
                f'    → far is {"more positive" if far_is_more_positive else "more negative"}')
        print(f'  ndc_y for world y=+0.5: {ndc_y_value:+.4f}    → NDC y is {ndc_y_label}')
        print(f'  facing-camera CCW triangle screen cross_z = {cross_z:+.6f}')
        print(f'[{projection_name}] sort={sort_should_be}({sort_status})  '
                f'frontside={"correct" if front_status == "OK" else front_status.lower()}({front_status})  '
                f'ndc_y={ndc_y_label}({"OK" if ndc_y_is_up else "FLIPPED"})')
        print()


def main() -> None:
        perspective_matrix = glm.perspective(fovy=45.0, aspect=1.0, znear=0.1, zfar=10.0)
        ortho_matrix = glm.ortho(left=-1.0, right=1.0, bottom=-1.0, top=1.0, znear=0.1, zfar=10.0)
        probe('perspective', perspective_matrix)
        probe('ortho', ortho_matrix)


if __name__ == '__main__':
        main()
