## 1. Executive Decision

Keep `query.view3d.mesh_triangle_pick.v1` unchanged. Add a **new sibling capability/query kind**:

```text
query.view3d.mesh_triangle_pick.geometry.v1
```

Do **not** add opportunistic optional fields to the existing v1 payload, and do **not** create a broad `v2` yet. The existing v1 is already a clean identity-only contract: one panel point, at most one frontmost supported triangle, public `visual_id`, public canonical `primitive_index`, and strict opaque orthographic DATA-space semantics. The expansion should be explicit, separately advertised, and independently testable. 

`query.view3d.mesh_triangle_pick.geometry.v1` should return the existing v1 identity envelope plus a small required geometry bundle on hits:

```text
hit_barycentric
hit_panel_ndc_z
hit_data_xyz
```

Add a separate small optional capability for facing information:

```text
query.view3d.mesh_triangle_pick.facing.v1
```

This avoids the word “rich,” which is too open-ended, and avoids a `v2`, which would imply replacement or semantic correction of v1. The new capability is a strict superset path, not a mutation of the accepted baseline.

---

## 2. Accepted Payload Boundary

`query.view3d.mesh_triangle_pick.geometry.v1` inherits all accepted S044 v1 prerequisites and response rules:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.mesh_triangle_pick.v1
```

It remains limited to:

```text
orthographic View3D
DATA-space MeshVisual triangle geometry
opaque effective alpha == 1.0
depth_mode == "opaque_less"
one panel point request
at most one frontmost visible supported triangle
public visual_id
public canonical primitive_index
```

For `status=hit`, the v1 identity fields remain required, and the following fields become required for `geometry.v1`.

| Field             |                         Type | Units / coordinate space                                                                                          | Scope   | Requiredness                                                                                          | Validity prerequisites                                                                                                              | Numerical tolerance expectation                                                                                                                                                              | Capability                                    |
| ----------------- | ---------------------------: | ----------------------------------------------------------------------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| `hit_barycentric` | `tuple[float, float, float]` | Dimensionless barycentric coordinates relative to the selected public source triangle vertex order `(i0, i1, i2)` | Per-hit | Required on hit; absent on miss/unsupported/stale/invalid                                             | Selected primitive must map to a public canonical triangle; projected triangle must be non-degenerate; orthographic DATA-space only | Components should sum to `1.0` within `5e-5`; each component may lie in `[-5e-5, 1 + 5e-5]` at edges because of finite precision; conformance fixtures should compare with `abs_tol <= 5e-5` | `query.view3d.mesh_triangle_pick.geometry.v1` |
| `hit_panel_ndc_z` |                      `float` | Panel NDC z, where `-1` is near, `+1` is far, and smaller is closer                                               | Per-hit | Required on hit; absent on non-hit                                                                    | Same as above; visible fragment must be inside the accepted near/far clip interval, modulo tolerance                                | `abs_tol <= 5e-5`; expected range `[-1 - 5e-5, 1 + 5e-5]`                                                                                                                                    | `query.view3d.mesh_triangle_pick.geometry.v1` |
| `hit_data_xyz`    | `tuple[float, float, float]` | DATA-space coordinates of the hit point                                                                           | Per-hit | Required on hit; absent on non-hit                                                                    | DATA-space mesh only; no mesh-local transform, instancing, perspective, or NDC3 expansion                                           | Per-component tolerance `<= max(1e-6, 5e-5 * max(1, selected_visual_bbox_diag))`                                                                                                             | `query.view3d.mesh_triangle_pick.geometry.v1` |
| `front_facing`    |                       `bool` | Projected panel-NDC winding classification using accepted P032 area sign                                          | Per-hit | Required on hit only when `query.view3d.mesh_triangle_pick.facing.v1` is advertised; otherwise absent | Projected triangle must be non-degenerate; classification uses source face order after View3D projection                            | No numeric tolerance in payload; conformance fixtures must avoid near-zero projected area, e.g. `abs(area2) >= 1e-3`                                                                         | `query.view3d.mesh_triangle_pick.facing.v1`   |

No new per-request metadata is accepted. No new per-visual metadata is accepted. The existing `panel_ndc_xy` remains the request/panel position field inherited from v1.

A separate `hit_panel_ndc_xyz` field should **not** be added now. It would duplicate `panel_ndc_xy`. The canonical panel-NDC hit position is:

```text
(panel_ndc_xy[0], panel_ndc_xy[1], hit_panel_ndc_z)
```

---

## 3. Deferred Payloads

| Deferred field / feature              | Reason to defer                                                                                                              | Future trigger                                                                                                  |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `hit_camera_z`, camera-space depth    | Derivable from `hit_panel_ndc_z` and the View3D projection; adding it now creates redundant invariants and tolerance burdens | Add only if a concrete client need appears, probably under `query.view3d.mesh_triangle_pick.camera_depth.v1`    |
| Normalized depth buffer value         | Redundant with panel NDC z and risks confusion with backend depth ranges such as `[0, 1]`                                    | Only as a derived GSP value, never as backend raw depth                                                         |
| Raw backend depth                     | Not backend-neutral; may encode API-specific depth range, precision, reversed depth, or framebuffer implementation details   | Should remain a non-goal for public GSP semantics                                                               |
| Ray parameter / ray distance          | Orthographic rays have arbitrary origin choices; perspective semantics are not accepted yet                                  | Future `query.view3d.mesh_triangle_pick.perspective.v1` or `query.view3d.ray_readback.v1` integration           |
| UV                                    | Interpolation semantics are easy, but useful UV payloads imply attribute-query semantics beyond pure geometry                | Future `query.view3d.mesh_triangle_pick.attributes.v1`                                                          |
| Texel, texture id, displayed RGBA     | Requires strict Texture2D renderer evidence, sampler conformance, color pipeline semantics, and alpha/readback rules         | Future `query.view3d.mesh_triangle_pick.texture_readback.v1` after Datoviz texture support is public and tested |
| Base color, scalar value, material id | These are attribute/material queries, not geometry picking; color encodings and material resolution need their own contract  | Future attribute/material query ADR                                                                             |
| Per-hit normal                        | Ambiguous across flat normals, generated normals, smooth normals, transforms, and shading mode                               | Future `query.view3d.mesh_triangle_pick.attributes.v1` with explicit normal source semantics                    |
| Multi-hit / `hit_policy="all"`        | Requires ordering, occlusion, tie, duplicate, truncation, and max-result semantics                                           | Future `query.view3d.mesh_triangle_pick.multi_hit.v1`                                                           |
| Vertex picking                        | Different primitive type, different tolerance model, different identity rules                                                | Future `query.view3d.mesh_vertex_pick.v1`                                                                       |
| Edge picking                          | MeshVisual has faces, not public edge primitives; canonical edge identity must be specified                                  | Future `query.view3d.mesh_edge_pick.v1`                                                                         |
| NDC3 mesh picking                     | Explicitly deferred by current v1; no DATA hit position exists                                                               | Future `query.view3d.mesh_triangle_pick.ndc3.v1`                                                                |
| Perspective picking                   | Requires accepted ray generation, clipping, depth, and barycentric semantics                                                 | Future `query.view3d.mesh_triangle_pick.perspective.v1`                                                         |
| Mesh-local transforms                 | Need local/data/world naming and post-transform vs pre-transform identity semantics                                          | Future `query.view3d.mesh_triangle_pick.transforms.v1`                                                          |
| Instancing                            | Needs public `instance_index`, public per-instance transform, and canonical primitive identity                               | Future `query.view3d.mesh_triangle_pick.instancing.v1`                                                          |
| External model-loading hooks          | Need stable source-to-public primitive maps; backend asset handles are not acceptable                                        | Future model-ingest/source-map ADR                                                                              |
| Backend-native ids                    | Violates GSP backend-neutrality and VisPy2 producer constraints                                                              | Non-goal                                                                                                        |

---

## 4. Barycentric Semantics

For the selected public triangle:

```text
primitive_index = k
faces[k] = (i0, i1, i2)
p0 = positions[i0]
p1 = positions[i1]
p2 = positions[i2]
```

`hit_barycentric = (λ0, λ1, λ2)` is defined by:

```text
λ0 + λ1 + λ2 = 1
hit_data_xyz = λ0 * p0 + λ1 * p1 + λ2 * p2
```

The order is always the **source face vertex order** `(i0, i1, i2)`. It is not sorted, not winding-normalized, and not remapped to backend draw order.

For the accepted orthographic DATA-space scope, this is equivalent to solving in projected panel NDC:

```text
q0 = View3D.project(p0)
q1 = View3D.project(p1)
q2 = View3D.project(p2)

