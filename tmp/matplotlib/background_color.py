"""Example of setting the background color of the figure and axes in matplotlib."""

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

fig.patch.set_facecolor((1, 0, 0, 1))
ax.set_facecolor((0, 1, 0, 1))
ax.plot([1, 2, 3])

plt.show()
