# Datoviz v0.4 Backend Spec - Draft

Datoviz v0.4 is the flagship high-performance GPU backend for GSP.

The old GSP Datoviz adapter targeting Datoviz v0.3 should be treated as legacy mapping reference only.
For axes implementation, the source of truth is `github.com/datoviz/datoviz` branch `v0.4-dev`
and the local checkout headers under `include/datoviz/`. Do not implement from `datoviz.org` or
v0.3-era `panel.axes(...)` examples.

Target mapping:

- GSP session -> Datoviz scene/app/view runtime;
- GSP figure/panel -> Datoviz figure/panel;
- GSP resources -> Datoviz scene buffers, textures, sampled fields;
- GSP visual families -> Datoviz v0.4 visual constructors;
- GSP queries -> Datoviz panel query system;
- GSP capabilities -> Datoviz capability snapshot.

M004 must identify exact API gaps before implementation.

## M004 assessment result

Detailed assessment lives in `docs/datoviz_v04_gap_analysis.md`.

The implementation target is the C-shaped Datoviz v0.4 scene/app API exposed through the top-level
Python facade (`import datoviz as dvz`) and raw ctypes bindings. Do not target the old v0.3-style
Python wrapper surface (`datoviz.App`, `datoviz.visuals`, `datoviz._panel`, `datoviz._figure`,
`datoviz._texture`): those modules/classes were absent in the inspected local v0.4 package.

### First backend slice target

| GSP concept | Datoviz v0.4 target | Status |
|---|---|---|
| Session/server | `dvz_scene()` plus app/view lifecycle | feasible |
| Figure/canvas | `dvz_figure(scene, width, height, flags)` | feasible |
| Panel/viewport | `dvz_panel()` or `dvz_panel_full()` | feasible; convert GSP pixel viewports to normalized panel desc |
| Point visual | `dvz_point()` plus `dvz_visual_set_data()` for `position`, `color`, `diameter_px` | feasible after point-size semantic alignment |
| Path visual | `dvz_path()` plus `position`, `color`, `stroke_width_px`, subpaths, caps, and joins | feasible when path helpers are exposed |
| Image visual | `dvz_image()` plus `position`, `texcoords`, sampled field or texture binding | feasible after image origin/interpolation confirmation |
| Mesh visual | `dvz_mesh()` plus direct `position`/`color` attribute upload and index upload | implemented for bounded 2D NDC S025 cases; DATA/3D/query remain gated |
| Capabilities | `dvz_capability_snapshot()` | feasible |
| Queries | `dvz_panel_query()` / `dvz_scene_poll_query()` | conceptually aligned; local `../datoviz` headers define `DvzQueryResult`, but the current GSP env imports Datoviz 0.3.5 |
| Capture | offscreen view capture or `dvz.capture()` | feasible for PNG screenshots only |

### Implementation constraints

- Use `DvzCapabilitySnapshot` to build GSP `CapabilitySnapshot` before planning.
- Treat screenshot capture as sRGB RGBA8 output, not scientific readback.
- Use sampled fields (`dvz_sampled_field`, `dvz_visual_set_field`) for scalar/color images where possible; `dvz_visual_set_texture` is a transitional RGBA8 convenience path.
- Do not claim query support in the Python GSP adapter until query results are decodable.
- Do not edit the Datoviz repository from this repo; create handoff tasks for Datoviz-side API or binding gaps.

## M007 adapter slice

The first Datoviz v0.4 protocol adapter lives in `src/gsp_datoviz/protocol_renderer.py`.
It is intentionally separate from the legacy Datoviz renderer path and targets only the
top-level C-shaped facade (`dvz_scene`, `dvz_figure`, `dvz_panel_full`, `dvz_point`,
`dvz_marker`, `dvz_image`, `dvz_visual_set_data`, `dvz_visual_set_texture`, and
`dvz_panel_add_visual`).

Current supported surface:

