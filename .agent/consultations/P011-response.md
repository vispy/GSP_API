# Consultation Result: S026 Color Mapping and Colorbars

## Executive recommendation

S026 should define a **small public v1 scalar color system**, not a general Matplotlib-like color system. The first implementable slice should introduce canonical named colormaps, explicit linear normalization, scalar-to-RGBA encoding for scalar images and item-level point/marker colors, semantic colorbars linked to a color scale, and query/readback fields that report both source scalar values and displayed RGBA. This answers the uploaded S026 architecture request as a protocol baseline, not an implementation design. 

The recommended v1 scope is:

* Public strict v1:

  * `ColorScale`
  * canonical named `ColorMapId`
  * explicit `LinearNormalize`
  * `ScalarColorEncoding`
  * scalar color support for:

    * scalar `ImageVisual`
    * `PointVisual` color
    * `MarkerVisual` fill color
  * semantic `ColorbarGuide` with explicit ticks
  * scalar query/readback payload `gsp.scalar-color-query@0.1`

* Capability-gated within S026:

  * `MeshVisual` per-face scalar colors for strict 2D flat meshes
  * Datoviz GPU-side normalization
  * Datoviz canonical LUT upload
  * colorbar rendering in non-Matplotlib backends
  * scalar/colorbar query support where a backend cannot reconstruct source scalar values

* Deferred:

  * arbitrary Matplotlib colormap names
  * user-defined continuous transfer functions
  * categorical palettes and legends
  * log/symlog/power/two-slope/boundary norms
  * auto/percentile clim as protocol semantics
  * NaN/masked/bad color semantics
  * custom under/over colors
  * segment/path scalar strokes
  * mesh per-vertex scalar colors
  * volume/surface transfer functions
  * remote chunk-wise dynamic normalization

The durable architectural move is to make **color mapping a semantic protocol resource**, not a backend object, draw-call parameter, or Matplotlib `ScalarMappable` clone.

## Protocol contract draft

