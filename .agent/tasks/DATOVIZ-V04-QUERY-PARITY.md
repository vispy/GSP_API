# DATOVIZ-V04-QUERY-PARITY - Match GSP query semantics in Datoviz adapter

Goal: implement Datoviz v0.4 query parity now that Python can decode `DvzQueryResult` in the local `../datoviz` checkout.

Depends on:

- `DATOVIZ-V04-QUERY-BINDING` decoder work in GSP

Required GSP behavior:

- advertise no Datoviz query modes until the decoded result path exists and is tested;
- enable `panel-query` only when Datoviz can distinguish hit, miss, outside-panel, unsupported,
  stale/dropped async results, and backend/readback failure;
- enable `point-item` only when Datoviz point hits can return a stable visual id and item id;
- enable `image-texel` only when Datoviz image hits can return texel coordinates, displayed RGBA,
  and source value or a clear diagnostic for unavailable source-value readback.

Acceptance:

- Datoviz adapter capability snapshot advertises only implemented query modes.
- Query tests skip cleanly when Datoviz runtime is unavailable.
- Datoviz query results map into `gsp.protocol.QueryResult` without backend-specific payload fields.

Recommended first slice:

- pure decode helper for `DvzQueryResult`;
- status enum mapping to GSP `QueryStatus`;
- visual family/target mapping to GSP `VisualFamily`;
- point item hit mapping;
- image texel/displayed RGBA mapping when payload fields are present;
- no Datoviz source-value readout claim unless value fields are populated and semantics are verified.
