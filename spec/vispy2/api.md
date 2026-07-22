# VisPy2 API - Draft

VisPy2 is the high-level Python producer API for GSP.

M008 introduces an experimental MVP slice. It is intentionally small and should
not be treated as a full Matplotlib compatibility layer.

Current first API:

```python
import gsp_vispy2 as vp

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

The S025/S039 VisPy2 producer exposes only the accepted untextured `MeshVisual` fields, including
the bounded flat-Lambert face-normal extension. It does not expose material objects, public sampler
objects, texture handles, culling/depth-state controls, mesh-local transforms, Datoviz slots, or
backend draw calls. S050 later accepts one thin Texture2D/UV producer extension below.

## S050/S059 Texture2D mesh producer extension

VisPy2 extends the existing `Axes.mesh` producer with texture data, UVs, and the bounded filter:

```python
def mesh(
    self,
    positions,
    faces,
    *,
    color,
    color_mode=None,
    coordinate_space="data",
    shading="unlit_rgba",
    normal_mode=None,
    normals=None,
    normal_generation="none",
    order=0.0,
    transform=None,
    texture=None,
    uvs=None,
    texture_filter="nearest",
):
    ...
```

`texture is None and uvs is None` preserves current mesh behavior exactly, including the existing
required `color` argument and the untextured S039 flat-Lambert parameters. Supplying both `texture`
and `uvs` emits one GSP `Texture2D` resource, stores it on `Figure.texture_resources()`, sets
`MeshVisual.texture2d_id`, `uv_mode="vertex"`, `uvs=uvs`, and `shading="texture2d_unlit"`.
Supplying exactly one of `texture` or `uvs` is an error.

`texture` must be strict `uint8 (H,W,4)` with no filename, URI, PIL object, RGB expansion, float
scaling, or color-profile handling in v1. `uvs` must be finite `(N,2)`. `color` remains the
multiplicative base color. `texture_filter` accepts `nearest` or `linear`, defaults to nearest, and
linear requires both texture and UVs. When `texture` is supplied, VisPy2 rejects non-default
`shading` and does not expose `sampler`, `wrap`, independent min/mag, `mipmap`, `material`, `light`, `texture_id`,
culling/depth-state, or backend-specific keywords in this stage.

`gsp_vispy2.producer.mesh.texture2d_unlit.v1` is producer-only. `Figure.render_matplotlib()` and other
renderer paths must still check renderer capabilities and diagnose unsupported textured meshes.
`gsp_vispy2.producer.mesh.texture_filter.linear.v1` separately identifies producer support for the
linear field and does not imply renderer support.

## S026 color mapping direction

S026 accepts shared `ColorScale` resources, canonical named colormaps, explicit linear normalization,
slot-specific scalar color encodings, and semantic `ColorbarGuide` objects. VisPy2 may expose
producer conveniences such as scalar `imshow(..., cmap=..., clim=...)`, point/marker scalar color
values, and `colorbar(...)`, but it must emit explicit GSP color scales and must not expose
Matplotlib `ScalarMappable` objects, Datoviz shader controls, backend colormap registries, or auto
normalization as protocol semantics.

`colorbar(...)` may expose GSP style conveniences such as `ramp_width_px`, `tick_length_px`,
`label_gap_px`, `min_length_px`, and `length_fraction`. These lower to `ColorbarGuideStyle`; they
are canvas/reference-pixel semantics, not backend-native colorbar objects.

## S027 transform/view direction

S027 accepts producer conveniences for 2D affine transforms and deterministic view state, such as
`affine2d(...)`, visual `transform=...`, and `set_view2d(...)`/existing x/y limit methods emitting
`View2D`. These APIs must emit GSP protocol records and must not expose Matplotlib transform objects,
Datoviz slots, shader handles, backend camera objects, or public controller event state. Public 3D
camera/projection/navigation APIs remain deferred.

## S034 Matplotlib layout render result

`Figure.render_matplotlib()` preserves the legacy tuple return shape. Callers that need resolved
layout identity can use `Figure.render_matplotlib_with_layout(snapshot_id=...)`, which returns a
render result containing the Matplotlib figure, axes, `ResolvedLayoutSnapshot`, and
`layout_snapshot_id`. This is the VisPy2-facing proof that a render result can report the layout
snapshot used by the Matplotlib reference path.
