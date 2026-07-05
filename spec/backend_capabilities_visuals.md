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
| Datoviz v0.4 protocol renderer | supported retained update target | supported when live input bindings are available | supported by fake-facade smoke | The protocol renderer updates panel domains/View2D state and records zero visual upload calls during scripted navigation. |

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
does not imply mesh triangle picking. S044 mesh triangle picking is separately gated by
`query.view3d.mesh_triangle_pick.v1`.

S050 accepts strict face culling only under the projected-NDC capability names
`meshvisual.face_culling.data3d.projected_ndc.v1` and
`meshvisual.face_culling.ndc3.panel_winding.v1`. These capabilities require the exact panel-NDC
winding rule, reversed-bound behavior, framebuffer-y independence, and culling before depth/order
and query selection. Culling-aware picking is separately gated by
`query.view3d.mesh_triangle_pick.face_culling.v1`.

Current S036 support summary:

| Backend | Static View3D projection | `(N,3)` MeshVisual render | Opaque depth | Ray readback | 3D picking |
|---|---:|---:|---:|---:|---:|
| Matplotlib | reference | adapted reference | adapted face order only | reference | S044 CPU oracle candidate |
| Datoviz v0.4 protocol renderer | supported with P022 bindings | adapted GSP panel-NDC lowering | adapted face order only | ray context only | S044 implementation candidate |
| VisPy2 producer API | deferred | deferred | deferred | deferred | deferred |

Structured diagnostics include `view3d_not_supported`, `mesh3d_requires_view3d`,
`mesh3d_coordinate_space_unsupported`, `mesh3d_alpha_not_strict`,
`mesh3d_face_culling_unsupported`, `mesh3d_face_culling_adapted`,
`mesh3d_culling_winding_ambiguous`, `mesh3d_culling_transform_conflict`,
`query_3d_mesh_culling_unsupported`, `query_3d_visual_hit_deferred`, and
`query_3d_snapshot_mismatch`.

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
`meshvisual.positions3d.data.view3d.v1`, and `meshvisual.positions3d.ndc.v1` for local builds with
the P022 camera ctypes layouts and explicit orthographic-bounds API. Builds that also expose the
revisioned panel `View3D` descriptor/state APIs may claim
`view3d.retained_data_space_visuals.v1`: DATA `(N,3)` mesh vertices stay in DATA space, attach to
the retained panel View3D, and ordinary camera/projection updates do not rewrite unchanged vertex or
index buffers. S050 face-order invariance evidence also permits those retained DATA-space View3D
builds to claim `meshvisual.positions3d.opaque_depth.v1` for fully opaque meshes with native
depth-test/write enabled. Builds without that retained descriptor/state path use the adapted CPU
projection path for DATA meshes and must not claim strict opaque depth. Older builds must continue
reporting structured unsupported diagnostics rather than silently flattening z or exposing
backend-native camera objects.

Datoviz may claim `query.view3d.ray_readback.v1` for canonical ray-context payload generation when
the same P022 camera binding is available. This capability does not imply GPU visual hit picking for
3D meshes.

Datoviz may claim `query.view3d.mesh_triangle_pick.v1` only after it can return public GSP
`visual_id` and canonical mesh triangle `primitive_index` for the accepted S044 scope, with
freshness checks for layout, View3D revision, projection snapshot, and pick-scene snapshot. Native
Datoviz ids, shader names, framebuffer attachments, and draw-state names are not public evidence.

Datoviz claims `view3d.navigation.orbit_pan_zoom.v1` only when the retained DATA-space visual path
and live input bindings are both available. The protocol renderer replays canonical
`View3DNavigationAction` values into retained Datoviz camera/projection state, validates Datoviz
state readback against canonical GSP state, preserves visual identity, and does not rewrite
unchanged mesh vertex/index buffers during ordinary View3D navigation.

## S038 MeshVisual material boundary, S039 Lambert extension, and S050 Texture2D extension

