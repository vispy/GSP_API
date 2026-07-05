# View3D Mesh Triangle Pick Geometry Payload

Status: accepted from P033 response.

Semantic purpose: define the first strict geometry payload expansion for
`query.view3d.mesh_triangle_pick.v1` without mutating the existing identity-only query contract.

## Capability

Strict geometry support is advertised by:

```text
query.view3d.mesh_triangle_pick.geometry.v1
```

Prerequisites:

```text
view3d.static.orthographic.v1
meshvisual.positions3d.data.view3d.v1
meshvisual.positions3d.opaque_depth.v1
query.view3d.mesh_triangle_pick.v1
```

Optional projected-facing support is advertised separately:

```text
query.view3d.mesh_triangle_pick.facing.v1
```

## Scope

`geometry.v1` inherits the accepted S044 v1 scope:

- orthographic `View3D`;
- `depth_mode="opaque_less"`;
- opaque, depth-writing, DATA-space `MeshVisual` triangle geometry;
- one panel point request;
- at most one result: frontmost visible supported triangle, miss, unsupported, stale, or invalid;
- public GSP visual ids and public canonical triangle indices only.

The existing `query.view3d.mesh_triangle_pick.v1` payload remains unchanged. `geometry.v1` is a
sibling capability/query kind, not optional opportunistic fields on v1 and not a broad v2.

## Hit Fields

For `status="hit"`, the v1 identity fields remain required and `geometry.v1` adds:

| Field | Type | Units / space | Requiredness |
|---|---|---|---|
| `hit_barycentric` | `tuple[float, float, float]` | Dimensionless barycentric coordinates relative to public source face vertex order `(i0, i1, i2)`. | Required on hit, absent on non-hit. |
| `hit_panel_ndc_z` | `float` | Panel NDC z: `-1` near, `+1` far, smaller closer. | Required on hit, absent on non-hit. |
| `hit_data_xyz` | `tuple[float, float, float]` | DATA-space hit coordinates. | Required on hit, absent on non-hit. |

When `query.view3d.mesh_triangle_pick.facing.v1` is advertised, hits additionally include:

| Field | Type | Units / space | Requiredness |
|---|---|---|---|
| `front_facing` | `bool` | P032 projected panel-NDC winding classification. | Required on hit only when facing capability is advertised; otherwise absent. |

No new per-request metadata and no new per-visual metadata are accepted. Do not add
`hit_panel_ndc_xyz`; the canonical panel-NDC hit position is:

```text
(panel_ndc_xy[0], panel_ndc_xy[1], hit_panel_ndc_z)
```

## Barycentric Semantics

For selected public triangle:

```text
primitive_index = k
faces[k] = (i0, i1, i2)
p0 = positions[i0]
p1 = positions[i1]
p2 = positions[i2]
```

`hit_barycentric = (lambda0, lambda1, lambda2)` is defined by:

```text
lambda0 + lambda1 + lambda2 = 1
hit_data_xyz = lambda0 * p0 + lambda1 * p1 + lambda2 * p2
```

The order is always the source face vertex order `(i0, i1, i2)`. It is not sorted,
winding-normalized, or remapped to backend draw order.

For the accepted orthographic DATA-space scope, this is equivalent to solving in projected panel
NDC:

```text
q0 = View3D.project(p0)
q1 = View3D.project(p1)
q2 = View3D.project(p2)

(panel_ndc_x, panel_ndc_y)
  = lambda0 * (q0.x, q0.y)
  + lambda1 * (q1.x, q1.y)
  + lambda2 * (q2.x, q2.y)
```

Because the accepted projection is affine, DATA/ray barycentrics and projected panel-NDC
barycentrics must agree in exact arithmetic.

Finite-precision tolerance:

```text
abs(sum(lambda) - 1.0) <= 5e-5
lambda_i may be as low as -5e-5 or as high as 1 + 5e-5 for valid edge/vertex hits
```

Implementations must not clamp or snap barycentrics before returning them.

No edge id or vertex id is inferred from barycentric values in this capability. A hit exactly on a
shared edge is still a triangle hit for the single triangle selected by the v1 frontmost/tie
behavior. First-wave conformance fixtures should avoid exact shared-edge and equal-depth ties except
for explicit ambiguity tests.

Projected-degenerate triangles have undefined barycentrics and must not produce geometry hits.
Partially clipped triangles, if later tested, keep barycentrics relative to the original public
source triangle, not generated clipped vertices. Initial fixtures should avoid clipping-boundary
hits.

## Depth And Hit Position

Accepted depth field:

```text
hit_panel_ndc_z: float
```

Definition:

```text
hit_panel_ndc_z = lambda0 * q0.z + lambda1 * q1.z + lambda2 * q2.z
```

Expected range is `[-1 - 5e-5, 1 + 5e-5]`.

Accepted DATA hit field:

```text
hit_data_xyz = lambda0 * p0 + lambda1 * p1 + lambda2 * p2
```

This is accepted only for orthographic `View3D`, DATA-space mesh positions, no mesh-local transform,
no instancing, and no perspective projection.

Deferred depth and ray fields:

```text
hit_camera_z
hit_camera_distance
hit_ray_t
hit_depth_normalized
raw_depth
backend_depth
```

Clients owning the matching `View3D` snapshot can derive camera-space depth:

```text
camera_z = near + (hit_panel_ndc_z + 1) * (far - near) / 2
```

## Facing

`front_facing` belongs to `query.view3d.mesh_triangle_pick.facing.v1`, not `geometry.v1`.

