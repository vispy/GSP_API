# M211 - S050 culling and alpha semantics consultation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Blocked pending ChatGPT Pro consultation.

## Summary

Prepare and resolve a self-contained ChatGPT Pro consultation before accepting strict 3D culling or
non-opaque mesh alpha semantics.

## Required Context

- `.agent/S050_STRICT_3D_DEPTH_MESH_SCOPING.md`
- `spec/view3d.md`
- `src/gsp/protocol/visuals.py`
- `src/gsp/protocol/view3d.py`

## Deliverables

- Create a consultation packet under `.agent/consultations/`.
- Ask for explicit semantics for face winding, front/back culling, transform interactions,
  query behavior, alpha blending, and capability naming.
- Do not implement dependent behavior until the user provides the consultation result.

## Stop Conditions

- Stop before changing public culling or alpha semantics without an accepted consultation response.
- Stop before using existing source code as authority where it conflicts with spec silence.
