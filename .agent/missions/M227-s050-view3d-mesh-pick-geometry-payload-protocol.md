# M227 - S050 View3D mesh-pick geometry payload protocol

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Ready.

## Summary

Implement the accepted P033/ADR-0031 protocol surface and fixtures for
`query.view3d.mesh_triangle_pick.geometry.v1` and
`query.view3d.mesh_triangle_pick.facing.v1`, without changing the existing identity-only
`query.view3d.mesh_triangle_pick.v1` contract.

## Required Context

- `adr/ADR-0031-view3d-mesh-pick-geometry-payload.md`
- `spec/view3d_mesh_triangle_pick_geometry.md`
- `spec/view3d_mesh_triangle_picking.md`
- `spec/visuals/mesh_face_culling_alpha_s050.md`
- `.agent/decisions/S050_view3d_mesh_pick_geometry_payload.md`

## Deliverables

- Add protocol capability constants, payload fields/models, validators, and diagnostics for
  `geometry.v1` and `facing.v1`.
- Add public helper coverage for barycentric coordinates, panel-NDC z, DATA hit position, and
  projected facing.
- Add focused positive/negative fixtures for the accepted orthographic DATA-space strict subset.
- Keep Datoviz geometry capability unadvertised until public canonical triangle identity exists.

## Acceptance

- Existing `query.view3d.mesh_triangle_pick.v1` tests and payload shape remain unchanged.
- Geometry fields are required on geometry hits and forbidden on non-hits.
- Facing is separately gated and not silently emitted as an ungated optional field.
- Deferred multi-hit, vertex/edge, NDC3, perspective, transform, instancing, texture/material, and
  backend-native fields remain unsupported or absent.

## Stop Conditions

- Stop before mutating the v1 identity-only payload.
- Stop before using private Datoviz state, raw backend depth, backend-native ids, or undocumented
  depth semantics as public GSP fields.
