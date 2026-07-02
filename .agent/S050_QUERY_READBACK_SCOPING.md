# S050 Query/Readback Scoping

Generated: 2026-07-03

## Decision

Proceed with a safe query/readback status refresh before attempting more implementation.

M200 found that Datoviz mesh-triangle picking cannot be promoted until Datoviz exposes upstream
face/triangle query identity and freshness evidence. That blocker is specific to
`query.view3d.mesh_triangle_pick.v1`; it does not block cleanup of current query/readback status or
bounded evidence around already implemented non-mesh paths.

## Current State

| Area | State | Notes |
|---|---|---|
| Data-scope point/image query | Implemented as bounded Datoviz queue/poll/decode path | Supports `QueryScope.DATA`, panel coordinates, and frontmost hit policy when v0.4 query bindings are present. |
| Live point/image rich payloads | Evidence gap | Historical M031 smoke reached `hit`, but the tested mixed runtime left `visual_family`, `item_id`, `texel`, displayed RGBA, and value unset. |
| Guide/all-rendered query | Capability-gated implementation exists | Current code routes guides/all-rendered to panel-frame guide hit/readback when Datoviz exposes snapshot and guide-hit APIs; older docs still describe it as fully deferred. |
| `hit_policy=all` | Unsupported in Datoviz path | Existing behavior should remain explicit unsupported unless native/global ordering evidence is proven. |
| Extension query payloads | Mostly unsupported outside accepted scalar payload decoration | Do not silently include unsupported extension payloads. |
| Screenshot capture | Implemented as PNG export | It is not scientific or linear readback. |
| Raw/scientific readback | Deferred | Requires separate semantic decision before implementation. |
| Mesh triangle picking | Blocked | Requires upstream Datoviz face/triangle query contract; see `.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md`. |

## Next Missions

| Mission | State | Purpose |
|---|---|---|
| M205 | approved | Refresh Datoviz query/readback docs/status and run guardrail tests without changing public semantics. |
| M206 | draft | Re-run live point/image payload evidence against current local Datoviz v0.4 runtime, if runtime setup is already available. |

## M205 Scope

M205 should:

- update stale Datoviz backend/query wording that still says guide/all-rendered query is universally
  deferred;
- preserve the distinction between capability-gated guide query and strict guide parity;
- keep `hit_policy=all`, unsupported extension payloads, scientific readback, and mesh-triangle
  picking explicitly unsupported/deferred;
- run focused tests around Datoviz guide query capability, data-scope query rejection rules, capture
  metadata, and mesh-pick guardrails.

## Stop Conditions

- Stop before changing public query semantics.
- Stop before advertising Datoviz mesh-triangle picking.
- Stop before treating PNG capture as scientific readback.
- Stop before editing the sibling Datoviz repository.
- Stop if live runtime evidence requires manual GPU/build/account setup.
