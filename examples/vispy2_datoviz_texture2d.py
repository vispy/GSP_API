"""Render the bounded GSP Texture2D mesh profile with local Datoviz v0.4-dev.

The example uses only public ``gsp_vispy2`` producer and experimental session APIs. The accepted
profile is RGBA8, per-vertex UVs, nearest/clamp/no-mipmap sampling, multiplicative base color, and
unlit output. Linear filtering is intentionally not exposed while P036 is under consultation.

Run without arguments to inspect capability support without creating a window. Pass ``--show`` to
open a bounded two-frame Datoviz display.
"""

from __future__ import annotations

import argparse

import numpy as np

from gsp.protocol import MESH_MATERIAL_TEXTURE2D_UNLIT_CAPABILITY
import gsp_vispy2 as vp


def build_figure() -> vp.Figure:
    """Build one nearest-sampled quadrant texture on an indexed quad."""
    texture = np.array(
        [
            [[239, 65, 68, 255], [42, 157, 143, 255]],
            [[69, 123, 157, 255], [244, 162, 97, 255]],
        ],
        dtype=np.uint8,
    )
    positions = np.array(
        [[-0.75, -0.75], [0.75, -0.75], [0.75, 0.75], [-0.75, 0.75]],
        dtype=np.float32,
    )
    faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32)
    # GSP uses bottom-left UV origin while image row zero is the top row.
    uvs = np.array(
        [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],
        dtype=np.float32,
    )

    figure, axes = vp.subplots()
    axes.set_xlim(-1.0, 1.0)
    axes.set_ylim(-1.0, 1.0)
    axes.mesh(
        positions,
        faces,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
        coordinate_space="ndc",
        texture=texture,
        uvs=uvs,
        id="visual:texture2d-example",
    )
    return figure


def main() -> int:
    """Inspect support and optionally show the textured mesh."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--show",
        action="store_true",
        help="open a bounded two-frame Datoviz display after capability inspection",
    )
    args = parser.parse_args()

    figure = build_figure()
    with vp.open_session("datoviz") as session:
        inspection = session.inspect(figure, operation="display")
        inspection.require_executable()
        if not inspection.capabilities.supports_view3d_capability(
            MESH_MATERIAL_TEXTURE2D_UNLIT_CAPABILITY
        ):
            raise RuntimeError(
                "local Datoviz does not advertise the bounded Texture2D mesh capability"
            )
        if args.show:
            session.show(figure, block=True, frame_count=2)
        else:
            print("Datoviz Texture2D nearest profile: supported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
