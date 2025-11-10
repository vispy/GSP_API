import typing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


# Generate multiple polylines (for example, 3 sine waves with offsets)
num_lines = 2
num_points = 3

lines = []
colors = []
widths = []

for i in range(num_lines):
    x = np.linspace(0, 10, num_points)
    y = np.sin(x + i) + i * 1.5  # vertical offset for each line

    # Make color vary along the line (map y to color)
    color_values = plt.cm.plasma((y - y.min()) / (y.max() - y.min()))

    # Vary linewidth by slope magnitude
    line_widths = 1 + 3.0 * np.abs(np.gradient(y))

    # Build line segments for this line
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lines.append(segments)
    colors.append(color_values[:-1])
    widths.append(line_widths[:-1])

# Flatten everything for one LineCollection
segments_all = np.vstack(lines)
colors_all = np.vstack(colors)
widths_all = np.hstack(widths)

# Create one LineCollection
# line_collection = LineCollection(segments_all, colors=colors_all, linewidths=widths_all, capstyle="round")
line_collection = LineCollection([])
# line_collection = LineCollection(segments_all, colors=colors_all, linewidths=widths_all, capstyle="round")

line_collection.set_paths(typing.cast(list, segments_all))
line_collection.set_color(typing.cast(list, colors_all))
line_collection.set_linewidth(typing.cast(list, widths_all))
line_collection.set_capstyle("round")

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.add_collection(line_collection)
ax.autoscale()
ax.set_title("Multiple variable-width/color polylines in one LineCollection")
ax.set_xlabel("x")
ax.set_ylabel("y")

plt.show()