| GSP concept | Datoviz v0.4 path | M007 status |
|---|---|---|
| Capability snapshot | static GSP `CapabilitySnapshot` | implemented for first slice |
| Session/figure/panel | `dvz_scene()` + `dvz_figure()` + `dvz_panel_full()` | implemented |
| Point visual | `dvz_point()` + `position`, `color`, `diameter_px` attributes | implemented for NDC positions |
| Point size | GSP screen-pixel diameter uploaded to Datoviz `diameter_px` | implemented |
| Marker visual | `dvz_marker()` + `position`, `color`, `diameter_px`, `angle`, `shape` attributes | implemented when marker facade symbols are exposed |
| Path visual | `dvz_path()` + `position`, `color`, `stroke_width_px`, subpaths, caps, joins | implemented when path facade symbols are exposed |
| Image visual | `dvz_image()` + `position`, `texcoords`, sampled field or texture fallback | implemented for scalar gray and RGB/RGBA NDC images |
| Image scalar fields | sampled-field path | deferred to `DATOVIZ-V04-IMAGE-FIELD-CONTRACT` |
| Queries | Datoviz panel query APIs | not advertised; deferred to `DATOVIZ-V04-QUERY-BINDING` |

The adapter raises explicit unsupported errors for semantics not locked in this slice:

- non-NDC point/image coordinates;
- missing marker facade functions or non-NDC marker coordinates;
- missing path facade functions or non-NDC path coordinates;
- missing image sampling controls for requested interpolation;
- query/readback support.

## M066 PointVisual retained path

Point visuals are attached with an explicit `DvzVisualAttachDesc` instead of relying on a NULL
descriptor. For the S023 NDC smoke cases, the adapter uses `coord_space=DVZ_COORD_DATA` with the
default Datoviz panel domain `[-1, +1]`, matching the protocol NDC coordinate fixtures. The
descriptor also sets `z_layer=0` for deterministic future layering.

## M009 query handoff

Datoviz v0.4 query APIs are still not advertised by the GSP Datoviz adapter. During M009, Python
query decoding was blocked because `DvzQueryResult` fields were unavailable. M018 refreshed the
evidence against `../datoviz` on `v0.4-dev` commit `bc9adbb40`: the headers now define
`DvzQueryResult` with status, hit, visual identity, target ids, item/texel ids, positions, displayed
RGBA, and scalar/vector payload fields. However, the current GSP environment imports Datoviz `0.3.5`
from `.venv` and exposes no v0.4 `dvz_*` symbols, `DvzQueryResult`, or `DvzCapabilitySnapshot`.
Runtime query/capability work therefore remains capability-gated until a v0.4-dev Python binding is
active.

Required parity targets:

- point hits must map to GSP `QueryStatus.HIT`, `VisualFamily.POINT`, `visual_id`, and `item_id`;
- image hits must map to GSP `QueryStatus.HIT`, `VisualFamily.IMAGE`, `texel`, displayed RGBA, and
  source value where available;
- misses, outside-panel, unsupported, stale/dropped async results, and backend failures must map to
  distinct GSP statuses without hit payload fields.

## S027 transform/view capability target

Datoviz transform support is capability-gated. The adapter may satisfy accepted S027 semantics with
native GPU placement or explicit CPU adaptation for finite eager arrays, but it must report the
placement/adaptation and must not silently materialize virtual or huge sources.

Strict transform query support requires retained source coordinates and inverse reporting through
`gsp.transform-query@0.1`. If Datoviz can render a transformed visual but cannot provide the inverse
payload, the adapter must advertise render support separately from query inverse support and return a
structured unsupported diagnostic for strict inverse requests.

## M024 capability parity slice

The Datoviz adapter now translates `dvz_capability_snapshot()` into GSP `CapabilitySnapshot` when
the active Python facade exposes it. The translation is intentionally conservative:

- `max_buffer_size` maps to `CapabilitySnapshot.max_buffer_bytes`;
- proven Datoviz texture flags add `r32uint`/`rg32uint` alongside the existing RGBA8 texture path;
- readback flags stay in raw metadata until capture/offscreen parity is implemented;
- raw Datoviz capability fields are preserved in `metadata["datoviz_raw_capabilities"]`;
- shader formats and query profile bits are preserved as metadata;
- `query_modes` and typed query capabilities remain empty until `DvzQueryResult` decoding and
  status/payload mapping are implemented and tested.