| Concept / field                      |                                    Type | Validation                                                                                                      | Default                                                                                         | Required?                                | Status                                         |
| ------------------------------------ | --------------------------------------: | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------- |
| `ColorScale`                         |           protocol resource / dataclass | stable `id`; immutable after scene submission unless scene update protocol explicitly replaces it               | none                                                                                            | required when scalar colors are used     | strict v1                                      |
| `ColorScale.id`                      |                      string protocol id | non-empty; unique in scene/session scope                                                                        | none                                                                                            | required                                 | strict v1                                      |
| `ColorScale.colormap`                |                           `ColorMapRef` | must reference accepted v1 colormap id                                                                          | `gray` only for legacy scalar image compatibility; otherwise explicit                           | required in new S026 scenes              | strict v1                                      |
| `ColorScale.normalize`               |                       `LinearNormalize` | finite `vmin`, `vmax`; `vmin < vmax`                                                                            | no implicit protocol default                                                                    | required in new S026 scenes              | strict v1                                      |
| `ColorScale.description`             |                                  string | optional ASCII text; Unicode capability-dependent as for text                                                   | none                                                                                            | optional                                 | strict v1 metadata                             |
| `ColorMapRef.kind`                   |                                    enum | v1 value: `"named"` only                                                                                        | `"named"`                                                                                       | required                                 | strict v1                                      |
| `ColorMapRef.id`                     |                             enum string | one of accepted canonical ids                                                                                   | none                                                                                            | required                                 | strict v1                                      |
| `ColorMapRef.lut_resource_id`        |                             resource id | not accepted in v1                                                                                              | none                                                                                            | no                                       | deferred                                       |
| `ColorMapRef.backend_name`           |                                  string | prohibited as public protocol semantics                                                                         | none                                                                                            | no                                       | deferred                                       |
| `LinearNormalize.kind`               |                                    enum | v1 value: `"linear"` only                                                                                       | `"linear"`                                                                                      | required                                 | strict v1                                      |
| `LinearNormalize.vmin`               |                                 float64 | finite                                                                                                          | none                                                                                            | required                                 | strict v1                                      |
| `LinearNormalize.vmax`               |                                 float64 | finite and greater than `vmin`                                                                                  | none                                                                                            | required                                 | strict v1                                      |
| `LinearNormalize.clip`               |                                    bool | v1 must be `true`; `false` rejected                                                                             | `true`                                                                                          | required or implicit                     | strict v1                                      |
| `LinearNormalize.auto`               |                             bool / enum | not accepted in protocol scenes                                                                                 | none                                                                                            | no                                       | producer convenience only                      |
| `ScalarColorEncoding`                |               visual field / attachment | references one visual color slot and one `ColorScale`                                                           | none                                                                                            | required when scalar colors replace RGBA | strict v1                                      |
| `ScalarColorEncoding.slot`           |                                    enum | allowed slots depend on visual family                                                                           | none                                                                                            | required                                 | strict v1                                      |
| `ScalarColorEncoding.values`         | NumPy array / sidecar array in fixtures | finite float32/float64; shape must match visual item domain                                                     | none                                                                                            | required                                 | strict v1                                      |
| `ScalarColorEncoding.color_scale_id` |                               string id | must reference existing `ColorScale`                                                                            | none                                                                                            | required                                 | strict v1                                      |
| `ScalarColorEncoding.alpha`          |                  float32/float64 scalar | finite, `0 <= alpha <= 1`                                                                                       | `1.0`                                                                                           | optional                                 | strict v1                                      |
| `ScalarColorEncoding.domain`         |                                    enum | `"item"`, `"texel"`, or `"face"` depending on visual                                                            | inferred from visual slot                                                                       | optional/internal                        | strict v1                                      |
| Existing RGBA color field            |              existing RGBA array/scalar | unchanged validation                                                                                            | existing defaults                                                                               | still valid                              | strict v1                                      |
| RGBA + scalar encoding on same slot  |                           conflict rule | rejected unless one is explicitly marked inactive by future update protocol                                     | none                                                                                            | no                                       | strict v1                                      |
| `ImageVisual.color_scale_id`         |                               string id | only valid for scalar `(H, W)` images                                                                           | legacy gray/clim adapter may synthesize                                                         | required for S026 scalar images          | strict v1                                      |
| `ImageVisual.scalar_encoding`        |      implicit texel-domain scalar image | scalar values are the image array itself                                                                        | none                                                                                            | required for scalar images               | strict v1                                      |
| `PointVisual.color_encoding`         |                   `ScalarColorEncoding` | slot must be `"color"`; values shape `(N,)`                                                                     | none                                                                                            | optional                                 | strict v1                                      |
| `MarkerVisual.fill_color_encoding`   |                   `ScalarColorEncoding` | slot must be `"fill"`; values shape `(N,)`                                                                      | none                                                                                            | optional                                 | strict v1                                      |
| `MarkerVisual.stroke_color_encoding` |                   `ScalarColorEncoding` | not accepted in v1                                                                                              | none                                                                                            | no                                       | deferred                                       |
| `MeshVisual.face_color_encoding`     |                   `ScalarColorEncoding` | values shape `(F,)`; only strict 2D indexed triangles                                                           | none                                                                                            | optional                                 | capability-gated                               |
| `MeshVisual.vertex_color_encoding`   |                   `ScalarColorEncoding` | not accepted in v1                                                                                              | none                                                                                            | no                                       | deferred                                       |
| `SegmentVisual.color_encoding`       |                   `ScalarColorEncoding` | not accepted in v1                                                                                              | none                                                                                            | no                                       | deferred                                       |
| `PathVisual.color_encoding`          |                   `ScalarColorEncoding` | not accepted in v1                                                                                              | none                                                                                            | no                                       | deferred                                       |
| `ColorbarGuide`                      |                            guide object | linked to panel/view and `ColorScale`; not an independent visual                                                | none                                                                                            | optional                                 | strict protocol v1; rendering capability-gated |
| `ColorbarGuide.id`                   |                      string protocol id | non-empty; unique among guides                                                                                  | none                                                                                            | required                                 | strict v1                                      |
| `ColorbarGuide.panel_id`             |                               string id | must reference existing panel/view context                                                                      | none                                                                                            | required                                 | strict v1                                      |
| `ColorbarGuide.color_scale_id`       |                               string id | must reference existing `ColorScale`                                                                            | none                                                                                            | required                                 | strict v1                                      |
| `ColorbarGuide.linked_visual_ids`    |                      list of visual ids | each id must reference a visual using the same color scale                                                      | empty list                                                                                      | optional                                 | strict v1 metadata                             |
| `ColorbarGuide.orientation`          |                                    enum | `"vertical"` or `"horizontal"`                                                                                  | `"vertical"`                                                                                    | optional                                 | strict v1                                      |
| `ColorbarGuide.placement`            |                                    enum | `"right"`, `"left"`, `"bottom"`, `"top"`                                                                        | `"right"` for vertical, `"bottom"` for horizontal                                               | optional                                 | strict v1                                      |
| `ColorbarGuide.label`                |                                  string | ASCII required; Unicode capability-dependent                                                                    | empty                                                                                           | optional                                 | strict v1                                      |
| `ColorbarGuide.ticks`                |                           array float64 | finite; each tick may lie outside range but renders at clipped endpoint unless renderer rejects with diagnostic | none                                                                                            | optional                                 | strict v1 when explicit                        |
| `ColorbarGuide.tick_labels`          |                             list string | same length as `ticks`; ASCII required                                                                          | canonical numeric formatting only if spec defines it; otherwise explicit labels required for QA | optional                                 | strict v1                                      |
| `ColorbarGuide.tick_policy="auto"`   |                                    enum | not accepted as protocol conformance behavior                                                                   | none                                                                                            | no                                       | producer convenience/deferred                  |
| `ColorbarGuide.extend`               |                                    enum | not accepted in v1                                                                                              | none                                                                                            | no                                       | deferred                                       |
| Colorbar query payload               |                           typed payload | only if backend/server supports guide query                                                                     | none                                                                                            | optional                                 | capability-gated                               |