(panel_ndc_x, panel_ndc_y)
  = λ0 * (q0.x, q0.y)
  + λ1 * (q1.x, q1.y)
  + λ2 * (q2.x, q2.y)
```

Because the accepted projection is affine, DATA/ray barycentrics and projected panel-NDC barycentrics must agree in exact arithmetic.

Edge and vertex policy:

```text
λi == 0      means the hit lies on the opposite edge in exact arithmetic
λi == 1      means the hit lies on vertex i in exact arithmetic
λi < 0       means outside the source triangle in exact arithmetic
λi > 1       means outside the source triangle in exact arithmetic
```

Finite-precision tolerance:

```text
sum(λ) must be within 5e-5 of 1.0
λi may be as low as -5e-5 or as high as 1 + 5e-5 for valid edge/vertex hits
implementations must not clamp or snap barycentrics before returning them
```

No edge id or vertex id is inferred from barycentric values in this capability. A hit exactly on a shared edge is still a triangle hit for the single triangle selected by the v1 frontmost/tie behavior. Conformance fixtures should avoid exact shared-edge and equal-depth ties unless they are explicitly testing ambiguity behavior.

Projected-degenerate triangles:

```text
area2 = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
```

If `area2 == 0` in exact arithmetic, `hit_barycentric` is undefined. Such triangles must not produce geometry hits. Under P032 culling-aware picking, projected-degenerate triangles are excluded from the candidate set.

Partially clipped triangles:

If a triangle is partially clipped by near/far or panel boundaries but still contributes a visible fragment at the requested panel point, barycentrics are still relative to the **original public source triangle**, not to generated clipped vertices. Clipping must not introduce new public primitive indices or barycentric vertex order. Initial conformance fixtures should avoid clipping-boundary hits; later fixtures can harden this rule.

---

## 5. Depth And Hit Position Semantics

Accept exactly one public depth field now:

```text
hit_panel_ndc_z: float
```

Definition:

```text
hit_panel_ndc_z = λ0 * q0.z + λ1 * q1.z + λ2 * q2.z
```

where:

```text
qk = View3D.project(pk)
```

The coordinate convention is the accepted panel NDC convention:

```text
z = -1 near
z = +1 far
smaller z is closer
```

The canonical panel-NDC hit position is the composite value:

```text
hit_panel_ndc = (panel_ndc_xy[0], panel_ndc_xy[1], hit_panel_ndc_z)
```

Do not add a separate `hit_panel_ndc_xyz` field now.

Accept DATA-space hit position now:

```text
hit_data_xyz = λ0 * p0 + λ1 * p1 + λ2 * p2
```

This is accepted only for the current strict scope:

```text
orthographic View3D
DATA-space mesh positions
no mesh-local transform
no instancing
no perspective projection
```

For orthographic DATA-space triangles, `hit_data_xyz` must also equal the intersection between the orthographic pick ray and the selected triangle plane, within tolerance.

The following are deferred:

```text
hit_camera_z
hit_camera_distance
hit_ray_t
hit_depth_normalized
raw_depth
backend_depth
```

A client that owns the matching View3D snapshot can derive camera-space depth from the accepted projection:

```text
camera_z = near + (hit_panel_ndc_z + 1) * (far - near) / 2
```

That derived value should not be duplicated in the first expanded payload.

---

## 6. Multi-Hit / Hit Policy Decision

Do not accept multi-hit picking now.

The current v1 contract should remain:

```text
one panel point request
at most one result
frontmost visible supported triangle
opaque_less depth policy
```

Future capability boundary:

```text
query.view3d.mesh_triangle_pick.multi_hit.v1
```

A future multi-hit ADR should define at least:

```text
hit_policy: "frontmost" | "all_intersections"
max_hits: int | None
hits: tuple[MeshTriangleHit, ...]
truncated: bool
```

Ordering should probably be:

```text
primary: increasing hit_panel_ndc_z, smaller first
secondary: deterministic public visual order
tertiary: primitive_index
quaternary: instance_index, once instancing exists
```

But this should not be accepted until the tie rules are explicit.

Blockers:

```text
depth ties
shared-edge duplicate suppression
occluded-but-intersected triangles
face-culling interaction
clipping interaction
maximum result behavior
stable ordering across backends
transparent and non-opaque exclusions
Datoviz public API evidence for multi-hit queries
```

Opaque multi-hit should still exclude transparent picking. A future transparent-selection policy should be a separate capability, not an extension of the strict opaque path.

---

## 7. Vertex/Edge Picking Decision

Vertex and edge picking should be separate capabilities, not part of triangle-payload expansion.

Future capability names:

```text
query.view3d.mesh_vertex_pick.v1
query.view3d.mesh_edge_pick.v1
```

Reasons to separate:

```text
triangle picking is coverage/depth based
vertex and edge picking are tolerance/radius based
vertex and edge ambiguity is common
MeshVisual currently exposes faces, not canonical public edge records
source indices, emitted ordinals, and shared topology need separate rules
```

Future vertex identity should likely be:

```text
indexed mesh: public MeshVisual.positions row
unindexed emitted triangle list: emitted vertex ordinal
```

Future edge identity needs a dedicated decision. Two plausible public choices are:

```text
canonical undirected edge as (min(vertex_index_a, vertex_index_b), max(...))
or canonical edge ordinal derived from first occurrence in public face order
```

Do not decide this inside triangle picking.

Future request tolerance should be explicit and panel-space based, for example:

```text
radius_panel_px: float
```

or:

```text
radius_panel_ndc: float
```

A future ADR must define whether the query returns:

```text
nearest only
all within radius
nearest with ambiguity diagnostic
```

---

## 8. Culling / Alpha / Texture Interaction

P032 culling affects the candidate set, not the geometry field definitions.

When:

```text
query.view3d.mesh_triangle_pick.face_culling.v1
```

is advertised, culled and projected-degenerate triangles behave as absent:

```text
they do not occlude
they do not win by depth
they must not be returned as hits
```

`front_facing` may be returned only under:

```text
query.view3d.mesh_triangle_pick.facing.v1
```

Definition:

```text
area2 > 0  => front_facing = true
area2 < 0  => front_facing = false
```

Do not add:

```text
culled
culling_state
```

to returned hits now. For a successful hit, `culled` would always be false under strict culling semantics; for a miss, there may be many absent candidates, so a single culling state would be misleading.

Alpha remains strict:

```text
effective alpha must be 1.0 everywhere for eligible geometry
ordinary transparent picking is deferred
non-opaque texture alpha is deferred
```

For textured meshes, strict identity/geometry picking may be eligible only if the accepted opaque-alpha rule is satisfied:

```text
base alpha == 1.0
every texture alpha byte == 255
```

But no UV, texel, texture id, displayed RGBA, material id, or sampled color field should be added now.

---

## 9. Perspective / Transform / Instancing Boundary

Accepted now:

```text
orthographic View3D only
DATA-space MeshVisual positions only
public source triangle identity only
no mesh-local transform expansion
no instancing
no external model primitive maps
```

Perspective is explicitly deferred.

Future capability:

```text
query.view3d.mesh_triangle_pick.perspective.v1
```

For perspective, the right future rule is likely:

```text
hit_barycentric = geometric ray/triangle barycentric in DATA space
```

not plain post-divide screen-space barycentric. If a future query needs rasterization or screen-space interpolation weights, that should be a separate field, for example:

```text
hit_panel_barycentric
```

Do not overload `hit_barycentric`.

Mesh-local transforms are deferred.

Future capability:

```text
query.view3d.mesh_triangle_pick.transforms.v1
```

That future ADR must define whether hit positions are returned as:

```text
hit_local_xyz
hit_data_xyz
hit_world_xyz
```

For now, `hit_data_xyz` means the current untransformed DATA-space coordinates consumed by View3D.

Instancing is deferred.

Future capability:

```text
query.view3d.mesh_triangle_pick.instancing.v1
```

That future capability must add a public field such as:

```text
instance_index: int
```

and must specify whether `primitive_index` remains the source face row. It should. Instance identity must never be a backend draw id.

External model loading is deferred until GSP has a public source-map contract from loaded assets to canonical GSP visual ids, face rows, vertex rows, and instance records.

---

## 10. Capability Names And Diagnostics

Accepted new capabilities:

```text
query.view3d.mesh_triangle_pick.geometry.v1
query.view3d.mesh_triangle_pick.facing.v1
```

Existing prerequisite or interacting capabilities:

```text
query.view3d.mesh_triangle_pick.v1
query.view3d.mesh_triangle_pick.face_culling.v1
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
meshvisual.face_culling.data3d.projected_ndc.v1
meshvisual.face_culling.ndc3.panel_winding.v1
```

Reserved future capability names:

```text
query.view3d.mesh_triangle_pick.multi_hit.v1
query.view3d.mesh_triangle_pick.ndc3.v1
query.view3d.mesh_triangle_pick.perspective.v1
query.view3d.mesh_triangle_pick.camera_depth.v1
query.view3d.mesh_triangle_pick.attributes.v1
query.view3d.mesh_triangle_pick.texture_readback.v1
query.view3d.mesh_triangle_pick.transforms.v1
query.view3d.mesh_triangle_pick.instancing.v1
query.view3d.mesh_vertex_pick.v1
query.view3d.mesh_edge_pick.v1
```

Recommended diagnostics:

| Diagnostic string                                    | Meaning                                                                                                    |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `pick.unsupported.geometry_payload`                  | Backend supports identity v1 but not `geometry.v1`                                                         |
| `pick.unsupported.no_public_primitive_map`           | Backend hit cannot be mapped to public canonical `primitive_index`                                         |
| `pick.unsupported.no_public_geometry_reconstruction` | Backend cannot reconstruct barycentric/depth/DATA hit from public protocol state                           |
| `pick.unsupported.no_public_panel_ndc_depth`         | Backend exposes only raw or undocumented depth                                                             |
| `pick.unsupported.projected_degenerate`              | Selected or candidate triangle is projected-degenerate for geometry semantics                              |
| `pick.unsupported.facing_payload`                    | Backend does not support `front_facing`                                                                    |
| `pick.unsupported.face_culling`                      | Scene requires culling-aware picking but backend does not advertise it                                     |
| `pick.unsupported.ndc3_mesh`                         | NDC3 mesh picking requested before `ndc3.v1`                                                               |
| `pick.unsupported.perspective_projection`            | Perspective View3D picking requested before `perspective.v1`                                               |
| `pick.unsupported.mesh_transform`                    | Mesh-local transform affects geometry before transform picking is accepted                                 |
| `pick.unsupported.instanced_mesh`                    | Instanced mesh requested before instancing query semantics                                                 |
| `pick.unsupported.non_opaque_alpha`                  | Effective alpha is not strictly 1.0                                                                        |
| `pick.unsupported.texture_attribute_readback`        | UV/texel/color/material query field requested before attribute/readback capability                         |
| `pick.unsupported.multi_hit`                         | `hit_policy="all"` or equivalent requested before multi-hit capability                                     |
| `pick.unsupported.vertex_edge_pick`                  | Vertex/edge query requested through triangle-pick path                                                     |
| `pick.invalid.panel_xy_outside`                      | Request panel point is outside the panel                                                                   |
| `pick.stale.pick_scene_snapshot`                     | Expected pick-scene snapshot does not match current pick scene                                             |
| `pick.adapted.public_geometry_reconstruction`        | Backend returned public triangle identity, and GSP reconstructed geometry fields from public protocol data |

`pick.adapted.public_geometry_reconstruction` is acceptable for successful responses if the reconstruction uses only public GSP state and accepted projection semantics. It must not hide missing primitive identity.

---

## 11. Fixture Plan

Minimum positive fixtures before advertising `query.view3d.mesh_triangle_pick.geometry.v1`:

| Fixture                                                                                                   | Purpose                                                       |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Single orthographic DATA triangle, axis-aligned camera, interior point with known barycentric coordinates | Validate `hit_barycentric`, `hit_data_xyz`, `hit_panel_ndc_z` |
| Sloped triangle with different vertex z values                                                            | Validate interpolated panel-NDC depth                         |
| Two overlapping opaque DATA triangles at different depths                                                 | Validate frontmost visible triangle and depth ordering        |
| Reversed `xlim` or `ylim` orthographic projection                                                         | Validate accepted reversed bounds and barycentric correctness |
| Non-axis-aligned camera basis                                                                             | Validate accepted `forward/right/true_up` projection math     |
| Miss inside panel but outside triangle                                                                    | Validate miss payload omits geometry fields                   |
| Hit with stale `expected_pick_scene_snapshot_id`                                                          | Validate stale response and no hit geometry                   |
| Hit after geometry or depth-affecting scene change                                                        | Validate `pick_scene_snapshot_id` changes                     |

Minimum negative fixtures:

| Fixture                                                      | Expected result                                                                                          |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| NDC3 mesh under geometry query                               | `unsupported`, diagnostic `pick.unsupported.ndc3_mesh`                                                   |
| Perspective View3D under geometry query                      | `unsupported`, diagnostic `pick.unsupported.perspective_projection`                                      |
| Non-opaque alpha mesh                                        | `unsupported`, diagnostic `pick.unsupported.non_opaque_alpha`                                            |
| Textured mesh with any texture alpha byte `< 255`            | `unsupported`, diagnostic `pick.unsupported.non_opaque_alpha`                                            |
| Mesh-local transform that is not accepted by query semantics | `unsupported`, diagnostic `pick.unsupported.mesh_transform`                                              |
| Instanced mesh                                               | `unsupported`, diagnostic `pick.unsupported.instanced_mesh`                                              |
| Backend cannot map native hit to public face row             | `unsupported`, diagnostic `pick.unsupported.no_public_primitive_map`                                     |
| Projected-degenerate triangle                                | no geometry hit; diagnostic allowed if unsupported path is chosen                                        |
| Panel point outside panel                                    | `invalid`, diagnostic `pick.invalid.panel_xy_outside`                                                    |
| Miss response                                                | must not include `visual_id`, `primitive_index`, `hit_barycentric`, `hit_panel_ndc_z`, or `hit_data_xyz` |

Additional fixtures before advertising `query.view3d.mesh_triangle_pick.facing.v1`:

| Fixture                                                         | Purpose                                                 |
| --------------------------------------------------------------- | ------------------------------------------------------- |
| Front-facing triangle with `area2 > 0`                          | Validate `front_facing=true`                            |
| Back-facing triangle with `area2 < 0` and no culling            | Validate `front_facing=false` can be returned           |
| Back-face culled triangle when culling capability is advertised | Validate culled triangle is absent and does not occlude |
| Front-face culled triangle when front culling is active         | Validate front-facing triangle is absent                |

Fixtures should avoid exact shared edges, equal-depth ties, near-zero projected area, and clipping-boundary hits in the first conformance wave.

---

## 12. Datoviz Evidence Requirements

Datoviz must not advertise even the base strict mesh triangle pick until the public primitive mapping blocker is solved.

Sufficient public Datoviz evidence for `query.view3d.mesh_triangle_pick.v1`:

```text
DvzQueryResult.visual_id maps to the public GSP visual id through dvz_visual_id
one of face_id, primitive_id, or resolved_target/resolved_id reports a zero-based public triangle row
indexed meshes report MeshVisual.faces row, not GPU vertex id or draw primitive id
unindexed triangle-list meshes report emitted triangle ordinal
non-instanced mesh hits do not collapse to item_id = 0 or constant 1u
instanced ids are not misreported as triangle ids
freshness_serial or equivalent can support GSP pick_scene_snapshot_id freshness
```

The public API must document one of these acceptable mappings:

```text
resolved_target = DVZ_SCENE_TARGET_TRIANGLE
resolved_id = zero-based canonical triangle row
```

or:

```text
face_id = zero-based canonical face row
```

or:

```text
primitive_id = zero-based canonical triangle row
```

For `query.view3d.mesh_triangle_pick.geometry.v1`, Datoviz does **not** need native barycentric fields if GSP can reconstruct geometry from public state after receiving a valid public triangle id.

Sufficient evidence for each accepted field:

| Field                         | Datoviz evidence needed                                                                                                                                                                                                                                         |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hit_barycentric`             | Public canonical triangle id plus GSP-owned public `positions`, `faces`, View3D camera/projection state, and panel point. Native barycentric is optional. If native barycentric is exposed, Datoviz must document vertex order and coordinate semantics.        |
| `hit_panel_ndc_z`             | Prefer GSP reconstruction from public projected triangle vertices and barycentric coordinates. If using `DvzQueryResult.depth`, Datoviz must publicly document whether it is panel NDC z, normalized depth, or another value, and provide tests for conversion. |
| `hit_data_xyz`                | Public canonical triangle id plus public DATA positions are sufficient. No backend-native hit position is required.                                                                                                                                             |
| `front_facing`                | No native Datoviz field required. GSP can compute it from public projected vertices using the accepted P032 `area2` formula.                                                                                                                                    |
| Culling-aware hit eligibility | Public Datoviz behavior/tests must show culled triangles do not occlude, do not win depth, and are not returned.                                                                                                                                                |

