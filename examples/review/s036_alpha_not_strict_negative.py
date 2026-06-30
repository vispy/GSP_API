"""API review example: S036 translucent 3D mesh diagnostic.

This negative example intentionally does not use the default numbered review-example
sweep. It verifies that translucent 3D MeshVisual colors are rejected from the
opaque-depth path with mesh3d_alpha_not_strict.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from gsp.protocol import CoordinateSpace, MeshVisual, View3DDiagnosticCode
from gsp_matplotlib.protocol_renderer import render_mesh_visual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    mesh = MeshVisual(
        id="visual:alpha-not-strict",
        positions=np.array(
            [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.NDC,
        color=np.array([230, 57, 70, 128], dtype=np.uint8),
    )
    fig, ax = plt.subplots()
    try:
        try:
            render_mesh_visual(ax, mesh)
        except NotImplementedError as exc:
            diagnostic = View3DDiagnosticCode.MESH3D_ALPHA_NOT_STRICT.value
            if diagnostic in str(exc):
                print(diagnostic)
                return 0
            raise
        raise RuntimeError("expected mesh3d_alpha_not_strict diagnostic")
    finally:
        plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
