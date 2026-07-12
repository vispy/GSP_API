"""VisPy2 protocol segment producer example.

This example creates independent SegmentVisual strokes through the VisPy2 producer API.
"""

import numpy as np

import gsp_vispy2 as vp


starts = np.array(
    [[-0.76, 0.56], [-0.70, 0.16], [-0.64, -0.26], [-0.58, -0.66]],
    dtype=np.float32,
)
ends = np.array(
    [[0.58, 0.38], [0.64, 0.04], [0.70, -0.34], [0.76, -0.60]],
    dtype=np.float32,
)
colors = np.array(
    [[30, 136, 229, 255], [0, 137, 123, 255], [251, 140, 0, 255], [216, 27, 96, 255]],
    dtype=np.uint8,
)

fig, ax = vp.subplots()
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_title("Protocol segments")
ax.segments(
    starts,
    ends,
    color=colors,
    width=np.array([8.0, 16.0, 28.0, 42.0], dtype=np.float32),
    cap="round",
)

fig.savefig("examples/output/vispy2_protocol_segment.png")
