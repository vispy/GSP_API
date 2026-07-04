# Matplotlib Backend Spec - Draft

Matplotlib is the reference/conformance/publication backend.

Responsibilities:

- correctness over speed;
- small-scene conformance;
- PNG/SVG/PDF where possible;
- reference CPU query path;
- explicit diagnostics for unsupported behavior.

The backend should consume formal GSP models, not define protocol semantics.

## M003 reference slice

`gsp_matplotlib.protocol_renderer` renders the first formal protocol visual models:

- `PointVisual` to `matplotlib.collections.PathCollection`;
- `MarkerVisual` to shaped `matplotlib.collections.PathCollection` markers;
- `PathVisual` subpaths to open `matplotlib.patches.PathPatch` artists;
- `ImageVisual` to `matplotlib.image.AxesImage`.

This is a narrow conformance slice beside the legacy renderer. The legacy `MatplotlibRenderer` remains available for existing examples.

For `ImageVisual`, scalar images use the bounded v1 scalar mapping: gray colormap by default, optional explicit `clim`, explicit `origin`, and explicit `extent`. RGB/RGBA images bypass scalar colormap/clim.

For `MarkerVisual`, protocol sizes are canvas/reference-pixel diameters and are converted to
Matplotlib scatter area units through the resolved canvas contract, matching `PointVisual`. Marker
`stroke_width` is also a canvas/reference-pixel width and is converted to Matplotlib point linewidth
with `canvas_px * framebuffer_per_canvas_px * 72 / output_dpi`. The reference path supports the
conservative v1 shapes `disc`, `square`, `triangle`, `diamond`, and `cross`, plus scalar or
per-marker angles in radians.

For `PathVisual`, protocol widths are canvas/reference-pixel stroke widths and are converted to
Matplotlib point linewidths through the same resolved canvas formula. Each subpath is rendered as an
open path patch so Matplotlib can preserve cap and join styles without treating path interiors as
independent segments.

## M011 tiled-source reference proof

`gsp_matplotlib.tiled_image` materializes a `TiledImageSource` viewport mosaic through
`FakeTiledImageProvider` and renders it via the existing image protocol renderer. It also provides a
reference tiled-image query helper that returns normal `QueryResult` fields plus
`TiledImageQueryPayload`.

## M032 clipped tiled-source extent

When a tiled-source viewport source rectangle is partially outside source bounds, the Matplotlib
reference path renders only the clipped mosaic. The rendered `AxesImage` extent is clipped
proportionally to match the clipped source rectangle, and `query_tiled_image_source()` uses the same
clipped extent for hit testing and payload coordinates.

## S027 transform/view reference target

Matplotlib is the strict reference backend for accepted S027 semantics. It must implement finite
invertible 2D affine visual transforms, deterministic linear `View2D`, reversed limits, DATA/NDC
behavior, clipping after view mapping, accepted family-specific transform rules, and
`gsp.transform-query@0.1` inverse payloads for the strict 2D subset.

Matplotlib native transform objects are implementation details. They must not appear in protocol
records, fixtures, query payloads, or VisPy2 public API.

## S028 guide/View2D reference target

Matplotlib is also the strict reference backend for semantic guide consumption of `View2D`.

Reference guide rendering/query must:

- resolve x guide ticks from `View2D.xlim` and y guide ticks from `View2D.ylim`;
- accept reversed finite limits and render/query tick values through the original axis direction;
- preserve explicit tick values and labels exactly;
- use GSP deterministic auto ticks rather than Matplotlib locators as semantic authority;
- use the same `View2D` snapshot for guide rendering, guide-scoped query, all-rendered query, and
  data readouts.

Matplotlib axis artists remain backend realization details, not public protocol objects.

## S029/S034 resolved layout reference

Matplotlib can produce a `ResolvedLayoutSnapshot` from a drawn reference figure through
`gsp_matplotlib.layout.resolve_matplotlib_layout_snapshot()`. The snapshot exposes the native
Matplotlib artist geometry used for publication output as GSP logical-pixel rectangles:

- render target and DPI metadata;
- full panel rectangle;
- axes plot rectangle;
- title, axis-label, and tick-label boxes;
- grid clip rectangle equal to the resolved plot rectangle;
- affine data-to-logical-screen transform;
- guide z/layer records.

This is an extraction of the reference layout result, not a declaration that Matplotlib's
implementation details are the protocol contract. The backend advertises full resolved-layout
production but does not claim `layout_strict` until render, query, readback, and all-rendered guide
contributions all report and consume the same `layout_snapshot_id`.

## S034 guide style mapping

Matplotlib maps accepted logical-pixel guide style hints to native artist properties using:

```text
points = canvas_px * framebuffer_per_canvas_px * 72 / output_dpi
```

Supported style mappings include title font size and pad, axis label font size and label pad, tick
label font size, tick length, tick width, tick-label padding, and grid line width. These are semantic
GSP style hints; Matplotlib artist objects remain backend realization details.

`ColorbarGuideStyle.ramp_width_px` is lowered to colorbar axes thickness as a fraction of the
resolved canvas width or height. Colorbar guide thickness is GSP-owned style, not a Matplotlib
locator/layout default.

Matplotlib layout snapshots may carry an explicit `RenderTarget.device_scale` supplied by the caller.
The logical figure size and guide rectangles remain in canvas/reference pixels; derived framebuffer
dimensions come from the resolved canvas contract.