If `dvz_capability_snapshot()` is unavailable, the adapter falls back to the conservative static
GSP slice and records a diagnostic in metadata. Real runtime smoke tests skip cleanly when the
installed binding is still Datoviz 0.3.5 or otherwise lacks the v0.4 capability symbol.

## M025 query decode parity slice

The Datoviz adapter now includes a pure decoder for Python-visible `DvzQueryResult`-shaped objects.
This decoder is tested with synthetic objects and maps:

- Datoviz `hit`, `miss`, and `outside-panel` statuses to matching GSP `QueryStatus` values;
- Datoviz stale/dropped results to GSP `dropped`;
- Datoviz unsupported target/profile/family/format statuses to GSP `unsupported`;
- Datoviz GPU/readback/decode/unknown failures to GSP `failed`;
- point visual hits to GSP `VisualFamily.POINT` with `item_id`;
- image visual hits to GSP `VisualFamily.IMAGE` with displayed RGBA and value when present.

This remains decode parity, not runtime query parity. The adapter still advertises no query modes
until a runtime execution path and application visual-id mapping are validated.

## M026 runtime query binding gate

The Datoviz adapter now has a conditional query capability gate. When the active Python facade
exposes all of the following v0.4 query-binding requirements:

- `dvz_query_request`;
- `dvz_panel_query`;
- `dvz_scene_poll_query`;
- `DvzQueryResult` with decodable `_fields_`;

the GSP Datoviz capability snapshot advertises coarse `panel-query` support. If any requirement is
missing, query modes remain empty and the missing binding pieces are recorded in
`metadata["datoviz_query_binding_diagnostics"]`.

Point/image-specific query modes (`point-item`, `image-texel`) are still not advertised in this
slice. Those require a real runtime query execution proof plus stable application visual-id mapping
and payload validation.

## M027 sampled-field image parity slice

The Datoviz image adapter now prefers the explicit sampled-field path for bounded RGBA8 images when
the active v0.4 Python facade exposes:

- `dvz_sampled_field_desc`;
- `dvz_field_data_view`;
- `dvz_sampled_field`;
- `dvz_sampled_field_set_data`;
- `dvz_visual_set_field`.

For supported uint8 RGB/RGBA images, the adapter creates a scene-owned 2D `RGBA8_UNORM` sampled
field with color semantic and sRGB role, uploads tightly packed data, and binds it to the image
visual's `"field"` slot. If sampled-field symbols are unavailable, the existing transitional
`dvz_visual_set_texture()` RGBA8 path remains as fallback.

Scalar float sampled fields and color-scale semantics remain deferred. They require explicit scale
The M070 scalar path supports conservative CPU grayscale/clim normalization before upload; broader backend-native colormap bindings remain deferred.

## M028 capture/offscreen parity slice

The Datoviz adapter now has a bounded offscreen PNG capture path. The GSP capability snapshot
advertises `output_formats=("png",)` only when the active v0.4 Python facade exposes:

- `dvz_app`;
- `dvz_view_offscreen`;
- `dvz_view_capture_png`;
- either `dvz_app_render_once` or `dvz_app_run`.

`DatovizV04ProtocolRenderer.capture_png_bytes()` lazily creates an offscreen app/view pair for the
existing scene and figure, renders one frame, captures via `dvz_view_capture_png()`, reads the PNG
bytes, and removes the temporary file. The capture result is screenshot/export output: sRGB RGBA8
PNG bytes, not scientific linear readback.

Raw RGBA capture, canvas readback, video capture, visual conformance image comparison, and
headless GPU runtime execution remain deferred.

## M029 runtime point/image query execution proof

The Datoviz adapter now includes a bounded runtime query wrapper for the v0.4 queue/poll binding.
When the active Python facade exposes the M026 query requirements, the GSP capability snapshot
promotes:

- `panel-query`;
- `point-item`;
- `image-texel`;
- typed `data`-scope query capability for frontmost panel-coordinate requests.

