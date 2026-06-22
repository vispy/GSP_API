# M029-DATOVIZ-RUNTIME-QUERY-EXECUTION-PROOF - Datoviz runtime point/image query execution proof

## Mission

M029

## Goal

Wire the Datoviz v0.4 query queue/poll binding into the GSP adapter for bounded data-scope
point/image queries.

## Acceptance

- `DatovizV04ProtocolRenderer.query_panel()` queues with `dvz_panel_query()` and polls with
  `dvz_scene_poll_query()`.
- Returned `DvzQueryResult` objects decode into `gsp.protocol.QueryResult`.
- GSP request ids are preserved on runtime query results.
- Capability promotion is conditional on query binding readiness.
- Unsupported scopes, hit policies, and extension payloads remain explicit.

## Stop conditions

Stop before guide/all-rendered query support, `hit_policy=all`, extension payload support, live
GPU/headless runtime enforcement, v0.4 binding activation, or Datoviz repository edits.
