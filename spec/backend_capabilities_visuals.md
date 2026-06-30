# Backend Visual Capabilities - Accepted S023 Baseline

Status: accepted for S023; S024 text, S025 mesh, and S026 scalar color capability gates accepted.

S023 validates two backend paths:

| Backend | Role | S023 guarantee |
|---|---|---|
| Matplotlib | reference/publication backend | renders all S023 visual families and QA cases |
| Datoviz v0.4 | high-performance retained-scene adapter | renders all S023 QA cases when the v0.4 facade exposes required symbols |

## Capability-gated behavior

Datoviz v0.4 support is facade-symbol gated. Missing symbols must produce structured unsupported
reports rather than fallback approximations. Required visual families use:

- points: `dvz_point`, `position`, `color`, `diameter_px`;
- markers: `dvz_marker`, `position`, `color`, `diameter_px`, `angle`, `shape`, marker style helpers;
- segments: `dvz_segment`, `position_start`, `position_end`, `color`, `stroke_width_px`, caps;
- paths: `dvz_path`, `position`, `color`, `stroke_width_px`, subpaths, caps, joins;
- images: `dvz_image`, `position`, `texcoords`, sampled-field binding or texture fallback,
  image sampling controls.
- text: verified v0.4 retained text/glyph path only; no legacy/private text APIs. Current v0.4
  evidence includes `dvz_text`, `dvz_text_set_string`, `dvz_text_style`,
  `dvz_text_set_style`, `dvz_text_placement`, and `dvz_text_set_placement`; unsupported GSP rows
  mean the adapter has not yet verified the full TextVisual contract.
- mesh: `dvz_mesh`, `position`, `color`, direct index upload, and
  `dvz_visual_set_depth_test` for bounded 2D NDC triangle meshes. Per-face RGBA is adapted by
  duplicating vertices because the Datoviz path is per-vertex color. Use `dvz_visual_set_depth_test`,
  not the stale `dvz_visual_set_depth` name.

Remaining non-S023 limitations are follow-up scope, not hidden S023 failures:

- backend-native colormap registries beyond grayscale;
- public glyph resources and mesh features beyond the bounded S025 2D NDC `MeshVisual` slice;
- tiled/remote/virtual image sources in Datoviz;
- scientific readback and full query payload parity;
- all-rendered/guide query scopes.

## S024 TextVisual capability gates

A backend may claim core `TextVisual` support only when it can render printable ASCII text with
positions, RGBA alpha, logical pixel font sizes, horizontal anchors, basic vertical anchors, generic
font roles, and NDC positioning. Full support additionally includes DATA positioning, baseline
anchoring, rotation, multiline, and per-item color/size/rotation either natively or through internal
batching.

Recommended capability names include `visual.text`, `text.positions.ndc`, `text.positions.data`,
`text.font_size_px`, `text.rgba`, `text.alpha`, `text.anchor_x`, `text.anchor_y_basic`,
`text.anchor_y_baseline`, `text.rotation`, `text.font_roles`, `text.unicode_ascii`,
`text.multiline`, `text.per_item_color`, `text.per_item_size`, and `text.per_item_rotation`.

Structured diagnostics include `TEXT_UNSUPPORTED`, `TEXT_API_UNVERIFIED`,
`TEXT_ANCHOR_UNSUPPORTED`, `TEXT_BASELINE_UNSUPPORTED`, `TEXT_ROTATION_UNSUPPORTED`,
`TEXT_PER_ITEM_STYLE_UNSUPPORTED`, `TEXT_SIZE_DPI_UNVERIFIED`, `TEXT_MULTILINE_UNSUPPORTED`,
`TEXT_GLYPH_MISSING`, `TEXT_ATLAS_CREATION_FAILED`, `TEXT_FONT_ROLE_UNRESOLVED`,
`TEXT_FONT_SUBSTITUTED`, `TEXT_SHAPING_UNSUPPORTED`, and `TEXT_BIDI_UNSUPPORTED`.

## S025 MeshVisual capability gates

A backend may claim strict `MeshVisual` support only when it can render 2D indexed triangle meshes
with finite NDC/DATA positions, uniform RGBA, per-face RGBA, flat colors, deterministic visual order,
and validation diagnostics. Optional capabilities include `mesh.color.vertex`, `mesh.normals.face`,
`mesh.normals.vertex`, `mesh.normal_generation.face_flat`, `mesh.shading.lambert`,
`mesh.depth_test`, `mesh.depth_write`, `mesh.face_culling`, `mesh.alpha`, `mesh.query.face_2d`,
`mesh.render_3d`, and `mesh.query.face_3d`.

