# M212 - S050 3D query payload expansion consultation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Blocked pending ChatGPT Pro consultation.

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
