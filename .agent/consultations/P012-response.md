Consultation response for P012. 

## 1. Recommendation Summary

* **S027 should be a 2D-first transform/view/query-inverse stage.** Accept deterministic 2D affine visual-local/model transforms, deterministic linear `View2D`, and required query inverse/readout semantics.

* **Do not accept public 3D camera semantics in S027.** Reserve names and diagnostic/capability vocabulary for 3D camera/projection, but defer public `View3D`, `Camera`, `Projection`, depth, perspective, orbit controls, and 3D mesh query semantics.

* **Keep `CoordinateSpace.NDC` and `CoordinateSpace.DATA` stable.** Do not add new public visual coordinate-space enum values in S027. Instead, define transform stages around existing spaces: source/local coordinates, declared visual coordinate space, panel NDC, and framebuffer pixels.

* **Add one narrow transform resource: affine 2D.** Public transform resources should support only finite, invertible homogeneous 2D affine matrices. No transform graph, no stack, no nonlinear transforms, no shader/material transforms.

* **Allow both named transform resources and small inline visual transforms.** Named resources are canonical for retained scenes and updates; inline transforms are allowed for fixtures, simple scenes, and producer convenience.

* **Define `View2D` as panel-level deterministic state.** `View2D` maps DATA coordinates to panel NDC using explicit linear `xlim`/`ylim`. Pan and zoom are represented as updates to `View2D`, not as protocol-level controller events.

* **Query inverse is part of S027, not deferred.** Transformed query results must report panel coordinates, visual declared-space coordinates, source/local coordinates when invertible, data coordinates when applicable, transform chain identity, and inverse diagnostics.

* **Semantic guides derive from `View2D`.** Axis ticks, grids, labels, and data readouts must use `View2D` limits. Physical guide layout, collision avoidance, margins, and publication styling remain backend/layout policy.

* **Matplotlib is the strict reference backend.** It must implement the accepted 2D affine/view/query-inverse subset exactly enough for conformance images and query JSON.

* **Datoviz may satisfy S027 through native GPU transforms or explicit CPU/server-side adaptation.** CPU pre-transforming finite eager arrays is acceptable only if reported as an adaptation. Virtual/huge sources must not be silently materialized.

* **Capability discovery must describe semantic support and placement separately.** Placement may be GPU, CPU adapter, server-side, client-side, or mixed, but placement must not change semantic results.

* **Stop immediately on conflicts between existing code/backend behavior and accepted specs.** Do not invent third semantics from Matplotlib, Datoviz, or current source code behavior.

---

## 2. Accepted S027 Scope

| Concept                      |        Include in S027? | Public protocol shape                                                                                                                                  | Why / notes                                                                                                                                                                              |
| ---------------------------- | ----------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Transform resources          |                     Yes | `AffineTransform2DResource` with stable id and finite invertible 3×3 homogeneous matrix                                                                | Needed for mesh-local transforms, reusable transforms, retained scenes, replay, and resource updates. Keep to affine 2D only.                                                            |
| Inline visual transforms     |                     Yes | Optional `VisualTransformBinding` on visuals, containing either `TransformRef` or inline affine 2D matrix                                              | Useful for fixtures and simple producer APIs. Named resources remain preferred for updates and sharing.                                                                                  |
| Transform stack / graph      |                      No | Explicitly deferred                                                                                                                                    | A stack/graph would invite arbitrary composition, cycles, placement ambiguity, and Matplotlib-object leakage. S027 has at most one visual-local/model transform plus one panel `View2D`. |
| Source/data transforms       |  No, except terminology | Deferred protocol stage                                                                                                                                | Huge/virtual data-source transforms need their own source semantics. Do not materialize virtual data to satisfy S027.                                                                    |
| Attribute transforms         |             No new work | Existing color/size/scalar semantics remain                                                                                                            | S026 color-scale semantics are independent. S027 transforms positions/geometry only, not scalar normalization, sizes, strokes, or material attributes.                                   |
| Visual-local/model transform |                     Yes | Optional affine 2D transform applied to visual source/local positional coordinates before interpreting them in the visual’s declared `CoordinateSpace` | This is the durable minimal path for mesh-local transforms and reusable positioned glyph/geometry scenes.                                                                                |
| View2D                       |                     Yes | Panel-level `View2D` resource or inline panel property with `xlim`, `ylim`, linear mapping, clipping policy                                            | This is the core S027 view contract.                                                                                                                                                     |
| View3D / camera              |            No public v1 | Reserved names and capability/diagnostic vocabulary only                                                                                               | 3D requires depth, projection, clipping, face/mesh query, camera controls, and lighting/material decisions. Defer.                                                                       |
| Projection                   |            No public v1 | Implicit fixed 2D linear projection only                                                                                                               | Do not add `Projection` enum except possibly an internal/reserved `VIEW2D_LINEAR` name.                                                                                                  |
| Controller/navigation state  | No public controller v1 | Pan/zoom represented as explicit `View2D` updates                                                                                                      | Deterministic state first. Event systems, controllers, gestures, inertia, linked views, and live interaction belong later.                                                               |
| Query inverse                |                     Yes | Required transformed-query payload and diagnostics                                                                                                     | Query/readback is first-class; S027 must define how coordinates are reported after transforms.                                                                                           |
| Guide interaction            |                     Yes | Axis/grid/tick semantics consume `View2D`; titles/panel text/colorbars remain mostly independent                                                       | Enough to align axes/readouts with transformed data scenes. Avoid full layout engine.                                                                                                    |
| Transform capabilities       |                     Yes | Capability records for affine 2D, View2D, visual-family support, query inverse, placement, and adaptation                                              | Required to prevent hidden Datoviz/remote fallback approximations.                                                                                                                       |
| Image affine transforms      |               Mostly no | Existing `ImageVisual.extent` + `View2D` only; arbitrary image model affine deferred                                                                   | Rotated/skewed images require textured-quad semantics and texel inverse rules. Axis-aligned extents already cover the accepted image case.                                               |
| 2D mesh-local transform      |                     Yes | Affine 2D visual transform on strict flat indexed triangles                                                                                            | Directly unblocks local mesh placement without accepting 3D camera/material semantics.                                                                                                   |
| Z/depth semantics            |                      No | Preserve source z for query if present; no accepted depth ordering or perspective semantics                                                            | Avoid accidental 3D acceptance. Strict S027 rendering/query is x/y 2D.                                                                                                                   |

---

## 3. Protocol Model

### 3.1 Enums

#### `CoordinateSpace`

Existing enum remains stable:

