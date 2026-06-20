# Datoviz v0.4 Gap Analysis For GSP

Status: M004 assessment.

This document assesses how the current GSP point/image/query/capability concepts map to Datoviz v0.4. It is intentionally not an implementation patch. The legacy `src/gsp_datoviz/` adapter remains unchanged.

## Executive Summary

Datoviz v0.4 can support a GSP backend, but not through the old v0.3-style Python API used by the legacy adapter. The current usable surface is the C-shaped `scene`/`app` API exposed through the top-level Python facade (`import datoviz as dvz`) and raw ctypes bindings.

The old adapter imports `datoviz.App`, `datoviz.visuals`, `datoviz._panel`, `datoviz._figure`, and `datoviz._texture`. In the local Datoviz checkout/package these surfaces are missing. The adapter therefore needs a rewrite around `dvz_scene`, `dvz_figure`, `dvz_panel`, `dvz_point`, `dvz_image`, `dvz_visual_set_data`, sampled fields, query APIs, and capture APIs.

Point rendering maps cleanly. Image rendering maps, but the preferred v0.4 path is sampled fields plus `dvz_visual_set_field`; `dvz_visual_set_texture` is documented as a transitional convenience wrapper. Query concepts are aligned with GSP's panel-query model, but the current Python ctypes binding exposes `DvzQueryResult` without fields, which blocks Python-side query result decoding. Capability snapshots are available and should drive GSP adaptation.

## Inputs Inspected

GSP files:

- `LEGACY_MAP.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/renderer/datoviz_renderer.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_points.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_image.py`
- `src/gsp/protocol/`
- `src/gsp/protocol/visuals.py`

Datoviz docs and local package:

- `/Users/cyrille/GIT/Viz/datoviz/docs/start/quickstart.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/start/choose-your-layer.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/reference/feature-status.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/reference/queries.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/reference/visual-attributes.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/how-to/capture-an-image.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/how-to/pick-and-probe.md`
- `/Users/cyrille/GIT/Viz/datoviz/docs/how-to/probe-fields.md`
- local introspection of `/Users/cyrille/GIT/Viz/datoviz/datoviz/`

Online primary docs checked:

- <https://datoviz.org/reference/api_c/>
- <https://datoviz.org/reference/api_py/>

## Environment Inventory

Local introspection found:

- `datoviz.__file__`: `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py`
- `datoviz.App`: missing
- `datoviz.visuals`: missing
- `datoviz._panel`: missing
- `datoviz._figure`: missing
- `datoviz._texture`: missing
- `dvz_scene`, `dvz_figure`, `dvz_panel`, `dvz_panel_full`, `dvz_point`, `dvz_image`, `dvz_visual_set_data`, `dvz_visual_set_field`, `dvz_visual_set_texture`, `dvz_capability_snapshot`, `dvz_panel_query`, `dvz_panel_query_now`, and `dvz_scene_poll_query`: present

Important mismatch:

- The public online Python API reference still documents a high-level `datoviz._app.App`/visual wrapper surface. The local v0.4 docs say the normal Python facade preserves C-shaped `dvz_*` names and does not provide the old high-level plotting wrapper. For GSP implementation, use the local v0.4 C-shaped API as the implementation target.

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
| Queries | `dvz_visual_set_query_capabilities()`, `dvz_panel_query()`, `dvz_scene_poll_query()` | conceptually feasible; Python result decoding gap |
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
- Datoviz positions are documented as `(N, 3)` normalized positions in quickstart. For GSP `DATA` coordinates, either bind a panel/controller transform or pre-transform with `dvz_panel_data_to_visual_positions()`.
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
- prefer `dvz_sampled_field()` + `dvz_sampled_field_set_data()` + `dvz_visual_set_field(image, "field", field)`;
- transitional RGBA8 convenience path: `dvz_visual_set_texture(image, pixels, width, height)`;
- attach to panel with `dvz_panel_add_visual()`.

Gaps and adaptation:

- GSP `extent` must be converted to four corner positions. Existing Datoviz examples use four data positions, transform them with `dvz_panel_data_to_visual_positions()`, and upload triangle-strip positions.
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

- queue: `dvz_panel_query(panel, x, y, &request)`;
- synchronous helper: `dvz_panel_query_now(panel, runtime, x, y, &request, &result)`;
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

Blocking gap:

- `DvzQueryResult` is exposed as a class but has no `_fields_` in local introspection. Python code can allocate it only if ctypes permits opaque storage, but cannot decode fields such as status, hit, visual id, resolved target, or coordinates. A Python GSP adapter cannot implement query/readback results cleanly until this binding is fixed or a helper API returns decoded values.

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
8. Defer query tests until `DvzQueryResult` is decodable from Python.

## Required Handoffs

The following Datoviz-side or binding-side tasks should be resolved before a full GSP Datoviz backend implementation claims parity:

- Expose a stable Python binding for `DvzQueryResult` fields or provide a decoded query-result helper.
- Clarify the promoted Python facade contract in docs versus online high-level `App` reference, so GSP agents do not target the obsolete wrapper.
- Confirm image interpolation and origin handling for `DvzSampledField`/`dvz_image`.
- Confirm whether GSP should use `dvz_visual_set_texture()` for RGBA8 only or move immediately to sampled fields for all images.

## ChatGPT Pro Consultation

No ChatGPT Pro consultation is required for M004. The assessment identifies implementation gaps and handoff tasks. A future implementation mission may need consultation if point-size semantics, image coordinate conventions, or GPU-authoritative query payload semantics need final protocol decisions.