`DvzQueryResult.has_depth` and `DvzQueryResult.depth` are useful only if their public semantics are documented. A raw Vulkan/framebuffer depth value is not sufficient evidence for a public GSP depth field.

Acceptable Datoviz implementation strategy after the primitive-id fix:

```text
1. Use public Datoviz query to identify public visual_id and public face/primitive row.
2. Use GSP public scene records to reconstruct barycentric, hit_panel_ndc_z, hit_data_xyz, and front_facing.
3. Advertise geometry.v1 only after conformance fixtures pass.
```

This is backend-neutral and does not leak Datoviz-native handles, shader slots, draw ids, framebuffer internals, or private Vulkan state.

---

## 13. Implementation Plan

1. Accept an ADR for the new payload boundary:

```text
query.view3d.mesh_triangle_pick.geometry.v1
query.view3d.mesh_triangle_pick.facing.v1
```

2. Leave `query.view3d.mesh_triangle_pick.v1` unchanged.

3. Add protocol models for the geometry query response as a strict superset of the v1 hit envelope.

4. Add validators:

```text
geometry fields required on hit
geometry fields forbidden on non-hit
identity fields still forbidden on non-hit
panel_ndc_xy required for hit/miss as in v1
depth_mode must be "opaque_less" for hit/miss
```

