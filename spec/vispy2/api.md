# VisPy2 API - Draft

VisPy2 is the high-level Python producer API for GSP.

M008 introduces an experimental MVP slice. It is intentionally small and should
not be treated as a full Matplotlib compatibility layer.

Current first API:

```python
import vispy2 as vp

fig, ax = vp.subplots()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.imshow(image)
ax.scatter(x, y, color=rgba, size=36)
fig.render_matplotlib()
fig.savefig("out.png")
```

VisPy2 should target GSP, not Datoviz directly.

## M008 contract

- `vp.subplots()` returns a minimal `Figure, Axes` pair.
- `Axes.scatter()` emits a GSP `PointVisual`.
- `Axes.imshow()` emits a GSP `ImageVisual`.
- `Axes.set_xlim()` and `Axes.set_ylim()` update semantic `View2D`, not backend-local state.
- `Figure.visuals()` returns the GSP protocol visuals in creation order.
- `Figure.panels()`, `Figure.views()`, and `Figure.attachments()` expose semantic scene structure
  without expanding axes into user data visuals.
- `Figure.render_matplotlib()` renders through `gsp_matplotlib.protocol_renderer`.
- `Figure.savefig()` is a convenience wrapper over the same Matplotlib reference path.

Out of scope:

- Datoviz-specific behavior;
- broad Matplotlib API compatibility;
- legends, ticks, styling systems, or layout engines;
- generated axes in `Figure.visuals()`.

## Axis direction

Axes are semantic panel/view/guide intent, not ordinary user data visuals. Backends should realize
that intent through capability-declared axis providers, such as Matplotlib native axes or Datoviz
v0.4-dev panel axes. Generated primitive axes are backend artifacts and must not be appended to
`Figure.visuals()`.

## Tick resolution

`auto-linear-nice-v0` is resolved by GSP reference code, not by Matplotlib locators or Datoviz native
auto ticks. Explicit tick values and labels pass through exactly. Backends may use native auto ticks
only as adapted output unless they render the GSP-resolved values and labels exactly.
