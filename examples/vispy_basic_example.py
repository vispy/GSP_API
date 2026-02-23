"""Basic example showing how to use the Vispy2 scatter visual with a Matplotlib renderer and a Canvas."""

# pip imports
import numpy as np

# local imports
import gsp
import vispy2
import gsp_matplotlib

# Create a canvas
canvas = gsp.core.Canvas(width=400, height=400, dpi=127)

# Create a renderer
renderer_base = gsp_matplotlib.renderer.MatplotlibRenderer(canvas)

# Create an AxesManaged instance for the canvas
axes_managed = vispy2.axes.AxesManaged(renderer_base, 40, 40, 320, 320)

# Create a visual
positions = np.random.rand(100, 3).astype(np.float32) * 2.0 - 1
points = vispy2.scatter(positions)

# Add the visual to the AxesManaged instance
axes_managed.add_visual(points)

# start the animation loop
axes_managed.start()
