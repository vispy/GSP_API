# M227 - S050 View3D mesh-pick geometry payload protocol

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

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

## Result

Completed locally.

Implemented the accepted S050 geometry/facing protocol surface without mutating the identity-only
`query.view3d.mesh_triangle_pick.v1` payload. Added public helpers for projected barycentric
coordinates, panel-NDC z interpolation, DATA-space hit interpolation, and projected facing. Added a
separate `View3DMeshTrianglePickGeometryPayload` for
`query.view3d.mesh_triangle_pick.geometry.v1`; geometry fields are required on hits and forbidden
on non-hits, while `front_facing` is emitted only through the opt-in facing path.

The Matplotlib CPU reference path now has an opt-in
`query_view3d_mesh_triangle_pick_geometry()` wrapper that reconstructs geometry from public GSP
scene records and keeps the existing identity-only query unchanged. Datoviz geometry/facing
capabilities remain unadvertised.

Focused validation passed:

- `uv run pytest tests/test_view3d_protocol.py tests/test_matplotlib_protocol_query.py -q`
- `uv run mypy src/gsp/protocol/mesh_pick_geometry.py src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_query.py --strict --show-error-codes`
- `python -m compileall -q src/gsp/protocol src/gsp_matplotlib tests/test_view3d_protocol.py tests/test_matplotlib_protocol_query.py`

Full-suite Datoviz fake/QA and full-tree mypy issues remain separate existing debt from M226.
