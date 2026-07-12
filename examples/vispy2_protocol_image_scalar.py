"""VisPy2 protocol scalar-image producer example.

This example demonstrates the bounded S023 scalar image contract: gray colormap plus explicit clim.
"""

import numpy as np

import gsp_vispy2 as vp


y, x = np.mgrid[0:12, 0:16].astype(np.float32)
image = (x - 4.0) / 8.0 + (y - 6.0) / 12.0

fig, ax = vp.subplots()
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_title("Protocol scalar image")
ax.imshow(
    image.astype(np.float32),
    extent=(-0.78, 0.78, -0.58, 0.58),
    colormap="gray",
    clim=(-0.5, 1.25),
)

fig.savefig("examples/output/vispy2_protocol_image_scalar.png")