`DatovizV04ProtocolRenderer.query_panel()` accepts only `QueryScope.DATA`,
`QueryCoordinateSpace.PANEL`, and `QueryHitPolicy.FRONTMOST` in this slice. It creates a
`DvzQueryRequest`, assigns a stable numeric request id derived from the GSP query id, queues with
`dvz_panel_query()`, polls once with `dvz_scene_poll_query()`, decodes the returned
`DvzQueryResult`, and remaps the result id back to the GSP request id. A bounded poll with no
available result returns `dropped` with a diagnostic.

Guide scope, all-rendered scope, `hit_policy=all`, extension query payloads, and live GPU/headless
execution proof remain deferred. Runtime tests skip cleanly while the installed GSP environment
imports Datoviz 0.3.5 rather than a v0.4-dev facade.

## M030 v0.4-dev binding activation smoke

The local Datoviz v0.4-dev wheel-stage can be activated for GSP smoke testing without modifying the
GSP lockfile:

```bash
PYTHONPATH=../datoviz/build/manylinux-x86_64/wheel-stage:. \
LD_LIBRARY_PATH=../datoviz/build/manylinux-x86_64/wheel-stage/datoviz:../datoviz/build/manylinux-x86_64/src \
uv run python tools/datoviz_v04_smoke.py
```

The smoke imports `datoviz` from the v0.4-dev wheel-stage, validates the `dvz_*` facade shape,
constructs `DatovizV04ProtocolRenderer`, adds point and image visuals, verifies sampled-field and
capture binding readiness, and runs the bounded query wrapper. After Datoviz commit
`8bb192c2da6df70279eedac5b2eaed9f45aab96c`, Python query-result decoding is ready:

- `query_ready=true`;
- promoted query modes: `panel-query`, `point-item`, `image-texel`;
- `DvzQueryResult._fields_` includes the required fields for status, hit identity, coordinates,
  displayed color, scalar/vector value, and label payloads;
- the smoke can assign and read `request_id`, `status`, `hit`, `panel_position`, `visual_id`,
  `item_id`, `texel_id`, `display_rgba`, `scalar`, `vector`, and `label`.

## M031 live offscreen query result proof

GSP now proves the Datoviz v0.4-dev live query path when the regenerated Datoviz wheel-stage Python
binding is paired with repaired native runtime libraries from the built wheel:

```bash
PYTHONPATH=../datoviz/build/manylinux-x86_64/wheel-stage:. \
LD_LIBRARY_PATH=../datoviz/build/manylinux-x86_64/wheel-stage/datoviz:/tmp/gsp-datoviz-wheelhouse-smoke/datoviz.libs:/tmp/gsp-datoviz-wheelhouse-smoke/datoviz \
DVZ_WHEEL_RUNTIME_DIRS=/tmp/gsp-datoviz-wheelhouse-smoke/datoviz.libs:/tmp/gsp-datoviz-wheelhouse-smoke/datoviz:../datoviz/build/manylinux-x86_64/wheel-stage/datoviz \
DVZ_SHADERC_RUNTIME_LIBRARY=/tmp/gsp-datoviz-wheelhouse-smoke/datoviz/libshaderc_shared.so.1 \
uv run python tools/datoviz_v04_smoke.py --require-query-ready --require-live-query-hit
```

Adapter behavior added in M031:

- point visuals call `dvz_visual_set_query_capabilities(..., DVZ_QUERY_CAPABILITY_ITEM)`;
- image visuals call `dvz_visual_set_query_capabilities(..., ITEM | PIXEL)`;
- `query_panel()` queues a Datoviz panel query, renders one offscreen frame when
  `dvz_view_render_once()`/equivalent is available, polls `dvz_scene_poll_query()`, and decodes the
  live result;
- the smoke reports `live_query_status`, `live_query_hit`, visual identity fields, displayed color,
  value, and diagnostics.