Structured diagnostics include `MESH_UNSUPPORTED`, `MESH_API_UNVERIFIED`,
`MESH_INDEXED_GEOMETRY_UNSUPPORTED`, `MESH_POSITION_DIM_UNSUPPORTED`,
`MESH_COLOR_MODE_UNSUPPORTED`, `MESH_VERTEX_COLOR_SIMPLIFIED`, `MESH_NORMALS_UNSUPPORTED`,
`MESH_SHADING_UNSUPPORTED`, `MESH_DEPTH_UNSUPPORTED`, `MESH_CULLING_UNSUPPORTED`,
`MESH_ALPHA_LIMITED`, `MESH_QUERY_UNSUPPORTED`, `MESH_3D_VIEW_UNSUPPORTED`,
`MESH_TEXTURE_DEFERRED`, and `MESH_INSTANCING_DEFERRED`.

## S026 scalar color capability gates

A backend may claim strict scalar color support only when it can reproduce GSP canonical LUT mapping,
explicit linear normalization, endpoint clipping, and required scalar query fields for the supported
visual slots. Optional capabilities include Datoviz GPU normalization, canonical LUT upload,
non-Matplotlib colorbar rendering, colorbar ramp query, and strict 2D mesh per-face scalar color.

Recommended capability names include `gsp.scalar-color@0.1`, `gsp.colormap.named.<id>@0.1`,
`gsp.colormap.lut-upload@0.1`, `gsp.normalize.linear.gpu@0.1`,
`gsp.scalar-image.color-scale@0.1`, `gsp.point.scalar-color@0.1`,
`gsp.marker.scalar-fill@0.1`, `gsp.mesh.face-scalar-color@0.1`,
`gsp.colorbar-guide.render@0.1`, `gsp.scalar-query.source-value@0.1`,
`gsp.scalar-query.normalized-value@0.1`, `gsp.scalar-query.displayed-rgba@0.1`, and
`gsp.colorbar-query@0.1`.

Structured diagnostics include `unsupported_colormap_id`, `colormap_approximated`,
`lut_upload_unsupported`, `gpu_linear_normalize_unsupported`, `cpu_premap_scalar_to_rgba`,
`cpu_premap_not_allowed_for_virtual_data`, `mesh_face_scalar_unsupported`,
`colorbar_render_unsupported`, `scalar_query_source_unavailable`,
`scalar_query_normalized_unavailable`, `colorbar_query_unsupported`, `nonfinite_scalar_rejected`,
and `invalid_color_scale_domain`.

## S035 View2D navigation capability gates

A backend may claim `interaction.view2d.navigation.v1` only when it accepts S035 semantic navigation
actions and returns explicit `View2D` updates with revision/snapshot metadata. Raw native input
events are backend or producer adapters; they are not public protocol semantics.

Recommended placement values:

| Placement | Meaning |
|---|---|
| `retained-gpu-state` | Accepted `View2D` updates lower to retained panel/view/projection or equivalent uniform/state updates. |
| `cpu-remap` | Backend remaps finite eager arrays on the CPU; this is adapted and not the strict high-performance path. |
| `client-side` | Client applies the semantic action and sends only accepted `View2D` state updates. |
| `server-side` | Server owns action application and returns accepted `View2D` results. |
| `unsupported` | Backend cannot apply the navigation capability. |

Strict retained navigation requires unchanged visual buffers and visual objects to remain stable
during pan/zoom. A backend must not re-upload point/image/mesh/path/segment/marker/text geometry
buffers or recreate visuals in the strict fast path.

Current S035 support summary:

| Backend | Programmatic S035 actions | Native drag/wheel review | Retained fast-path proof | Notes |
|---|---:|---:|---:|---|
| Matplotlib | supported reference | supported in example review | not applicable | Reference implementation updates axes limits and redraws. |
| Datoviz v0.4 protocol renderer | supported retained update target | deferred | supported by fake-facade smoke | The protocol renderer updates panel domains/View2D state and records zero visual upload calls during scripted navigation. |

Review/smoke commands:

