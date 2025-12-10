import numpy as np

import datoviz as dvz

app = dvz.App(background="white")
figure = app.figure(100, 30)
panel = figure.panel()
panzoom = panel.panzoom()

# # Define the strings and string parameters.
# strings = ["Hello world"] * 8
# string_count = len(strings)
# glyph_count = sum(map(len, strings))
# string_pos = np.zeros((string_count, 3), dtype=np.float32)
# string_pos[:, 0] = -0.8
# string_pos[:, 1] = 1 - 1.8 * np.linspace(0.3, 1, string_count) ** 2
# scales = np.linspace(1, 4, string_count).astype(np.float32)

# # Per-glyph parameters.
# colors = dvz.cmap("hsv", np.mod(np.linspace(0, 2, glyph_count), 1))

# visual = app.glyph(font_size=30)
# visual.set_strings(strings, string_pos=string_pos, scales=scales)
# visual.set_color(colors)


texts = ["Hello", "Datoviz"]
text_count = len(texts)
glyph_count = sum(map(len, texts))
vertices_numpy = np.array([[0.0, 0.0, 0.0], [0.5, 2.5, 0.0]]).astype(np.float32)
colors_numpy = np.zeros((glyph_count, 4), dtype=np.uint8)
colors_numpy[:, 0] = 255.0  # Red channel
colors_numpy[:, 3] = 255.0  # Alpha channel
font_sizes_numpy = np.array([20.0, 40.0]).astype(np.float32)
anchors_numpy = np.array([[0.0, 0.0], [1.0, 1.0]]).astype(np.float32)
angles_numpy = np.array([90.0, 45.0]).astype(np.float32)

scales = np.ones((text_count,), dtype=np.float32) * 1.0

visual = app.glyph(font_size=30)
visual.set_strings(texts, string_pos=vertices_numpy, scales=scales)
visual.set_color(colors_numpy)


panel.add(visual)
app.run()
app.destroy()
