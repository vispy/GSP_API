import numpy as np

import datoviz as dvz

app = dvz.App()
figure = app.figure()
panel = figure.panel(background=((255, 255, 255, 255), (255, 255, 255, 255), (255, 255, 255, 255), (255, 255, 255, 255)))
panzoom = panel.panzoom()

# Define the strings and string parameters.
visual1 = app.glyph(font_size=30)
visual1.set_strings(
    ["Hello world"],
    scales=np.array([1.0], dtype=np.float32),
    string_pos=np.array([[0.0, 0.2, 0.0]], dtype=np.float32),
    anchor=(0.0, 0.5),
)

visual2 = app.glyph(font_size=30)
visual2.set_strings(
    ["Hello world"],
    scales=np.array([1.0], dtype=np.float32),
    string_pos=np.array([[0.0, 0.0, 0.0]], dtype=np.float32),
    anchor=(-1.0, 0.5),
)

panel.add(visual1)
panel.add(visual2)
app.run()
app.destroy()
