"""Minimal example showing mouse events handling."""

import datoviz as dvz

print(f"Datoviz version: {dvz.get_version()}")

app = dvz.App()
figure = app.figure()


@app.connect(figure)
def on_mouse(event: dvz.MouseEvent):
    """Handle mouse events."""
    event_name = event.mouse_event()
    if event_name in ("press", "release"):
        print(f"{event_name}")


app.run()
app.destroy()
