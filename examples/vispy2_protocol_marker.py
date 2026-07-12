"""VisPy2 protocol marker producer example.

This example creates a formal GSP MarkerVisual through the VisPy2 producer API and renders it through
the Matplotlib protocol backend. It intentionally does not call backend implementation APIs directly.
"""

import numpy as np

import gsp_vispy2 as vp


fig, ax = vp.subplots()
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_title("Protocol markers")
ax.markers(
    np.array([-0.72, -0.36, 0.0, 0.36, 0.72], dtype=np.float32),
    np.array([-0.34, 0.30, 0.08, -0.22, 0.42], dtype=np.float32),
    shape=("disc", "square", "triangle", "diamond", "cross"),
    fill_color=np.array(
        [
            [216, 27, 96, 255],
            [30, 136, 229, 255],
            [0, 137, 123, 255],
            [251, 140, 0, 255],
            [94, 53, 177, 255],
        ],
        dtype=np.uint8,
    ),
    size=np.full(5, 64.0, dtype=np.float32),
    stroke_color=np.array([16, 16, 16, 255], dtype=np.uint8),
    stroke_width=4.0,
)

fig.savefig("examples/output/vispy2_protocol_marker.png")
