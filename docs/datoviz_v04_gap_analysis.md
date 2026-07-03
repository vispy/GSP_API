# Datoviz v0.4 Gap Analysis For GSP

Status: M004 assessment, with post-M011 local Datoviz inventory update and M018 binding evidence
refresh.

This document assesses how the current GSP point/image/query/capability concepts map to Datoviz v0.4 as found in the sibling checkout `../datoviz/` on its current branch. It is intentionally not an implementation patch. The legacy `src/gsp_datoviz/` adapter remains unchanged.

## Executive Summary

Datoviz v0.4 can support a GSP backend, but not through the old v0.3-style Python API used by the legacy adapter. The current usable surface is the C-shaped `scene`/`app` API exposed through the top-level Python facade (`import datoviz as dvz`) and raw ctypes bindings.

The old adapter imports `datoviz.App`, `datoviz.visuals`, `datoviz._panel`, `datoviz._figure`, and `datoviz._texture`. In the local Datoviz checkout/package these surfaces are missing. The adapter therefore needs a rewrite around `dvz_scene`, `dvz_figure`, `dvz_panel`, `dvz_point`, `dvz_image`, `dvz_visual_set_data`, sampled fields, query APIs, and capture APIs.

Point rendering maps cleanly. Image rendering maps through sampled fields plus
`dvz_visual_set_field` for scalar/mapped images and `dvz_visual_set_texture_rgba8` for already
packed RGBA8 images. Query concepts are aligned with GSP's panel-query model. During M004/M009, Python-side
query result decoding was blocked because `DvzQueryResult` had no `_fields_`. M018 confirms that
the current `../datoviz` v0.4-dev headers now define a rich `DvzQueryResult` struct, but the current
GSP virtual environment still imports Datoviz `0.3.5` and exposes none of the v0.4 `dvz_*` facade
or ctypes classes. Capability snapshots are available in the headers and should drive GSP
adaptation once a v0.4-dev Python binding is active.

## Inputs Inspected

GSP files:

- `LEGACY_MAP.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/renderer/datoviz_renderer.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_points.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_image.py`
- `src/gsp/protocol/`
- `src/gsp/protocol/visuals.py`

Authoritative Datoviz v0.4 inputs from `../datoviz/`:

- `/Users/cyrille/GIT/Viz/datoviz/docs/start/quickstart.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/start/choose-your-layer.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/reference/feature-status.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/reference/queries.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/reference/visual-attributes.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/how-to/capture-an-image.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/how-to/pick-and-probe.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/how-to/probe-fields.md`
- local introspection of `/Users/cyrille/GIT/Viz/datoviz/datoviz/`

## Environment Inventory

Local introspection found:

- `datoviz.__file__`: `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`
- `datoviz.App`: missing
- `datoviz.visuals`: missing
- `datoviz._panel`: missing
- `datoviz._figure`: missing
- `datoviz._texture`: missing
- `dvz_scene`, `dvz_figure`, `dvz_panel`, `dvz_panel_full`, `dvz_point`, `dvz_image`, `dvz_visual_set_data`, `dvz_visual_set_field`, `dvz_visual_set_texture_rgba8`, `dvz_capability_snapshot`, `dvz_panel_query_px`, `dvz_panel_query_now_px`, and `dvz_scene_poll_query`: present

## Post-M011 local Datoviz inventory update

Checked against the local sibling checkout `../datoviz` on `v0.4-dev` after M011:

- `datoviz.__file__`: `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`
- `dvz_scene`, `dvz_figure`, `dvz_panel_full`, `dvz_panel_add_visual`: present
- `dvz_point`, `dvz_image`, `dvz_visual_set_data`, `dvz_visual_set_texture_rgba8`: present
- `dvz_sampled_field`, `dvz_sampled_field_set_data`, `dvz_visual_set_field`: present
- `dvz_capability_snapshot`: present
- `dvz_panel_query_px`, `dvz_panel_query_now_px`, `dvz_scene_poll_query`: present
- `DvzQueryResult`: present in the current header with a decodable field layout

Notable `DvzQueryResult` fields in the current header include:

- request/frame identity: `request_id`, `freshness_serial`
- status and hit: `status`, `hit`
- object identity: `scene_id`, `figure_id`, `panel_id`, `visual_id`, `visual_family`
- positions: `panel_position`, `framebuffer_position`, `visual_position`, `data_position`, `uvw`
- resolved targets: `raw_target`, `raw_id`, `resolved_target`, `resolved_id`
- item payload ids: `item_id`, `group_id`, `face_id`, `vertex_id`, `voxel_id`, `texel_id`
- color/value payloads: `display_rgba`, `value_kind`, `scalar`, `vector`, `category_id`, `label`, `unit`, `scale`

M018 environment check:

- `PYTHONPATH=. uv run python` in this repo imports `datoviz 0.3.5` from the local virtual
  environment.
- That installed package exposes no public `dvz_*` symbols, no `DvzQueryResult`, and no
  `DvzCapabilitySnapshot`.
- The header evidence removes a C ABI uncertainty, but the GSP runtime binding blocker remains until
  the v0.4-dev Python facade/raw binding is installed or put on `PYTHONPATH`.

This does not by itself prove runtime query correctness, panel/query request setup, visual query
capability enabling, or mapping of Datoviz enum values to GSP `QueryStatus`/`VisualFamily`.

Important constraint:

- Do not use online Datoviz API pages as authority for this GSP v0.4 work unless they are verified against `../datoviz/` current branch. The inspected local v0.4 docs say the normal Python facade preserves C-shaped `dvz_*` names and does not provide the old high-level plotting wrapper. For GSP implementation, use the local v0.4 C-shaped API as the implementation target.

## Legacy Adapter Breakage

| Legacy code | v0.4 finding | Impact |
|---|---|---|
| `import datoviz as dvz; dvz.App(...)` | `datoviz.App` is absent in the local v0.4 package. | `DatovizRenderer` cannot import or instantiate. |
| `from datoviz._panel import Panel` | `datoviz._panel` is absent. | Private-type imports must be removed. Use opaque ctypes pointer types or local wrapper classes. |
| `from datoviz._figure import Figure` | `datoviz._figure` is absent. | Same as above. |
| `from datoviz._texture import Texture` | `datoviz._texture` is absent. | Texture handling must use sampled fields or v0.4 texture helpers. |
| `from datoviz.visuals import Point/Image/Visual` | `datoviz.visuals` is absent. | Per-visual wrapper methods like `set_position()` and `set_color()` are not available. |
| `renderer._dvz_app.point(...)` | v0.4 point creation is `dvz.dvz_point(scene, flags)`. | Rewrite creation path. |
| `dvz_panel.add(visual)` | v0.4 attach path is `dvz_panel_add_visual(panel, visual, attach_desc_or_null)`. | Rewrite panel attachment. |
| `dvz_texture = app.texture_2D(...)` | v0.4 image path prefers `DvzSampledField` + `dvz_visual_set_field()`. | Rewrite image resource model. |
| `app.screenshot(...)` | v0.4 capture path is view/offscreen/capture functions or `dvz.capture(scene, figure, path=...)`. | Rewrite screenshot path. |

## Target Runtime Mapping

| GSP concept | Datoviz v0.4 target | Status |
|---|---|---|
| GSP session/server | `DvzScene*` plus `DvzApp*`/view lifecycle | feasible |
| Canvas/figure | `dvz_figure(scene, width, height, flags)` | feasible |
| Panel/viewport | `dvz_panel(figure, DvzPanelDesc)` or `dvz_panel_full(figure)` | feasible; GSP pixel viewport must map to normalized panel desc |
| Point visual | `dvz_point(scene, flags)` + `dvz_visual_set_data()` | feasible |
| Image visual | `dvz_image(scene, flags)` + position/texcoords + sampled field | feasible with coordinate decisions |
| Visual attachment | `dvz_panel_add_visual(panel, visual, NULL or DvzVisualAttachDesc*)` | feasible |
| Buffer attributes | dense NumPy arrays via `dvz_visual_set_data()` | feasible for first slice |
| Resource ownership | scene-owned buffers/fields; data writes copy caller memory unless documented otherwise | feasible but not zero-copy yet |
| Capability snapshot | `dvz_capability_snapshot()` / `DvzCapabilitySnapshot` | feasible |
| Queries | `dvz_visual_set_query_capabilities()`, `dvz_panel_query_px()`, `dvz_scene_poll_query()` | feasible for next proof; Python result fields are now visible in local `../datoviz` |
| Capture | `dvz_view_offscreen` + render/capture, or Python `dvz.capture()` | feasible for raster PNG; not linear scientific readback |

