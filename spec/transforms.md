# Transform, View, and Query Inverse - Accepted S027 Baseline

Status: accepted S027 baseline; protocol, Matplotlib reference behavior, Datoviz gates, VisPy2
producer API, and deterministic QA coverage are implemented. Public static `View3D` orthographic
semantics are defined separately by S036 in `spec/view3d.md`.

Semantic purpose: define deterministic 2D visual transforms, panel view state, and transformed
query/readback fields without accepting public 3D camera or controller semantics.

## Scope

S027 is 2D-first. It accepts:

| Concept | Status | Semantics |
|---|---:|---|
| `AffineTransform2DResource` | accepted | Named finite invertible 2D affine transform resource. |
| Inline affine transform | accepted | Small visual-local transform record for fixtures and producer convenience. |
| `TransformRef` | accepted | Reference to a named transform resource. |
| `VisualTransformBinding` | accepted | Optional transform binding on visuals with positional geometry. |
| `View2D` | accepted | Panel-level linear mapping from DATA coordinates to panel NDC. |
| Query inverse payload | accepted | Required for strict transformed query support. |
| 3D camera/projection/controller | partly advanced by S036 | Static orthographic `View3D` is accepted in `spec/view3d.md`; public 3D navigation/controller semantics remain deferred. |

`CoordinateSpace.DATA` and `CoordinateSpace.NDC` remain the only accepted public visual coordinate
spaces. Do not add `LOCAL`, `MODEL`, `WORLD`, `SCREEN`, `PIXEL`, `CAMERA`, `CLIP`, `AXES`, or
`FIGURE` as visual coordinate-space enum values in S027.

## Transform model

Accepted transform kinds:

| Kind | Status | Meaning |
|---|---:|---|
| `AFFINE_2D` | accepted | Finite invertible homogeneous 2D affine transform. |
| `AFFINE_3D` | reserved | Not accepted in S027; reject if requested. |

`AffineTransform2DResource` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `id` | protocol id | yes | Stable transform resource id. |
| `kind` | enum | yes | Must be `AFFINE_2D`. |
| `matrix` | 3x3 finite float | yes | Row-major homogeneous matrix applied to `[x, y, 1]^T`. |
| `label` | string | no | Debug metadata only. |
| `metadata` | mapping | no | Non-semantic extension/debug data if existing protocol style allows it. |

Matrix validation:

- shape is exactly 3x3;
- all values are finite;
- final row is exactly `[0, 0, 1]` within strict validation tolerance;
- upper-left 2x2 determinant is non-zero;
- strict inverse computations use float64.

Recommended diagnostics:

| Code | Meaning |
|---|---|
| `GSP_TRANSFORM_BAD_SHAPE` | Matrix is not 3x3. |
| `GSP_TRANSFORM_NONFINITE` | Matrix contains NaN or infinity. |
| `GSP_TRANSFORM_NON_AFFINE` | Final row is not `[0, 0, 1]`. |
| `GSP_TRANSFORM_SINGULAR` | Upper-left 2x2 matrix is not invertible. |
| `GSP_TRANSFORM_UNSUPPORTED_KIND` | Requested transform kind is not accepted. |
| `GSP_TRANSFORM_UNSUPPORTED_DIMENSION` | Requested transform dimension is not accepted. |

Inline affine transforms validate the same way as named resources. A fixture using an inline matrix
and one using a named transform resource with the same matrix must render and query equivalently.

## Transform order

For accepted visuals, the transform order is:

1. start from visual source/local positional coordinates;
2. apply the optional visual-local affine transform;
3. interpret the transformed coordinates in the visual's declared `CoordinateSpace`;
4. for DATA visuals, apply the panel `View2D` mapping to panel NDC;
5. for NDC visuals, skip `View2D`;
6. clip according to panel/view policy;
7. map panel NDC to framebuffer pixels and rasterize.

Visual transforms affect positions and geometry only. They do not change point or marker size, marker
stroke width, segment/path width, text font size, scalar color normalization, colorbar semantics, or
material attributes.

Family-specific rules:

