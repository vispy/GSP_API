import os
import numpy as np
from mpl3d.camera import Camera
from gsp_nico import Canvas, Viewport, Buffer, Pixels, Renderer

canvas = Canvas(100, 100, 96.0)
viewport = Viewport(canvas, 0, 0, 100, 100)

point_count = 1024
coords = Buffer.from_numpy(np.random.uniform(-1, +1, (point_count, 3)), "vec3")
colors = Buffer.from_bytes(bytearray([255, 0, 0, 255] * point_count), "rgba8")
pixels = Pixels(coords, colors)

camera = Camera("perspective")
viewport.add(pixels, camera.view, camera.proj)

renderer = Renderer("datoviz")
output = renderer.render(canvas, "png")

# save output image
dirname = os.path.dirname(__file__)
image_path = os.path.join(dirname, f"output/{os.path.basename(__file__).replace('.py', '')}.png")
with open(image_path, "wb") as f:
    f.write(output)
print(f"Image saved to: {image_path}")
