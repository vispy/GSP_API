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

## S035 canvas size policies

The Datoviz adapter accepts `CanvasSize` requests. It maps them to Datoviz view-size descriptors when
the v0.4 facade exposes that API, otherwise it falls back to GSP-side resolution. Live GLFW views use
resolved host logical dimensions; offscreen views and figures use resolved framebuffer dimensions.

Screen-space visual fields ending in `_px` are canvas/reference pixels. Before upload, the adapter
multiplies point/marker diameters, text sizes, segment/path widths, and marker stroke widths by
`ResolvedCanvas.framebuffer_per_canvas_px`.

`ColorbarGuideStyle` values are lowered through the same resolved canvas scale before setting
Datoviz colorbar descriptor fields such as `ramp_width_px`, `tick_length_px`, `label_gap_px`, and
placement width/height.

`DVZ_WINDOW_SIZE_SCALE` is not part of the Datoviz or GSP contract. Use `reference_px` for live
physical-size comparability and `pixel_exact` for deterministic captures.

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
| Image visual | `dvz_image()` plus `position`, `texcoords`, sampled fields, or packed RGBA8 upload | feasible after image origin/interpolation confirmation |
| Mesh visual | `dvz_mesh()` plus direct `position`/`color` attribute upload and index upload | implemented for bounded 2D NDC S025 cases; DATA/3D/query remain gated |
| Capabilities | `dvz_capability_snapshot()` | feasible |
| Queries | `dvz_panel_query_px()` / `dvz_scene_poll_query()` | conceptually aligned when the generated binding exposes current query functions and `DvzQueryResult` fields |
| Capture | offscreen view capture or `dvz.capture()` | feasible for PNG screenshots only |

### Implementation constraints

- Use `DvzCapabilitySnapshot` to build GSP `CapabilitySnapshot` before planning.
- Treat screenshot capture as sRGB RGBA8 output, not scientific readback.
- Use sampled fields (`dvz_sampled_field`, `dvz_visual_set_field`) for scalar/color images, and `dvz_visual_set_texture_rgba8` only for already-packed `uint8[..., 4]` RGBA images.
- Do not claim query support in the Python GSP adapter until query results are decodable.
- Do not edit the Datoviz repository from this repo; create handoff tasks for Datoviz-side API or binding gaps.

## M007 adapter slice

