import numpy as np
import matplotlib.pyplot as plt

# Example base image
base = np.random.rand(100, 100, 3)  # RGB

# Example overlay with transparency
overlay = np.zeros((50, 50, 4))
overlay[..., :3] = 1.0  # white color
overlay[..., 3] = np.linspace(0, 1, 50)[:, None]  # gradient alpha

fig, ax = plt.subplots()
ax.imshow(base)

# Overlay, respecting alpha channel
ax.imshow(overlay, extent=(25.0, 75.0, 25.0, 75.0), origin="upper")

plt.show()
