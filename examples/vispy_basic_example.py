"""Basic example showing how to use AxesManaged with a Matplotlib renderer and a Canvas."""

# pip imports
import numpy as np

# local imports
from gsp.core import Canvas
from gsp.constants import Constants
from gsp.types import Buffer, BufferType
from gsp.utils.unit_utils import UnitUtils
from gsp.visuals import Points
from gsp_extra.bufferx import Bufferx
from gsp_matplotlib.renderer import MatplotlibRenderer
from vispy2.axes import AxesManaged

# Create a canvas
canvas = Canvas(width=400, height=400, dpi=127, background_color=Constants.Color.white)

# Create a renderer
renderer_base = MatplotlibRenderer(canvas)

# Create an AxesManaged instance for the canvas
axes_managed = AxesManaged(renderer_base, 40, 40, 320, 320)

# Create a visual
positions = np.random.rand(100, 3).astype(np.float32) * 2.0 - 1
positions_buffer = Bufferx.from_numpy(positions, BufferType.vec3)
sizes_buffer = Bufferx.from_numpy(np.array([10] * len(positions), dtype=np.float32), BufferType.float32)
face_colors_buffer = Buffer(len(positions), BufferType.rgba8)
face_colors_buffer.set_data(bytearray([255, 0, 0, 255]) * len(positions), 0, len(positions))
edge_colors_buffer = Buffer(len(positions), BufferType.rgba8)
edge_colors_buffer.set_data(Constants.Color.blue * len(positions), 0, len(positions))
edge_widths = np.array([UnitUtils.pixel_to_point(1, canvas.get_dpi())] * len(positions), dtype=np.float32)
edge_widths_buffer = Bufferx.from_numpy(edge_widths, BufferType.float32)
points = Points(positions_buffer, sizes_buffer, face_colors_buffer, edge_colors_buffer, edge_widths_buffer)

# Add the visual to the AxesManaged instance
axes_managed.add_visual(points)

# start the animation loop
axes_managed.start()