## Colormap and normalization policy

S026 v1 should accept exactly these canonical colormap identifiers:

| Id        | Purpose                                        | Required strict behavior                     |
| --------- | ---------------------------------------------- | -------------------------------------------- |
| `gray`    | scalar image baseline and simple scalar fields | exact monotonic black-to-white canonical LUT |
| `viridis` | default scientific sequential colormap         | canonical committed LUT                      |
| `magma`   | scientific sequential colormap                 | canonical committed LUT                      |
| `plasma`  | scientific sequential colormap                 | canonical committed LUT                      |
| `inferno` | scientific sequential colormap                 | canonical committed LUT                      |
| `cividis` | color-vision-friendly sequential colormap      | canonical committed LUT                      |

The spec should commit a canonical **256-entry RGBA uint8 LUT** for every accepted colormap. The protocol meaning of `viridis` is therefore “the GSP canonical `viridis` table,” not “whatever the current backend calls viridis.”

Sampling rule:

```text
t_raw = (value - vmin) / (vmax - vmin)
t = clamp(t_raw, 0.0, 1.0)
lut_index = min(255, floor(t * 256))
rgba = canonical_lut[colormap_id][lut_index]
rgba.a = round(rgba.a * ScalarColorEncoding.alpha)
```

For `gray`, the canonical LUT should be equivalent to:

```text
lut[i] = [i, i, i, 255] for i in 0..255
```

with alpha then multiplied by the encoding alpha.

Normalization policy:

| Feature                           | S026 v1 decision                                  |
| --------------------------------- | ------------------------------------------------- |
| Linear clim                       | accepted                                          |
| Explicit `vmin`, `vmax`           | required in new S026 color scales                 |
| `vmin < vmax`                     | required                                          |
| Non-finite limits                 | rejected                                          |
| Auto clim                         | producer convenience only; not protocol semantics |
| Percentile clim                   | deferred                                          |
| Log norm                          | deferred                                          |
| Symlog norm                       | deferred                                          |
| Power/gamma norm                  | deferred                                          |
| Centered/two-slope diverging norm | deferred                                          |
| Boundary/discrete norm            | deferred                                          |
| Categorical norm                  | deferred                                          |
| Histogram equalization            | deferred                                          |
| Remote/chunk-wise dynamic norm    | deferred                                          |

Out-of-range behavior:

* Values below `vmin` are classified as `under` and displayed using the first LUT entry.
* Values above `vmax` are classified as `over` and displayed using the last LUT entry.
* No custom under/over colors in S026 v1.
* No triangular colorbar extensions in S026 v1.
* Query payloads may report `range_class = "under" | "in_range" | "over"`.

NaN and masked behavior:

* Strict S026 v1 scalar arrays must contain only finite values.
* NaN, masked arrays, `bad` colors, validity masks, and transparent missing-data rendering are deferred.
* If a producer accepts user NaNs, it must either reject before emitting GSP or convert to an explicit future extension; it must not silently map NaN to a backend-specific color.

Alpha behavior:

* Scalar values control color, not opacity.
* S026 v1 supports one uniform `alpha` multiplier per scalar color encoding.
* Per-item alpha combined with scalar color is deferred.
* Colormap LUT alpha is canonical, normally 255 for accepted v1 colormaps.
* Existing RGBA fields retain their existing alpha semantics when scalar encoding is not used.

Auto clim:

* Protocol scenes should not contain `auto`.
* VisPy2 may expose convenience options such as `clim=None` or `clim="auto"` for eager in-memory arrays.
* The producer must resolve such convenience into explicit `vmin`, `vmax` before sending GSP.
* The exact producer policy should be documented outside the protocol contract.
* For huge virtual data sources, automatic global clim is deferred unless provided explicitly by the data-source manifest.

