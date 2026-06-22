# M031-DATOVIZ-LIVE-OFFSCREEN-QUERY-RESULT-PROOF - Datoviz live offscreen query result proof

## Mission

M031

## Goal

Prove that GSP can queue a Datoviz v0.4-dev panel query, execute an offscreen render frame, poll a
resolved `DvzQueryResult`, and decode it into a GSP `QueryResult`.

## Acceptance

- Point and image visuals opt into Datoviz query capabilities with `dvz_visual_set_query_capabilities()`.
- `DatovizV04ProtocolRenderer.query_panel()` renders an offscreen frame before polling when the
  v0.4 facade exposes offscreen render symbols.
- The smoke harness has a `--require-live-query-hit` gate.
- The updated local Datoviz wheel-stage plus repaired wheel runtime libraries produce a decoded live
  hit through GSP.

## Result

Completed. The live smoke returns `live_query_status=hit`, `live_query_hit=true`, and a decoded
`visual_id`. In the current mixed v0.4-dev artifact, Datoviz still leaves
`visual_family`, `item_id`, `texel`, displayed color, and value payload fields unset in the live
result even though the struct exposes those fields and synthetic readback works.

## Stop conditions

Stop before editing the Datoviz repository, claiming guide/all-rendered query parity, or claiming
complete identity/value payload parity until the Datoviz live runtime fills the corresponding
`DvzQueryResult` fields.
