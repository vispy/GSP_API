# M205 - S050 Datoviz query/readback status refresh

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Refresh Datoviz query/readback documentation and Mission Control status to match the current code
after S043-S050. This is a status/docs/guardrail mission, not new query semantics.

## Deliverables

- Update stale docs/spec wording that still describes guide/all-rendered Datoviz query as wholly
  deferred, while preserving capability gates and unsupported behavior for unverified builds.
- Preserve explicit unsupported boundaries for `hit_policy=all`, unsupported extension payloads,
  scientific/raw readback, and Datoviz mesh-triangle picking.
- Run focused Datoviz query/readback guardrail tests.
- Record a short closeout or status note.

## Acceptance

- Docs say Datoviz guide/all-rendered query is capability-gated by panel-frame snapshot and guide
  hit/readback APIs, not universally implemented or universally deferred.
- No public capability is promoted.
- Focused tests pass.

## Stop Conditions

- Stop before changing public query semantics.
- Stop before advertising Datoviz `query.view3d.mesh_triangle_pick.v1`.
- Stop before treating PNG capture as scientific readback.
- Stop before editing the sibling Datoviz repository.

## Result

Completed locally. See `.agent/S050_QUERY_READBACK_REFRESH.md`.

The Datoviz backend spec now distinguishes capability-gated guide/all-rendered query from older
fully-deferred wording. Mesh-triangle picking, `hit_policy=all`, unsupported extension payloads,
live rich payload parity, and scientific readback remain unpromoted.
