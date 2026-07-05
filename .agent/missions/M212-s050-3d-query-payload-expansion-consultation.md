# M212 - S050 3D query payload expansion consultation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Prepare and resolve a self-contained ChatGPT Pro consultation for 3D query payload expansion beyond
S044 mesh triangle picking v1.

## Required Context

- `.agent/S050_STRICT_3D_DEPTH_MESH_SCOPING.md`
- `.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`
- `.agent/S050_DATOVIZ_MESH_TRIANGLE_QUERY_HANDOFF.md`
- `spec/view3d_mesh_triangle_picking.md`
- `src/gsp/protocol/view3d.py`

## Deliverables

- Create a consultation packet under `.agent/consultations/`.
- Ask for capability and payload design for barycentric coordinates, depth values, multi-hit
  results, vertex/edge expansion, and perspective/transform interactions.
- Keep `query.view3d.mesh_triangle_pick.v1` unchanged unless the accepted response directs a
  versioned extension.

## Stop Conditions

- Stop before expanding S044 v1 payloads without consultation output.
- Stop before relying on Datoviz private internals for public query identity.

## Packet

Prepared `.agent/consultations/P033-3d-query-payload-expansion.md`.

Response archived as `.agent/consultations/P033-response.md`.

## Result

Completed. Accepted `query.view3d.mesh_triangle_pick.geometry.v1` for required hit barycentric,
panel-NDC z, and DATA hit position fields, plus separate
`query.view3d.mesh_triangle_pick.facing.v1` for projected-facing payloads. Existing
`query.view3d.mesh_triangle_pick.v1` remains unchanged. Multi-hit, vertex/edge, NDC3, perspective,
transform, instancing, texture/material readback, raw backend depth, and backend-native ids remain
deferred. Opened M227 as the bounded protocol/fixture follow-up.