## Visual-family integration

S026 should not make every visual family scalar-aware at once. It should add scalar color support only where the semantic item being colored is already unambiguous.

| Visual family                 | S026 v1 scalar support | Slot         | Scalar shape | Notes                                                                                                                         |
| ----------------------------- | ---------------------: | ------------ | ------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `ImageVisual` scalar `(H, W)` |                    yes | texel color  | `(H, W)`     | Replaces current gray-only scalar mapping with `ColorScale`; legacy `gray + clim` maps directly to `ColorScale(gray, linear)` |
| `ImageVisual` RGB/RGBA        |      no scalar mapping | none         | none         | Existing RGB/RGBA image semantics unchanged                                                                                   |
| `PointVisual`                 |                    yes | `color`      | `(N,)`       | Scalar value per point; mutually exclusive with RGBA color on same slot                                                       |
| `MarkerVisual`                |                    yes | `fill`       | `(N,)`       | Scalar value per marker fill; stroke remains existing RGBA                                                                    |
| `MarkerVisual` stroke         |                     no | none         | none         | Deferred to avoid slot explosion                                                                                              |
| `MeshVisual` per-face         |       capability-gated | `face_color` | `(F,)`       | Only for strict 2D flat indexed triangles; query aligns with accepted face-level query                                        |
| `MeshVisual` per-vertex       |                     no | none         | none         | Deferred due to interpolation, 3D, shading, and query ambiguity                                                               |
| `SegmentVisual`               |                     no | none         | none         | Deferred                                                                                                                      |
| `PathVisual`                  |                     no | none         | none         | Deferred                                                                                                                      |
| `TextVisual`                  |                     no | none         | none         | Deferred                                                                                                                      |

Scalar fields should **not replace existing RGBA fields globally**. They should coexist as alternative encodings for a specific visual color slot.

Recommended pattern:

```text
Either:
  visual.color = RGBA scalar/array

Or:
  visual.color_encoding = ScalarColorEncoding(
      slot="color",
      values=<float array>,
      color_scale_id=<ColorScale.id>,
      alpha=1.0,
  )

But not both for the same slot.
```

For `ImageVisual`, the scalar image array itself owns the source scalar values. For point/marker/mesh, the scalar encoding owns the scalar array. `ColorScale` owns only the mapping from scalar value to color; it does not own scalar data.

This separation is important for query/readback: the server must be able to report both the source value and the displayed RGBA without reverse-engineering colors.

## Colorbar and guide policy

Colorbars should be included in S026 v1 as **semantic guides**, not as visuals and not as layout objects.

A colorbar represents a `ColorScale` in a panel/view. It is not a rectangle mesh, not an image visual, not a Matplotlib axes object, and not a Datoviz shader artifact.

Minimal contract:

| Field               | Meaning                                                                              |
| ------------------- | ------------------------------------------------------------------------------------ |
| `id`                | Stable protocol id for the guide                                                     |
| `panel_id`          | Panel/view where the guide belongs                                                   |
| `color_scale_id`    | Color scale represented by the colorbar                                              |
| `linked_visual_ids` | Optional list of visuals using the color scale                                       |
| `orientation`       | `vertical` or `horizontal`                                                           |
| `placement`         | Semantic side: `right`, `left`, `bottom`, `top`                                      |
| `label`             | Optional text label                                                                  |
| `ticks`             | Optional explicit scalar tick values                                                 |
| `tick_labels`       | Optional explicit labels, same length as `ticks`                                     |
| `visible`           | Optional bool if guide visibility already exists in guide semantics; otherwise defer |

Strict v1 colorbar behavior:

* A colorbar is linked to a `ColorScale`, not directly to a backend mappable object.
* Multiple visuals may share one color scale and one colorbar.
* A visual may use a color scale without displaying a colorbar.
* Colorbar ticks are scalar-domain values, not normalized values.
* Explicit tick values are conformance-relevant.
* Explicit tick labels are preferred for visual QA.
* If tick labels are omitted, the spec must define a canonical numeric formatter before label rendering can be strict.
* Automatic tick selection is not protocol v1 semantics.
* Colorbar layout is semantic placement only; exact padding, size, and typography remain backend/layout policy unless later accepted.
* Colorbar labels reuse existing guide/text capability rules, including ASCII baseline and Unicode capability dependence.
* Colorbar query is optional/capability-gated, but the protocol should define its payload now.

Colorbars should interact with existing guide semantics as follows:

