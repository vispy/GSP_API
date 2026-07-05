## 1. Executive Decision

* **Accept face culling now, but only as a small, strict, capability-gated v1 contract.** The contract should define front/back classification in **projected panel NDC**, not in source/object coordinates and not in backend framebuffer/screen coordinates.
* **Defer strict non-opaque 3D alpha.** Keep non-opaque 3D meshes outside strict opaque-depth and strict triangle-pick paths. Ordinary alpha may remain an adapted rendering path, but without a backend-neutral blend/order/OIT contract.
* **Do not let existing source code or backend defaults define the semantics.** The accepted boundary should be spec-first, with backends advertising support only after fixtures prove the exact projected-winding behavior and alpha rejection rules. 

---

## 2. Accepted v1 Semantics

### Face winding / front face

Accept the following v1 definition for `(N,3)` `MeshVisual` triangles in `DATA` and `NDC` coordinate spaces.

For each source face:

```text
face = (i0, i1, i2)
```

Let the three panel-NDC vertices be:

```text
q0 = (x0, y0, z0)
q1 = (x1, y1, z1)
q2 = (x2, y2, z2)
```

For `coordinate_space == DATA`:

```text
qk = View3D.project(positions[ik])
```

using the accepted `Camera3D` and `OrthographicProjection3D` equations.

For `coordinate_space == NDC` and `(N,3)` positions:

```text
qk = positions[ik]
```

Then define the signed projected area:

```text
area2 =
    (x1 - x0) * (y2 - y0)
  - (y1 - y0) * (x2 - x0)
```

v1 front/back classification:

```text
front-facing  iff area2 > 0
back-facing   iff area2 < 0
ambiguous     iff area2 == 0
```

This means:

* **Front-facing is counter-clockwise in panel NDC x/y.**
* `z` does not participate in winding classification.
* The source face vertex order is preserved, but classification is performed **after DATA-to-panel-NDC projection**.
* Final framebuffer or pixel-space mapping must not affect classification.
* Backend screen conventions such as y-down pixel coordinates must not flip the protocol result.

### Effect of reversed bounds, camera orientation, and transforms

Reversed `View3D.xlim` and `ylim` **do affect** front/back classification because they affect the projected NDC coordinates.

A single reversed axis flips winding:

```text
normal xlim, normal ylim      -> sign(area2)
reversed xlim, normal ylim    -> -sign(area2)
normal xlim, reversed ylim    -> -sign(area2)
reversed xlim, reversed ylim  -> sign(area2)
```

Camera orientation also affects classification through the accepted camera basis and projection.

Current 2D `VisualTransformBinding` must not be silently mixed with strict 3D culling. Until 3D transforms are accepted, `face_culling != NONE` with a transform that could affect `(N,3)` geometry should be rejected from strict culling with a transform/culling diagnostic.

Future accepted 3D transforms should be defined as part of the geometry-to-panel-NDC pipeline before this winding test. That should be a later spec decision, not implied now.

### Face culling

Accept `FaceCulling.NONE`, `FaceCulling.BACK`, and `FaceCulling.FRONT` as protocol semantics, but make strict support capability-gated.

Culling rule:

```text
FaceCulling.NONE:
    keep all non-degenerate projected triangles

FaceCulling.BACK:
    suppress triangles with area2 < 0

FaceCulling.FRONT:
    suppress triangles with area2 > 0
```

For `area2 == 0`:

* the triangle is **projected-degenerate**;
* it is not classified as front or back;
* it must not contribute strict raster fragments;
* it must not be returned by strict rendered-surface triangle picking.

Culling happens before:

```text
depth_test
depth_write
order
alpha blending / adapted compositing
query hit selection
```

A culled triangle:

* produces no color contribution;
* performs no depth test;
* performs no depth write;
* cannot occlude another triangle;
* cannot be returned by strict `query.view3d.mesh_triangle_pick.v1`.

### Alpha

Accept only this v1 alpha/depth boundary:

```text
A 3D mesh is eligible for strict opaque depth only if its effective fragment alpha is provably 1.0 everywhere.
```

For non-textured unlit or flat-Lambert meshes, this means every resolved mesh color alpha must be exactly `1.0`.

For `texture2d_unlit`, the S050 alpha equation remains:

```text
output.a = clamp(base.a * tex.a, 0.0, 1.0)
```

Therefore strict opaque eligibility requires:

```text
base.a == 1.0 everywhere
and
all texture alpha bytes == 255
```

If any effective alpha may be below `1.0`, the mesh is non-opaque and must not participate in:

```text
meshvisual.positions3d.opaque_depth.v1
query.view3d.mesh_triangle_pick.v1
strict 3D opaque-depth conformance fixtures
```

No v1 backend-neutral alpha blend equation is accepted.

Do **not** accept now:

```text
straight alpha blending
premultiplied alpha blending
alpha test / discard
alpha-to-coverage
transparency sorting
depth peeling
weighted blended OIT
order-independent transparency
strict transparent picking
```

Adapted ordinary-alpha rendering may exist, but it is not a strict protocol feature.

### Textured alpha

For 3D strict opaque depth:

```text
any texture alpha byte < 255
=> mesh3d_alpha_not_strict
```

For 2D or NDC textured meshes, alpha may be rendered as non-strict ordinary alpha only if the backend has explicit renderer support for that path. That support should remain separate from S050 texture acceptance and from strict 3D culling/depth semantics.

---

## 3. Deferred Semantics

Keep the following out of v1:

* strict non-opaque 3D alpha rendering;
* any alpha blend equation;
* transparent mesh sorting;
* order-independent transparency;
* alpha test / discard thresholds;
* premultiplied-alpha contracts;
* strict behavior for partially clipped 3D triangles;
* scene graphs;
* mesh-local 3D transforms;
* transform-dependent culling;
* instancing;
* external model loading;
* public backend-native mesh handles;
* expanded 3D query payloads;
* strict transparent mesh picking;
* strict culling behavior for non-mesh 3D visual families.

---

## 4. Capability Names

| Capability                                        | Meaning                                                             | Strict requirements                                                                                                                                                                                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `meshvisual.face_culling.data3d.projected_ndc.v1` | Strict `FaceCulling` support for `DATA` `(N,3)` meshes in `View3D`. | Project vertices through the accepted `View3D` equations; classify front/back by signed area in panel NDC; respect reversed `xlim` / `ylim`; cull before depth/order/blending; no backend screen-space winding convention may alter the result. |
| `meshvisual.face_culling.ndc3.panel_winding.v1`   | Strict `FaceCulling` support for `NDC` `(N,3)` meshes.              | Interpret input positions directly as panel NDC; classify by `area2`; cull before depth/order/blending; do not use framebuffer y-down winding.                                                                                                  |
| `query.view3d.mesh_triangle_pick.face_culling.v1` | Strict 3D triangle picking respects `FaceCulling`.                  | Query candidate set must exclude culled and projected-degenerate triangles using the same projected-NDC winding rule as rendering. Returned face identity remains the canonical source face index.                                              |
| `meshvisual.positions3d.opaque_depth.v1`          | Existing strict opaque 3D depth capability.                         | Remains restricted to fully opaque 3D meshes. Culling may combine with it only if the relevant culling capability is also advertised.                                                                                                           |
| No `meshvisual.alpha.blend.*.v1` in this boundary | No strict alpha rendering capability is accepted now.               | Backends must not claim strict transparent 3D behavior, blend order, or OIT under this consultation boundary.                                                                                                                                   |

---

## 5. Diagnostics

