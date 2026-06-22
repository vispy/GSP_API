# M025-DATOVIZ-V04-QUERY-DECODE-PARITY - Datoviz v0.4 query decode parity

## Mission

M025

## Goal

Map Datoviz v0.4 `DvzQueryResult` fields into GSP `QueryResult` using a pure decoder.

## Acceptance

- Datoviz query statuses map to GSP terminal statuses.
- Point hits map visual id, family, item id, and optional coordinates.
- Image hits map visual id, family, texel proxy, displayed RGBA, and value when present.
- Runtime smoke skips cleanly when the active Datoviz binding lacks decodable query fields.
- Datoviz `query_modes` remain unadvertised.

## Stop conditions

Stop before runtime query execution, capability promotion, application-id preservation, or Datoviz
repository edits.
