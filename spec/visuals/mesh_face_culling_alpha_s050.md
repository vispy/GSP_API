# MeshVisual Face Culling And Alpha Boundary - S050

Status: accepted from P032 response.

Semantic purpose: define the first strict `MeshVisual.face_culling` contract for 3D triangle meshes
and keep non-opaque 3D alpha outside strict depth and strict picking semantics.

## Scope

Accepted in this boundary:

- projected-NDC front/back classification for `DATA` `(N,3)` meshes in `View3D`;
- panel-NDC front/back classification for `NDC` `(N,3)` meshes;
- strict `FaceCulling.BACK` and `FaceCulling.FRONT` behavior when capability-gated;
- strict exclusion of culled or projected-degenerate triangles from rendered-surface triangle
  picking;
- conservative effective-opacity rules for strict 3D opaque depth.

Deferred: strict transparent 3D rendering, alpha blend equations, transparency sorting, OIT, alpha
test/discard, strict transparent picking, strict clipping of partially clipped 3D triangles,
mesh-local 3D transforms, scene graphs, instancing, external model loading, backend-native mesh
handles, and expanded 3D query payloads.

## Projected Winding

For each source face:

```text
face = (i0, i1, i2)
```

Resolve panel-NDC vertices:

```text
q0 = (x0, y0, z0)
q1 = (x1, y1, z1)
q2 = (x2, y2, z2)
```

For `coordinate_space == DATA`, each `qk` is produced by the accepted `View3D` projection equations
in `spec/view3d.md`. For `coordinate_space == NDC` and `(N,3)` positions, each `qk` is the input
position directly.

The signed projected area is:

```text
area2 = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
```

Classification:

| Condition | Meaning |
|---|---|
| `area2 > 0` | front-facing |
| `area2 < 0` | back-facing |
| `area2 == 0` | projected-degenerate / ambiguous |

Front-facing means counter-clockwise in panel NDC x/y. `z` does not participate in winding
classification. Backend framebuffer or y-down pixel conventions must not flip the protocol result.

Reversed `View3D.xlim` or `View3D.ylim` affect classification because they affect panel-NDC
projection. One reversed axis flips winding; two reversed axes preserve winding.

## Culling Rule

`FaceCulling.NONE` keeps all non-projected-degenerate triangles.

`FaceCulling.BACK` suppresses triangles with:

```text
area2 < 0
```

`FaceCulling.FRONT` suppresses triangles with:

```text
area2 > 0
```

Projected-degenerate triangles have no strict raster contribution and no strict rendered-surface
pick hit.

Culling happens before depth test, depth write, visual order, alpha blending or adapted compositing,
and query hit selection.

A culled triangle produces no color contribution, performs no depth test or write, cannot occlude
another triangle, and cannot be returned by strict `query.view3d.mesh_triangle_pick.v1`.

## Transforms

Current 2D `VisualTransformBinding` semantics must not be silently mixed with strict `(N,3)` mesh
culling. Until 3D transform semantics are accepted, `face_culling != NONE` with a transform that
could affect `(N,3)` geometry must reject the strict culling path with
`mesh3d_culling_transform_conflict`.

Future accepted 3D transforms should be defined as part of the geometry-to-panel-NDC pipeline before
this winding test.

## Alpha Boundary

A 3D mesh is eligible for strict opaque depth only if its effective fragment alpha is provably
`1.0` everywhere.

For non-textured unlit or flat-Lambert meshes, every resolved mesh color alpha must be exactly
`1.0`. For `texture2d_unlit`, the S050 alpha equation remains:

```text
output.a = clamp(base.a * tex.a, 0.0, 1.0)
```

Strict opaque eligibility for textured meshes therefore requires:

```text
base.a == 1.0 everywhere
all texture alpha bytes == 255
```

If any effective alpha may be below `1.0`, the mesh must not participate in
`meshvisual.positions3d.opaque_depth.v1`, `query.view3d.mesh_triangle_pick.v1`, or strict 3D
opaque-depth conformance fixtures. Use `mesh3d_alpha_not_strict`; a more specific
`mesh3d_texture_alpha_not_strict` diagnostic may be used as detail for texture-alpha failures.

No v1 backend-neutral alpha blend equation is accepted.

## Capabilities