Current live proof result: `live_query_status=hit`, `live_query_hit=true`, and
`live_query_visual_id="datoviz:visual:1"`. The same smoke confirms that `DvzQueryResult._fields_`
contains `visual_family`, `item_id`, `texel_id`, `display_rgba`, `value_kind`, `scalar`, `vector`,
and `label`, and synthetic field readback succeeds. However, the current mixed v0.4-dev runtime
artifact leaves `visual_family`, `item_id`, `texel`, displayed color, and value unset in the live
result. Treat that as the remaining Datoviz live payload parity gap.

## M032 color pipeline selection

The Datoviz v0.4 adapter exposes a figure-wide color-pipeline option through
`DatovizV04ProtocolRenderer(color_pipeline=...)`:

- `linear_srgb` is the low-level renderer default and matches Datoviz's color-managed path:
  authored semantic sRGB colors are converted to linear RGB before scene arithmetic and alpha
  blending. This is the mathematically correct path.
- `legacy_srgb_blend` is the visual-QA and Matplotlib-parity default. It intentionally reproduces
  Matplotlib/Agg's legacy behavior: alpha is blended directly in display/sRGB values instead of in
  linear light.

`legacy_srgb_blend` requires a Datoviz binding with `dvz_figure_set_color_pipeline()` and
`DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND`. If the binding is missing, GSP raises
`DatovizV04Unavailable` instead of silently producing linear-light output.

The visual-QA harness defaults Datoviz renders to `legacy_srgb_blend` so alpha-overlap cases compare
against the Matplotlib reference's display-space blending behavior. Use
`python -m gsp.qa.visual run --datoviz-color-pipeline linear_srgb ...` for Datoviz-correct
linear-light comparisons.

The current Python binding may expose `dvz_figure_set_color_pipeline()` without exporting enum
constants; GSP therefore uses the documented v0.4 enum values
`DVZ_COLOR_PIPELINE_LINEAR_SRGB = 0` and `DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND = 1` as fallbacks.
If `legacy_srgb_blend` is requested and the setter is missing, GSP raises `DatovizV04Unavailable`
instead of silently producing linear-light output.

## S029 text and mesh probe update

The current local Datoviz v0.4 checkout exposes retained text APIs (`dvz_text`,
`dvz_text_set_string`, `dvz_text_style`, `dvz_text_set_style`, `dvz_text_placement`,
`dvz_text_set_placement`), retained mesh APIs (`dvz_mesh`, direct `dvz_visual_set_data`,
`dvz_visual_set_index_data`, `dvz_visual_set_depth_test`), and native colorbar APIs (`dvz_scale`,
`dvz_colormap_builtin`, `dvz_colorbar`). Current S029 Datoviz renders text, bounded 2D mesh, scalar
image colorbar, and S027 transform/View2D review cases as adapted rows; unsupported rows in those
families are GSP adapter/verification gaps, not evidence that Datoviz lacks the families.

Do not promote these rows to strict solely from symbol presence. Text still needs verified mapping
for font roles, multiline/non-ASCII handling, z-order, and query payloads. Mesh
still needs face-query payloads, depth/culling policy expansion, and strict parity audit. Per-face
RGBA is currently adapted by duplicating indexed vertices before upload to Datoviz's per-vertex color
mesh path. Colorbar rendering uses native Datoviz scale/colorbar objects, but explicit tick labels
and colorbar ramp query are not strict yet.

## Post-M011 parity gap update

The current GSP Datoviz adapter is still a slice, not parity:

- implemented: point visual, scalar gray and RGB/RGBA images via texture fallback or sampled field, Datoviz
  capability translation, query decoding and binding gate, bounded point/image query execution
  wrapper, bounded offscreen PNG capture, color-pipeline selection, native colorbar rendering,
  CPU-adapted named/inline affine transforms and DATA/View2D placement for finite eager visuals,
  v0.4-dev wheel-stage smoke harness;
- not implemented: strict explicit colorbar ticks/labels, colorbar query, live GPU/headless query
  execution validation, strict guide parity, guide/all-rendered query scopes, scientific readback,
  tiled-source support.

