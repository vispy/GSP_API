import numpy as np
from mpl3d.camera import Camera
from gsp_nico import Canvas, Viewport, Buffer, Pixels, Renderer

canvas = Canvas(512, 512, 96.0)
viewport = Viewport(canvas, 0, 0, 512, 512)
coords = Buffer.from_numpy(np.random.uniform(-1, +1, (1024, 3)), "vec3")
colors = Buffer.from_bytes(bytearray([255, 0, 0, 255]), "rgba8")
pixels = Pixels(coords, colors)

camera = Camera("perspective")
viewport.add(pixels, camera.view, camera.proj)

renderer = Renderer("matplotlib")
output = renderer.render(canvas, "RGBA")
