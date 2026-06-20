"""Minimal VisPy2 point-over-image producer example."""

import numpy as np

import vispy2 as vp


image = np.zeros((16, 16, 4), dtype=np.uint8)
image[..., 2] = 180
image[..., 3] = 255

fig, ax = vp.subplots()
ax.imshow(image, extent=(-1.0, 1.0, -1.0, 1.0))
ax.scatter(
    np.array([0.0, 0.45], dtype=np.float32),
    np.array([0.0, -0.35], dtype=np.float32),
    color=np.array([[255, 255, 255, 255], [230, 57, 70, 255]], dtype=np.uint8),
    size=np.array([64.0, 36.0], dtype=np.float32),
)

fig.savefig("examples/output/vispy2_protocol_point_over_image.png")
