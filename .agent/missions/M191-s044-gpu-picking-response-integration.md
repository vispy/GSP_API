# M191 - S044 View3D mesh triangle picking response integration

## Stage

S044 - Datoviz Grid Clipping Proof And View3D Mesh Triangle Picking

## Status

Completed by local-main-codex.

## Summary

Integrate the ChatGPT Pro response for View3D mesh triangle picking into durable GSP authority
before implementation starts.

## Deliverables

- Archive the P028 response.
- Add or update ADR/spec text for View3D mesh triangle picking semantics.
- Decide query payload shape, identity model, occlusion/depth behavior, freshness requirements,
  capability names, and strict/adapted boundaries.
- Open or refine implementation missions for the accepted slice.

## Acceptance

- Public semantics are backend-neutral and do not expose Datoviz-native implementation details.
- `query.view3d.ray_readback.v1` remains distinct from any visual-hit capability.
- M192 can proceed only after accepted P028 decisions are recorded.

## Stop Conditions

- Stop if the P028 response is missing, ambiguous, or conflicts with project authority.
- Stop if the accepted design would require public Datoviz object ids, shader ids, pipeline names,
  or toolkit event concepts.

## Result

Completed. Archived `.agent/consultations/P028-response.md`, accepted backend-neutral
`query.view3d.mesh_triangle_pick.v1`, added ADR-0028,
`.agent/decisions/S044_view3d_mesh_triangle_picking.md`, and
`spec/view3d_mesh_triangle_picking.md`, and made M192 ready for implementation.