| Diagnostic                          | Trigger                                                                                                                                                          | Required behavior                                                                                                                                      |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `mesh3d_face_culling_unsupported`   | `face_culling != NONE` on a 3D mesh, but the backend lacks the relevant strict culling capability.                                                               | Do not silently ignore culling. Either reject the strict path or render only as adapted behavior with this diagnostic.                                 |
| `mesh3d_face_culling_adapted`       | Backend applies approximate or reference-only culling but cannot satisfy the strict capability requirements.                                                     | Render may proceed as adapted, but the backend must not advertise the strict culling capability for that path.                                         |
| `mesh3d_culling_winding_ambiguous`  | A source-nondegenerate triangle becomes projected-degenerate: `area2 == 0`, or numerically indistinguishable from zero under the backend’s documented tolerance. | Treat as having no strict raster contribution and no strict pick hit. Emit at most once per visual or fixture group to avoid per-face diagnostic spam. |
| `mesh3d_culling_transform_conflict` | `face_culling != NONE` and a transform is present whose effect on `(N,3)` geometry is not accepted by the spec.                                                  | Reject strict culling for that visual. Do not guess transform ordering.                                                                                |
| `query_3d_mesh_culling_unsupported` | Strict triangle pick is requested on a visual with `face_culling != NONE`, but the query path lacks `query.view3d.mesh_triangle_pick.face_culling.v1`.           | Do not return hits that ignore culling. Reject the query for that visual or exclude it with this diagnostic.                                           |
| `mesh3d_alpha_not_strict`           | Any effective 3D mesh alpha may be below `1.0`, including base color alpha, per-face/vertex alpha, scalar encoding alpha, or texture alpha bytes below `255`.    | Exclude from strict opaque-depth and strict 3D triangle-pick paths. Adapted rendering may proceed only without strict claims.                          |
| `mesh_alpha_unsupported`            | A backend cannot render non-opaque mesh alpha even as adapted ordinary alpha.                                                                                    | Reject or omit the visual with diagnostic; do not substitute opaque rendering silently.                                                                |
| `mesh3d_alpha_depth_conflict`       | Non-opaque 3D mesh is combined with a strict depth path, or with `depth_test` / `depth_write` settings that would imply strict opaque-depth behavior.            | Do not claim `meshvisual.positions3d.opaque_depth.v1`. Either reject strict rendering or adapt depth behavior with diagnostics.                        |
| `mesh3d_texture_alpha_not_strict`   | Optional more specific diagnostic when `texture2d_unlit` has any texture alpha byte below `255` in a strict 3D context.                                          | Same required behavior as `mesh3d_alpha_not_strict`; useful as structured detail, but not a separate semantic category.                                |
| `mesh3d_clipping_adapted`           | Existing trigger: strict behavior would depend on partially clipped 3D triangles.                                                                                | Culling capability alone must not imply strict clipping support. Fixtures for culling v1 should avoid partially clipped triangles.                     |

---

## 6. Query Semantics

For `query.view3d.mesh_triangle_pick.v1`, culling should affect the candidate triangle set.

The strict candidate set is:

```text
strict candidates =
    DATA-space 3D mesh triangles
    that are fully opaque
    that pass the existing strict query scope
    that are not culled by FaceCulling
    that are not projected-degenerate
```

For `FaceCulling.NONE`, existing strict opaque pick semantics are unchanged.

For `FaceCulling.BACK`:

```text
exclude area2 < 0
```

For `FaceCulling.FRONT`:

```text
exclude area2 > 0
```

For `area2 == 0`:

```text
exclude from strict rendered-surface picking
```

Culled triangles behave as absent. They do not occlude, do not win by depth, and must not be returned as hits.

The query result payload should not be expanded in this v1 boundary. It should continue to use canonical GSP visual and source face identity. Backend-native mesh IDs, Vulkan handles, or private Datoviz triangle IDs must not leak into the protocol.

Future query payloads may add optional fields such as `front_facing`, `culling_state`, barycentrics, or interpolated attributes, but that should remain on the separate query-expansion track.

For non-opaque alpha:

```text
non-opaque 3D mesh => excluded from strict mesh_triangle_pick.v1
```

No transparent-picking semantics are accepted now.

---

## 7. Fixture Plan

### Positive fixtures

1. **NDC3 basic winding fixture**

   Two isolated `NDC` `(N,3)` triangles:

   ```text
   T0: CCW in panel NDC, area2 > 0
   T1: CW  in panel NDC, area2 < 0
   ```

   Expected:

   ```text
   FaceCulling.NONE  -> both visible
   FaceCulling.BACK  -> only T0 visible
   FaceCulling.FRONT -> only T1 visible
   ```

2. **DATA View3D projected winding fixture**

   Use a simple camera:

   ```text
   eye    = (0, 0, 1)
   target = (0, 0, 0)
   up     = (0, 1, 0)
   ```

   With normal bounds:

   ```text
   xlim = (-1, 1)
   ylim = (-1, 1)
   ```

   A triangle whose projected NDC area is positive must be front-facing.

   Expected:

   ```text
   FaceCulling.BACK keeps it
   FaceCulling.FRONT removes it
   ```