* Axis labels, titles, ticks, and grids remain view/panel guides.
* Colorbars are scalar-scale guides.
* They should live in the same guide namespace or a clearly parallel `guides` namespace, not in the visual list.
* They must have stable ids and be query-addressable if guide query capability is enabled.

## Query/readback semantics

Scalar/color-mapped visuals must preserve the existing unified panel-query model. The central rule is:

```text
Query returns what was semantically hit, the source scalar value if any,
the normalized/clipped scalar state, and the displayed RGBA.
```

Required scalar query payload for scalar-mapped visual hits:

```text
kind: "gsp.scalar-color-query@0.1"
visual_id: string
item_kind: "texel" | "point" | "marker" | "face"
item_id: int or structured item id
color_slot: "image" | "color" | "fill" | "face_color"
color_scale_id: string
colormap_id: string
source_value: float64
normalized_value_raw: float64
normalized_value_clipped: float64
range_class: "under" | "in_range" | "over"
lut_index: int
displayed_rgba: RGBA
```

Family-specific identity fields:

| Family                                     | Required identity fields                 |
| ------------------------------------------ | ---------------------------------------- |
| Scalar `ImageVisual`                       | `texel_x`, `texel_y`, source array value |
| `PointVisual`                              | `point_index`                            |
| `MarkerVisual`                             | `marker_index`                           |
| `MeshVisual` per-face scalar, if supported | `face_index`                             |

Existing image query payloads should be extended rather than replaced. For scalar images, source value remains the image texel value; `displayed_rgba` is the color-mapped value.

Colorbar query payload, capability-gated:

```text
kind: "gsp.colorbar-query@0.1"
guide_id: string
panel_id: string
color_scale_id: string
orientation: "vertical" | "horizontal"
scalar_value: float64
normalized_value_raw: float64
normalized_value_clipped: float64
range_class: "under" | "in_range" | "over"
lut_index: int
displayed_rgba: RGBA
```

Colorbar query semantics:

* Querying inside the colorbar ramp returns the scalar value represented at that panel coordinate.
* Querying a tick label may return guide/tick identity if guide-query support exists.
* Querying outside the ramp but inside colorbar layout decoration may return the guide id without scalar value.
* If a backend cannot map panel coordinates back into colorbar scalar coordinates, it must report query unsupported for colorbar guides.

Readback requirements:

* `displayed_rgba` is required for scalar-mapped visual hits in strict conformance.
* `source_value` is required when the scalar array is owned by the visual or scalar encoding.
* `normalized_value_raw`, `normalized_value_clipped`, `range_class`, and `lut_index` are required for S026 scalar query conformance.
* Backends may compute these server-side from protocol data; they do not need GPU readback if the semantic result is exact.
* Backend framebuffer color readback is not the authority for scalar semantics.

## Backend mapping guidance

### Matplotlib reference behavior

Matplotlib should be the reference/conformance backend for S026, but GSP should not expose Matplotlib `ScalarMappable`, `Normalize`, `Colormap`, `AxesImage`, or `Colorbar` objects as protocol concepts.

Matplotlib mapping should follow GSP semantics:

* Use the committed canonical 256-entry GSP LUTs.
* Use explicit linear normalization with clipping.
* Use scalar-domain tick values from `ColorbarGuide.ticks`.
* Use explicit `tick_labels` when provided.
* Render scalar `ImageVisual` through the image path, but with GSP color scale semantics.
* Render `PointVisual` and `MarkerVisual` scalar encodings by mapping scalar arrays to RGBA according to GSP rules before or during Matplotlib draw.
* Render `ColorbarGuide` from the linked `ColorScale`, not from an implicit Matplotlib mappable attached to an arbitrary artist.
* Query/readback should be computed from GSP scene data and panel geometry, not from Matplotlib internals where avoidable.

Conformance in Matplotlib:

| Behavior                                     | Conformance status |
| -------------------------------------------- | ------------------ |
| Canonical LUT color mapping                  | required           |
| Explicit linear clim                         | required           |
| Clipping to endpoint colors                  | required           |
| Scalar image rendering                       | required           |
| Point/marker scalar color rendering          | required           |
| Explicit colorbar ticks and labels           | required           |
| Query source scalar + displayed RGBA         | required           |
| Matplotlib auto ticks                        | not conformance    |
| Matplotlib arbitrary colormap registry       | not conformance    |
| Matplotlib masked array behavior             | not conformance    |
| Matplotlib `extend`, under, over, bad colors | not conformance    |
| Log/power/symlog/two-slope norms             | not conformance    |

### Datoviz capability-gated behavior

