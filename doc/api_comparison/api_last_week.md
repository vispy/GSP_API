# Pixel Example using Matplotlib Renderer

```python
# Create a canvas
canvas = Canvas(200, 200, 96.0)

# Create a viewport and add it to the canvas
viewport = Viewport(0, 0, canvas.get_width(), canvas.get_height())

# =============================================================================
# Add random points
# - various ways to create Buffers
# =============================================================================
point_count = 1024
group_count = 1

# Random positions - Create buffer from numpy array
positions_numpy = np.random.rand(point_count, 3).astype(np.float32) * 2.0 - 1
positions_buffer = Bufferx.from_numpy(positions_numpy, BufferType.vec3)

# all pixels red - Create buffer and fill it with a constant
colors_buffer = Buffer(group_count, BufferType.rgba8)
colors_buffer.set_data(bytearray([255, 0, 0, 255]) * colors_buffer.get_count(), 0, 1)

# Create the Pixels visual and add it to the viewport
pixels = Pixels(positions_buffer, colors_buffer, group_count)
model_matrix = Bufferx.mat4_identity()

# =============================================================================
# Render the canvas
# =============================================================================

# Create a camera
view_matrix = Bufferx.mat4_identity()
projection_matrix = Buffer(1, BufferType.mat4)
projection_matrix.set_data(bytearray(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float32).tobytes()), 0, 1)
camera = Camera(view_matrix, projection_matrix)

# Create a renderer and render the scene
matplotlibRenderer = MatplotlibRenderer(canvas)
rendered_image = matplotlibRenderer.render([viewport], [pixels], [model_matrix], [camera])

```

# Requirements at the time
- no matrix stored in the visual
- visual not attached to the viewport
- camera matrices (view and projection) provided at render time and per visual
- not ok to depend on numpy in the API
  - hence the creation of `Bufferx` helper class to convert from/to numpy arrays
  - `Bufferx` is not part of the public API, it is part of `gsp_extra`
- 


## Analysis

### PRO
- anybody can write a renderer easily
  - it can be done in user-space
  - datoviz + matplotlib renderer 

### CON