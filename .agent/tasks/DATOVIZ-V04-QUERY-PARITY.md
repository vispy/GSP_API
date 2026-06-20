# DATOVIZ-V04-QUERY-PARITY - Match GSP query semantics in Datoviz adapter

Goal: implement Datoviz v0.4 query parity after Python can decode `DvzQueryResult`.

Depends on:

- `DATOVIZ-V04-QUERY-BINDING`

Required GSP behavior:

- advertise no Datoviz query modes until the decoded result path exists;
- enable `panel-query` only when Datoviz can distinguish hit, miss, outside-panel, unsupported,
  stale/dropped async results, and backend/readback failure;
- enable `point-item` only when Datoviz point hits can return a stable visual id and item id;
- enable `image-texel` only when Datoviz image hits can return texel coordinates, displayed RGBA,
  and source value or a clear diagnostic for unavailable source-value readback.

Acceptance:

- Datoviz adapter capability snapshot advertises only implemented query modes.
- Query tests skip cleanly when Datoviz runtime is unavailable.
- Datoviz query results map into `gsp.protocol.QueryResult` without backend-specific payload fields.
