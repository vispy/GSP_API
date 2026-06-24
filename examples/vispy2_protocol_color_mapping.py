"""VisPy2 scalar color mapping producer example."""

import numpy as np

import vispy2 as vp


fig, ax = vp.subplots()
ax.set_title("VisPy2 scalar color mapping")
scale = ax.color_scale(cmap="viridis", clim=(0.0, 1.0), id="scale:viridis")

image = np.array(
    [
        [0.0, 0.2, 0.4],
        [0.6, 0.8, 1.0],
    ],
    dtype=np.float32,
)
ax.imshow(
    image,
    extent=(-1.0, 1.0, -0.6, 0.6),
    origin="lower",
    color_scale=scale,
    id="visual:image",
)
ax.scatter(
    [-0.75, 0.0, 0.75],
    [0.9, 0.9, 0.9],
    c=[0.0, 0.5, 1.0],
    color_scale=scale,
    size=26,
    id="visual:points",
)
ax.colorbar(
    scale,
    label="value",
    ticks=[0.0, 0.5, 1.0],
    tick_labels=["0", "0.5", "1"],
    linked_visual_ids=["visual:image", "visual:points"],
    id="guide:colorbar",
)

fig.savefig("examples/output/vispy2_protocol_color_mapping.png")
