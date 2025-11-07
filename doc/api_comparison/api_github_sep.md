- from https://github.com/vispy/GSP/pull/30#issuecomment-3325021521

```python
# Create a GSP scene
canvas = Canvas(512, 512, 100)
viewport = Viewport(0, 0, canvas.width, canvas.height, (1,1,1,1))
canvas.add(viewport)

# Add some random points
n_points = 100
positions = np.random.uniform(-0.5, 0.5, (n_points, 3))
pixels = Pixels(positions)
viewport.add(pixels)

# Render the scene with matplotlib
camera = Camera("perspective")
renderer = MatplotlibRenderer()
png_image = renderer.render(canvas, camera)

# Export the scene to JSON
json_renderer = JsonRenderer()
scene_json = json_renderer.render(canvas, camera)

# Render the scene remotely (if you have a GSP server running)
network_renderer = NetworkRenderer("http://localhost:5000")
png_image2 = network_renderer.render(canvas, camera)
```