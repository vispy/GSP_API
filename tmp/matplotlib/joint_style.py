"""
=========
JoinStyle
=========

The `matplotlib._enums.JoinStyle` controls how Matplotlib draws the corners
where two different line segments meet. For more details, see the
`~matplotlib._enums.JoinStyle` docs.
"""

import matplotlib.pyplot as plt

from matplotlib._enums import JoinStyle

"""Demonstrate how each JoinStyle looks for various join angles."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes


def plot_angle(ax: matplotlib.axes.Axes, x, y, angle, style):
    phi = np.radians(angle)
    xx = [x + 0.5, x, x + 0.5 * np.cos(phi)]
    yy = [y, y, y + 0.5 * np.sin(phi)]
    ax.plot(xx, yy, lw=12, color="tab:blue", solid_joinstyle=style)
    ax.plot(xx, yy, lw=1, color="black")
    ax.plot(xx[1], yy[1], "o", color="tab:red", markersize=3)


fig, ax = plt.subplots(figsize=(5, 4), constrained_layout=True)
ax.set_title("Join style")
for x, style in enumerate(["miter", "round", "bevel"]):
    ax.text(x, 5, style)
    for y, angle in enumerate([20, 45, 60, 90, 120]):
        plot_angle(ax, x, y, angle, style)
        if x == 0:
            ax.text(-1.3, y, f"{angle} degrees")
ax.set_xlim(-1.5, 2.75)
ax.set_ylim(-0.5, 5.5)
ax.set_axis_off()
fig.show()

plt.show()

# %%
# .. tags:: purpose: reference, styling: linestyle
