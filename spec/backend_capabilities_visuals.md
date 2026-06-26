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
