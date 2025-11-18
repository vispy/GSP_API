import pathlib
import datoviz as dvz

app = dvz.App(offscreen=True)
figure = app.figure()
panel = figure.panel()
panel.demo_2D()

# Save a PNG screenshot.
image_path = pathlib.Path(__file__).parent / "_offscreen_python.png"
app.screenshot(figure, str(image_path))

app.destroy()
