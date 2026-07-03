# M216 - S050 Datoviz live point/image payload parity evidence

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Re-run live Datoviz point/image query payload evidence against the current local v0.4 runtime if the
runtime and GPU/offscreen setup are already available. Determine whether the historical M031 payload
gap still exists for `visual_family`, `item_id`, `texel`, displayed RGBA, and value.

## Stop Conditions

- Stop if runtime setup requires manual build, credential, account, or GPU/display intervention.
- Stop before editing the sibling Datoviz repository.
- Stop before weakening GSP payload requirements to match an incomplete native result.

## Result

Completed locally. See `.agent/S050_DATOVIZ_LIVE_POINT_IMAGE_PAYLOAD_EVIDENCE.md`.

The current Datoviz binding uses `dvz_panel_query_px()`. GSP now targets that current symbol only.

Live evidence at `artifacts/visual_qa/s050/m216-live-query-payload/smoke.json` shows:

- query binding ready;
- live point query returns `visual_family="point"` and `item_id=0`;
- live image query returns `visual_family="image"` and visual id but no `texel`, displayed RGBA, or
  value.

Capability posture was tightened accordingly: Datoviz advertises `panel-query` and `point-item`,
but no longer advertises `image-texel` until live image texel/color/value payloads are proven.