5. Add public helper functions:

```text
project DATA point to panel NDC
invert panel NDC xy to orthographic camera-plane ray
compute triangle barycentric
compute hit_panel_ndc_z
compute hit_data_xyz
compute projected area2 and front_facing
```

6. Add conformance fixtures first against the Matplotlib CPU reference path.

7. Mark Matplotlib geometry picking as:

```text
pick.adapted.cpu_reference
```

or, for geometry reconstruction:

```text
pick.adapted.public_geometry_reconstruction
```

8. Keep Datoviz geometry picking unadvertised until upstream Datoviz provides public canonical triangle identity.

9. After Datoviz primitive identity is public and tested, implement Datoviz geometry payload reconstruction from public GSP records, not from private Datoviz state.

10. Add negative tests ensuring no backend can advertise `geometry.v1` while silently omitting fields or returning backend-native ids.

11. Add SPEC_INDEX entries and capability documentation.

12. Add reserved/deferred capability names to the design notes, but do not advertise them.

13. Add examples showing the canonical panel-NDC hit point:

```text
(panel_ndc_xy[0], panel_ndc_xy[1], hit_panel_ndc_z)
```

rather than adding `hit_panel_ndc_xyz`.

14. Add explicit language that future perspective, NDC3, transform, instancing, multi-hit, vertex/edge, texture, and material payloads require separate accepted decisions.

---

## 14. Risks / Non-Goals

Main risks:

```text
accidentally weakening the clean v1 identity-only contract
allowing optional fields on v1 to become de facto inconsistent backend behavior
exposing raw backend depth as if it were GSP depth
confusing screen-space, DATA-space, and perspective-correct barycentrics
overclaiming Datoviz support before public primitive ids exist
creating redundant depth fields with inconsistent tolerances
creating nondeterminism around shared edges and equal-depth ties
silently mishandling face culling or projected-degenerate triangles
```

Non-goals for this expansion:

```text
no v1 mutation
no broad v2
no raw backend ids
no Datoviz-native handles
no transparent picking
no multi-hit picking
no vertex/edge picking
no NDC3 picking
no perspective picking
no texture/color/material readback
no attribute interpolation payloads
no model-loading source-map semantics
no instancing
no mesh-local transform semantics
```

The conservative boundary is therefore:

```text
identity-only pick remains query.view3d.mesh_triangle_pick.v1

strict geometry pick becomes query.view3d.mesh_triangle_pick.geometry.v1

optional projected facing becomes query.view3d.mesh_triangle_pick.facing.v1

everything else remains explicitly deferred
```

