import matplotlib.pyplot as plt
import matplotlib.axes
import matplotlib.figure
import numpy as np

# Fixing random state for reproducibility
np.random.seed(0)

marker_count = 10
positions_x = np.random.rand(marker_count)
positions_y = np.random.rand(marker_count)
colors = np.sqrt(positions_x**2 + positions_y**2)
sizes = np.linspace(20, 200, marker_count)

figure, axes = plt.subplots(1, 1, sharex=True, sharey=True, layout="constrained")
figure: matplotlib.figure.Figure = figure
axes: matplotlib.axes.Axes = axes

axes.scatter(positions_x, positions_y, s=sizes, c=colors, marker=r"$\clubsuit$")

plt.show()