Definition:

```text
area2 > 0 => front_facing = true
area2 < 0 => front_facing = false
```

using the P032 projected panel-NDC winding rule. Do not return `culled` or `culling_state` now. For
a successful strict hit, `culled` would always be false; for a miss, many absent candidates may have
different culling states.

## Culling, Alpha, And Texture Interaction

P032 culling affects the candidate set, not the geometry field definitions. When
`query.view3d.mesh_triangle_pick.face_culling.v1` is advertised, culled and projected-degenerate
triangles behave as absent.

Alpha remains strict: eligible geometry requires effective alpha `1.0` everywhere. For textured
meshes, strict identity/geometry picking is eligible only when base alpha is `1.0` and every texture
alpha byte is `255`.

No UV, texel, texture id, displayed RGBA, material id, sampled color, or normal field is accepted
here.

## Deferred Capabilities

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

Multi-hit, vertex/edge picking, NDC3 picking, perspective picking, mesh-local transforms,
instancing, external model source maps, raw backend ids, and transparent picking require separate
accepted decisions.

## Diagnostics

Recommended diagnostics:

| Diagnostic | Meaning |
|---|---|
| `pick.unsupported.geometry_payload` | Backend supports identity v1 but not `geometry.v1`. |
| `pick.unsupported.no_public_primitive_map` | Backend hit cannot be mapped to public canonical `primitive_index`. |
| `pick.unsupported.no_public_geometry_reconstruction` | Backend cannot reconstruct barycentric/depth/DATA hit from public protocol state. |
| `pick.unsupported.no_public_panel_ndc_depth` | Backend exposes only raw or undocumented depth. |
| `pick.unsupported.projected_degenerate` | Selected or candidate triangle is projected-degenerate for geometry semantics. |
| `pick.unsupported.facing_payload` | Backend does not support `front_facing`. |
| `pick.unsupported.face_culling` | Scene requires culling-aware picking but backend does not advertise it. |
| `pick.unsupported.ndc3_mesh` | NDC3 mesh picking requested before `ndc3.v1`. |
| `pick.unsupported.perspective_projection` | Perspective View3D picking requested before `perspective.v1`. |
| `pick.unsupported.mesh_transform` | Mesh-local transform affects geometry before transform picking is accepted. |
| `pick.unsupported.instanced_mesh` | Instanced mesh requested before instancing query semantics. |
| `pick.unsupported.non_opaque_alpha` | Effective alpha is not strictly `1.0`. |
| `pick.unsupported.texture_attribute_readback` | UV/texel/color/material query field requested before attribute/readback capability. |
| `pick.unsupported.multi_hit` | Multi-hit requested before multi-hit capability. |
| `pick.unsupported.vertex_edge_pick` | Vertex/edge query requested through triangle-pick path. |
| `pick.invalid.panel_xy_outside` | Request panel point is outside the panel. |
| `pick.adapted.public_geometry_reconstruction` | Backend returned public triangle identity, and GSP reconstructed geometry fields from public protocol data. |

## Fixture Plan

Minimum positive fixtures before advertising `geometry.v1`:

- single orthographic DATA triangle with known interior barycentrics;
- sloped triangle with different vertex z values;
- two overlapping opaque DATA triangles at different depths;
- reversed `xlim` or `ylim`;
- non-axis-aligned camera basis;
- miss inside panel but outside triangle;
- stale `expected_pick_scene_snapshot_id`;
- geometry or depth-affecting scene change updates `pick_scene_snapshot_id`.

Minimum negative fixtures:

- NDC3 mesh returns `pick.unsupported.ndc3_mesh`;
- perspective `View3D` returns `pick.unsupported.perspective_projection`;
- non-opaque alpha returns `pick.unsupported.non_opaque_alpha`;
- texture alpha below `255` returns `pick.unsupported.non_opaque_alpha`;
- mesh-local transform returns `pick.unsupported.mesh_transform`;
- instancing returns `pick.unsupported.instanced_mesh`;
- missing public primitive map returns `pick.unsupported.no_public_primitive_map`;
- projected-degenerate triangle produces no geometry hit;
- outside panel returns `pick.invalid.panel_xy_outside`;
- miss omits identity and geometry fields.

Additional fixtures before advertising `facing.v1`:

- `area2 > 0` hit returns `front_facing=true`;
- `area2 < 0` hit with no culling returns `front_facing=false`;
- back-face and front-face culling cases prove culled triangles are absent when culling-aware
  picking is advertised.

## Datoviz Evidence

Datoviz must not advertise base mesh triangle picking or geometry payloads until public primitive
mapping is solved.

Sufficient public evidence for base v1:

```text
DvzQueryResult.visual_id maps to public GSP visual id through dvz_visual_id
face_id, primitive_id, or resolved_target/resolved_id reports a zero-based public triangle row
indexed meshes report MeshVisual.faces row, not GPU vertex id or draw primitive id
unindexed triangle-list meshes report emitted triangle ordinal
non-instanced mesh hits do not collapse to item_id = 0 or constant 1u
instanced ids are not misreported as triangle ids
freshness_serial or equivalent can support GSP pick_scene_snapshot_id freshness
```

For `geometry.v1`, native barycentric/depth/hit-position fields are optional if GSP can reconstruct
them from public GSP state after receiving a valid public triangle id. `DvzQueryResult.has_depth` and
`DvzQueryResult.depth` are useful only if their public semantics are documented. Raw Vulkan or
framebuffer depth is not public GSP evidence.
