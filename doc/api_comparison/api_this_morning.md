```python
canvas = Canvas(200, 200, 96.0)
viewport = Viewport(canvas, 0, 0, 200, 200)

point_count = 5_000
coords = Buffer.from_numpy(np.random.uniform(-1, +1, (point_count, 3)), "vec3")
colors = Buffer.from_bytes(bytearray([255, 0, 0, 255]), "rgba8")
pixels = Pixels(coords, colors)

camera = Camera("perspective")
viewport.add(pixels, camera.view, camera.proj)

renderer = Renderer("matplotlib")
output = renderer.render(canvas, "png")
```

## Requirements at the time
- it is now ok to depend on numpy