import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

# Generate some sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Define color and width variations
# Here we vary color by y-value and width by derivative magnitude
colors = plt.cm.viridis((y - y.min()) / (y.max() - y.min()))  # colormap based on y
widths = 1 + 40 * np.abs(np.gradient(y))  # thicker where slope is steep

# Create segments between consecutive points
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Create a LineCollection
lc = LineCollection(segments, colors=colors[:-1], linewidths=widths[:-1], capstyle="round")

# Plot
fig, ax = plt.subplots(figsize=(8, 4))
ax.add_collection(lc)
ax.autoscale()
ax.set_aspect("auto")
ax.set_title("Polyline with varying color and width per segment")
ax.set_xlabel("x")
ax.set_ylabel("y")

plt.show()