| Value  | S027 meaning                                                                                                                                                |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATA` | After optional visual-local/model transform, positional coordinates are in the panel’s data coordinate system and are mapped through `View2D` to panel NDC. |
| `NDC`  | After optional visual-local/model transform, positional coordinates are already in panel normalized device coordinates. `View2D` is not applied.            |

No new public `CoordinateSpace` values in S027.

Do **not** add `LOCAL`, `MODEL`, `WORLD`, `SCREEN`, `PIXEL`, `AXES`, `FIGURE`, `CLIP`, or `CAMERA` as public visual coordinate-space values in S027. These may appear as explanatory transform stages or query field names, not as accepted visual-space enum values.

---

#### `TransformKind`

| Value                                             |      Include? | Meaning                                                                            |
| ------------------------------------------------- | ------------: | ---------------------------------------------------------------------------------- |
| `AFFINE_2D`                                       |           Yes | Finite invertible 2D affine transform represented by a homogeneous 3×3 matrix.     |
| `AFFINE_3D`                                       | Reserved only | Not accepted in S027. Fatal diagnostic if used without explicit future capability. |
| `NONLINEAR`                                       |            No | Deferred.                                                                          |
| `LOG`, `CRS`, `CATEGORICAL`, `SHADER`, `MATERIAL` |            No | Explicit non-goals.                                                                |

---

#### `ViewKind`

| Value                                |      Include? | Meaning                                                         |
| ------------------------------------ | ------------: | --------------------------------------------------------------- |
| `VIEW2D_LINEAR`                      |           Yes | Deterministic linear mapping from DATA x/y limits to panel NDC. |
| `VIEW3D_CAMERA`                      | Reserved only | Not accepted in S027.                                           |
| `POLAR`, `LOG`, `GEO`, `CATEGORICAL` |            No | Deferred.                                                       |

---

#### `TransformPlacement`

This is **capability/reporting vocabulary**, not scene semantics.

| Value         | Meaning                                                                              |
| ------------- | ------------------------------------------------------------------------------------ |
| `GPU_BACKEND` | Backend applies transform natively on GPU or equivalent retained renderer path.      |
| `CPU_ADAPTER` | Adapter pre-transforms finite eager data before handing it to backend.               |
| `SERVER_SIDE` | Remote/server implementation applies transform before rendering or query.            |
| `CLIENT_SIDE` | Producer/client applies transform before sending data. Must be explicit, not hidden. |
| `MIXED`       | Different accepted visual families or operations use different placements.           |
| `UNSUPPORTED` | Backend cannot support requested transform semantics.                                |

Placement must not affect rendered/query semantics except through declared numeric tolerance.

---

#### `InverseStatus`

| Value            | Meaning                                                                                                                              |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `EXACT`          | Inverse mapping was performed according to accepted S027 semantics. Floating-point tolerance is allowed.                             |
| `APPROXIMATE`    | Backend produced an approximate inverse and emitted a diagnostic. Not strict-conformance unless explicitly allowed for that fixture. |
| `UNSUPPORTED`    | Backend rendered or accepted the visual but cannot provide inverse coordinates.                                                      |
| `FAILED`         | Inverse should have been available but failed for this query.                                                                        |
| `NOT_APPLICABLE` | Field does not apply, e.g. `data_coord` for pure NDC overlay visual.                                                                 |
| `AMBIGUOUS`      | Multiple inverse candidates exist and S027 does not define a unique continuous coordinate.                                           |

---

### 3.2 `AffineTransform2DResource`

Public named transform resource.

| Field      | Required? | Default                                                                                         | Validation / semantics                                                                      |
| ---------- | --------: | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `id`       |       Yes | None                                                                                            | Stable protocol id. Unique within scene/session resource namespace.                         |
| `kind`     |       Yes | `AFFINE_2D`                                                                                     | No other accepted kind in S027.                                                             |
| `matrix`   |       Yes | Identity only if explicitly omitted by producer convenience API, not by wire/protocol dataclass | 3×3 finite numeric matrix, row-major serialization, applied to column vector `[x, y, 1]^T`. |
| `label`    |        No | None                                                                                            | Debugging only; not semantic.                                                               |
| `metadata` |        No | Empty                                                                                           | Non-semantic extension/debug field only if existing protocol style allows it.               |

Matrix convention:

* Serialized as row-major 3×3.

* Applied as:

  `x' = m00*x + m01*y + m02`

  `y' = m10*x + m11*y + m12`

  `w' = m20*x + m21*y + m22`

* S027 accepts only affine matrices where the final row is `[0, 0, 1]`.

* All values must be finite.

* The upper-left 2×2 determinant must be non-zero.

* Strict reference inverse is computed in float64.

* Singular transforms are invalid for S027 strict semantics.

Recommended validation diagnostic codes:

| Code                             | Meaning                                  |
| -------------------------------- | ---------------------------------------- |
| `GSP_TRANSFORM_BAD_SHAPE`        | Matrix is not 3×3.                       |
| `GSP_TRANSFORM_NONFINITE`        | Matrix contains NaN or infinity.         |
| `GSP_TRANSFORM_NON_AFFINE`       | Final row is not `[0, 0, 1]`.            |
| `GSP_TRANSFORM_SINGULAR`         | Upper-left 2×2 matrix is not invertible. |
| `GSP_TRANSFORM_UNSUPPORTED_KIND` | Transform kind is not accepted.          |

---

### 3.3 `InlineAffineTransform2D`

Allowed only where the protocol already allows inline nested records.

| Field    | Required? | Default                                             | Validation / semantics             |
| -------- | --------: | --------------------------------------------------- | ---------------------------------- |
| `kind`   |       Yes | `AFFINE_2D`                                         | Same as resource.                  |
| `matrix` |       Yes | Identity if omitted only in high-level producer API | Same validation as named resource. |

Inline transforms must canonicalize to the same semantic object as named resources. A fixture using an inline matrix and a fixture using a named transform resource with the same matrix must render and query equivalently.

---

### 3.4 `TransformRef`

Reference to named resource.

| Field      | Required? | Default | Validation / semantics                                                                                                                                                                                       |
| ---------- | --------: | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`       |       Yes | None    | Must resolve to an accepted transform resource in the current scene/session at frame execution.                                                                                                              |
| `required` |        No | `true`  | If true, unsupported transform semantics reject or deactivate the visual according to existing fatal-diagnostic policy. If false, backend may deactivate with diagnostic if project adaptation rules permit. |

Do not include backend handles, Matplotlib transform objects, Datoviz slot names, shader names, memory addresses, or resource pointers.

---

### 3.5 `VisualTransformBinding`

Optional field on public visuals that have positional geometry.

| Field        | Required? | Default             | Validation / semantics                                                                                                                                                   |
| ------------ | --------: | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`      |        No | Identity            | Either `TransformRef` or `InlineAffineTransform2D`.                                                                                                                      |
| `applies_to` |        No | `POSITION_GEOMETRY` | S027 has only one accepted value. It transforms positional coordinates only.                                                                                             |
| `dimension`  |        No | `2`                 | S027 accepts only 2D x/y transform. Existing z coordinate, if present, is preserved for source/query reporting but is not used for S027 view/projection/depth semantics. |

Accepted visual-family behavior:

