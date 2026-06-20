# VisPy2 API - Draft

VisPy2 is the high-level Python producer API for GSP.

M008 introduces an experimental MVP slice. It is intentionally small and should
not be treated as a full Matplotlib compatibility layer.

Current first API:

```python
import vispy2 as vp

fig, ax = vp.subplots()
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
- `Figure.visuals()` returns the GSP protocol visuals in creation order.
- `Figure.render_matplotlib()` renders through `gsp_matplotlib.protocol_renderer`.
- `Figure.savefig()` is a convenience wrapper over the same Matplotlib reference path.

Out of scope:

- Datoviz-specific behavior;
- broad Matplotlib API compatibility;
- legends, ticks, transforms, styling systems, or layout engines;
- new protocol concepts beyond the v0.1 point/image slice.