Datoviz support should be explicit and diagnostic-driven. There should be no hidden fallback that changes semantics without reporting.

Recommended capability flags:

| Capability                              | Meaning                                                     |
| --------------------------------------- | ----------------------------------------------------------- |
| `gsp.scalar-color@0.1`                  | backend understands S026 scalar color protocol              |
| `gsp.colormap.named.gray@0.1`           | exact or accepted-tolerance support for canonical `gray`    |
| `gsp.colormap.named.viridis@0.1`        | exact or accepted-tolerance support for canonical `viridis` |
| `gsp.colormap.named.magma@0.1`          | same for `magma`                                            |
| `gsp.colormap.named.plasma@0.1`         | same for `plasma`                                           |
| `gsp.colormap.named.inferno@0.1`        | same for `inferno`                                          |
| `gsp.colormap.named.cividis@0.1`        | same for `cividis`                                          |
| `gsp.colormap.lut-upload@0.1`           | backend can upload canonical LUTs internally                |
| `gsp.normalize.linear.gpu@0.1`          | backend can normalize scalar values on GPU                  |
| `gsp.scalar-image.color-scale@0.1`      | scalar image color mapping supported                        |
| `gsp.point.scalar-color@0.1`            | point scalar color supported                                |
| `gsp.marker.scalar-fill@0.1`            | marker fill scalar color supported                          |
| `gsp.mesh.face-scalar-color@0.1`        | strict 2D face scalar mesh color supported                  |
| `gsp.colorbar-guide.render@0.1`         | backend can render semantic colorbar guides                 |
| `gsp.scalar-query.source-value@0.1`     | backend/server can return source scalar value               |
| `gsp.scalar-query.normalized-value@0.1` | backend/server can return normalized scalar fields          |
| `gsp.scalar-query.displayed-rgba@0.1`   | backend/server can return displayed RGBA                    |
| `gsp.colorbar-query@0.1`                | backend/server can query colorbar ramp                      |

Required diagnostics:

| Diagnostic code                           | Severity                                       | Meaning                                                                   |
| ----------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------- |
| `unsupported_colormap_id`                 | fatal or deactivated                           | requested named colormap unavailable and no exact LUT adaptation exists   |
| `colormap_approximated`                   | warning or fatal depending on conformance mode | backend native colormap differs from canonical GSP LUT beyond strict path |
| `lut_upload_unsupported`                  | fatal or CPU adaptation                        | backend cannot upload canonical LUT                                       |
| `gpu_linear_normalize_unsupported`        | warning with adaptation                        | backend cannot normalize scalar values on GPU                             |
| `cpu_premap_scalar_to_rgba`               | info/warning                                   | server mapped scalar values to RGBA before sending backend colors         |
| `cpu_premap_not_allowed_for_virtual_data` | fatal                                          | huge/virtual source cannot be eagerly color-mapped                        |
| `scalar_visual_family_unsupported`        | deactivated/fatal                              | requested scalar slot unsupported                                         |
| `colorbar_render_unsupported`             | deactivated with diagnostic                    | colorbar guide accepted by protocol but not rendered                      |
| `scalar_query_source_unavailable`         | diagnostic                                     | backend cannot return source scalar for query                             |
| `scalar_query_normalized_unavailable`     | diagnostic                                     | backend cannot return normalized fields                                   |
| `colorbar_query_unsupported`              | diagnostic                                     | colorbar guide query unavailable                                          |
| `nonfinite_scalar_rejected`               | fatal validation                               | scalar array contains NaN/Inf                                             |
| `invalid_color_scale_domain`              | fatal validation                               | missing or invalid `vmin/vmax`                                            |

Datoviz adaptation policy:

* CPU pre-mapping scalar values to RGBA is acceptable for finite eager arrays if reported.
* CPU pre-mapping must retain the scalar source array server-side if query claims scalar readback support.
* CPU pre-mapping is not acceptable for huge virtual data sources unless the virtual source explicitly provides a finite color-mapped tile/buffer contract.
* GPU normalization is preferable but not required for protocol correctness.
* Backend-native shader names, slots, material structs, texture handles, and draw-call details must remain internal.

## Visual QA plan

Required strict QA cases:

1. **Scalar image gray, explicit clim**

   * Small deterministic `(H, W)` scalar image in NDC.
   * `ColorScale(gray, linear vmin/vmax)`.
   * Include values below, at, inside, and above clim.
   * Verify endpoint clipping and query payload.

2. **Scalar image viridis**

   * Small deterministic image with values mapping to known LUT indices.
   * Verify canonical displayed RGBA at selected texels.
   * Compare Matplotlib rendered output against stored contact-sheet reference within accepted tolerance.

