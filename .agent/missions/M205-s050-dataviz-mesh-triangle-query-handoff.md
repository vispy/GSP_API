# M205 - S050 Datoviz mesh triangle query upstream handoff

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Convert M200 evidence into a concise upstream Datoviz handoff for native mesh face/triangle query
identity. This keeps GSP Datoviz mesh triangle picking unsupported until Datoviz exposes a public,
tested canonical triangle id.

## Deliverables

- Add `.agent/S050_DATOVIZ_MESH_TRIANGLE_QUERY_HANDOFF.md`.
- Name exact Datoviz files/functions requiring inspection or change.
- Specify expected query result fields and id semantics.
- Specify minimal native fixture requirements.
- Keep GSP Datoviz `query.view3d.mesh_triangle_pick.v1` unadvertised.

## Acceptance

- Handoff names exact Datoviz files/functions requiring change.
- Handoff specifies required query result fields and canonical id semantics.
- Handoff includes minimal native fixture requirements.
- No Datoviz checkout files are edited.
- No GSP public protocol semantics or capabilities are changed.

## Result

Completed locally. See `.agent/S050_DATOVIZ_MESH_TRIANGLE_QUERY_HANDOFF.md`.
