"""VisPy2 protocol guide API example with image, scatter, limits, and ticks."""

import numpy as np

import gsp_vispy2 as vp


image = np.zeros((24, 24, 4), dtype=np.uint8)
image[..., 0] = np.linspace(40, 220, 24, dtype=np.uint8)[None, :]
image[..., 1] = np.linspace(210, 50, 24, dtype=np.uint8)[:, None]
image[..., 2] = 120
image[..., 3] = 255

fig, ax = vp.subplots()
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_xlabel("x position")
ax.set_ylabel("y position")
ax.set_title("VisPy2 guide API")
ax.set_xticks([-1.0, 0.0, 1.0], labels=["left", "center", "right"])
ax.set_yticks([-1.0, 0.0, 1.0])
ax.grid(True)
ax.imshow(image, extent=(-1.0, 1.0, -1.0, 1.0), origin="lower")
ax.scatter(
    np.array([-0.6, 0.0, 0.55], dtype=np.float32),
    np.array([-0.35, 0.25, 0.5], dtype=np.float32),
    color=np.array([[29, 53, 87, 255], [230, 57, 70, 255], [42, 157, 143, 255]], dtype=np.uint8),
    size=np.array([42.0, 64.0, 48.0], dtype=np.float32),
)

fig.savefig("examples/output/vispy2_protocol_guides.png")
