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
ax.imshow(image, colormap="gray", clim=(0.0, 1.0))
ax.scatter(x, y, color=rgba, size=36)
ax.markers(x, y, shape="triangle", fill_color=rgba, size=36, angle=0.0)
ax.path(vertices, path_lengths=(len(vertices),), color=rgba, width=4, join="round")
ax.plot(x, y, color=rgba, width=4)
ax.mesh(positions, faces, color=rgba, color_mode="face")
fig.render_matplotlib()
fig.savefig("out.png")
```

VisPy2 should target GSP, not Datoviz directly.

## M008 contract

- `vp.subplots()` returns a minimal `Figure, Axes` pair.
- `Axes.scatter()` emits a GSP `PointVisual`.
- `Axes.markers()` emits a GSP `MarkerVisual`.
- `Axes.path()` and `Axes.plot()` emit a GSP `PathVisual`.
- `Axes.mesh()` emits a GSP `MeshVisual` for inline indexed triangles.
- `Axes.imshow()` emits a GSP `ImageVisual`, including bounded scalar `colormap`/`clim` options.
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
- public mesh material, light, texture, transform, or backend draw-call surfaces;
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

Reversed `View2D` limits from `set_xlim(right, left)`, `set_ylim(top, bottom)`, or `set_view2d(...)`
are valid. They reverse axis direction while preserving semantic tick values. Auto ticks are resolved
over the finite numeric interval spanned by the limits, then rendered/query-mapped through the
original `View2D` orientation.

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
contributions. Guide-specific fields are carried in `GuideQueryPayload`. Guide queries use the same
`View2D` snapshot as guide rendering, including reversed axis direction. The broader query-scope
model for `data`, `guides`, and `all-rendered` remains governed by the accepted S015 capability
rules.

## Mesh producer API

The bounded S025 mesh API exposes accepted `MeshVisual` protocol semantics:

- `Axes.mesh(positions, faces, color=..., color_mode=None, coordinate_space="data", order=0.0)`
  creates inline indexed triangular mesh geometry.
- `positions` accepts `(N,2)` or `(N,3)` float arrays. The strict reference path is 2D.
- `faces` accepts integer `(M,3)` triangle indices.
- `color` accepts uniform `(4,)`, per-face `(M,4)`, or explicit per-vertex `(N,4)` RGBA.
- `color_mode` may be `"uniform"`, `"face"`, or `"vertex"` when inference is ambiguous or when the
  caller wants explicit association.
- `coordinate_space` accepts existing GSP coordinate spaces, defaulting to `DATA`.

The VisPy2 producer does not expose materials, lights, textures, normals, shading, culling, depth
state, mesh-local transforms, Datoviz slots, or backend draw calls. Those remain protocol- or
backend-capability work, not high-level producer API.

## S026 color mapping direction

S026 accepts shared `ColorScale` resources, canonical named colormaps, explicit linear normalization,
slot-specific scalar color encodings, and semantic `ColorbarGuide` objects. VisPy2 may expose
producer conveniences such as scalar `imshow(..., cmap=..., clim=...)`, point/marker scalar color
values, and `colorbar(...)`, but it must emit explicit GSP color scales and must not expose
Matplotlib `ScalarMappable` objects, Datoviz shader controls, backend colormap registries, or auto
normalization as protocol semantics.

## S027 transform/view direction

S027 accepts producer conveniences for 2D affine transforms and deterministic view state, such as
`affine2d(...)`, visual `transform=...`, and `set_view2d(...)`/existing x/y limit methods emitting
`View2D`. These APIs must emit GSP protocol records and must not expose Matplotlib transform objects,
Datoviz slots, shader handles, backend camera objects, or public controller event state. Public 3D
camera/projection/navigation APIs remain deferred.
