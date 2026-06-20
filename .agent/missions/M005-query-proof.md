# M005 - Query proof

## Goal

Implement the first GSP panel-query proof: point-over-image query in the reference backend, with a schema compatible with future Datoviz GPU query.

## State

Completed in the current Codex session.

## Required reading

- `docs/datoviz_v04_gap_analysis.md`
- `spec/query.md`
- `src/gsp/protocol/`
- `src/gsp/protocol/visuals.py`
- `src/gsp_matplotlib/protocol_renderer.py`

## Scope guard

Implement the first query proof in the Matplotlib/reference path. Keep the schema compatible with Datoviz v0.4 query concepts, but do not implement the Datoviz query backend until `DvzQueryResult` is decodable from Python.

## Stop conditions

Stop for ChatGPT Pro consultation if query semantics conflict with visual/transform semantics.

## Result

- Added first query request/result schema in `gsp.protocol.query`.
- Added CPU-side Matplotlib/reference query proof in `gsp_matplotlib.protocol_query`.
- Added focused tests for point-over-image frontmost hits, image texel/value hits, and misses.
- Left Datoviz query implementation deferred until `DvzQueryResult` is decodable from Python.
