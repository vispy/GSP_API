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
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_title("Demo")
ax.set_xticks([0, 0.5, 1], labels=["zero", "half", "one"])
ax.grid(True)
ax.imshow(image)
ax.scatter(x, y, color=rgba, size=36)
ax.markers(x, y, shape="triangle", fill_color=rgba, size=36, angle=0.0)
fig.render_matplotlib()
fig.savefig("out.png")
```

VisPy2 should target GSP, not Datoviz directly.

## M008 contract

- `vp.subplots()` returns a minimal `Figure, Axes` pair.
- `Axes.scatter()` emits a GSP `PointVisual`.
- `Axes.markers()` emits a GSP `MarkerVisual`.
- `Axes.imshow()` emits a GSP `ImageVisual`.
- `Axes.set_xlim()` and `Axes.set_ylim()` update semantic `View2D`, not backend-local state.
- `Axes.set_xlabel()`, `set_ylabel()`, `set_title()`, `set_xticks()`, `set_yticks()`, and
  `grid()` update semantic guide intent.
- `Figure.visuals()` returns the GSP protocol visuals in creation order.
- `Figure.panels()`, `Figure.views()`, and `Figure.attachments()` expose semantic scene structure
  without expanding axes into user data visuals.
- `Figure.render_matplotlib()` renders through `gsp_matplotlib.protocol_renderer`.
- `Figure.savefig()` is a convenience wrapper over the same Matplotlib reference path.

Out of scope:

- Datoviz-specific behavior;
- broad Matplotlib API compatibility;
- legends, styling systems, or layout engines;
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

The Matplotlib reference path realizes semantic `AxisGuide` objects with native Matplotlib axes
artists, but tick values and labels still come from GSP-resolved semantics. `PanelTextGuide` title
intent is rendered as a Matplotlib title.

## VisPy2 guide APIs

The bounded S013 guide API provides Matplotlib-like convenience methods while still emitting GSP
protocol objects:

- `Axes.set_xlabel()` and `Axes.set_ylabel()` update the x/y `AxisGuide.label_text`.
- `Axes.set_title()` creates or clears a title `PanelTextGuide`.
- `Axes.set_xticks()` and `Axes.set_yticks()` create explicit `TickSpec` values and optional labels.
- `Axes.grid(True, axis="both" | "x" | "y")` updates `AxisGuide.grid_visible`.

These methods do not expose backend-provider details and do not append generated guides to
`Figure.visuals()`.

## Guide query

The reference Matplotlib path has bounded guide-query support for semantic axis tick/spine
contributions. Guide-specific fields are carried in `GuideQueryPayload`. The broader query-scope
model for `data`, `guides`, and `all-rendered` remains consultation-gated.
