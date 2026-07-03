# M200 - S050 Datoviz native mesh-pick evidence spike

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by codex-ucl.

## Summary

Run a bounded evidence spike for Datoviz native View3D mesh triangle picking. The mission must
determine whether the current local Datoviz v0.4 source/runtime exposes enough public information
for GSP to safely implement and advertise `query.view3d.mesh_triangle_pick.v1`.

This is evidence work first, not capability promotion.

## Required Context

- `PROJECT_CHARTER.md`
- `ARCHITECTURE.md`
- `SPEC_INDEX.md`
- `spec/view3d_mesh_triangle_picking.md`
- `spec/view3d.md`
- `spec/query.md`
- `spec/backends/datoviz.md`
- `spec/backend_capabilities_visuals.md`
- `adr/ADR-0028-view3d-mesh-triangle-picking.md`
- `.agent/decisions/S044_view3d_mesh_triangle_picking.md`
- `.agent/S050_SCOPING.md`

## Deliverables

- Audit GSP Datoviz adapter code related to View3D, query capabilities, and current mesh-pick
  structured unsupported behavior.
- Inspect the local Datoviz v0.4 source/header/facade evidence from the sibling checkout without
  editing it.
- Record exact source/runtime symbols relevant to visual identity, primitive/triangle identity,
  pick framebuffer/result freshness, and View3D/layout revision matching.
- Produce one durable note under `.agent/`, for example `.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`.
- If GSP-only implementation is viable, draft the next implementation mission with focused tests
  and stop conditions.
- If Datoviz API support is insufficient, draft a handoff note describing the exact upstream API
  evidence needed.

## Acceptance

- The report clearly says one of:
  - GSP-only implementation is viable;
  - Datoviz upstream API work is required;
  - a protocol/architecture question blocks implementation.
- No public Datoviz capability is promoted.
- No sibling Datoviz files are edited.
- The current GSP worktree remains safe for follow-up implementation.

## Result

Completed locally in the current Mission Control session. See
`.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`.

Verdict: Datoviz upstream API work is required before GSP can safely implement or advertise
`query.view3d.mesh_triangle_pick.v1`. Current Datoviz source/facade exposes general mesh item
queries and public Datoviz visual ids, but not a public mesh triangle/face query path that returns
canonical triangle ids with freshness evidence tied to the pick scene.

## Stop Conditions

- Stop before editing `/Users/cyrille/GIT/Viz/datoviz` or any external repository.
- Stop before advertising Datoviz `query.view3d.mesh_triangle_pick.v1`.
- Stop before changing public GSP protocol semantics.
- Stop and create a ChatGPT Pro consultation packet if native Datoviz picking requires a new public
  GSP semantic decision.
- Stop if provider/runtime setup requires manual credential, account, or build-system intervention.

## Result

Completed as run `R20260703-091617-M200`. See
`.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`.

Outcome: Datoviz upstream API work is required before GSP can safely advertise
`query.view3d.mesh_triangle_pick.v1`. The local Datoviz v0.4 query plumbing exposes visual identity
and query result fields, but the current mesh query path does not populate a public canonical
face/triangle id for mesh hits.
