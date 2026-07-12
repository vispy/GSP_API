"""VisPy2 protocol path producer example.

This example creates an open multi-subpath PathVisual through the VisPy2 producer API.
"""

import numpy as np

import gsp_vispy2 as vp


subpath_a = np.array(
    [[-0.82, 0.54], [-0.48, 0.20], [-0.20, 0.48], [0.08, 0.12]], dtype=np.float32
)
subpath_b = np.array(
    [[-0.78, -0.04], [-0.42, -0.36], [-0.08, -0.06], [0.28, -0.40], [0.62, -0.08]],
    dtype=np.float32,
)
subpath_c = np.array(
    [[0.20, 0.62], [0.48, 0.28], [0.74, 0.56], [0.86, 0.16]], dtype=np.float32
)
positions = np.ascontiguousarray(np.vstack([subpath_a, subpath_b, subpath_c]))

fig, ax = vp.subplots()
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_title("Protocol paths")
ax.path(
    positions,
    path_lengths=(len(subpath_a), len(subpath_b), len(subpath_c)),
    color=np.array(
        [[30, 136, 229, 255], [216, 27, 96, 255], [0, 137, 123, 255]], dtype=np.uint8
    ),
    width=np.array([10.0, 22.0, 34.0], dtype=np.float32),
    cap="round",
    join="round",
)

fig.savefig("examples/output/vispy2_protocol_path.png")
