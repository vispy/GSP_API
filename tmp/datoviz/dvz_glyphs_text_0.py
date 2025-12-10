import numpy as np

import datoviz as dvz

app = dvz.App(background="white")
figure = app.figure()
panel = figure.panel()
panzoom = panel.panzoom()

# Define the strings and string parameters.
texts = ["Hello", "world"]
string_count = len(texts)
glyph_count = sum(map(len, texts))
string_pos = np.zeros((string_count, 3), dtype=np.float32)
string_pos[:, 0] = -0.8
string_pos[:, 1] = 1 - 1.8 * np.linspace(0.3, 1, string_count) ** 2
scales = np.linspace(1, 4, string_count).astype(np.float32)

# Per-glyph parameters.
colors_numpy0 = dvz.cmap("hsv", np.mod(np.linspace(0, 2, glyph_count), 1))
colors_numpy = np.zeros((glyph_count, 4), dtype=np.uint8)
colors_numpy[:, 0] = 255.0  # Red channel
colors_numpy[:, 3] = 255.0  # Alpha channel

visual = app.glyph(font_size=30)
visual.set_strings(texts, string_pos=string_pos, scales=scales)
visual.set_color(colors_numpy0)

panel.add(visual)
app.run()
app.destroy()
