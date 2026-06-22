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
| Point visual | `dvz_point()` plus `dvz_visual_set_data()` for `position`, `color`, `diameter` | feasible after point-size semantic alignment |
| Image visual | `dvz_image()` plus `position`, `texcoords`, sampled field or texture binding | feasible after image origin/interpolation confirmation |
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
`dvz_image`, `dvz_visual_set_data`, `dvz_visual_set_texture`, and
`dvz_panel_add_visual`).

Current supported surface:

| GSP concept | Datoviz v0.4 path | M007 status |
|---|---|---|
| Capability snapshot | static GSP `CapabilitySnapshot` | implemented for first slice |
| Session/figure/panel | `dvz_scene()` + `dvz_figure()` + `dvz_panel_full()` | implemented |
| Point visual | `dvz_point()` + `position`, `color`, `diameter` attributes | implemented for NDC positions |
| Point size | GSP marker-area size converted to Datoviz diameter pixels | implemented |
| Image visual | `dvz_image()` + `position`, `texcoords`, `dvz_visual_set_texture()` | implemented for uint8 RGB/RGBA, nearest, NDC extents |
| Image scalar fields | sampled-field path | deferred to `DATOVIZ-V04-IMAGE-FIELD-CONTRACT` |
| Queries | Datoviz panel query APIs | not advertised; deferred to `DATOVIZ-V04-QUERY-BINDING` |

The adapter raises explicit unsupported errors for semantics not locked in this slice:

- non-NDC point/image coordinates;
- non-nearest image interpolation;
- scalar, grayscale, or floating-point images that should use sampled fields;
- query/readback support.

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

## Post-M011 parity gap update

The current GSP Datoviz adapter is still a slice, not parity:

- implemented: point visual, RGBA/RGB uint8 image via `dvz_visual_set_texture`, static capabilities;
- not implemented: sampled-field image path, Datoviz capability translation, query decoding,
  runtime query execution proof, offscreen/capture proof, tiled-source support.

Recommended next mission: establish the Datoviz v0.4 Python facade/raw binding import path, then
implement Datoviz query/capability parity. Scope implementation to translating
`dvz_capability_snapshot()` and decoding `DvzQueryResult` into GSP `CapabilitySnapshot` and
`QueryResult`, with skip-clean runtime tests. Keep sampled-field scalar images, capture, and tiled
data-source Datoviz support as explicit follow-ups unless required for the query proof.

## P002 axis provider update

Datoviz v0.4-dev headers expose a native panel-axis candidate provider:

- `dvz_panel_set_domain()`;
- `dvz_panel_view2d()` / `dvz_panel_set_view2d()`;
- `dvz_panel_axis()`;
- `dvz_axis_set_label()`;
- `dvz_axis_set_tick_policy()`;
- optional grid/style/visible-domain helpers.

GSP models this as `datoviz.v04.panel_axis.wip`. The provider is capability-gated on actual Python
facade/raw binding symbols. Native backend auto ticks are adapted output unless Datoviz can accept
GSP-resolved explicit ticks or an equivalent declared GSP policy.