The first Datoviz v0.4 protocol adapter lives in `src/gsp_datoviz/protocol_renderer.py`.
It is intentionally separate from the legacy Datoviz renderer path and targets only the
top-level C-shaped facade (`dvz_scene`, `dvz_figure`, `dvz_panel_full`, `dvz_point`,
`dvz_marker`, `dvz_image`, `dvz_visual_set_data`, `dvz_visual_set_texture_rgba8`, and
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
| Queries | Datoviz panel query APIs plus View3D ray-context payloads | point/image query advertised when `DvzQueryResult` is bindable; `view3d-ray` advertised with P022 camera binding |

The adapter raises explicit unsupported errors for semantics not locked in this slice:

- non-NDC point/image coordinates;
- missing marker facade functions or non-NDC marker coordinates;
- missing path facade functions or non-NDC path coordinates;
- missing image sampling controls for requested interpolation;
- query/readback support.

## S037 View3D binding

Datoviz v0.4 static public `(N, 3)` `MeshVisual` rendering is supported when the local Datoviz
binding exposes the P022 camera prerequisites recorded in `.agent/S037_DATOVIZ_VIEW3D_EVIDENCE.md`.
Older Datoviz builds without camera ctypes layouts or `dvz_camera_set_orthographic_bounds()` remain
structured unsupported.

The private binding layer accepts only public GSP state:

- `View3D.id`, `panel_id`, `camera`, `projection`, `depth_mode`, and `revision`;
- `MeshVisual.positions`, faces/indices, colors, depth mode, and coordinate space;
- `CoordinateSpace.DATA` and `CoordinateSpace.NDC`.

Evidence required for the support claim:

- DATA `(N, 3)` meshes move correctly when canonical camera/projection changes;
- NDC `(N, 3)` meshes are interpreted directly as panel NDC3;
- opaque less-depth behavior is proven independent of submission order before
  `meshvisual.positions3d.opaque_depth.v1` is claimed;
- projection snapshot ids match canonical S036 state changes;
- query ray-readback payloads match canonical S036 CPU snapshot semantics for
  `query.view3d.ray_readback.v1`;
- public API does not expose Datoviz camera, controller, draw-state, or material names.

The protocol renderer prefers a retained DATA-space View3D mesh path when the Datoviz binding
exposes `DvzPanelView3DDesc`, `DvzPanelView3DState`, `dvz_panel_set_view3d_desc()`,
`dvz_panel_view3d_state()`, `dvz_panel_camera()`, and camera view/projection readback/update
symbols. In that path, DATA `(N,3)` mesh vertices are uploaded unchanged, attached with panel DATA
coordinates, and ordinary camera/projection updates touch retained View3D state only. After S050
runtime evidence, this retained DATA-space path may claim strict
`meshvisual.positions3d.opaque_depth.v1` for fully opaque meshes: the accepted proof renders the
same nearer-fragment-wins red/blue samples with original and reversed face submission order. Older
bindings fall back to CPU-projected GSP panel NDC and adapted face ordering, and must not claim
strict opaque depth.

GSP lowers retained `View3D.camera` through `dvz_panel_set_view3d_desc()` on setup and
`dvz_camera_set_view()` on updates, and lowers `OrthographicProjection3D.xlim`, `.ylim`, and
`.near_far` through `dvz_camera_set_orthographic_bounds()`. Datoviz
`query.view3d.ray_readback.v1` returns canonical ray-context payloads from public `View3D` state and
snapshot ids.

When the retained `View3D` substrate and Datoviz live input bindings are both present, GSP enables
live `View3D` review navigation by translating pointer input into canonical S037 actions: left-drag
orbit, right-drag pan, wheel zoom, and double-click reset. Each accepted action is reduced through
public GSP `View3DNavigationAction` semantics, lowered into retained Datoviz camera/projection
state, checked against Datoviz state readback, and followed by a retained frame request without
rewriting unchanged mesh vertex/index buffers. Older bindings keep static `View3D` rendering and
report structured diagnostics instead of claiming `view3d.navigation.orbit_pan_zoom.v1`. S044
accepts a separate backend-neutral `query.view3d.mesh_triangle_pick.v1` target for opaque DATA-space
mesh triangles; Datoviz support remains unadvertised until public visual/triangle mapping and
pick-state freshness are proven. Materials, lights, textures, perspective, and culling remain
deferred.

S050 accepts a culling contract but does not promote Datoviz culling by default. Datoviz may
advertise `meshvisual.face_culling.data3d.projected_ndc.v1` or
`meshvisual.face_culling.ndc3.panel_winding.v1` only after public runtime evidence proves GSP
projected panel-NDC winding, reversed `xlim`/`ylim` behavior, culling before depth writes, and no
leakage from framebuffer y-down or native front-face conventions. Datoviz may advertise
`query.view3d.mesh_triangle_pick.face_culling.v1` only after the public query path applies the same
culling rule and returns canonical public face identity. Private Vulkan state, private shader slots,
native mesh ids, and backend draw-state names are not strict evidence.

Datoviz must also keep `query.view3d.mesh_triangle_pick.geometry.v1` and
`query.view3d.mesh_triangle_pick.facing.v1` unadvertised until the public primitive-identity blocker
for base `query.view3d.mesh_triangle_pick.v1` is solved. After Datoviz exposes a public visual id
and canonical face/triangle row, GSP may reconstruct barycentric coordinates, panel-NDC z,
DATA-space hit position, and projected facing from public GSP scene records. Native Datoviz
barycentric/depth fields are optional, and raw or undocumented framebuffer depth is not public GSP
evidence.

## S040 flat Lambert CPU resolve

Datoviz strict S039 flat Lambert support must use CPU-resolved exact per-face colors, not native
Datoviz lighting/material controls.

The strict route is:

- validate `MeshVisual.shading="flat_lambert"` with the accepted S039 protocol validation path;
- resolve explicit or generated face normals in DATA coordinates using protocol code;
- compute one RGBA value per canonical face using `spec/visuals/mesh_flat_lambert_s039.md`;
- upload an unlit Datoviz mesh payload that preserves one constant color per face;
- preserve the existing View3D DATA-space orthographic and opaque-depth prerequisites.

Triangle-expanded upload is the preferred representation. Each canonical triangle contributes three
uploaded vertices and all three vertices receive the same resolved RGBA value. This prevents
Datoviz vertex-color interpolation from changing S039 face-level color semantics.

Native Datoviz normals, lighting, material diffuse/specular/emission controls, shader slots, and
draw-state names are not public GSP semantics and are not strict S040 evidence. They must remain
unused, disabled, or proven inert for the CPU-resolved route.

Datoviz may advertise `meshvisual.material.flat_lambert.v1`,
`meshvisual.normals.face3d.v1`, `meshvisual.normal_generation.face_flat.v1`,
`view3d.light.ambient.v1`, and `view3d.light.directional.v1` only after the CPU-resolved path and
its View3D/depth/unlit prerequisites are fixture-backed. Non-opaque 3D mesh alpha remains
non-strict via `mesh3d_alpha_not_strict`.

## S050 textured mesh gate

Datoviz may advertise `texture2d.rgba8.v1`, `meshvisual.uv.vertex2d.v1`, and
`meshvisual.material.texture2d_unlit.v1` only after public Datoviz APIs prove all accepted S050
semantics:

- canonical RGBA8 texture upload from `uint8 (H,W,4)` data;
- canonical per-vertex UV binding indexed by GSP mesh faces;
- nearest min/mag filtering;
- clamp-to-edge in `u` and `v`;
- no mipmaps or LOD-dependent sampling;
- compatible image-origin behavior for `image[0]` as the top row and high `v` sampling top texels;
- unmanaged numeric RGBA sampling without implicit sRGB/color-profile conversion;
- multiplicative unlit output with no native lighting/material tint.

Private Vulkan objects, private shader slots, private mesh ids, backend-native texture handles, and
draw-state names are not public GSP semantics and are not strict S050 evidence. Textured meshes may
combine with `meshvisual.positions3d.opaque_depth.v1` only on the retained DATA-space View3D path
and only when base alpha is `1.0` and every texture alpha byte is `255`.

M220 found that current v0.4-dev public bindings expose candidate mesh texture symbols:
`dvz_mesh`, mesh `"texcoords"` uploads, RGBA8 sampled fields, `dvz_visual_set_field(...,
"texture", field)`, and `dvz_visual_set_texture_rgba8()`. Datoviz must still keep S050 texture
capabilities unadvertised until runtime fixtures or upstream public documentation prove mesh
nearest/clamp/no-mipmap sampling, top-row/high-v origin behavior, unmanaged numeric RGBA behavior,
and exact multiplicative unlit output.

## M066 PointVisual retained path

Point visuals are attached with an explicit `DvzVisualAttachDesc` instead of relying on a NULL
descriptor. For the S023 NDC smoke cases, the adapter uses `coord_space=DVZ_VISUAL_COORD_DATA` with the
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
- point/image data query modes are advertised when `DvzQueryResult` queue/poll/decode bindings are
  available;
- `view3d-ray` is advertised when the P022 camera binding is present and returns canonical
  `gsp.view3d-query@0.1` payloads.

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
- `dvz_panel_query_px`;
- `dvz_scene_poll_query`;
- `DvzQueryResult` with decodable `_fields_`;

the GSP Datoviz capability snapshot advertises coarse `panel-query` support. If any requirement is
missing, query modes remain empty and the missing binding pieces are recorded in
`metadata["datoviz_query_binding_diagnostics"]`.

Point/image-specific query modes are promoted only after live runtime payload validation. As of
M216, point identity is proven and `point-item` is advertised; image texel/color/value payloads are
not proven and `image-texel` remains unadvertised.

## M027 sampled-field image parity slice

The Datoviz image adapter now prefers the explicit sampled-field path for bounded RGBA8 images when
the active v0.4 Python facade exposes:

- `dvz_sampled_field_desc`;
- `dvz_field_data_view`;
- `dvz_sampled_field`;
- `dvz_sampled_field_set_data`;
- `dvz_visual_set_field`.

For scalar and RGB images, the adapter creates a scene-owned 2D `RGBA8_UNORM` sampled field with
color semantic and sRGB role, uploads tightly packed data, and binds it to the image visual's
`"field"` slot. Already-packed `uint8[..., 4]` RGBA images use the current
`dvz_visual_set_texture_rgba8()` upload path.

Backend-native scalar float sampled fields and color-scale semantics remain deferred. The M070
scalar path supports conservative CPU grayscale/clim normalization before upload; broader
backend-native colormap bindings remain deferred.

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
When the active Python facade exposes the current query requirements and the M216 point identity
payload proof holds, the GSP capability snapshot promotes:

- `panel-query`;
- `point-item`;
- typed `data`-scope query capability for frontmost panel-coordinate identity requests.

`DatovizV04ProtocolRenderer.query_panel()` accepts only `QueryScope.DATA`,
`QueryCoordinateSpace.PANEL`, and `QueryHitPolicy.FRONTMOST` in this slice. It creates a
`DvzQueryRequest`, assigns a stable numeric request id derived from the GSP query id, queues with
`dvz_panel_query_px()`, polls once with `dvz_scene_poll_query()`, decodes the returned
`DvzQueryResult`, and remaps the result id back to the GSP request id. A bounded poll with no
available result returns `dropped` with a diagnostic.

In the M029 slice, guide scope, all-rendered scope, `hit_policy=all`, extension query payloads, and
live GPU/headless execution proof remained deferred. Later S043 work added a capability-gated
guide/all-rendered route through Datoviz panel-frame guide hit/readback APIs. Builds without those
APIs still return structured `axis-guide-query-unsupported` or `all-rendered-guides-unsupported`
diagnostics. `hit_policy=all`, unsupported extension payloads, image texel/color/value parity, and
headless runtime proof remain separate follow-up scope.

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
- promoted query modes: current M216 policy now advertises `panel-query` and `point-item`;
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

M216 refreshed this proof against the current local v0.4-dev binding at Datoviz commit
`a9492af6526fbb722e2c0783811758f1b15be10e`. The current API uses
`dvz_panel_query_px()`. The live smoke proves:

- query binding readiness and a live `hit` result;
- point-only query returns `visual_family="point"` and `item_id=0`;
- image-only query returns `visual_family="image"` and a visual id, but still no `texel`,
  displayed RGBA, or value;
- synthetic `DvzQueryResult` field readback still covers `item_id`, `texel_id`, `display_rgba`,
  scalar/vector values, and labels.

Therefore GSP advertises `panel-query` and `point-item`, keeps `image-texel` unadvertised, and
rejects non-identity Datoviz live data queries unless a supported scalar extension payload can be
decorated from retained GSP-side metadata.

## M032 color pipeline selection

The Datoviz v0.4 adapter exposes a figure-wide color-pipeline option through
`DatovizV04ProtocolRenderer(color_pipeline=...)`:

- `linear_srgb` is an explicit diagnostic/Datoviz-native option and matches Datoviz's
  color-managed path: authored semantic sRGB colors are converted to linear RGB before scene
  arithmetic and alpha blending.
- `legacy_srgb_blend` is the renderer, visual-QA, and Matplotlib-parity default. It intentionally
  reproduces Matplotlib/Agg's legacy behavior: alpha is blended directly in display/sRGB values
  instead of in linear light.

`legacy_srgb_blend` requires a Datoviz binding with `dvz_figure_set_color_pipeline()` and
`DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND`. If the binding is missing, GSP raises
`DatovizV04Unavailable` instead of silently producing linear-light output.

The visual-QA harness defaults Datoviz renders to `legacy_srgb_blend` so alpha-overlap cases compare
against the Matplotlib reference's display-space blending behavior. Use
`python -m gsp.qa.visual run --datoviz-color-pipeline linear_srgb ...` only for explicit
linear-light diagnostics.

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
  CPU-adapted named/inline affine transforms, retained panel-domain DATA/View2D placement for
  finite eager visuals, explicit adapted CPU-remap fallback for finite eager DATA positions,
  v0.4-dev wheel-stage smoke harness;
- not implemented or still gated: strict explicit colorbar ticks/labels, colorbar query, live
  GPU/headless query execution validation, full strict guide parity, `hit_policy=all`, unsupported
  extension payloads, scientific readback, tiled-source support, and Datoviz mesh-triangle picking.
  Guide/all-rendered query is now capability-gated by panel-frame guide hit/readback APIs rather
  than universally deferred.

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

## S034/S044 resolved layout and guide diagnostics

Datoviz guide/layout behavior remains semantic/adapted unless all strict guide evidence is present.
Recent v0.4-dev builds can produce a partial panel frame/layout snapshot and can independently prove
native axis grid clipping to the plot rectangle, but those facts do not by themselves imply
`layout_strict=true`.

The S044 posture is:

- `PanelTextGuide(role=TITLE)` may be rendered as adapted screen text for review output, but this
  does not participate in layout-strict guide geometry or guide query.
- Native axis style mapping is partial and limited to exposed Datoviz fields such as
  `tick_size_px`, `label_size_px`, tick lengths/widths, label/tick gaps, grid width, and plot margin
  fields.
- Grid clipping to `plot_rect_px` is independently native-verified only for Datoviz source builds
  containing commit `9ba820489` or equivalent source/test sentinels. Verified builds report
  `grid_clip_to_plot_rect: native-verified`; older or unverified builds retain
  `grid_clip_not_enforced` and `grid_clip_native_api_unverified`.
- Guide query and all-rendered guide contributions are native-verified only when the Datoviz
  facade exposes panel-frame snapshot, guide hit/readback, and rendered-contribution APIs with
  matching snapshot ids. Builds missing any of those pieces remain structured unsupported.
- Font metrics and raster parity are backend-defined and must not be claimed as parity.

Capability snapshots expose `s034_guide_layout_audit` metadata plus diagnostics. Verified grid
clipping builds include `grid_clip_native_verified`; unverified builds include
`grid_clip_not_enforced` and `grid_clip_native_api_unverified`. The remaining guide strictness
blockers, including `panel_text_guide_as_screen_text`, `axis_style_mapping_partial`,
`guide_query_missing`, `all_rendered_guides_unsupported`, and `font_metrics_parity_false`, remain
separate.

## S035 retained View2D navigation

The Datoviz v0.4 protocol renderer supports the retained target path for accepted S035 `View2D`
navigation updates. `DatovizV04ProtocolRenderer.apply_retained_view2d_navigation()` replaces the
canonical renderer view and reapplies the Datoviz panel domain/View2D state through
`dvz_panel_set_domain()`, `dvz_panel_view2d()`, and `dvz_panel_set_view2d()`.

The retained fast-path invariant is part of the backend contract: after the initial scene upload,
pan/zoom must not call visual data upload, texture upload, index upload, sampled-field upload, or
visual creation for unchanged visuals. The S035 smoke command verifies that invariant with a
Datoviz fake facade:

```bash
uv run python tools/s035_navigation_smoke.py --backend datoviz-fake --steps 40 --points 25000
```

Current support status:

| Capability | Status | Notes |
|---|---:|---|
| Programmatic retained `View2D` update | supported | Uses retained panel domain/View2D state. |
| Visual buffer stability during navigation | supported by fake-facade smoke | Zero upload/recreation calls are expected after baseline scene creation. |
| Adapted CPU-remap navigation fallback | adapted | Retains source DATA positions and reuploads derived view-space positions only when explicitly selected. |
| Datoviz v0.4 union input adapter | supported | Datoviz union input events are normalized into S035 pointer events, then accepted actions update canonical `View2D`. |
| Live resize/scale handling | supported | Resize updates the logical panel rect used for pointer sensitivity; resize and scale refresh native axes from the accepted `View2D`. |
| Datoviz native panzoom controller | native-only demo | `dvz_view_panzoom()` is not strict GSP navigation unless synchronized back into canonical `View2D`. |
| Live GPU runtime performance benchmark | deferred | Requires a bounded benchmark beyond the fake-facade retained-update proof and one-frame live launch. |

Strict Datoviz live navigation is the GSP action path. The adapter subscribes to
`dvz_input_subscribe_event()`, not the raw pointer stream, because Datoviz emits gesture-derived
events such as `DVZ_POINTER_EVENT_DRAG`, `DVZ_POINTER_EVENT_DRAG_STOP`, and
`DVZ_POINTER_EVENT_DOUBLE_CLICK` on the union input stream. Raw `DVZ_POINTER_EVENT_MOVE` is ignored
for GSP navigation; `DRAG` drives pan/zoom, `DRAG_STOP` ends the active gesture, wheel events zoom
about the cursor, and double-click emits a reset action to the controller home view.

Accepted `View2D` updates are applied through retained panel state. Resize events update the live
logical panel rectangle used by the pointer adapter before subsequent pan/zoom sensitivity is
computed. Resize and scale events refresh native axes from the accepted `View2D` without changing
the data view. CPU remapping remains an adapted fallback only and must not be advertised as the
retained fast path.

Native axis refresh follows tick authority. Backend-auto ticks are cleared before reapplying the
Datoviz tick policy so grid lines and tick labels regenerate after a committed `View2D` change.
Explicit GSP tick values/labels are not cleared on navigation: they remain fixed data-space guide
intent and move with the `View2D`.

Datoviz may continue to provide native interaction systems such as `dvz_view_panzoom()` for direct
Datoviz users and native demos. GSP does not reuse those systems for strict behavior unless their
resulting state is synchronized into canonical GSP `View2D` state and covered by conformance tests.

## S025 MeshVisual target

S025 Datoviz work uses retained `dvz_mesh` support after the S029 capability probe. The adapter
preserves the bounded review-pack slice for inline indexed 2D triangles, uniform RGBA, vertex RGBA,
DATA/View2D placement through native panel domains, and per-face RGBA adapted by vertex
duplication. It still emits structured unsupported reports for face scalar colors, normals, shading,
3D projection, and mesh query gaps. Public GSP fields must not expose Datoviz slot names, material
structs, helper geometry loaders, or draw calls.

For S036, `(N, 3)` `MeshVisual` inputs remain unsupported in the retained v0.4 adapter even though
the lower payload helper can format 3D positions. The adapter has no accepted public `View3D` camera
binding yet, so it rejects the public visual with `mesh3d_coordinate_space_unsupported` rather than
silently flattening z or exposing backend-native camera/draw-state names.
