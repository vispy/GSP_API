# ADR-0031 - View3D Mesh Pick Geometry Payload

## Status

Accepted

## Context

S044 accepted `query.view3d.mesh_triangle_pick.v1` as an identity-only, backend-neutral query for
the frontmost strict-scope opaque DATA-space `MeshVisual` triangle. P032 later accepted
projected-NDC face culling and culling-aware picking as an additive capability, while leaving the
v1 payload unchanged.

P033 reviewed whether to add barycentric coordinates, depth, hit position, facing, multi-hit,
vertex/edge picking, perspective, texture/material readback, and backend-native fields.

## Decision

Keep `query.view3d.mesh_triangle_pick.v1` unchanged. Add a sibling strict geometry payload
capability:

```text
query.view3d.mesh_triangle_pick.geometry.v1
```

`geometry.v1` inherits all S044 prerequisites and response rules, and remains limited to
orthographic `View3D`, DATA-space opaque mesh triangles, `depth_mode="opaque_less"`, one panel point
request, and at most one frontmost visible supported triangle. On hits, it adds the required fields:

```text
hit_barycentric: tuple[float, float, float]
hit_panel_ndc_z: float
hit_data_xyz: tuple[float, float, float]
```

Do not add opportunistic optional fields to the existing v1 payload, and do not create a broad v2.
The expansion is separately advertised and independently testable.

Accept a separate facing payload capability:

```text
query.view3d.mesh_triangle_pick.facing.v1
```

When advertised, hits include:

```text
front_facing: bool
```

Facing uses the P032 projected panel-NDC winding rule. `area2 > 0` is front-facing and `area2 < 0`
is back-facing.

## Geometry Semantics

For selected public triangle `faces[k] = (i0, i1, i2)`, barycentric coordinates are ordered by the
public source face vertex order:

```text
hit_barycentric = (lambda0, lambda1, lambda2)
lambda0 + lambda1 + lambda2 = 1
hit_data_xyz = lambda0 * p0 + lambda1 * p1 + lambda2 * p2
```

The order is not sorted, winding-normalized, or remapped to backend draw order. For the accepted
orthographic DATA-space scope, DATA/ray barycentrics and projected panel-NDC barycentrics must agree
in exact arithmetic.

`hit_panel_ndc_z` is:

```text
hit_panel_ndc_z = lambda0 * q0.z + lambda1 * q1.z + lambda2 * q2.z
```

where `qk = View3D.project(pk)`. The panel-NDC depth convention remains `-1` near, `+1` far, smaller
is closer. The canonical panel-NDC hit position is:

```text
(panel_ndc_xy[0], panel_ndc_xy[1], hit_panel_ndc_z)
```

No separate `hit_panel_ndc_xyz` field is accepted.

## Tolerances

For returned barycentrics:

```text
abs(sum(lambda) - 1.0) <= 5e-5
lambda_i may lie in [-5e-5, 1 + 5e-5] at edges
```

Implementations must not clamp or snap barycentrics before returning them. First-wave fixtures
should avoid exact shared edges, equal-depth ties, near-zero projected area, and clipping-boundary
hits.

`hit_panel_ndc_z` fixtures should compare with `abs_tol <= 5e-5`. `hit_data_xyz` fixture tolerance is
per-component:

```text
<= max(1e-6, 5e-5 * max(1, selected_visual_bbox_diag))
```

## Deferred

Deferred after this ADR:

- camera-space depth, normalized depth-buffer values, raw backend depth, ray distance;
- UV, texel, texture id, displayed RGBA, base color, scalar value, material id, and normals;
- multi-hit / `hit_policy="all"` 3D picking;
- vertex and edge picking;
- NDC3 mesh picking;
- perspective picking;
- mesh-local transforms, instancing, and external model loading;
- backend-native ids and handles.

Reserved future capability names are listed in
`spec/view3d_mesh_triangle_pick_geometry.md`.

## Backend Expectations

Matplotlib may serve as a CPU reference/adapted path for geometry reconstruction. It should continue
to diagnose CPU reference behavior rather than claiming GPU fragment-depth strictness.

Datoviz must not advertise base mesh triangle picking or geometry payloads until public Datoviz
APIs expose canonical public triangle identity. After that upstream primitive-id blocker is solved,
GSP can reconstruct `hit_barycentric`, `hit_panel_ndc_z`, `hit_data_xyz`, and `front_facing` from
public GSP scene records. Native Datoviz barycentric fields are optional; private Datoviz state is
not public evidence.

## Source

`.agent/consultations/P033-response.md` converted into this ADR and
`spec/view3d_mesh_triangle_pick_geometry.md`.