3. **Point scalar colors**

   * NDC points with scalar values producing first, middle, and last LUT colors.
   * Query each point.
   * Verify `source_value`, normalized values, `range_class`, `lut_index`, and `displayed_rgba`.

4. **Marker fill scalar colors**

   * Markers with fixed shape, size, stroke RGBA, and scalar fill.
   * Verify scalar fill does not affect stroke color.
   * Query marker item identity and scalar payload.

5. **Shared color scale**

   * One `ColorScale` shared by scalar image and marker visual.
   * One colorbar linked to the same scale.
   * Verify all use the same `color_scale_id` and canonical LUT mapping.

6. **Colorbar guide with explicit ticks**

   * Vertical colorbar on right.
   * Explicit label and tick labels.
   * Verify Matplotlib reference layout at semantic level and contact sheet visually.
   * Query inside ramp if colorbar query is implemented.

7. **Validation failures**

   * Unknown colormap id.
   * Missing color scale.
   * Non-finite scalar value.
   * `vmin >= vmax`.
   * Shape mismatch between scalar values and visual item count.
   * RGBA and scalar encoding specified for same slot.

Required query tests:

* Scalar image texel query returns source value and displayed RGBA.
* Point query returns point id and scalar payload.
* Marker query returns marker id, fill slot, scalar payload.
* Out-of-range values return `under` or `over` with clipped endpoint color.
* Colorbar ramp query returns scalar value if capability is enabled.

Optional / capability-gated QA cases:

* Datoviz scalar image with canonical LUT upload.
* Datoviz point/marker scalar colors via GPU normalization.
* Datoviz CPU pre-mapped scalar adaptation with diagnostic.
* Colorbar unsupported diagnostic in Datoviz.
* Strict 2D `MeshVisual` per-face scalar colors.
* Mesh face query returning face id, source scalar, normalized value, and displayed RGBA.
* Backend colormap approximation report when native colormap differs from canonical LUT.

## Explicit deferrals

The following must not be implemented as public S026 protocol semantics:

* Arbitrary Matplotlib colormap names.
* Backend-native colormap registries.
* User-defined continuous colormap functions.
* Embedded user LUTs as public protocol resources.
* Runtime colormap plugins.
* Matplotlib `ScalarMappable` object semantics.
* Matplotlib `Normalize` object graph semantics.
* Datoviz shader APIs, slot names, material structs, or texture handles.
* Auto clim as protocol behavior.
* Percentile clim.
* Histogram equalization.
* Log, symlog, power/gamma, centered, two-slope, boundary, and categorical normalization.
* NaN, masked array, validity mask, and `bad` color semantics.
* Custom under/over colors.
* Colorbar `extend` triangles.
* Colorbar automatic locator/formatter semantics.
* Categorical palettes.
* Legends.
* Scalar stroke colors for segments and paths.
* Scalar text colors.
* Marker scalar stroke colors.
* Mesh per-vertex scalar colors.
* 3D scalar mesh shading semantics.
* Scalar interpolation across mesh faces.
* Materials, lighting, and texture transfer functions.
* Multi-channel scalar compositing.
* Volume rendering transfer functions.
* Tiled/remote image dynamic normalization.
* Distributed dataset global min/max discovery.
* Any behavior requiring network access or external colormap packages for conformance.

## Implementation mission sequence

1. **S026-ADR: accept the semantic boundary**

   * Convert this consultation into an ADR.
   * State accepted v1, capability-gated items, producer conveniences, and explicit deferrals.
   * Stop condition: if the ADR conflicts with PROJECT_CHARTER, ARCHITECTURE, accepted specs, or ADR-0015, stop and resolve the conflict before implementation.

2. **S026-SPEC-A: `ColorScale`, colormap ids, and linear normalization**

   * Define `ColorScale`, `ColorMapRef`, `LinearNormalize`, canonical LUTs, sampling rule, clipping rule, and validation.
   * Add canonical LUT fixtures to the spec/test data.
   * Update `SPEC_INDEX.md`.
   * Stop condition: no renderer work until validation tests pass for all accepted and rejected cases.

3. **S026-SPEC-B: scalar image migration**

   * Map existing scalar `ImageVisual(gray, clim)` semantics onto `ColorScale(gray, linear)`.
   * Require explicit color scale for new S026 scalar image scenes.
   * Keep RGB/RGBA image semantics unchanged.
   * Add Matplotlib reference behavior and scalar image query payload.
   * Stop condition: if existing ADR-0015 optional `clim` behavior cannot be reconciled deterministically, stop and record a compatibility decision.

