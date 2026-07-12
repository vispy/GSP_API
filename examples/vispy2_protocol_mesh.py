"""VisPy2 protocol mesh producer example.

This example creates a formal GSP MeshVisual through the VisPy2 producer API and renders it through
the Matplotlib protocol backend. It intentionally uses the strict S025 2D flat triangle subset.
"""

import numpy as np

import gsp_vispy2 as vp


positions = np.array(
    [
        [-0.72, -0.56],
        [0.02, -0.64],
        [0.66, -0.34],
        [0.52, 0.52],
        [-0.36, 0.64],
    ],
    dtype=np.float32,
)
faces = np.array([[0, 1, 4], [1, 2, 3], [1, 3, 4]], dtype=np.uint32)
face_colors = np.array(
    [[30, 136, 229, 255], [216, 27, 96, 255], [0, 137, 123, 255]],
    dtype=np.uint8,
)

fig, ax = vp.subplots()
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_title("Protocol mesh")
ax.mesh(positions, faces, color=face_colors, color_mode="face", id="visual:mesh")

fig.savefig("examples/output/vispy2_protocol_mesh.png")
