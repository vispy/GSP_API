# S050 View3D Mesh Pick Geometry Payload

Status: accepted from P033 response.

Authority:

- `adr/ADR-0031-view3d-mesh-pick-geometry-payload.md`
- `spec/view3d_mesh_triangle_pick_geometry.md`
- `.agent/consultations/P033-response.md`

## Decision

Keep `query.view3d.mesh_triangle_pick.v1` unchanged. Add sibling capability/query kind
`query.view3d.mesh_triangle_pick.geometry.v1` for required hit geometry fields:

```text
hit_barycentric
hit_panel_ndc_z
hit_data_xyz
```

Add separate facing capability:

```text
query.view3d.mesh_triangle_pick.facing.v1
```

`front_facing` uses the P032 projected panel-NDC winding rule and is not part of the base geometry
payload.

## Boundary

The accepted geometry payload is limited to the existing strict S044 scope: orthographic `View3D`,
opaque DATA-space mesh triangles, one panel point, frontmost visible supported triangle, public
`visual_id`, and public canonical `primitive_index`.

No v1 mutation, broad v2, multi-hit, vertex/edge picking, NDC3 picking, perspective picking,
texture/material readback, mesh-local transforms, instancing, external model source maps, raw
backend depth, or backend-native ids are accepted.

## Implementation Gate

Implement protocol models and fixtures first. Matplotlib may be a CPU reference/adapted path.
Datoviz remains unadvertised until public Datoviz APIs expose canonical public triangle identity;
after that, GSP can reconstruct geometry fields from public GSP scene records.
