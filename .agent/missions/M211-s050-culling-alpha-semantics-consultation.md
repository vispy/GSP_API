# M211 - S050 culling and alpha semantics consultation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

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

## Packet

Prepared `.agent/consultations/P032-culling-alpha-semantics.md`.

Response archived as `.agent/consultations/P032-response.md`.

## Result

Completed. Accepted projected panel-NDC face culling as a small capability-gated v1 contract via
ADR-0030 and `spec/visuals/mesh_face_culling_alpha_s050.md`. Strict non-opaque 3D alpha remains
deferred; strict opaque-depth and strict mesh-triangle-pick paths require effective alpha `1.0`
everywhere. Opened M226 as the bounded implementation/fixture follow-up without changing renderer
capability advertisements.
