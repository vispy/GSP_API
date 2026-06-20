# M005 - Query proof

## Goal

Implement the first GSP panel-query proof: point-over-image query in the reference backend, with a schema compatible with future Datoviz GPU query.

## State

Ready for Mission Control discussion. Launch only after explicit approval.

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
