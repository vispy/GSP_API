from pathlib import Path

import imageio.v3 as iio
import numpy as np

import datoviz as dvz

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
width, height = 800, 600
half_width, half_height = width / 2.0, height / 2.0
svg_path = "M50,10 L61.8,35.5 L90,42 L69,61 L75,90 L50,75 L25,90 L31,61 L10,42 L38.2,35.5 Z"


def generate_data():
    grid_x = 6
    grid_y = 5
    N = grid_x * grid_y

    # Grid coordinates in [-1, 1]
    x = np.linspace(-1, 1, grid_x)
    y = np.linspace(-1, 1, grid_y)
    X, Y = np.meshgrid(x, y)
    x_flat = X.flatten()
    y_flat = Y.flatten()
    z_flat = np.zeros_like(x_flat)

    positions = np.stack([x_flat, y_flat, z_flat], axis=1).astype(np.float32)
    positions *= 0.8  # margin

    # Hue along x-axis
    hue = (x_flat + 1) / 2
    colors = dvz.cmap("hsv", hue)

    # Size: exponential growth from 10px to 50px along y-axis
    y_norm = (y_flat + 1) / 2
    sizes = 25 * 2.0**y_norm
    sizes = sizes.astype(np.float32)

    return N, positions, colors, sizes


def make_visual(panel):
    N, position, color, size = generate_data()
    angle = np.linspace(0, 2 * np.pi, N)
    visual = app.marker(
        position=position,
        color=color,
        size=size,
        angle=angle,
        edgecolor=(255, 255, 255, 255),
        linewidth=2.0,
    )
    panel.add(visual)
    return visual


# =============================================================================
#
# =============================================================================
app = dvz.App()
figure = app.figure()

# Code Stroke
panel = figure.panel(offset=(0, half_height), size=(half_width, half_height))
visual = make_visual(panel)
visual.set_mode("code")
visual.set_aspect("stroke")
visual.set_shape("spade")

# run app
app.run()
app.destroy()