S038 accepts only implicit unlit RGBA material semantics for existing `MeshVisual` colors:

```text
meshvisual.material.unlit_rgba.v1
```

A backend may claim this capability only when accepted `MeshVisual` RGBA color sources are rendered
without lighting, normals, texture sampling, view-dependent color changes, or backend material
tinting. Opaque alpha only is strict; non-opaque 3D mesh alpha remains non-strict via
`mesh3d_alpha_not_strict`.

S039 additionally accepts flat Lambert face-normal shading for DATA-space 3D meshes:

```text
meshvisual.material.flat_lambert.v1
meshvisual.normals.face3d.v1
meshvisual.normal_generation.face_flat.v1
view3d.light.ambient.v1
view3d.light.directional.v1
```

Strict S039 support requires `(N,3)` DATA positions, a resolved `View3D`, explicit or generated face
normals, scalar ambient and at most one DATA-space directional light, and the exact formula in
`spec/visuals/mesh_flat_lambert_s039.md`.

For Datoviz, S040 accepts only a CPU-resolved strict route for S039 flat Lambert promotion. The
adapter may advertise S039 Lambert, face-normal, generated-normal, ambient-light, and
directional-light capabilities only after it resolves exact per-face colors before upload, preserves
constant color per canonical face, keeps native Datoviz lighting/material controls unused, and
passes fixture-backed View3D/depth/unlit prerequisites. Native Datoviz lighting API availability is
not strict GSP S039 evidence.

S050 accepts the first texture material slice:

```text
texture2d.rgba8.v1
meshvisual.uv.vertex2d.v1
meshvisual.material.texture2d_unlit.v1
vispy2.producer.mesh.texture2d_unlit.v1
```

Strict textured mesh support requires immutable RGBA8 `Texture2D` resources, per-vertex UVs, fixed
nearest/clamp/no-mipmap sampling, multiplicative unlit RGBA output, and the diagnostics in
`spec/visuals/mesh_texture2d_unlit_s050.md`. A renderer must not advertise
`meshvisual.material.texture2d_unlit.v1` until automated fixtures prove those semantics. Matplotlib
currently remains unsupported for textured meshes; Datoviz support requires public API evidence for
canonical texture upload, UV binding, sampling, image origin, and color behavior.

Current S050 support summary:

| Surface | `texture2d.rgba8.v1` | `meshvisual.uv.vertex2d.v1` | `meshvisual.material.texture2d_unlit.v1` | `vispy2.producer.mesh.texture2d_unlit.v1` | Notes |
|---|---:|---:|---:|---:|---|
| Protocol validation | supported | supported | validation only | n/a | Validates immutable RGBA8 textures and per-vertex UV fields; does not render. |
| Matplotlib renderer | unsupported | unsupported | unsupported | n/a | Direct renderer and visual QA reject with `meshvisual_material_texture2d_unlit_unsupported`. |
| Datoviz renderer | blocked | blocked | blocked | n/a | M220 found public upload/binding candidates but sampler, origin, unmanaged RGBA, and exact unlit multiplication remain unproven. |
| VisPy2 producer | n/a | n/a | n/a | supported | Emits canonical `Texture2D` resources and `texture2d_unlit` `MeshVisual` records only; renderer support remains separate. |

The following lighting and material capability names remain reserved/deferred after S050:

```text
meshvisual.normals.vertex3d.v1
meshvisual.material.smooth_lambert.v1
meshvisual.material.flat_phong.v1
```

Textured lighting, public samplers, broader color-space rules, strict transparency, culling
expansion, model loading, and expanded query payloads remain deferred. Legacy Matplotlib Phong or
per-triangle affine texture output is experimental/adapted until a public cross-backend contract
exists.

S050 also accepts the first face-culling boundary without accepting strict transparency. Strict
opaque-depth and strict mesh-triangle-pick paths remain limited to effective alpha `1.0` everywhere;
texture alpha below `255` keeps textured 3D meshes out of strict opaque paths.
