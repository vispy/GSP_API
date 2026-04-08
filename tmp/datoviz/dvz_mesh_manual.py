import numpy as np

import datoviz as dvz

N = 5
colors = dvz.cmap("spring", np.linspace(0, 1, N))
scale = 0.35

sc = dvz.ShapeCollection()
sc.add_tetrahedron(offset=(-1, 0, 0.5), scale=scale, color=colors[0])
sc.add_hexahedron(offset=(0, 0, 0.5), scale=scale, color=colors[1])
sc.add_octahedron(offset=(1, 0, 0.5), scale=scale, color=colors[2])
sc.add_dodecahedron(offset=(-0.5, 0, -0.5), scale=scale, color=colors[3])
sc.add_icosahedron(offset=(+0.5, 0, -0.5), scale=scale, color=colors[4])


app = dvz.App()
figure = app.figure()
panel = figure.panel(
    background=(
        (255, 255, 255, 255),
        (255, 255, 255, 255),
        (255, 255, 255, 255),
        (255, 255, 255, 255),
    )
)
arcball = panel.arcball(initial=(0, 0, 0))

# position for a single triangle
positions = np.array(
    [
        [-0.5 + 1, 0.5, 0.0],
        [+0.5 + 1, 0.5, 0.0],
        [-0.5 + 1, -0.5, 0.0],
    ],
    dtype=np.float32,
)


indices = np.array([0, 2, 1], dtype=np.uint32)

normals = np.array(
    [
        [0.0, 0.0, +1.0],
        [0.0, 0.0, +1.0],
        [0.0, 0.0, +1.0],
    ],
    dtype=np.float32,
)

colors = np.array(
    [
        [255, 0, 0, 255],
        [255, 0, 0, 255],
        [255, 0, 0, 255],
    ],
    dtype=np.uint8,
)

sc.add_custom(positions=positions, indices=indices, normals=normals, colors=colors, offset=(0, 0, 0), scale=1.0)

# visual_mesh = app.mesh(position=positions, index=indices)
# panel.add(visual_mesh)

visual_shape_collection = app.mesh(sc, lighting=False)
panel.add(visual_shape_collection)

app.run()
app.destroy()

sc.destroy()
