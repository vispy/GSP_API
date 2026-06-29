# Color Mapping and Colorbars - Accepted S026 Baseline

Status: accepted protocol baseline for S026; implementation pending.

Semantic purpose: map finite scalar values to canonical RGBA colors, share that mapping across
visuals, expose semantic colorbars, and support query/readback that reports both source scalar values
and displayed RGBA.

## Public model

S026 defines a small public scalar color system.

| Concept | Required | Semantics |
|---|---:|---|
| `ColorScale` | yes for scalar colors | Shared scalar-to-color mapping resource. |
| `ColorMapRef` | yes | Named canonical GSP colormap reference. |
| `LinearNormalize` | yes | Explicit finite linear `vmin`/`vmax` normalization with clipping. |
| `ScalarColorEncoding` | yes for scalar visual slots | Slot-specific scalar values linked to a `ColorScale`. |
| `ColorbarGuide` | optional | Semantic guide representing a `ColorScale` in a panel/view. |
| `ColorbarGuideStyle` | no | Canvas-pixel colorbar style hints shared by backend lowerings. |

`ColorScale` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `id` | protocol id | yes | Stable resource id. |
| `colormap` | `ColorMapRef` | yes | Accepted named canonical colormap. |
| `normalize` | `LinearNormalize` | yes | Explicit scalar-domain limits. |
| `description` | string | no | Optional metadata. ASCII required for strict text output. |

`ColorMapRef` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `kind` | enum | yes | S026 v1 accepts `named` only. |
| `id` | `ColorMapId` | yes | One accepted canonical colormap id. |

`LinearNormalize` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `kind` | enum | yes | S026 v1 accepts `linear` only. |
| `vmin` | finite float | yes | Lower scalar-domain limit. |
| `vmax` | finite float | yes | Upper scalar-domain limit; must be greater than `vmin`. |
| `clip` | bool | yes | Must be `true` in strict v1. |

`ScalarColorEncoding` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `slot` | enum | yes | Visual color slot being scalar-mapped. |
| `values` | finite float array | yes | Scalar values matching the visual item domain. |
| `color_scale_id` | protocol id | yes | References an existing `ColorScale`. |
| `alpha` | finite float in `[0, 1]` | no | Uniform alpha multiplier; default `1.0`. |
| `domain` | enum | no | Inferred from slot when omitted. |

`ColorbarGuide` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `id` | protocol id | yes | Stable guide id. |
| `panel_id` | protocol id | yes | Panel/view context where the guide belongs. |
| `color_scale_id` | protocol id | yes | Color scale represented by the colorbar. |
| `linked_visual_ids` | tuple of ids | no | Visuals using the same color scale. |
| `orientation` | enum | no | `vertical` or `horizontal`; default `vertical`. |
| `placement` | enum | no | `right`, `left`, `bottom`, or `top`; defaults by orientation. |
| `label` | string | no | Optional label. ASCII required for strict output. |
| `ticks` | finite float tuple | no | Explicit scalar-domain tick values. |
| `tick_labels` | tuple of strings | no | Same length as `ticks` when provided. |
| `style` | `ColorbarGuideStyle` | no | Explicit colorbar ramp/tick/gap sizing in canvas/reference pixels. |

`ColorbarGuideStyle` fields:

| Field | Type | Default | Semantics |
|---|---|---:|---|
| `ramp_width_px` | positive finite float | `36.0` | Color ramp thickness in canvas/reference pixels. |
| `tick_length_px` | positive finite float | `6.0` | Tick length in canvas/reference pixels. |
| `label_gap_px` | positive finite float | `6.0` | Gap between ramp/ticks and label in canvas/reference pixels. |
| `min_length_px` | positive finite float | `160.0` | Minimum ramp length in canvas/reference pixels. |
| `length_fraction` | positive finite float `<= 1` | `0.62` | Fraction of panel/canvas length used for the ramp. |

Colorbars are guides, not visuals. They are not Matplotlib axes, backend mappables, image ramps, or
layout objects in the public protocol.

## Colormap and normalization policy

Accepted `ColorMapId` values:

- `gray`;
- `viridis`;
- `magma`;
- `plasma`;
- `inferno`;
- `cividis`.

Each accepted colormap is defined by a canonical 256-entry RGBA uint8 LUT. The protocol meaning of a
named colormap is the GSP canonical LUT, not a backend registry entry.

Sampling rule:

```text
t_raw = (value - vmin) / (vmax - vmin)
t = clamp(t_raw, 0.0, 1.0)
lut_index = min(255, floor(t * 256))
rgba = canonical_lut[colormap_id][lut_index]
rgba.a = round(rgba.a * alpha)
```

For `gray`, the canonical LUT is equivalent to `lut[i] = [i, i, i, 255]` for `i` in `0..255`,
followed by the scalar encoding alpha multiplier.

Range classes:

- values below `vmin` are `under` and use LUT index `0`;
- values within `[vmin, vmax]` are `in_range`;
- values above `vmax` are `over` and use LUT index `255`.

Strict S026 scalar arrays must contain only finite values. NaN, masked arrays, `bad` colors, validity
masks, transparent missing-data rendering, custom under/over colors, colorbar extensions,
auto/percentile limits, and non-linear norms are deferred.

Protocol scenes must not contain auto normalization. Producers may expose convenience auto options
for eager arrays, but must resolve them to explicit `vmin`/`vmax` before emitting GSP.

## Visual-family integration

Strict v1 scalar slots:

