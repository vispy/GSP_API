import matplotlib.pyplot as plt
import numpy as np
import pathlib


# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create figure with transparent background
fig, ax = plt.subplots()

# Make figure and axes background transparent
fig.patch.set_alpha(0)
ax.set_facecolor("none")

# Plot data
ax.plot(x, y)

# Optional: remove top/right borders for cleaner look
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Save with transparent background in the same directory as the script
script_dir = pathlib.Path(__file__).parent
output_path = script_dir / "transparent_plot.png"
plt.savefig(output_path, transparent=True)

plt.show()