## Point Visual Mapping

GSP `PointVisual` first slice:

- `positions`: float32/float64 `(N, 2)` or `(N, 3)`
- `colors`: rgba8 `(N, 4)` or float `(N, 4)`
- `sizes`: scalar or `(N,)`, currently Matplotlib-style marker area in M003
- `coordinate_space`: `ndc` or `data`

Datoviz v0.4 point path:

```python
visual = dvz.dvz_point(scene, 0)
dvz.dvz_visual_set_data(visual, "position", positions_3d)
dvz.dvz_visual_set_data(visual, "color", rgba8)
dvz.dvz_visual_set_data(visual, "diameter", diameters_px)
dvz.dvz_panel_add_visual(panel, visual, None)
```

Gaps and adaptation:

- Datoviz uses `"diameter"` in pixels. GSP must normalize `PointVisual.sizes` semantics before implementing Datoviz. M003 used Matplotlib marker area. A shared point-size semantic is needed before visual parity can be claimed.
- Datoviz point colors accept RGBA8 or scalar float with a color scale. GSP first slice can use RGBA8 directly.
- Historical note: early v0.4 quickstarts used normalized positions. Current Datoviz retained
  panel visuals can use DATA positions with `dvz_panel_set_domain()` and the default DATA
  attachment. CPU pre-normalization is now a legacy adapter fallback, not the preferred path.
- Query capability for point picking maps to `DVZ_QUERY_CAPABILITY_ITEM` and target `DVZ_SCENE_TARGET_ITEM`.

## Image Visual Mapping

GSP `ImageVisual` first slice:

- `image`: `(H, W)`, `(H, W, 3)`, or `(H, W, 4)`
- `extent`: `(left, right, bottom, top)`
- `coordinate_space`: `ndc` or `data`
- `interpolation`: `nearest` or `linear`
- `origin`: `upper` or `lower`

Datoviz v0.4 image path:

- create visual with `dvz_image(scene, flags)`;
- upload geometry via `"position"` and `"texcoords"` attributes;
- prefer `dvz_sampled_field()` + `dvz_sampled_field_set_data()` + `dvz_visual_set_field(image, "field", field)` for scalar/mapped images;
- packed RGBA8 path: `dvz_visual_set_texture_rgba8(image, pixels, width, height, size_bytes)`;
- attach to panel with `dvz_panel_add_visual()`.

Gaps and adaptation:

- GSP `extent` must be converted to four DATA corner positions and uploaded with the default DATA
  attachment. The current Datoviz panel domain/view policy performs the panel mapping.
- GSP `origin` maps to texture coordinate ordering, not a one-flag Datoviz image property. The adapter must generate `texcoords` from origin.
- GSP float scalar images should use sampled fields with scalar semantic and color scale, not the RGBA8 convenience wrapper.
- `ImageInterpolation` mapping was not confirmed as a first-class sampled-field setting in the Python facade during M004. This needs implementation verification.
- Image probing maps conceptually to `DVZ_QUERY_CAPABILITY_PIXEL` and `DVZ_SCENE_TARGET_PIXEL`, but GSP source-value readout still requires application-owned field sampling after a rendered hit.

## Capability Mapping

Datoviz exposes `DvzCapabilitySnapshot` through `dvz_capability_snapshot()`. Local ctypes fields include:

- resource limits: `max_buffer_size`, `max_texture_dimension_2d`, `max_bind_groups`, `max_vertex_buffers`, `max_color_attachments`;
- shader formats: `shader_format_wgsl`, `shader_format_glsl`;
- render/readback support: `supports_render_target_sampling`, `supports_color_blending`, `supports_readback`, `max_readback_size`;
- texture/render-target formats including `r32uint`, `rg32uint`;
- query profiles: `query_profile_u32_r32`, `query_profile_u64_rg32`, `query_profile_u64_2xr32`.

GSP `CapabilitySnapshot` should translate this into:

- `transports`: `inproc` for local ctypes path;
- `buffer_dtypes`: initial support for `float32`, `uint8/rgba8`, `uint32` where visual families need them;
- `texture_formats`: populated from sampled-field formats and snapshot format flags;
- `visual_families`: at least `point`, `image` once adapter support is implemented;
- `query_modes`: item/pixel/sample only when Datoviz capability flags and visual-family query capabilities are enabled;
- `output_formats`: `png` for screenshot capture only.