| Visual family | Accepted transform effect |
|---|---|
| Point | Transform point centers only; size remains screen pixels. |
| Marker | Transform anchors only; size, stroke, glyph, and display/panel angle are unchanged. |
| Segment | Transform endpoints. |
| Path | Transform vertices. |
| Text | Transform anchors only; font size remains screen pixels and rotation remains display/panel angle. |
| Mesh | Transform strict 2D flat triangle vertices. |
| Image | Use existing axis-aligned `extent` plus `View2D`; arbitrary image model affine is deferred. |
| Colorbar/guide | Not transformed as data visuals; guides derive from view state. |

## View2D model

`View2D` fields:

| Field | Type | Required | Semantics |
|---|---|---:|---|
| `id` | protocol id | yes if named | Stable view id where the scene uses named views. |
| `kind` | enum | yes | Must be `VIEW2D_LINEAR`. |
| `xlim` | pair of finite floats | yes | DATA x range mapped linearly to panel NDC `[-1, +1]`. |
| `ylim` | pair of finite floats | yes | DATA y range mapped linearly to panel NDC `[-1, +1]`. |
| `clip` | bool | no | Default `true`. |

Reversed limits are valid and reverse that axis. Equal endpoints, non-finite values, log scales,
categorical/date/geospatial scales, equal-aspect constraints, fixed-aspect layout, and public
`View3D` are deferred or rejected.

Panel DATA mapping:

```text
ndc_x = -1 + 2 * (x - xlim[0]) / (xlim[1] - xlim[0])
ndc_y = -1 + 2 * (y - ylim[0]) / (ylim[1] - ylim[0])
```

Pan and zoom are represented as explicit `View2D` updates. S027 does not define mouse, keyboard,
gesture, wheel, inertia, linked-view, or controller event protocols.

Semantic axis guides, grids, labels, and data readouts consume `View2D` limits. Physical placement,
collision avoidance, margins, and publication styling are backend/layout policy.

## S028 guide/View2D integration

Semantic guides are not transformed as data visuals. They consume the panel `View2D` snapshot used
for the corresponding data render/query operation.

For a given axis guide:

- the guide domain is the matching `View2D` limit pair: `xlim` for x guides and `ylim` for y guides;
- reversed limits are valid and reverse the rendered axis direction;
- explicit tick values and labels pass through exactly, including values outside the current domain;
- deterministic auto ticks are resolved over the numeric interval spanned by the two finite limits,
  independent of whether the limits are increasing or reversed;
- rendered tick/grid positions are mapped through the original `View2D` limit pair, so a reversed
  axis displays the same tick values in the opposite panel direction;
- guide labels and panel titles are semantic guide state and are not public `TextVisual` objects;
- data readouts and guide query payloads must identify the same `View2D` snapshot used to render
  the data visuals and guides.

S028 does not add public log, nonlinear, categorical, date/time, geospatial, equal-aspect,
fixed-aspect, guide collision, automatic layout, 3D camera/projection, controller, gesture, or live
navigation semantics.

## Query inverse

Strict transformed query support uses extension payload kind `gsp.transform-query@0.1`.

Required fields:

- `visual_id`;
- `panel_xy` or framebuffer coordinate used for the query;
- `panel_ndc`;
- `declared_coordinate_space`;
- `declared_space_coord`;
- `source_coord` when the inverse transform is available;
- `data_coord` for DATA visuals;
- `transform_ids` or inline transform digest;
- `view_id` or view digest for DATA visuals;
- `inverse_status`;
- `diagnostics`.

Accepted `InverseStatus` values:

| Status | Meaning |
|---|---|
| `EXACT` | Inverse mapping follows S027 semantics within numeric tolerance. |
| `APPROXIMATE` | Approximate inverse with diagnostic; not strict unless a fixture allows it. |
| `UNSUPPORTED` | Backend cannot provide inverse coordinates. |
| `FAILED` | Backend should have provided inverse coordinates but failed. |
| `NOT_APPLICABLE` | Field does not apply, for example DATA coordinate for an NDC overlay. |
| `AMBIGUOUS` | Multiple inverse candidates exist and S027 does not define one unique coordinate. |