3. **Reversed xlim fixture distinguishing source-order from projected winding**

   Use the same DATA triangle and camera, but reverse only `xlim`:

   ```text
   xlim = (1, -1)
   ylim = (-1, 1)
   ```

   Expected:

   ```text
   projected area sign flips
   FaceCulling.BACK now removes the triangle
   FaceCulling.FRONT now keeps it
   ```

   This catches incorrect source-order or object-space culling.

4. **Framebuffer y-down trap fixture**

   Use an `NDC` triangle that is CCW in panel NDC.

   Expected:

   ```text
   FaceCulling.BACK keeps it
   ```

   A backend that classifies after y-down framebuffer mapping will incorrectly cull it.

5. **Culling before depth fixture**

   Two overlapping opaque triangles:

   ```text
   near triangle: culled by current FaceCulling mode
   far triangle: not culled
   ```

   Expected:

   ```text
   far triangle visible
   near culled triangle performs no depth write and cannot occlude
   ```

6. **Culling before query fixture**

   Ray intersects two opaque triangles:

   ```text
   nearest triangle: culled
   farther triangle: not culled
   ```

   Expected strict pick:

   ```text
   returns farther non-culled triangle
   ```

7. **Texture alpha strict-opaque fixture**

   `texture2d_unlit` 3D mesh with:

   ```text
   base.a = 1.0
   all texture alpha bytes = 255
   ```

   Expected:

   ```text
   eligible for strict opaque depth if all other strict-depth requirements pass
   ```

### Negative fixtures

1. **Unsupported culling**

   Backend lacks culling capability, visual has:

   ```text
   face_culling = BACK
   ```

   Expected:

   ```text
   mesh3d_face_culling_unsupported
   no strict culling claim
   no silent ignore
   ```

2. **Projected-degenerate triangle**

   Source triangle is non-degenerate in DATA space but projects to:

   ```text
   area2 == 0
   ```

   Expected:

   ```text
   mesh3d_culling_winding_ambiguous
   no strict raster contribution
   no strict pick hit
   ```

3. **Transform/culling conflict**

   Visual has:

   ```text
   face_culling != NONE
   transform != None
   ```

   where the transform’s effect on `(N,3)` geometry is not accepted.

   Expected:

   ```text
   mesh3d_culling_transform_conflict
   strict culling rejected
   ```

4. **Non-opaque vertex or face color**

   3D mesh with any resolved alpha:

   ```text
   alpha < 1.0
   ```

   Expected:

   ```text
   mesh3d_alpha_not_strict
   no meshvisual.positions3d.opaque_depth.v1
   no strict mesh_triangle_pick.v1 participation
   ```

5. **Texture alpha below 255**

   3D `texture2d_unlit` mesh with any texture byte:

   ```text
   alpha < 255
   ```

   Expected:

   ```text
   mesh3d_alpha_not_strict
   optionally mesh3d_texture_alpha_not_strict
   ```

6. **Alpha/depth conflict**

   Non-opaque 3D mesh with strict depth requested or implied.

   Expected:

   ```text
   mesh3d_alpha_depth_conflict
   no strict depth claim
   ```

7. **Query culling unsupported**

   Backend can render culling but query path cannot apply the same culling rule.

   Expected:

   ```text
   query_3d_mesh_culling_unsupported
   no strict culling-aware pick result
   ```

### Runtime evidence before backend promotion

Before advertising culling capabilities, a backend must pass fixtures covering:

```text
normal bounds
reversed xlim
reversed ylim
NDC panel winding
framebuffer y-down trap
culling before depth
culling before query, if query capability is claimed
```

Before advertising culling combined with strict opaque depth, the backend must also pass strict less-depth runtime evidence for the retained 3D path.

Before admitting textured meshes to strict opaque depth, the backend must prove:

```text
all base alpha == 1.0
all texture alpha bytes == 255
sampling path cannot introduce alpha < 1.0
```

---

## 8. Implementation Plan

### Protocol validation steps

1. Validate `FaceCulling` syntactically as protocol surface:

   ```text
   NONE
   BACK
   FRONT
   ```

2. For strict culling-capable paths, define the canonical projected-NDC winding function in the spec.