Unsupported behavior must be explicit. In particular, screenshot capture is not scientific readback.

## Query Mapping

GSP's unified panel query model aligns well with Datoviz v0.4 docs:

- queue: `dvz_panel_query_px(panel, x, y, &request)`;
- synchronous helper: `dvz_panel_query_now_px(panel, runtime, x, y, &request, &result)`;
- polling: `dvz_scene_poll_query(scene, &result)`;
- enable per-visual support: `dvz_visual_set_query_capabilities(visual, flags)`.

Local ctypes exposes:

- `DvzQueryRequest` fields;
- `DvzQueryCapabilityFlag`;
- `DvzQueryHitPolicy`;
- `DvzQueryProfile`;
- `DvzQueryStatus`;
- `DvzQueryValueKind`;
- `DvzSceneTargetKind`.

M004/M009 blocking gap, now updated:

- Earlier local introspection found `DvzQueryResult` exposed without `_fields_`, blocking Python-side decoding.
- M018 inventory found the needed fields in `../datoviz` v0.4-dev headers.
- The next Datoviz mission should first establish a v0.4-dev Python facade/raw binding import path,
  then implement a bounded decoder from `DvzQueryResult` to GSP `QueryResult`, with skip-clean
  runtime tests if Datoviz query execution is unavailable in CI/local headless environments.

## Capture And Readback

Datoviz v0.4 supports PNG capture through offscreen views and convenience Python `dvz.capture(scene, figure, path=...)`.

GSP mapping:

- Use capture for `output_formats=["png"]`, screenshots, examples, and visual conformance artifacts.
- Do not map capture to GSP scientific readback.
- Query/readback must use query APIs and capability-gated result semantics.

## Proposed Implementation Shape For A Future Mission

Do not port the old adapter in place line-by-line. Instead:

1. Add a new adapter module around C-shaped Datoviz v0.4 APIs.
2. Wrap opaque pointers in small Python classes owned by the adapter, not Datoviz-private classes.
3. Convert GSP protocol visual models to dense NumPy arrays.
4. Keep point and image support narrow first.
5. Gate every feature through a translated `CapabilitySnapshot`.
6. Add import-only and no-GPU construction tests first.
7. Add offscreen capture tests only when the environment can create a Datoviz offscreen view reliably.
8. Add query decode tests once `DvzQueryResult` is decodable from the active Python binding; keep
   runtime query execution tests skip-clean if app/offscreen runtime is unavailable.

## Required Handoffs

The following Datoviz-side or binding-side tasks should be resolved before a full GSP Datoviz backend implementation claims parity:

- Keep the `DvzQueryResult` fields stable in the v0.4 Python binding, or provide a decoded
  query-result helper.
- Clarify the promoted Python facade contract in the `../datoviz/` docs/release artifacts, so GSP agents do not target obsolete wrapper examples or any stale published pages.
- Confirm image interpolation and origin handling for `DvzSampledField`/`dvz_image`.
- Keep GSP latest-only: sampled fields for scalar/mapped images and `dvz_visual_set_texture_rgba8()` only for already-packed RGBA8 images.

## Recommended next Datoviz parity mission

Start with bounded Datoviz query/capability parity:

1. Translate `dvz_capability_snapshot()` into GSP `CapabilitySnapshot` instead of the current static
   Datoviz adapter capability surface.
2. Add a pure decoder from Python `DvzQueryResult` instances to GSP `QueryResult` once the active
   environment imports a v0.4 binding.
3. Map Datoviz query statuses and visual families to GSP enums with explicit diagnostics for
   unsupported/stale/dropped/failed cases.
4. Enable Datoviz query modes only when the adapter can produce the corresponding GSP semantics.
5. Add tests that construct synthetic `DvzQueryResult` objects when possible, plus runtime
   query/capture tests that skip cleanly when the local Datoviz runtime cannot execute them.
6. Leave sampled-field scalar image parity, offscreen capture parity, and tiled-source Datoviz
   support as follow-up missions unless they are needed for query/capability tests.

## ChatGPT Pro Consultation

No ChatGPT Pro consultation is required for M004. The assessment identifies implementation gaps and handoff tasks. A future implementation mission may need consultation if point-size semantics, image coordinate conventions, or GPU-authoritative query payload semantics need final protocol decisions.