Recommended query diagnostics:

- `GSP_QUERY_INVERSE_UNSUPPORTED`;
- `GSP_QUERY_INVERSE_FAILED`;
- `GSP_QUERY_INVERSE_APPROXIMATE`;
- `GSP_QUERY_INVERSE_AMBIGUOUS`;
- `GSP_QUERY_INVERSE_MISSING_SOURCE`;
- `GSP_QUERY_VIEW_MISMATCH`;
- `GSP_QUERY_DEPTH_DEFERRED`.

## Capabilities and backend mapping

Capability discovery must describe semantic support and placement separately. Recommended placement
values are `GPU_BACKEND`, `CPU_ADAPTER`, `SERVER_SIDE`, `CLIENT_SIDE`, `MIXED`, and `UNSUPPORTED`.

Recommended capability names:

- `gsp.transform.affine2d@0.1`;
- `gsp.transform.inline-affine2d@0.1`;
- `gsp.view2d.linear@0.1`;
- `gsp.transform-query@0.1`;
- `gsp.transform.point@0.1`;
- `gsp.transform.marker@0.1`;
- `gsp.transform.segment@0.1`;
- `gsp.transform.path@0.1`;
- `gsp.transform.text@0.1`;
- `gsp.transform.mesh2d@0.1`;
- `gsp.transform.placement.<placement>@0.1`.

Matplotlib is the strict reference backend. It must implement named and inline affine transforms,
updates, `View2D`, reversed limits, DATA/NDC behavior, accepted visual-family transform rules, and
query inverse payloads for the strict 2D subset.

Datoviz support is capability-gated. It may use native backend transforms or explicit CPU adaptation
for finite eager arrays. CPU adaptation must be reported, must retain source coordinates for query
inverse when inverse support is claimed, and must not materialize virtual or huge sources silently.

VisPy2 may expose producer conveniences such as `affine2d(...)`, `transform=...`, and
`set_view2d(...)`, but it must emit GSP protocol records and must not expose Matplotlib transform
objects, Datoviz slots, shader handles, or backend-native camera objects.

## Visual QA plan

Required positive cases:

- identity, translate, scale, rotate, and shear affine transforms;
- named transform resource and inline transform equivalence;
- transform resource update across frames;
- `View2D` explicit limits and reversed x/y limits;
- DATA visuals transformed through `View2D`;
- NDC overlay visuals skipping `View2D`;
- point, marker, segment, path, text, and mesh2d family coverage;
- transformed query inverse reporting source/data/panel coordinates.

Required negative cases:

- bad matrix shape;
- non-finite matrix value;
- non-affine final row;
- singular transform;
- missing transform reference;
- requested 3D affine/camera/perspective projection;
- unsupported log/nonlinear view;
- equal-aspect request;
- arbitrary image affine transform;
- virtual-source CPU pretransform attempt;
- backend missing query inverse while claiming strict support;
- depth or 3D mesh query request.

## Explicit deferrals

Do not implement these as public S027 protocol semantics: transform stacks or graphs, arbitrary
chained nodes, backend-native transform objects, public `View3D`, public camera/projection/depth
semantics, orbit/pan/zoom controller events, interaction gestures, animation timelines, layout
engines, equal-aspect layout, nonlinear/log/category/date/geospatial transforms, unit conversion,
arbitrary Python callables, shader/material transforms, image rotation/skew/perspective, texture
coordinate transforms, instancing, remote renderer scheduling, huge distributed source transforms,
or hidden CPU materialization of virtual sources.

## S029/S034 resolved layout boundary

Resolved layout extends the S027/S028 boundary without changing `View2D` semantics. `View2D` remains
the deterministic data-domain state. `ResolvedLayoutSnapshot` records how that data domain maps into
logical pixels for one render target, including the plot rectangle, guide geometry, grid clipping,
and data-to-screen transform. Reversed `View2D` limits remain semantic view state and are represented
in the resolved transform.
