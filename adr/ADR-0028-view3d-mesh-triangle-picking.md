# ADR-0028 - View3D Mesh Triangle Picking

## Status

Accepted

## Context

S036 accepted orthographic `View3D`, `(N, 3)` `MeshVisual` rendering, opaque-depth capability
gates, and `query.view3d.ray_readback.v1`. Ray readback returns a public camera/layout ray context;
it does not identify a rendered visual or primitive.

S044 reviewed whether the next query slice should be a Datoviz GPU picking feature or a
backend-neutral public picking protocol.

## Decision

Accept backend-neutral `query.view3d.mesh_triangle_pick.v1`.

The first strict picking capability is not "GPU picking" publicly. It is a View3D mesh-triangle
query that returns at most one result for a panel point: the frontmost visible supported opaque
DATA-space `MeshVisual` triangle, a miss, or a structured unsupported/stale/invalid result.

Strict S044 support is limited to orthographic `View3D`, `depth_mode="opaque_less"`, opaque
DATA-space `MeshVisual` triangle geometry, public GSP visual identity, public canonical triangle
indices, and a backend-neutral `pick_scene_snapshot_id` freshness boundary.

The response must identify both the public `visual_id` and public `primitive_index` for strict hits.
A visual-only strict v1 is rejected because it cannot prove the public primitive mapping needed for
conformance.

`query.view3d.ray_readback.v1` remains separate. It may share panel coordinate and snapshot
conventions, but it is not a prerequisite for picking and does not imply visual-hit support.

## Capability Boundary

Add:

```text
query.view3d.mesh_triangle_pick.v1
```

Prerequisites for strict support:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
```

Do not add public `query.view3d.gpu_pick.v1`; GPU is an implementation strategy. Reserve
`query.view3d.visual_pick.v1` for a broader future visual-level query.

## Deferred

NDC3 mesh picking, transparent meshes, non-mesh visuals, instancing, perspective projection,
culling semantics, textures, multi-hit selection, barycentric coordinates, interpolated DATA/world
hit positions, normalized or raw depth values, ray distance, backend event/controller objects, and
public Datoviz-native identifiers are deferred.

## Consequences

Matplotlib may provide a limited CPU reference oracle for strict-scope fixtures, with adapted
diagnostics. Datoviz may implement the query with any private GPU strategy, but returned ids must be
public GSP ids and public canonical triangle indices.

Backends must not encode unsupported or stale states as misses. They must return structured
diagnostics and must not claim strict support when native state, hidden draw ids, unsupported
occluders, stale pick buffers, or mismatched layout/view/projection state can affect the answer.

## Source

`.agent/consultations/P028-response.md` converted into this ADR and
`spec/view3d_mesh_triangle_picking.md`.
