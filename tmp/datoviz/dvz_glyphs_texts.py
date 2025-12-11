import numpy as np

import datoviz as dvz

app = dvz.App(background="white")
figure = app.figure(100, 30)
panel = figure.panel()
panzoom = panel.panzoom()

# =============================================================================
#
# =============================================================================
text_strings = ["Hello", "Datoviz"]
text_count = len(text_strings)
glyph_count = sum(map(len, text_strings))

vertices_numpy = np.array([[0.0, 0.0, 0.0], [0.5, 2.5, 0.0]]).astype(np.float32)

colors_numpy = np.zeros((glyph_count, 4), dtype=np.uint8)
colors_numpy[:, 0] = 255.0  # Red channel
colors_numpy[:, 3] = 255.0  # Alpha channel

font_sizes_numpy = np.array([20.0, 40.0]).astype(np.float32)
anchors_numpy = np.array([[0.0, 0.0], [1.0, 1.0]]).astype(np.float32)
angles_numpy = np.array([90.0, 45.0]).astype(np.float32)


glyph_scales = np.ones((text_count,), dtype=np.float32) * 1.0

glyph_visual = app.glyph(font_size=100)
glyph_visual.set_strings(text_strings, string_pos=vertices_numpy, scales=glyph_scales)
glyph_visual.set_color(colors_numpy)

panel.add(glyph_visual)

# =============================================================================
#
# =============================================================================
app.run()
app.destroy()