4. **S026-SPEC-C: `ScalarColorEncoding` for `PointVisual` and `MarkerVisual`**

   * Add scalar encoding to point color and marker fill only.
   * Define mutual exclusion with RGBA on the same slot.
   * Add validation tests for shapes, finite values, alpha, and missing color scales.
   * Add query payload tests.
   * Stop condition: no segment/path/mesh vertex scalar work may enter this mission.

5. **S026-SPEC-D: `ColorbarGuide`**

   * Define colorbars as semantic guides linked to `ColorScale`.
   * Support orientation, placement, label, explicit ticks, and explicit tick labels.
   * Define interaction with existing guide namespace.
   * Add Matplotlib reference rendering.
   * Add guide/colorbar query payload as capability-gated.
   * Stop condition: if layout requirements expand beyond semantic placement, split advanced layout into a later guide/layout stage.

6. **S026-MPL: Matplotlib reference implementation**

   * Implement canonical LUT mapping.
   * Implement scalar image, point scalar color, marker fill scalar color, and colorbar guide.
   * Ensure query/readback is computed from GSP semantics.
   * Add visual QA contact sheets.
   * Stop condition: do not use Matplotlib behavior as a hidden protocol extension.

7. **S026-VISPY2: producer API updates**

   * Add bounded producer conveniences for scalar colors:

     * `imshow(..., cmap=..., clim=...)`
     * `scatter(..., color_values=..., cmap=..., clim=...)` or equivalent existing API naming
     * `markers(..., fill_values=..., cmap=..., clim=...)`
     * `colorbar(..., scale=..., label=..., ticks=..., tick_labels=...)`
   * Resolve any auto/default clim before emitting GSP.
   * Emit explicit `ColorScale` resources.
   * Stop condition: VisPy2 must target GSP semantics only, not Matplotlib or Datoviz-specific options.

8. **S026-DVZ: Datoviz capability report and adaptations**

   * Add structured capability discovery for scalar color features.
   * Implement exact LUT path where feasible.
   * Add CPU pre-map fallback for eager arrays if acceptable.
   * Emit diagnostics for unsupported colorbars, unsupported scalar slots, unavailable query payloads, and approximated colormaps.
   * Stop condition: no silent approximation; no eager CPU pre-map for huge virtual data.

9. **S026-MESH-FACE optional mission**

   * Only after image, point, marker, colorbar, query, and Matplotlib reference pass.
   * Add capability-gated per-face scalar colors for strict 2D `MeshVisual`.
   * Reuse `gsp.mesh-query@0.1` plus scalar payload.
   * Stop condition: if interpolation, vertex colors, 3D, normals, shading, or culling enter the discussion, defer.

10. **S026-QA and conformance lock**

* Build deterministic NDC contact sheets.
* Add scalar query/readback tests.
* Add unsupported/adaptation diagnostic tests.
* Add manual review notes.
* Stop condition: S026 is not accepted until Matplotlib reference and protocol validation agree on canonical RGBA for selected scalar values.

## Risks and review checklist

Key risks:

* Accidentally cloning Matplotlib’s color architecture instead of defining GSP semantics.
* Treating backend colormap names as protocol authority.
* Allowing implicit auto clim into conformance.
* Hiding Datoviz fallbacks or colormap approximations.
* Adding NaN/masked/under/over custom behavior before the scalar baseline is stable.
* Turning colorbars into visuals or layout objects too early.
* Expanding scalar color to all visual families before query semantics are clear.
* Losing source scalar values after CPU pre-mapping to RGBA.
* Making huge virtual datasets behave like eager NumPy arrays.

Review checklist:

* Every scalar-mapped visual references an explicit `ColorScale`.
* Every `ColorScale` has a canonical colormap id and explicit finite `vmin/vmax`.
* No protocol scene contains backend colormap names, Matplotlib objects, Datoviz handles, or shader concepts.
* RGBA and scalar encoding are mutually exclusive per color slot.
* Query returns both source scalar value and displayed RGBA for strict scalar visual hits.
* Out-of-range behavior is clipping, not custom under/over colors.
* NaN and masked arrays are rejected or deferred, not silently rendered.
* Colorbar ticks used in QA are explicit.
* Matplotlib reference uses GSP canonical LUTs, not version-dependent registry behavior.
* Datoviz unsupported behavior produces structured diagnostics.
* Auto clim exists only as producer-side convenience and is resolved before GSP emission.
* Segment/path scalar colors, categorical legends, log norms, and arbitrary LUTs remain out of S026.

