"""Minimal VisPy2 imshow producer example."""

import numpy as np

import vispy2 as vp


image = np.zeros((32, 32, 4), dtype=np.uint8)
image[..., 0] = np.linspace(0, 255, 32, dtype=np.uint8)[None, :]
image[..., 1] = np.linspace(255, 0, 32, dtype=np.uint8)[:, None]
image[..., 3] = 255

fig, ax = vp.subplots()
ax.imshow(image, extent=(-1.0, 1.0, -1.0, 1.0), origin="lower")

fig.savefig("examples/output/vispy2_protocol_imshow.png")