```bash
uv run python examples/protocol_view2d_navigation.py --backend matplotlib
uv run python examples/protocol_view2d_navigation.py --backend matplotlib --scripted-smoke
uv run python tools/s035_navigation_smoke.py --backend both --steps 40 --points 25000
```

## S036 View3D and 3D Mesh capability gates

A backend may claim `view3d.static.orthographic.v1` only when it accepts public `View3D` state with
`Camera3D(eye, target, up)` and `OrthographicProjection3D` without exposing backend-native camera or
controller objects. `(N, 3)` `MeshVisual` DATA and NDC rendering are separately gated by
`meshvisual.positions3d.data.view3d.v1` and `meshvisual.positions3d.ndc.v1`.

Strict `meshvisual.positions3d.opaque_depth.v1` requires accepted nearer-fragment-wins semantics for
opaque meshes. Adapted face ordering, painter sorting, or unverified clipping must not be advertised
as strict opaque-depth support. Query ray readback is gated by `query.view3d.ray_readback.v1` and
does not imply 3D mesh picking.

Current S036 support summary:

| Backend | Static View3D projection | `(N,3)` MeshVisual render | Opaque depth | Ray readback | 3D picking |
|---|---:|---:|---:|---:|---:|
| Matplotlib | reference | adapted reference | adapted face order only | reference | deferred |
| Datoviz v0.4 protocol renderer | supported with P022 bindings | supported with P022 bindings | supported with P022 bindings | ray context only | deferred |
| VisPy2 producer API | deferred | deferred | deferred | deferred | deferred |

Structured diagnostics include `view3d_not_supported`, `mesh3d_requires_view3d`,
`mesh3d_coordinate_space_unsupported`, `mesh3d_alpha_not_strict`,
`query_3d_visual_hit_deferred`, and `query_3d_snapshot_mismatch`.

## S037 View3D navigation and Datoviz binding capability gates

A backend may claim `view3d.navigation.orbit_pan_zoom.v1` only when it accepts backend-neutral
`View3DNavigationAction` values for orbit, pan, zoom, reset, set-camera, and set-projection;
validates base revisions and projection snapshot ids; and returns a new canonical `View3D` state
with a fresh revision and projection snapshot id. Native backend controller objects are not public
API.

Matplotlib supports S036 static projection and ray readback strictly, but `(N, 3)` mesh rendering is
adapted: DATA meshes are projected by canonical CPU `View3D` math and rendered as 2D
`PolyCollection` faces; NDC3 meshes are interpreted as panel NDC3 and then rendered through the same
2D path. Matplotlib opaque-depth behavior is adapted for opaque, non-intersecting triangles by
sorting faces far-to-near by average panel-NDC z. This is not strict GPU fragment-depth semantics.

Datoviz v0.4 may claim `view3d.static.orthographic.v1`,
`meshvisual.positions3d.data.view3d.v1`, `meshvisual.positions3d.ndc.v1`, and
`meshvisual.positions3d.opaque_depth.v1` only for local builds with the P022 camera ctypes layouts
and explicit orthographic-bounds API. Older builds must continue reporting structured unsupported
diagnostics rather than silently flattening z or exposing backend-native camera objects.

Datoviz may claim `query.view3d.ray_readback.v1` for canonical ray-context payload generation when
the same P022 camera binding is available. This capability does not imply GPU visual hit picking for
3D meshes.

## S038 MeshVisual material boundary

S038 accepts only implicit unlit RGBA material semantics for existing `MeshVisual` colors:

```text
meshvisual.material.unlit_rgba.v1
```

A backend may claim this capability only when accepted `MeshVisual` RGBA color sources are rendered
without lighting, normals, texture sampling, view-dependent color changes, or backend material
tinting. Opaque alpha only is strict; non-opaque 3D mesh alpha remains non-strict via
`mesh3d_alpha_not_strict`.

The following lighting and texture capability names remain reserved/deferred, not claimed in S038:

```text
meshvisual.material.flat_lambert.v1
meshvisual.material.flat_phong.v1
view3d.light.ambient.v1
view3d.light.directional.v1
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
```

Lighting or textured mesh support is strict only after public normal, light-space, texture, UV,
sampler, color-space, alpha, and color-combination rules are accepted and evidence backed. Legacy
Matplotlib Phong or per-triangle affine texture output is experimental/adapted until a public
cross-backend contract exists.
