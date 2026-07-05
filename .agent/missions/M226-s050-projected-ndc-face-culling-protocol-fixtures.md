# M226 - S050 projected-NDC face culling protocol fixtures

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Ready.

## Summary

Implement the accepted P032/ADR-0030 protocol support and fixtures for strict projected-NDC
`MeshVisual.face_culling`, without advertising backend strict capability promotion.

## Required Context

- `adr/ADR-0030-mesh-face-culling-alpha-boundary.md`
- `spec/visuals/mesh_face_culling_alpha_s050.md`
- `spec/visuals/mesh.md`
- `spec/view3d.md`
- `spec/view3d_mesh_triangle_picking.md`
- `.agent/decisions/S050_mesh_face_culling_alpha_boundary.md`

## Deliverables

- Add or centralize canonical projected-NDC winding helpers for DATA and NDC `(N,3)` mesh triangles.
- Add focused protocol/fixture coverage for NDC3 winding, DATA projected winding, reversed `xlim`,
  reversed `ylim`, framebuffer-y trap, culling before depth, projected-degenerate diagnostics, and
  non-opaque alpha exclusion from strict paths.
- Keep renderer capability advertisements unchanged unless a backend passes the strict fixture gate.
- Preserve the existing `query.view3d.mesh_triangle_pick.v1` payload shape; do not add expanded
  query fields.

## Acceptance

- Fixtures encode the accepted projected-NDC culling semantics and alpha boundary.
- Existing `FaceCulling.NONE` behavior is unchanged.
- Unsupported backends do not silently ignore non-`NONE` culling in strict paths.
- No strict non-opaque alpha or expanded query payload behavior is accepted.

## Stop Conditions

- Stop before using backend-native front-face state, framebuffer coordinates, private Datoviz ids,
  or legacy material culling behavior as protocol authority.
- Stop if implementation requires mesh-local 3D transform semantics, transparent picking, or strict
  alpha blending.