3. Reject or diagnose strict culling when:

   ```text
   coordinate_space unsupported
   positions are not (N,3)
   View3D projection unavailable for DATA
   transform semantics are unresolved
   projected winding is ambiguous
   backend lacks relevant capability
   ```

4. Apply culling before depth, order, alpha, and query candidate selection.

5. For strict 3D opaque-depth eligibility, compute or conservatively validate effective opacity:

   ```text
   all color alpha == 1.0
   all texture alpha == 255
   opacity_policy does not introduce non-opaque behavior
   ```

6. If opacity cannot be proven, emit:

   ```text
   mesh3d_alpha_not_strict
   ```

### Matplotlib behavior

Matplotlib should be treated as a reference/adapted backend for this boundary.

Recommended sequence:

1. Implement the canonical projected-NDC winding calculation in CPU code.
2. Apply CPU face filtering before constructing 2D polygon collections.
3. Emit `mesh3d_face_culling_adapted` unless and until visual fixtures demonstrate exact culling behavior for the supported subset.
4. Continue documenting 3D mesh depth as adapted painter sorting.
5. Do not advertise `meshvisual.positions3d.opaque_depth.v1`.
6. Do not advertise strict alpha behavior.
7. Keep rejecting or adapting non-opaque 3D meshes with `mesh3d_alpha_not_strict`.

Matplotlib may become useful as the conformance reference for winding classification, but not for strict 3D depth.

### Datoviz behavior

Datoviz should wait for public runtime evidence.

Recommended sequence:

1. Do not rely on private Vulkan state, private shader slots, mesh IDs, or backend-native handles.
2. Advertise `meshvisual.face_culling.data3d.projected_ndc.v1` only after public APIs demonstrate:

   * retained DATA-space View3D mesh rendering;
   * correct BACK/FRONT behavior;
   * correct reversed `xlim` / `ylim` behavior;
   * culling before depth writes;
   * no framebuffer-y convention leakage.
3. Advertise culling plus `meshvisual.positions3d.opaque_depth.v1` only after strict less-depth runtime proof exists for the same retained DATA-space path.
4. Do not advertise `query.view3d.mesh_triangle_pick.face_culling.v1` until a public, canonical face identity path exists.
5. Keep `texture2d_unlit` strict-depth promotion blocked until sampler, origin, color, and alpha proof exist through public APIs.

### VisPy2 producer behavior

VisPy2 should expose protocol fields, not backend handles.

Recommended behavior:

1. Allow producers to set:

   ```text
   face_culling = NONE | BACK | FRONT
   opacity_policy = ORDINARY_ALPHA
   ```

2. Validate obvious strict conflicts early:

   * non-opaque 3D mesh in strict-depth context;
   * texture alpha below `255`;
   * culling with unresolved 3D transform;
   * requested strict pick with culling but no query culling capability.

3. Emit GSP protocol records without backend-native objects.

4. Do not promise that ordinary alpha is strict.

5. Do not expose Datoviz mesh handles, Vulkan handles, or native controller objects.

---

## 9. Risks / Non-Goals

Primary overclaiming risks:

* using source vertex order as if it directly defined front/back in 3D;
* using backend screen-space winding after y-down framebuffer mapping;
* assuming GPU default front-face state matches GSP panel-NDC semantics;
* claiming culling support without testing reversed `xlim` / `ylim`;
* claiming strict culling while silently ignoring transforms;
* claiming strict depth for non-opaque alpha;
* treating painter-sorted Matplotlib output as strict depth;
* treating ordinary alpha as a blend contract;
* allowing texture alpha below `255` into strict opaque-depth paths;
* coupling culling to expanded query payloads prematurely;
* relying on private Datoviz/Vulkan implementation details as protocol evidence.

Non-goals for this v1:

```text
full rendering engine semantics
transparent 3D rendering
OIT
alpha test/discard
scene graphs
3D transform stacks
backend-native mesh identity
expanded picking payloads
strict clipping of partially clipped triangles
```

The clean boundary is: **accept projected-NDC culling as strict and capability-gated; keep alpha strictness opaque-only; document all non-opaque 3D alpha as adapted or unsupported until a separate alpha consultation defines blend, order, and query semantics.**