| Capability | Meaning |
|---|---|
| `meshvisual.face_culling.data3d.projected_ndc.v1` | Strict `FaceCulling` support for DATA `(N,3)` meshes in `View3D`, classified after projection into panel NDC. |
| `meshvisual.face_culling.ndc3.panel_winding.v1` | Strict `FaceCulling` support for NDC `(N,3)` meshes, classified directly in panel NDC. |
| `query.view3d.mesh_triangle_pick.face_culling.v1` | Strict 3D triangle picking excludes culled and projected-degenerate triangles using the same projected-NDC rule. |

These capabilities do not imply `meshvisual.positions3d.opaque_depth.v1`, alpha blending, strict
transparent rendering, or expanded query payloads.

## Diagnostics

| Diagnostic | Trigger | Required behavior |
|---|---|---|
| `mesh3d_face_culling_unsupported` | `face_culling != NONE` on a 3D mesh, but the backend lacks the relevant strict culling capability. | Do not silently ignore culling. Reject the strict path or render only as adapted behavior with this diagnostic. |
| `mesh3d_face_culling_adapted` | Backend applies approximate/reference-only culling but cannot satisfy the strict capability requirements. | Rendering may proceed as adapted, but no strict culling capability is advertised. |
| `mesh3d_culling_winding_ambiguous` | A source-nondegenerate triangle becomes projected-degenerate or numerically indistinguishable from zero area. | No strict raster contribution and no strict pick hit. Emit at most once per visual or fixture group. |
| `mesh3d_culling_transform_conflict` | `face_culling != NONE` and unresolved transform semantics could affect `(N,3)` geometry. | Reject strict culling for that visual. |
| `query_3d_mesh_culling_unsupported` | Strict triangle pick is requested on a culled visual, but query lacks `query.view3d.mesh_triangle_pick.face_culling.v1`. | Do not return hits that ignore culling. Reject or exclude the visual with this diagnostic. |
| `mesh3d_alpha_not_strict` | Any effective 3D mesh alpha may be below `1.0`. | Exclude from strict opaque-depth and strict 3D triangle-pick paths. |
| `mesh_alpha_unsupported` | Backend cannot render non-opaque mesh alpha even as adapted ordinary alpha. | Reject or omit the visual with diagnostic; do not substitute opaque rendering silently. |
| `mesh3d_alpha_depth_conflict` | Non-opaque 3D mesh is combined with a strict depth path or settings implying strict opaque-depth behavior. | Do not claim `meshvisual.positions3d.opaque_depth.v1`; reject strict rendering or adapt with diagnostics. |
| `mesh3d_texture_alpha_not_strict` | Optional structured detail when `texture2d_unlit` has any texture alpha byte below `255` in a strict 3D context. | Same required behavior as `mesh3d_alpha_not_strict`. |

`mesh3d_clipping_adapted` remains the diagnostic for strict behavior depending on partially clipped
3D triangles. Culling support does not imply strict clipping support.

## Query Semantics

For `query.view3d.mesh_triangle_pick.v1`, culling affects the candidate triangle set. Strict
candidates are DATA-space 3D mesh triangles that are fully opaque, pass the existing strict query
scope, are not culled, and are not projected-degenerate.

The v1 query payload is not expanded by this boundary. It continues to use public GSP visual id and
canonical source face identity. Backend-native mesh ids, Vulkan handles, private Datoviz triangle
ids, barycentrics, interpolated attributes, depth values, and `front_facing` fields remain deferred
to the separate 3D query-expansion track.

Non-opaque 3D meshes are excluded from strict mesh-triangle picking. No transparent-picking
semantics are accepted.

## Fixture Requirements

Before strict advertisement, a backend must pass fixtures covering:

- NDC3 basic winding: CCW kept by `BACK`, CW kept by `FRONT`;
- DATA `View3D` projected winding under normal bounds;
- reversed `xlim` and reversed `ylim` cases that catch source-order or object-space culling;
- framebuffer y-down trap where panel-NDC CCW remains front-facing;
- culling before depth, proving a culled near triangle does not occlude a farther kept triangle;
- culling before query for any backend claiming culling-aware picking;
- non-opaque color and texture-alpha negative fixtures.

Before advertising culling combined with strict opaque depth, the backend must also pass strict
less-depth runtime evidence for the same retained 3D path.

Before admitting textured meshes to strict opaque depth, the backend must prove base alpha is
`1.0`, every texture alpha byte is `255`, and sampling cannot introduce alpha below `1.0`.
