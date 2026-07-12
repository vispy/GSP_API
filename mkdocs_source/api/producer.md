# Producer API

The independent `gsp_vispy2` package produces GSP records. It is not an official upstream VisPy 2.0
release. `subplots()` returns one semantic `Figure` and `Axes`; methods append visuals, resources,
guides, views, and attachments in deterministic creation order.

::: gsp_vispy2
    options:
      members:
        - subplots
        - affine2d
        - scatter
        - markers
        - segments
        - path
        - plot
        - text
        - mesh
        - imshow
        - color_scale
        - colorbar
        - open_session

## Experimental Datoviz session preview

Datoviz execution is available through an explicitly owned, bounded experimental session. Inspect
the plan before execution, keep non-blocking displays inside the session context, and use a positive
frame count for blocking runs:

```python
with vp.open_session("datoviz") as session:
    plan = session.inspect(figure, operation="display")
    plan.require_executable()
    display = session.show(figure, block=True, frame_count=2)
```

For explicit polling, create the display with `block=False` and call `session.poll(display)`; every
call advances exactly one frame. Closing the session closes every owned display, is idempotent, and
makes later inspect, show, and poll operations raise `SessionLifecycleError`.

This preview does not provide implicit temporary sessions, retained data updates, user-close
callbacks, generic `Display.update()`, or event-loop embedding guarantees. Bare `Figure.show()`
continues to use Matplotlib.

::: gsp_vispy2.session
    options:
      members:
        - open_session
        - Session
        - Display
        - SessionInspection
        - SessionDiagnostic
        - SessionLifecycleError
        - SessionExecutionError
      show_source: false

## Figure and axes

::: gsp_vispy2.protocol.Figure
    options:
      members: true
      show_source: false

::: gsp_vispy2.protocol.Axes
    options:
      members: true
      show_source: false