Recommended next mission: establish the Datoviz v0.4 Python facade/raw binding import path, then
implement Datoviz query/capability parity. Scope implementation to translating
`dvz_capability_snapshot()` and decoding `DvzQueryResult` into GSP `CapabilitySnapshot` and
`QueryResult`, with skip-clean runtime tests. Keep backend-native colormap expansion, capture, and tiled
data-source Datoviz support as explicit follow-ups unless required for the query proof.

## P002 axis provider update

Datoviz v0.4-dev headers expose a native panel-axis candidate provider:

- `dvz_panel_set_domain()` carrying ordered GSP `View2D` X/Y endpoints;
- `dvz_panel_view2d()` / `dvz_panel_set_view2d()` carrying fitting/aspect/padding policy only;
- `dvz_panel_axis()`;
- `dvz_axis_set_label()`;
- `dvz_axis_set_tick_policy()`;
- `dvz_axis_set_ticks()` when the facade exposes explicit tick values/labels;
- optional grid/style/visible-domain/coordinate-transform helpers.

GSP models this as `datoviz.v04.panel_axis.wip`. The provider is capability-gated on actual Python
facade/raw binding symbols. Native backend auto ticks are adapted output because they are not the
GSP deterministic `AUTO_LINEAR_NICE_V0` tick policy. Explicit GSP tick values/labels can be rendered
for review through `dvz_axis_set_ticks` when the binding exposes it.

GSP must set `dvz_panel_set_domain()` before enabling `DvzPanelView2D` policy, because current
Datoviz treats `DvzPanelView2D` as policy-only and resolves source data limits from panel domains.
The adapter preserves reversed endpoint order when setting those domains.

S028 guide/View2D support must remain capability-gated. Datoviz may claim strict guide support only
when it can verify that panel axes consume the same `View2D` domain as data visuals, preserve
explicit GSP tick values/labels, handle reversed finite limits consistently, and report guide query
support from the same view snapshot. Otherwise it must report adapted or unsupported guide behavior
with structured diagnostics.

S030 closeout status for the current GSP Datoviz adapter:

| Capability | GSP status | Diagnostic |
|---|---|---|
| Panel axis provider symbols | `adapted` when Python facade exposes required v0.4-dev symbols | `datoviz.v04.panel_axis.wip` |
| Backend auto ticks | `adapted` | Datoviz-native ticks may render but are not GSP-resolved tick output. |
| Explicit GSP tick values/labels | `adapted` review path | Requires `dvz_axis_set_ticks`; proven by S030 review artifacts. |
| Grid lines | capability-gated/adapted | Requires `dvz_axis_set_grid`; alignment remains backend-native for auto ticks. |
| Axis labels | capability-gated/adapted | Requires `dvz_axis_set_label`; title/panel text remains outside strict Datoviz S028 support. |
| Reversed finite `View2D` axes | `adapted` guide review path; data-view promotion requires adapter/readback proof | Datoviz now supports ordered panel domains with policy-only `DvzPanelView2D`; strict guide parity still excludes title/query. |
| Guide picking/query | intentionally deferred | `axis_guide_query_unsupported` |
| `all-rendered` query with guides | unsupported | `all_rendered_guides_unsupported`; do not silently degrade to data-only. |

This is sufficient for S030 closeout because Matplotlib remains the strict reference path and the
Datoviz adapter reports the missing guide semantics explicitly. The final S030 review pack classifies
`guide/view2d_auto_grid` and `guide/view2d_reversed_explicit` as rendered `adapted` rows, not strict
rows. Future Datoviz releases may promote the provider toward strict status after title layout and
guide-query payload semantics are exposed and validated through the Python facade, or after the GSP
guide-row contract explicitly excludes those semantics.


## S025 MeshVisual target

S025 Datoviz work uses retained `dvz_mesh` support after the S029 capability probe. The adapter
preserves the bounded review-pack slice for inline indexed 2D triangles, uniform RGBA, vertex RGBA,
DATA/View2D placement through native panel domains, and per-face RGBA adapted by vertex
duplication. It still emits structured unsupported reports for face scalar colors, normals, shading,
3D projection, and mesh query gaps. Public GSP fields must not expose Datoviz slot names, material
structs, helper geometry loaders, or draw calls.
