```python
canvas = Canvas(size=(10*cm,10*cm))
viewport = Viewport(canvas, position = (10*px, 10*px), size=(1-10*px, 1-10*px)
colormap = Colormap("viridis)

camera_1 = Camera()
positions = Buffer(1000, vec3)
positions[...] = np.random.uniform(-1,1,(1000,3))
points = Points(positions, fill_colors = colormap(Out("screen.z"))
viewport.add(points, camera_1)

camera_2 = Camera()
title = "A Title"
title = Text(title, size=14*pt, position = (0.5, 1.0 - 4*pt), anchor = (0.5,1.0))
viewport.add(title, camera_2)

canvas.render("output.pdf")
canvas.render("output.png", dpi=200)
gsp.write("output.yaml")
```