| Visual family                       | S027 transform behavior                                                                                                                                                                               |
| ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PointVisual`                       | Transform point centers only. Sizes remain logical screen-pixel diameters.                                                                                                                            |
| `MarkerVisual`                      | Transform marker anchor positions only. Marker size, stroke width, and marker glyph geometry remain screen-pixel semantics. Existing marker angle remains display/panel angle, not model-transformed. |
| `SegmentVisual`                     | Transform endpoint positions. Stroke width remains screen pixels.                                                                                                                                     |
| `PathVisual`                        | Transform path vertices. Stroke width, cap, join, and miter semantics remain screen/panel stroke semantics.                                                                                           |
| `TextVisual`                        | Transform text anchor positions only. Font size remains screen pixels. Existing text rotation remains display/panel rotation unless a future spec says otherwise.                                     |
| `MeshVisual`                        | Transform 2D flat triangle vertices for strict S025 mesh subset. Face identity and face-level query remain stable.                                                                                    |
| `ImageVisual`                       | No arbitrary model affine in S027. Use existing `extent`, `origin`, interpolation, and `View2D`. Axis-aligned extent translation/scale is already expressible by changing extent.                     |
| `ColorbarGuide`, axes, panel guides | Not transformed as visuals by S027 visual-local transform. They consume view/color-scale semantics separately.                                                                                        |

Validation:

* Transform is applied before `CoordinateSpace` mapping to panel NDC.
* For `coordinate_space=DATA`, transformed x/y are DATA coordinates.
* For `coordinate_space=NDC`, transformed x/y are panel NDC coordinates.
* Transform does not apply to sizes, stroke widths, font sizes, scalar values, colors, materials, texture coordinates, or query payload values.
* 3D affine, perspective, nonlinear, log, CRS, categorical, or shader transforms are fatal unsupported cases.

---

### 3.6 `View2D`

Panel-level deterministic data-to-panel mapping.

| Field           |                                             Required? | Default                                   | Validation / semantics                                                                                       |
| --------------- | ----------------------------------------------------: | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `id`            | Yes for resource form; optional for inline panel form | None                                      | Stable id if referenced.                                                                                     |
| `kind`          |                                                   Yes | `VIEW2D_LINEAR`                           | Only accepted S027 view kind.                                                                                |
| `xlim`          |                                                   Yes | `[-1, 1]` for implicit compatibility view | Two finite numbers. Values must not be equal. Reversed limits are allowed and mean inverted x axis.          |
| `ylim`          |                                                   Yes | `[-1, 1]` for implicit compatibility view | Two finite numbers. Values must not be equal. Reversed limits are allowed and mean inverted y axis.          |
| `clip`          |                                                    No | `true`                                    | DATA and NDC contributions are clipped to the panel viewport unless existing visual semantics say otherwise. |
| `aspect_policy` |                                                    No | `INDEPENDENT_XY`                          | S027 strict behavior maps x and y independently. Equal aspect is deferred.                                   |
| `scale_x`       |                                                    No | `LINEAR`                                  | Only linear accepted.                                                                                        |
| `scale_y`       |                                                    No | `LINEAR`                                  | Only linear accepted.                                                                                        |
| `label_x`       |                                                    No | None                                      | Optional semantic axis label source for guide defaults.                                                      |
| `label_y`       |                                                    No | None                                      | Optional semantic axis label source for guide defaults.                                                      |

Mapping:

* `x = xlim[0]` maps to panel NDC `-1`.
* `x = xlim[1]` maps to panel NDC `+1`.
* `y = ylim[0]` maps to panel NDC `-1`.
* `y = ylim[1]` maps to panel NDC `+1`.
* Reversed limits invert the corresponding axis.
* No automatic padding, autoscale, aspect correction, margins, or layout adjustment is part of S027 strict semantics.

Recommended diagnostic codes:

| Code                            | Meaning                                            |
| ------------------------------- | -------------------------------------------------- |
| `GSP_VIEW2D_INVALID_LIMITS`     | Limits are non-finite or zero-span.                |
| `GSP_VIEW2D_UNSUPPORTED_SCALE`  | Nonlinear/log/categorical scale requested.         |
| `GSP_VIEW2D_ASPECT_UNSUPPORTED` | Equal/fixed/aspect-constrained behavior requested. |
| `GSP_VIEW2D_UNSUPPORTED_KIND`   | View kind is not accepted.                         |

---

### 3.7 `PanelViewBinding`

Panel or subplot-level binding to a view.

| Field      |             Required? | Default                                                                                    | Validation / semantics               |
| ---------- | --------------------: | ------------------------------------------------------------------------------------------ | ------------------------------------ |
| `panel_id` |                   Yes | None                                                                                       | Existing panel id.                   |
| `view`     |                    No | Implicit `View2D([-1, 1], [-1, 1])` if DATA visuals exist and no explicit view is provided | Inline `View2D` or `ViewRef`.        |
| `view_ref` | Alternative to `view` | None                                                                                       | Must resolve to a `View2D` resource. |

Rules:

* A panel may have at most one accepted S027 `View2D`.
* DATA visuals in that panel use that `View2D`.
* NDC visuals in that panel do not use that `View2D`.
* Multiple panels may reference the same `View2D` resource.
* Updating a `View2D` resource is the accepted representation of pan/zoom/navigation state in S027.

---

### 3.8 `TransformCapability`

Capability record exposed by server/backend.

| Field                                | Meaning                                                                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| `supports_transform_resources`       | Backend accepts named affine 2D resources.                                                                              |
| `supports_inline_visual_transforms`  | Backend accepts inline affine 2D transforms on visuals.                                                                 |
| `supported_transform_kinds`          | Must include only `AFFINE_2D` for S027 strict support.                                                                  |
| `supported_visual_families`          | Per-family support for point, marker, segment, path, text-anchor, mesh2d, image extent-only.                            |
| `supports_view2d_linear`             | Backend supports deterministic `View2D` mapping.                                                                        |
| `supports_query_inverse2d`           | Backend can report required inverse/readout fields.                                                                     |
| `placements`                         | Per visual family and operation: `GPU_BACKEND`, `CPU_ADAPTER`, `SERVER_SIDE`, `CLIENT_SIDE`, `MIXED`, or `UNSUPPORTED`. |
| `max_eager_items_for_cpu_adaptation` | Optional explicit bound if CPU pre-transforming is used.                                                                |
| `supports_virtual_source_transform`  | Must be false in S027 unless a future source-transform spec exists.                                                     |
| `unsupported_diagnostics`            | Structured list of unsupported cases and diagnostic codes.                                                              |

Capability names should be versioned, for example:

* `gsp.transform.affine2d.resource@0.1`
* `gsp.transform.affine2d.inline@0.1`
* `gsp.view2d.linear@0.1`
* `gsp.query.inverse2d@0.1`
* `gsp.visual-transform.point.affine2d@0.1`
* `gsp.visual-transform.marker.affine2d@0.1`
* `gsp.visual-transform.segment.affine2d@0.1`
* `gsp.visual-transform.path.affine2d@0.1`
* `gsp.visual-transform.text-anchor.affine2d@0.1`
* `gsp.visual-transform.mesh2d.affine2d@0.1`
* `gsp.transform.placement.gpu-backend@0.1`
* `gsp.transform.placement.cpu-adapter@0.1`
* `gsp.camera3d.deferred@0.1` as an explicit negative/reserved capability marker, not support.

---

## 4. Coordinate Spaces And Transform Order

### 4.1 Accepted coordinate spaces

S027 accepts only the existing public visual coordinate spaces:

| Space  | Meaning                                                                                                                                    |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `DATA` | Visual positional coordinates, after optional model transform, are interpreted in panel data coordinates and mapped through `View2D`.      |
| `NDC`  | Visual positional coordinates, after optional model transform, are interpreted directly as panel NDC coordinates in `[-1, +1]` convention. |

S027 defines the following **stages** but does not add them as public `CoordinateSpace` enum values:

| Stage                        | Meaning                                                                                                                                              |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Source/local coordinate      | The coordinate stored in the visual’s position/vertex/anchor array before optional visual transform.                                                 |
| Declared visual coordinate   | The coordinate after optional visual-local/model transform, interpreted as either DATA or NDC according to the visual’s existing `coordinate_space`. |
| Data coordinate              | Coordinate in the panel data system. Exists for DATA visuals and for inverse readout of a `View2D` query.                                            |
| Panel NDC coordinate         | Coordinate in panel-local normalized device coordinates.                                                                                             |
| Framebuffer pixel coordinate | Backend/output pixel coordinate. Required for rendering internally; optional for query reports unless existing query input uses pixels.              |

---

### 4.2 Transform order

For accepted S027 visuals:

1. **Source/local positional data**

   The visual provides positions, vertices, anchors, endpoints, or mesh vertices.

2. **Optional visual-local/model affine 2D transform**

   Apply `VisualTransformBinding.model` to x/y coordinates.

   * If no transform is provided, identity is used.
   * z, if present, is preserved as source metadata but is not used for S027 projection or depth.
   * Sizes, stroke widths, text font sizes, colors, scalar values, marker glyph geometry, and material properties are not transformed.

3. **Declared visual coordinate-space interpretation**

   * If `coordinate_space=DATA`, transformed x/y are DATA coordinates.
   * If `coordinate_space=NDC`, transformed x/y are panel NDC coordinates.

4. **Panel view transform**

   * DATA visuals: apply panel `View2D`.
   * NDC visuals: skip `View2D`.

5. **Panel clipping**

   Clip to panel viewport if `View2D.clip=true` or equivalent panel clipping is active.

6. **Framebuffer mapping**

   Convert panel NDC to backend framebuffer pixels using panel viewport. This is backend/session infrastructure, not a visual semantic transform.

7. **Rasterization/composition**

   Existing visual-family rules apply. Stroke widths, marker sizes, font sizes, and point diameters remain logical screen pixels.

---

### 4.3 Existing `NDC` and `DATA` mapping

Existing scenes remain valid:

* A visual with `coordinate_space=NDC` and no transform behaves exactly as before.
* A visual with `coordinate_space=DATA` and no explicit view uses the compatibility default `View2D(xlim=[-1, 1], ylim=[-1, 1])` unless the project chooses to require explicit views in new fixtures.
* Visual QA fixtures should use explicit `View2D` even when limits are `[-1, 1]`.

Important compatibility rule:

* Existing deterministic NDC fixtures over `[-1, +1]` must not become data-view fixtures accidentally.
* NDC overlays are unaffected by pan/zoom/view-limit changes.

---

### 4.4 Query inverse/readout mapping

For a DATA visual:

1. Start with query panel coordinate.
2. Convert to panel NDC if necessary.
3. Invert `View2D` to obtain DATA coordinate.
4. Hit-test according to visual-family semantics.
5. For the winning contribution, invert the visual-local/model transform to obtain source/local coordinate, when meaningful.
6. Report visual identity, item/face/texel id, data coordinate, source/local coordinate, panel coordinate, displayed RGBA, and transform inverse status.

For an NDC visual:

1. Start with query panel coordinate.
2. Convert to panel NDC if necessary.
3. Hit-test according to visual-family semantics.
4. If a visual-local/model transform exists, invert it to obtain source/local coordinate.
5. Report no DATA coordinate unless an extension explicitly defines one.

For item-level visuals such as points, markers, and text:

* The source/local coordinate may be the anchor/center coordinate of the hit item.
* A continuous local offset is optional.
* Query should not invent continuous glyph/marker interior coordinates unless accepted by that visual-family spec.

For mesh/path/segment visuals:

* Source/local coordinate should be reported when inverse mapping is meaningful.
* Mesh strict query remains face-level. Barycentric coordinates may be optional extension data, not required S027 core.

---

## 5. Query/Readback Semantics

S027 should add a transform/view query payload, for example:

`gsp.transform-query@0.1`

### 5.1 Required query fields for transformed visual hits

| Field                                       |                                Required? | Meaning                                                                                                                                                 |
| ------------------------------------------- | ---------------------------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `panel_id`                                  |                                      Yes | Panel queried.                                                                                                                                          |
| `query_panel_coord`                         |                                      Yes | Query coordinate in the accepted panel-query input convention.                                                                                          |
| `query_panel_ndc`                           |                                      Yes | Query coordinate converted to panel NDC.                                                                                                                |
| `visual_id`                                 |                                      Yes | Stable visual id of winning contribution.                                                                                                               |
| `visual_family`                             |                                      Yes | Visual family name.                                                                                                                                     |
| `coordinate_space`                          |                                      Yes | Visual’s declared `CoordinateSpace`: `DATA` or `NDC`.                                                                                                   |
| `view_id`                                   |                Required for DATA visuals | `View2D` used for DATA-to-panel mapping. `null` / not applicable for NDC visuals.                                                                       |
| `data_coord`                                |                Required for DATA visuals | Data coordinate corresponding to the query/hit after inverse `View2D`.                                                                                  |
| `declared_space_coord`                      |                                      Yes | Coordinate after model transform, in the visual’s declared space. For DATA visuals, same coordinate system as `data_coord`; for NDC visuals, panel NDC. |
| `source_coord`                              |  Required when invertible and meaningful | Source/local coordinate before visual-local/model transform.                                                                                            |
| `transform_ids`                             |                                      Yes | Ordered ids of transform resources used. Empty for identity/no named transform. Inline transforms may report a stable digest or `inline`.               |
| `inverse_status`                            |                                      Yes | `EXACT`, `APPROXIMATE`, `UNSUPPORTED`, `FAILED`, `NOT_APPLICABLE`, or `AMBIGUOUS`.                                                                      |
| `displayed_rgba`                            | Yes if existing visual query supports it | Final displayed color/readout under existing query semantics.                                                                                           |
| `item_id` / `face_id` / `texel` / family id |               According to visual family | Existing query identity fields remain authoritative.                                                                                                    |
| `diagnostics`                               |                         Yes if not exact | Structured diagnostics for unsupported/approximate/failed inverse.                                                                                      |

### 5.2 Optional query fields

| Field                     | Meaning                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `framebuffer_px_coord`    | Pixel coordinate in target framebuffer or captured image.                                  |
| `source_z`                | Preserved z value if source positions have three components. Not a depth semantic in S027. |
| `depth_ndc`               | Optional only if backend has explicit future depth capability. Not strict S027.            |
| `draw_order_index`        | Scene/visual/item order used to resolve topmost hit in strict 2D. Recommended.             |
| `local_offset_px`         | For marker/text/point hit testing, offset from item anchor in screen pixels.               |
| `barycentric`             | Optional mesh extension payload.                                                           |
| `transform_matrix_digest` | Stable digest for inline transform or resolved resource version.                           |
| `view_limits`             | Echo of `View2D` limits used for query; useful for replay/debug.                           |

### 5.3 Query inverse diagnostics

Recommended diagnostic codes:

| Code                                 | Severity                             | Meaning                                                                        |
| ------------------------------------ | ------------------------------------ | ------------------------------------------------------------------------------ |
| `GSP_QUERY_INVERSE_UNSUPPORTED`      | Non-fatal or fatal depending fixture | Backend cannot provide inverse coordinates for this accepted visual/transform. |
| `GSP_QUERY_INVERSE_FAILED`           | Fatal for strict conformance         | Backend should have been able to invert but failed.                            |
| `GSP_QUERY_INVERSE_APPROXIMATE`      | Warning                              | Backend reports approximate inverse. Not strict unless fixture allows.         |
| `GSP_QUERY_INVERSE_AMBIGUOUS`        | Warning/error                        | Multiple inverse candidates exist and no unique coordinate is defined.         |
| `GSP_QUERY_TRANSFORM_MISSING_SOURCE` | Error                                | Backend discarded source/local coordinates required for readout.               |
| `GSP_QUERY_VIEW_MISMATCH`            | Error                                | Query result used a different view state than the rendered frame.              |
| `GSP_QUERY_DEPTH_DEFERRED`           | Warning/error                        | Query requested z/depth ordering not accepted in S027.                         |

### 5.4 Winner selection and ordering

Strict S027 query should use the existing unified panel-query model: “what rendered scene contribution is under this panel coordinate?”

For S027 2D fixtures:

* Winner is the topmost rendered contribution under accepted scene/visual ordering.
* No new depth buffer semantics are accepted.
* z values do not define ordering in S027.
* If alpha blending already has accepted behavior for a visual family, query should follow that family’s existing displayed-color/readout rules.
* Otherwise, report the topmost accepted contribution and include `draw_order_index` when available.

---

## 6. Backend Requirements

### 6.1 Matplotlib strict reference requirements

Matplotlib must implement the complete S027 strict subset.

Required:

* Named affine 2D transform resources.
* Inline affine 2D visual transforms.
* Transform updates applied at deterministic frame boundaries.
* `View2D` linear mapping with explicit `xlim`/`ylim`.
* Reversed x/y limits.
* DATA visuals transformed through `View2D`.
* NDC visuals independent of `View2D`.
* Visual-family support for:

  * point centers;
  * marker anchors;
  * segment endpoints;
  * path vertices;
  * text anchors;
  * strict 2D mesh vertices.
* Screen-pixel semantics preserved for:

  * point sizes;
  * marker sizes;
  * marker stroke widths;
  * segment/path stroke widths;
  * text font sizes.
* Text rotation remains display/panel rotation; model transform affects anchor only.
* Axis/grid/tick guide semantics derive from `View2D`.
* Query inverse for accepted visual families and transform subset.
* Structured diagnostics for unsupported image affine, nonlinear transforms, 3D cameras, projection, aspect constraints, and controller state.

Matplotlib may use its native transform stack internally, but public protocol behavior must not expose or depend on Matplotlib object graphs.

Strict reference tolerances should be specified:

* Transform and inverse numeric comparisons in float64 with explicit absolute/relative tolerance.
* Visual QA image tolerance separate from coordinate-query tolerance.
* Query coordinates should be checked numerically, not by screenshots alone.

Matplotlib must reject or fatal-diagnose:

* 3D camera/projection requests.
* Nonlinear/log/categorical/geospatial transforms.
* Arbitrary image affine transforms.
* Singular transforms.
* Transform stacks/graphs.
* Equal-aspect constraints if not accepted by S027.
* Controller/event-system requests.

---

### 6.2 Datoviz capability-gated requirements

Datoviz must not silently approximate S027 semantics.

It may claim S027 support only for combinations it can actually render and query with declared diagnostics.

Allowed implementation placements:

| Placement                          |                               Allowed? | Conditions                                                                                                                                      |
| ---------------------------------- | -------------------------------------: | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Native GPU/backend transform       |                                    Yes | Must preserve accepted semantics and query inverse.                                                                                             |
| Adapter CPU pre-transform          |                                    Yes | Only for finite eager arrays within declared bounds. Must report `CPU_ADAPTER` placement/adaptation. Must retain source data for query inverse. |
| Server-side transform              |     Yes for remote Datoviz-like server | Must be explicit capability placement.                                                                                                          |
| Client-side producer pre-transform | Only if producer explicitly chooses it | Must not be hidden backend fallback.                                                                                                            |
| Virtual source materialization     |                                     No | Do not eagerly materialize huge/virtual datasets to satisfy transform support.                                                                  |

Datoviz should be allowed to:

* Accept finite eager point/marker/segment/path/mesh2d transforms via CPU pre-transform if native transform slots are unavailable.
* Use Datoviz panel/domain controls to implement `View2D` where exact.
* Map NDC-only fixtures through an internal `[-1, +1]` data-domain panel only when semantics are equivalent and diagnostic/capability reporting is clear.
* Deactivate transformed query support with structured diagnostics if runtime bindings cannot return required hit/readback data.
* Reject transform support for a visual family independently from rendering that visual without transform.

Datoviz must reject or fatal-diagnose:

| Case                                                  | Recommended code                              |
| ----------------------------------------------------- | --------------------------------------------- |
| 3D camera/projection                                  | `GSP_CAMERA3D_DEFERRED`                       |
| 3D affine/model transform                             | `GSP_TRANSFORM_UNSUPPORTED_DIMENSION`         |
| Nonlinear/log/CRS/categorical transform               | `GSP_TRANSFORM_UNSUPPORTED_KIND`              |
| Arbitrary image affine transform                      | `GSP_TRANSFORM_IMAGE_AFFINE_DEFERRED`         |
| Query inverse unavailable after accepted transform    | `GSP_QUERY_INVERSE_UNSUPPORTED`               |
| CPU adaptation would exceed declared finite bounds    | `GSP_TRANSFORM_CPU_ADAPTATION_LIMIT_EXCEEDED` |
| Virtual source would require eager materialization    | `GSP_TRANSFORM_VIRTUAL_SOURCE_DEFERRED`       |
| Backend native view cannot match `View2D` exactly     | `GSP_VIEW2D_BACKEND_MISMATCH`                 |
| Mixed DATA/NDC layering cannot be represented exactly | `GSP_VIEW2D_NDC_LAYERING_UNSUPPORTED`         |

Datoviz capability reports should distinguish:

* rendering support;
* query support;
* capture support;
* inverse-readout support;
* placement;
* maximum finite eager adaptation size;
* visual-family support.

---

### 6.3 Remote/web renderer behavior

Remote and web renderers must implement the same semantic contract.

Required:

* Capability discovery before scene submission.
* Explicit support or rejection of affine 2D resources, inline transforms, `View2D`, and query inverse.
* Transform resources and view state included in replay/debug fixtures independent of transport encoding.
* Query inverse performed against the same scene/view/transform snapshot as the rendered frame.
* No assumption that JSON/base64 is mandatory for local or remote operation.
* For virtual data sources, transforms may be server-side only if declared and if source semantics allow it.

Remote renderers may:

* Apply transforms server-side.
* Cache transform resources.
* Compile transform resources into backend-native pipelines.
* Return approximate query inverse only with explicit non-strict diagnostic.

Remote renderers must not:

* Change semantic results because of transport.
* Hide server-side simplification.
* Apply client-side eager materialization to virtual/huge datasets unless the data-source spec explicitly allows it.
* Report Matplotlib/Datoviz-native transform object names as public protocol fields.

---

## 7. VisPy2 Producer API

VisPy2 should expose S027 through small semantic APIs, not backend-native transform objects.

Recommended minimal shape:

### 7.1 View API

* `panel.set_view2d(xlim=(x0, x1), ylim=(y0, y1))`
* `panel.view2d(...)` as constructor/update helper if that matches existing style.
* `plot.set_xlim(...)`, `plot.set_ylim(...)`, or existing guide/view-limit helpers may delegate to `View2D`.
* `pan` and `zoom` helpers may exist, but they must produce explicit `View2D` updates.

Do not expose:

* Matplotlib `Transform`, `Axes.transData`, `transAxes`, etc.
* Datoviz camera/arcball/panzoom internals.
* Event-controller state as public protocol state.

---

### 7.2 Transform API

Recommended:

* `scene.affine2d(matrix=..., id=None)`
* Convenience constructors:

  * `scene.translate2d(tx, ty)`
  * `scene.scale2d(sx, sy, center=None)`
  * `scene.rotate2d(theta, center=None)`
* Visual creation accepts:

  * `transform=...`
  * `coordinate_space="data"` or `"ndc"` using existing mapping.

Examples of intended semantics, not implementation code:

* `scatter(x, y, transform=t, coordinate_space="data")` means source x/y are transformed by `t` into DATA coordinates, then mapped through `View2D`.
* `text(labels, pos, transform=t)` means anchors are transformed; font size and text rotation remain screen/panel semantics.
* `mesh(vertices, faces, transform=t)` means strict 2D mesh vertices are transformed before DATA/NDC mapping.

Do not expose:

* Transform stacks.
* Arbitrary callable transforms.
* Nonlinear/log transforms.
* CRS/geospatial transforms.
* Shader/material transforms.
* 3D camera APIs as accepted S027 behavior.

---

### 7.3 Query API

VisPy2 query results should expose accepted fields using stable semantic names:

* `result.panel_coord`
* `result.panel_ndc`
* `result.data_coord`
* `result.source_coord`
* `result.coordinate_space`
* `result.transform_ids`
* `result.inverse_status`
* existing family-specific fields: `item_id`, `face_id`, `texel`, `value`, `displayed_rgba`

If inverse is unsupported, VisPy2 should surface backend diagnostics rather than filling coordinates with guessed values.

---

### 7.4 Guide API

Existing semantic guide methods should bind to `View2D`:

* view limits drive ticks/grid;
* labels/title remain semantic guide fields;
* colorbars remain tied to `ColorScale`;
* guide layout remains backend policy unless explicit placement already exists in accepted specs.

---

## 8. Visual QA And Conformance Fixtures

### 8.1 Positive deterministic fixtures

| Fixture                          | Purpose                                               | Expected artifact/report behavior                                                                                      |
| -------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `view2d_identity_points`         | DATA points with `View2D([-1,1],[-1,1])`              | Same visual placement as previous NDC-style baseline where data equals NDC. Query returns matching data/source coords. |
| `view2d_pan_zoom_points`         | DATA points under non-default x/y limits              | Render shifts/scales deterministically. Query inverse returns original data/source coords.                             |
| `ndc_overlay_ignores_view2d`     | Mix DATA visual and NDC overlay, then change `View2D` | DATA visual changes; NDC overlay remains fixed in panel.                                                               |
| `affine2d_translate_points`      | Point center model transform                          | Rendered centers translated; sizes unchanged. Query source coord differs from data coord by inverse translation.       |
| `affine2d_scale_segments`        | Segment endpoints transformed                         | Endpoint positions scale; stroke width remains screen pixels.                                                          |
| `affine2d_rotate_path`           | Path vertices rotated around origin                   | Geometry rotates; path width/cap/join remain screen semantics.                                                         |
| `text_anchor_transform`          | Text anchor transformed                               | Anchor moves; font size unchanged; text rotation remains display/panel rotation.                                       |
| `mesh2d_affine_face_query`       | Strict 2D mesh transformed                            | Face renders in transformed position; query returns face id and inverse source coordinate/readout.                     |
| `reversed_xlim_ylim`             | Inverted axes                                         | Data-to-panel mapping reverses deterministically; guides/ticks reflect reversed limits.                                |
| `guide_ticks_follow_view2d`      | Axis/grid guide with changed view limits              | Tick/grid positions derive from `View2D`; labels/title unaffected except normal guide behavior.                        |
| `resource_vs_inline_equivalence` | Same matrix inline and named resource                 | Render/query outputs equivalent within tolerance.                                                                      |
| `transform_resource_update`      | Update named transform between frames                 | New frame reflects updated transform; query report uses updated transform id/version/digest.                           |
| `clip_after_view_transform`      | Geometry outside view after transform                 | Clipped to panel; query outside clipped contribution returns no hit or lower contribution.                             |
| `mixed_visual_family_transform`  | Point/path/text/mesh in same panel                    | Each family applies accepted transform to positions only; sizes/text remain screen pixels.                             |

---

### 8.2 Negative validation fixtures

| Fixture                                   | Expected result                                                                                       |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `transform_bad_shape_2x3`                 | Fatal validation diagnostic `GSP_TRANSFORM_BAD_SHAPE`.                                                |
| `transform_nonfinite_nan`                 | Fatal validation diagnostic `GSP_TRANSFORM_NONFINITE`.                                                |
| `transform_non_affine_perspective_row`    | Fatal validation diagnostic `GSP_TRANSFORM_NON_AFFINE`.                                               |
| `transform_singular_zero_scale`           | Fatal validation diagnostic `GSP_TRANSFORM_SINGULAR`.                                                 |
| `transform_missing_ref`                   | Fatal unresolved-resource diagnostic.                                                                 |
| `transform_3d_affine_requested`           | Rejected with `GSP_TRANSFORM_UNSUPPORTED_DIMENSION`.                                                  |
| `camera3d_requested`                      | Rejected/deactivated with `GSP_CAMERA3D_DEFERRED`.                                                    |
| `projection_perspective_requested`        | Rejected with projection/camera deferred diagnostic.                                                  |
| `view2d_log_scale_requested`              | Rejected with `GSP_VIEW2D_UNSUPPORTED_SCALE`.                                                         |
| `view2d_equal_aspect_requested`           | Rejected or deactivated with `GSP_VIEW2D_ASPECT_UNSUPPORTED` unless a later spec accepts it.          |
| `image_rotate_affine_requested`           | Rejected with `GSP_TRANSFORM_IMAGE_AFFINE_DEFERRED`.                                                  |
| `query_inverse_backend_missing`           | Non-strict failure report with `GSP_QUERY_INVERSE_UNSUPPORTED`. Strict backend must fail conformance. |
| `virtual_source_cpu_pretransform_attempt` | Rejected with `GSP_TRANSFORM_VIRTUAL_SOURCE_DEFERRED`.                                                |
| `z_depth_order_requested`                 | Rejected/deactivated with `GSP_QUERY_DEPTH_DEFERRED` or `GSP_Z_DEPTH_DEFERRED`.                       |

---

### 8.3 Required conformance artifacts

Each positive fixture should produce:

* scene/protocol fixture;
* Matplotlib reference image;
* query input points;
* expected query JSON;
* expected diagnostic JSON, usually empty;
* replay result.

Each negative fixture should produce:

* invalid or unsupported scene fixture;
* expected structured diagnostic;
* no silent fallback rendering unless explicitly marked as an adaptation fixture.

Datoviz-specific QA should produce:

* capability report;
* adaptation report;
* rendered capture where supported;
* query report where supported;
* unsupported report where not supported.

---

## 9. ADR/Spec Updates

Recommended files:

| File                                                               | Purpose                                                                                                                        |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `docs/specs/S027_transform_view_query_inverse.md`                  | Main accepted S027 spec. Defines scope, transform order, `View2D`, query inverse, capability semantics, diagnostics, fixtures. |
| `docs/specs/protocol/transforms_v0_1.md`                           | Protocol dataclasses/enums for `AffineTransform2DResource`, `TransformRef`, `VisualTransformBinding`, validation rules.        |
| `docs/specs/protocol/views_v0_1.md`                                | `View2D`, panel binding, linear data-to-panel mapping, clipping, guide relationship.                                           |
| `docs/specs/protocol/query_inverse_v0_1.md`                        | Required transformed-query fields, inverse statuses, family-specific readout rules.                                            |
| `docs/specs/protocol/transform_capabilities_v0_1.md`               | Capability names, placement vocabulary, adaptation reporting, diagnostic codes.                                                |
| `docs/adr/ADR_S027_2D_FIRST_TRANSFORMS.md`                         | Decision: S027 accepts 2D affine + View2D only; defers 3D camera/projection/controllers.                                       |
| `docs/adr/ADR_S027_TRANSFORM_RESOURCES_NOT_BACKEND_OBJECTS.md`     | Decision: public transforms are protocol resources, not Matplotlib/Datoviz/native objects.                                     |
| `docs/adr/ADR_S027_VIEW_STATE_NOT_CONTROLLER_STATE.md`             | Decision: pan/zoom represented as deterministic `View2D` updates; event/controller systems deferred.                           |
| `docs/adr/ADR_S027_QUERY_INVERSE_REQUIRED.md`                      | Decision: query inverse/readout is required for strict support.                                                                |
| `docs/specs/matplotlib_reference/S027_transform_view_reference.md` | Matplotlib strict behavior, tolerances, guide/query mapping, unsupported cases.                                                |
| `docs/specs/datoviz/S027_transform_capability_gates.md`            | Datoviz native/adapted/deactivated/rejected behavior, CPU pre-transform bounds, diagnostics.                                   |
| `docs/specs/vispy2/S027_transform_view_api.md`                     | Minimal VisPy2 API surface and forbidden backend leaks.                                                                        |
| `docs/specs/qa/S027_visual_qa_fixtures.md`                         | Positive/negative fixture inventory and expected artifacts.                                                                    |
| `docs/SPEC_INDEX.md`                                               | Add S027 specs and status.                                                                                                     |
| `docs/ARCHITECTURE.md`                                             | Update layered transform/view/query semantics without replacing accepted architecture.                                         |
| `.agent/consultations/P012-response.md`                            | Store this consultation response.                                                                                              |
| `.agent/tasks/S027.md` or equivalent stage task file               | Convert accepted spec into mission plan.                                                                                       |

---

## 10. Mission Breakdown

| Mission | Title                                | Goal                                                         | Deliverables                                                                                        | Acceptance                                                                                   | Stop Conditions                                                                                         |
| ------- | ------------------------------------ | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| M099    | S027 ADR scope lock                  | Convert consultation into accepted architectural decisions   | ADRs for 2D-first scope, transform resources, deterministic view state, query inverse               | ADRs accepted; S027 explicitly defers 3D camera/projection/controllers                       | Any maintainer decision to include public 3D camera in S027 before 2D query semantics are locked        |
| M100    | Transform protocol dataclasses/enums | Add conceptual protocol objects for affine 2D transforms     | `AffineTransform2DResource`, `TransformRef`, `VisualTransformBinding`, `TransformKind`, diagnostics | Validation tests pass for identity, translate, scale, rotate, bad shape, nonfinite, singular | Existing code already exposes incompatible public transform semantics; stop and report                  |
| M101    | View2D protocol dataclasses/enums    | Add deterministic panel `View2D` model                       | `View2D`, panel binding/ref handling, `ViewKind`, view diagnostics                                  | Tests pass for default, explicit limits, reversed limits, invalid limits                     | Existing guide/view-limit API has incompatible authority-level semantics                                |
| M102    | Transform/view validation fixtures   | Establish positive and negative schema fixtures              | Fixture files and validation expected results                                                       | All negative fixtures emit exact structured diagnostics                                      | Any unsupported case silently accepted without diagnostic                                               |
| M103    | Matplotlib reference rendering       | Implement strict S027 reference rendering                    | Matplotlib mapping for DATA/NDC, affine visual transforms, View2D, clipping                         | Positive render fixtures match expected images within tolerance                              | Matplotlib cannot implement a required S027 semantic without copying backend object model into protocol |
| M104    | Matplotlib query inverse             | Implement strict query/readback inverse in reference backend | Query payload `gsp.transform-query@0.1`, source/data/panel coords, inverse status                   | Query JSON matches expected values for point/path/segment/text/mesh2d fixtures               | Query result cannot be tied to same transform/view snapshot as render                                   |
| M105    | Guide/View2D integration             | Bind semantic guides to deterministic view state             | Axis/tick/grid behavior using `View2D`; guide fixtures                                              | Ticks/grid/readouts reflect view limits, including reversed axes                             | Existing guide spec conflicts with `View2D` semantics                                                   |
| M106    | Datoviz capability audit             | Determine native/adapted S027 subset                         | Capability report, evidence notes, unsupported matrix                                               | Clear accepted/simplified/deactivated/rejected behavior per visual family                    | Datoviz behavior cannot be verified with current bindings                                               |
| M107    | Datoviz gates and adaptation         | Add structured Datoviz support without hidden fallback       | Runtime gates, CPU pre-transform path if bounded, diagnostics                                       | Datoviz emits explicit placement/adaptation reports; no virtual eager materialization        | Required Datoviz fallback would silently change semantics or materialize huge sources                   |
| M108    | VisPy2 producer API                  | Expose minimal transform/view controls                       | `set_view2d`, affine constructors, visual `transform=` support, query fields                        | Producer emits accepted GSP protocol only; no Matplotlib/Datoviz object leakage              | Existing public VisPy2 API forces incompatible transform semantics                                      |
| M109    | Visual QA fixtures                   | Add deterministic visual QA for S027                         | Positive/negative render/query fixtures and expected artifacts                                      | Matplotlib strict baseline passes; Datoviz produces support/adaptation/unsupported reports   | Fixture requires non-goal behavior such as equal aspect, image rotation, or camera                      |
| M110    | Replay and fixture schema update     | Ensure transport-independent replay of transforms/views      | Debug JSON/replay schema additions for transform resources and `View2D`                             | Replay reproduces render/query artifacts independent of encoding path                        | Replay schema requires JSON/base64 for local in-process semantics                                       |
| M111    | Documentation/examples               | Document accepted S027 behavior                              | User/developer docs, examples for transformed scatter/path/mesh2d and pan/zoom via view updates     | Examples are minimal, deterministic, and match specs                                         | Docs imply 3D camera, arbitrary transforms, or controller support                                       |
| M112    | S027 closeout and conflict audit     | Close stage only after specs/tests/backend reports align     | Updated SPEC_INDEX, ARCHITECTURE notes, legacy map, closeout report                                 | All accepted artifacts present; unsupported backend behavior structured                      | Any unresolved contradiction between accepted specs, ADRs, and implementation                           |

---

## 11. Non-Goals And Boundaries

S027 must not implement or publicly define:

* General transform stacks or transform graphs.
* Arbitrary chained transform nodes.
* Matplotlib transform-object exposure.
* Datoviz slot/shader/private transform exposure.
* 3D camera, orbit camera, perspective camera, orthographic 3D camera, frustum, clipping planes, depth buffers, or 3D mesh query semantics.
* Public `View3D`.
* Public `Projection` semantics beyond implicit 2D linear view mapping.
* Controller state, event systems, mouse/keyboard gestures, wheel zoom semantics, drag interaction, inertia, linked brushing, or live navigation protocols.
* Animation timelines, keyframes, transitions, interpolation, or time-varying transform resources.
* Layout engines, constraints, auto-layout, tight layout, constrained layout, guide collision solving, or colorbar placement optimization.
* Equal-aspect or fixed-aspect data layout unless later explicitly accepted.
* Nonlinear transforms.
* Log transforms.
* Categorical transforms.
* CRS/geospatial transforms.
* Unit conversion systems.
* Date/time axis transforms.
* Arbitrary Python callables as transforms.
* Shader/material transforms.
* 3D lighting, normals, materials, textures, culling, alpha sorting, or physically based rendering.
* Image rotation/skew/perspective as public S027 semantics.
* Texture-coordinate transforms.
* Instancing semantics, except that S027 may prepare the ground by defining reusable affine transform resources.
* Huge distributed source transformations.
* Eager materialization of virtual sources for transform adaptation.
* Remote renderer scheduling, frame pacing, synchronization policies, or transport-specific semantics.
* Backend-specific approximations without structured diagnostics.
* Public semantics inferred from current code when accepted specs are absent.

Strict do-not-do rule:

> If a worker needs to invent behavior for transform order, coordinate reporting, view mapping, camera, controller state, aspect, depth, or backend fallback, the mission must stop and request ADR/spec clarification.

---

## 12. Open Questions

### 12.1 Questions requiring human decision

1. **Should CPU pre-transform adaptation count as strict support for finite eager data?**
   Recommendation: yes, if explicitly reported and if query inverse retains source data. But project leadership should confirm because this affects Datoviz flagship expectations.

2. **Should singular affine transforms be invalid or render-only valid?**
   Recommendation: invalid in S027 because query inverse is first-class. Allowing render-only singular transforms complicates conformance.

3. **Should S027 require explicit `View2D` for all DATA visuals, or keep implicit `[-1, 1]` compatibility?**
   Recommendation: keep implicit compatibility but require explicit views in new fixtures/spec examples.

4. **Should equal aspect be accepted now?**
   Recommendation: no. Equal aspect introduces layout/content-rect semantics. Defer to a dedicated layout/aspect stage.

5. **Should nonzero z in 2D visual positions be ignored, preserved, or rejected?**
   Recommendation: preserve in source/query payload if present, ignore for S027 rendering/order/projection, and reject only when the scene requests depth/camera semantics.

6. **Should image axis-aligned scale/translate transforms be accepted as syntactic sugar over extent?**
   Recommendation: not as core protocol. Producers may rewrite to extent, but public arbitrary image transform remains deferred.

7. **Should transform resources have explicit version numbers?**
   Recommendation: useful for query/replay diagnostics, but not required if scene snapshots already provide stable frame identity.

8. **Should `TransformRef.required` be added, or should existing adaptation policy fully handle this?**
   Recommendation: prefer existing adaptation policy if already sufficient. Add `required` only if current protocol lacks per-feature fallback intent.

---

### 12.2 Questions agents can answer by inspection

1. Where should visual base classes accept `VisualTransformBinding` with minimal code churn?

2. Does the current panel/session model already have a canonical place for `View2D`, or is a new panel-view resource namespace needed?

3. How do existing guide APIs represent view limits, and can they map directly to `View2D.xlim`/`ylim`?

4. What Matplotlib reference code currently handles NDC versus DATA visuals, and where should S027 transform order be inserted?

5. Does the existing query harness already carry panel NDC coordinates, or must that field be added?

6. Which visual-family query payloads can already include extra extension payloads such as `gsp.transform-query@0.1`?

7. Which Datoviz v0.4 facade/runtime paths can support:

   * native data-domain view limits;
   * NDC overlay equivalence;
   * CPU pre-transformed finite buffers;
   * retained source arrays for query inverse;
   * capture/query after transform adaptation?

8. What are current eager-buffer size limits for safe CPU pre-transform adaptation?

9. Do replay/debug JSON schemas already support resource references and inline records uniformly?

10. Are existing visual QA tolerances sufficient for affine rotations and inverse-coordinate checks, or do S027 fixtures need separate numeric query tolerances?

11. Does VisPy2 already expose view-limit methods that should become `View2D` emitters?

12. Are any existing public APIs already named `Camera`, `Transform`, `View`, or `Projection` in a way that would conflict with reserved S027 terminology?

