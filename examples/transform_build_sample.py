import numpy as np
import os
import math

__dirname__ = os.path.dirname(os.path.abspath(__file__))

# Create a 3d sinusoidal wave pattern
half_size = 0.5
point_count = 50
x = np.linspace(-half_size, half_size, point_count)
z = np.linspace(-half_size, half_size, point_count)
x, z = np.meshgrid(x, z)
y = np.sin(np.sqrt(x**2 + z**2) * math.pi * 7) / 10
positions = np.vstack((x.flatten(), y.flatten(), z.flatten())).T

# save positions to a .npy file
file_path = f"{__dirname__}/data/sample_positions_3d.npy"
np.save(file_path, positions)
