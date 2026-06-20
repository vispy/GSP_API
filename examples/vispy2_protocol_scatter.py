"""Minimal VisPy2 scatter producer example."""

import numpy as np

import vispy2 as vp


fig, ax = vp.subplots()
ax.scatter(
    np.array([-0.7, 0.0, 0.7], dtype=np.float32),
    np.array([-0.3, 0.4, -0.1], dtype=np.float32),
    color=np.array([[230, 57, 70, 255], [29, 53, 87, 255], [42, 157, 143, 255]], dtype=np.uint8),
    size=np.array([36.0, 64.0, 49.0], dtype=np.float32),
)

fig.savefig("examples/output/vispy2_protocol_scatter.png")