## S034 layout-aware guide query

`gsp_matplotlib.layout_query.query_resolved_layout_guides()` can query guide boxes from a
`ResolvedLayoutSnapshot` in logical panel-pixel coordinates. It returns `GuideQueryPayload` hits and
reports the snapshot id used. This covers resolved title, axis-label, tick-label, legend, and
colorbar boxes where present in the snapshot.

This is the reference geometry-query path for layout snapshots. `query_scoped_scene()` can consume a
resolved layout snapshot for guide-scope and all-rendered guide contributions.

`gsp_matplotlib.protocol_renderer.render_protocol_scene_with_layout()` renders protocol visuals and
semantic guides into a Matplotlib figure and returns the resolved layout snapshot plus
`layout_snapshot_id`. Matplotlib still does not claim full `layout_strict`; readback and promotion
criteria remain separate closure work.

## S035 View2D navigation reference

Matplotlib is the strict reference backend for S035 programmatic `View2D` navigation. The helper
`gsp_matplotlib.navigation.apply_view2d_navigation_action()` applies accepted `pan_by`,
`zoom_about`, `set_view`, and `reset_view` actions to a current `View2D`, validates controller
revision/layout freshness, and returns a `NavigationResult` with the next explicit view.

Matplotlib live review support is intentionally an adapter around that semantic path. The example
`examples/protocol_view2d_navigation.py --backend matplotlib` converts native Matplotlib
drag/wheel events into S035 pointer events and semantic actions, then updates axes limits from the
accepted `View2D`. The scripted review command is:

```bash
uv run python examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke
```

Matplotlib does not define public raw-event semantics for GSP. Its native callback ids, canvas
events, and artist invalidation behavior remain backend implementation details.

## S036 View3D projection reference

Matplotlib is the reference backend for S036 static orthographic projection math.
`render_mesh_visual()` accepts `(N, 3)` `MeshVisual` positions for the projection subset:

- DATA positions require a `View3D` and are projected through `Camera3D` plus
  `OrthographicProjection3D` into panel NDC;
- NDC positions are interpreted as panel NDC3, with x/y lowered to axes-fraction coordinates;
- existing `(N, 2)` mesh behavior remains unchanged;
- existing 2D affine visual transforms on `(N, 3)` mesh geometry are rejected with
  `mesh3d_transform_unsupported`;
- DATA `(N, 3)` meshes without a `View3D` are rejected with `mesh3d_requires_view3d`.

For opaque, non-intersecting fixture triangles, Matplotlib sorts projected faces far-to-near by
average panel-NDC z so nearer faces are drawn last. `FaceCulling.NONE` leaves reversed-winding faces
visible. `depth_test=disabled` preserves declared face order, and translucent 3D mesh colors are
rejected with `mesh3d_alpha_not_strict`. Partially clipped 3D triangles remain adapted/unverified
and are not part of the strict M157 fixture.

This path provides projection/rendering coverage and an adapted face-order fixture only. It must not
be advertised as strict `meshvisual.positions3d.opaque_depth.v1` support until S036 depth fixtures
prove accepted fragment-depth semantics.

`gsp_matplotlib.protocol_query.query_view3d_ray_context()` provides the S036 reference
projection-inverse query path. It returns `gsp.view3d-query@0.1` payloads for panel coordinates,
reports `query_3d_snapshot_mismatch` for stale layout/view-projection snapshots, and keeps `(N, 3)`
`MeshVisual` face picking deferred with `query_3d_visual_hit_deferred`.

## S037 View3D navigation review adapter

Matplotlib consumes the backend-neutral S037 `View3DNavigationAction` protocol for live review
examples. Live review examples enable this navigation by default; `--no-interactive-navigation`
opens a static live window. `examples/review/_review_runner.py` adapts native Matplotlib events
privately:

- left-drag -> `orbit`;
- right/middle-drag -> `pan`;
- wheel -> `zoom`;
- `r` -> `reset`.

The adapter applies actions through `apply_view3d_navigation_action()`, receives a canonical
`View3DNavigationResult`, and re-renders the scene with the new canonical `View3D`. Matplotlib
callback ids, canvas events, axes, artists, and drag/wheel constants are implementation details, not
public GSP API.

This does not change Matplotlib's adapted 3D rendering claim: `(N, 3)` meshes are still CPU-projected
to 2D `PolyCollection` faces and sorted by average panel-NDC z for the adapted opaque fixture path.

## S050 textured mesh policy

Matplotlib must not advertise `meshvisual.material.texture2d_unlit.v1` through the current
`PolyCollection` or CPU-projected 3D mesh path. Per-face or per-vertex colors are not texture
mapping, and silently dropping texture fields would violate the S050 material contract.

Until a fixture-backed CPU textured-triangle rasterizer exists, Matplotlib should reject
`MeshVisual.shading="texture2d_unlit"` with
`meshvisual_material_texture2d_unlit_unsupported`. A future CPU rasterizer would still need to prove
the accepted UV orientation, nearest/clamp/no-mipmap sampling, color multiplication, alpha
diagnostics, and any claimed depth behavior separately.

The direct `render_mesh_visual()` path also rejects `texture2d_unlit` before constructing a
`PolyCollection`; texture fields must not be silently dropped into uniform, per-face, or per-vertex
RGBA fallback geometry.