| Visual | Slot | Scalar shape | Notes |
|---|---|---:|---|
| scalar `ImageVisual` | `image` / texel color | `(H, W)` | The image array owns source scalar values. |
| `PointVisual` | `color` | `(N,)` | Mutually exclusive with RGBA colors on the same slot. |
| `MarkerVisual` | `fill` | `(N,)` | Stroke remains existing RGBA. |

Capability-gated S026 slot:

| Visual | Slot | Scalar shape | Notes |
|---|---|---:|---|
| `MeshVisual` | `face_color` | `(F,)` | Strict 2D flat indexed triangles only. |

Deferred slots include marker stroke, segment/path stroke, text color, mesh vertex color, 3D scalar
mesh shading, and scalar interpolation across mesh faces.

Existing RGBA fields remain valid when scalar encoding is absent. RGBA and scalar encoding for the
same slot are mutually exclusive.

Existing scalar `ImageVisual(gray, clim)` scenes are compatibility-mapped to
`ColorScale(gray, LinearNormalize(vmin, vmax))`. New S026 scalar image scenes should use explicit
color scales.

## Query/readback semantics

Scalar-mapped visual hits use extension payload kind `gsp.scalar-color-query@0.1`.

Required scalar payload fields:

- `visual_id`;
- `item_kind`: `texel`, `point`, `marker`, or `face`;
- item identity such as texel coordinates, point index, marker index, or face index;
- `color_slot`: `image`, `color`, `fill`, or `face_color`;
- `color_scale_id`;
- `colormap_id`;
- `source_value`;
- `normalized_value_raw`;
- `normalized_value_clipped`;
- `range_class`: `under`, `in_range`, or `over`;
- `lut_index`;
- `displayed_rgba`.

Colorbar ramp query uses extension payload kind `gsp.colorbar-query@0.1` when supported. It reports
guide id, panel id, color scale id, orientation, scalar value, raw/clipped normalized values, range
class, LUT index, and displayed RGBA.

Displayed RGBA is required for strict scalar query conformance. Source scalar value is required when
the scalar array is owned by the visual or scalar encoding. Semantic query/readback may be computed
from GSP scene data; framebuffer readback is not the authority for scalar semantics.

## Backend mapping

Matplotlib is the strict reference backend for S026 scalar color behavior. It must use GSP canonical
LUTs, explicit linear normalization, clipping, scalar-domain colorbar ticks, and explicit tick labels
where provided. Matplotlib arbitrary colormap registries, auto locators/formatters, masked arrays,
`extend`, custom under/over/bad colors, and non-linear norms are not conformance behavior.

Datoviz support is capability-gated. CPU pre-mapping scalar values to RGBA is acceptable for finite
eager arrays if reported and if scalar source values remain available for query. CPU pre-mapping is
not acceptable for huge virtual data sources unless the virtual source explicitly provides such a
contract. GPU normalization and LUT upload are preferred but not required for protocol correctness.

Recommended capability names include:

- `gsp.scalar-color@0.1`;
- `gsp.colormap.named.<id>@0.1`;
- `gsp.colormap.lut-upload@0.1`;
- `gsp.normalize.linear.gpu@0.1`;
- `gsp.scalar-image.color-scale@0.1`;
- `gsp.point.scalar-color@0.1`;
- `gsp.marker.scalar-fill@0.1`;
- `gsp.mesh.face-scalar-color@0.1`;
- `gsp.colorbar-guide.render@0.1`;
- `gsp.scalar-query.source-value@0.1`;
- `gsp.scalar-query.normalized-value@0.1`;
- `gsp.scalar-query.displayed-rgba@0.1`;
- `gsp.colorbar-query@0.1`.

Diagnostics should cover unsupported colormap ids, approximated colormaps, missing LUT upload, GPU
normalization fallback, CPU pre-mapping, virtual-data pre-map rejection, unsupported scalar visual
families, unsupported colorbar rendering/query, unavailable scalar query fields, non-finite scalar
values, and invalid color scale domains.

## Visual QA plan

Required strict cases:

- scalar image gray with explicit clim;
- scalar image viridis with known LUT indices;
- point scalar colors;
- marker fill scalar colors;
- shared color scale across image/marker plus colorbar;
- colorbar guide with explicit ticks and labels;
- validation failures for unknown colormap, missing scale, non-finite value, `vmin >= vmax`, shape
  mismatch, and RGBA/scalar conflict.

Required query tests:

- scalar image texel query returns source value and displayed RGBA;
- point query returns point id and scalar payload;
- marker query returns marker id, fill slot, and scalar payload;
- out-of-range values report `under` or `over` with clipped endpoint color;
- colorbar ramp query returns scalar value where capability is enabled.

Optional/capability-gated cases include Datoviz LUT upload/GPU normalization, CPU pre-map diagnostics,
colorbar unsupported diagnostics, strict 2D mesh per-face scalar colors, and mesh face scalar query.

## Explicit deferrals

Do not implement these as public S026 protocol semantics: arbitrary backend colormap names, user LUT
resources, runtime colormap plugins, Matplotlib `ScalarMappable` or `Normalize` object graphs,
Datoviz shader APIs or slot names, auto/percentile clim, histogram equalization, log/symlog/power/
two-slope/boundary/categorical norms, NaN/masked/bad values, custom under/over colors, colorbar
extensions, automatic colorbar locator/formatter semantics, categorical palettes, legends, scalar
stroke colors, scalar text colors, marker scalar stroke, mesh vertex scalar colors, 3D scalar mesh
shading, scalar interpolation across mesh faces, volume transfer functions, remote dynamic
normalization, or distributed global min/max discovery.
