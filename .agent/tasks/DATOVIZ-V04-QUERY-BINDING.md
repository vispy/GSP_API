# DATOVIZ-V04-QUERY-BINDING - Expose query result decoding for Python GSP

Goal: make Datoviz v0.4 query results usable from the Python GSP adapter.

Status: header layout refreshed by M018; runtime Python binding remains blocked in the current GSP
environment because `import datoviz` resolves to Datoviz `0.3.5` with no v0.4 `dvz_*` symbols.

Finding from M004:

- `dvz_panel_query()`, `dvz_panel_query_now()`, and `dvz_scene_poll_query()` are exposed in the local Python facade.
- `DvzQueryRequest`, query enums, and capability flags are exposed.
- During M004/M009, `DvzQueryResult` was exposed as a class but local introspection showed no `_fields_`, so Python code could not decode status, hit, visual identity, resolved target/id, panel position, data position, or payload fields.
- M018 inventory of `../datoviz` on `v0.4-dev` commit `bc9adbb40` found that the header
  `DvzQueryResult` struct now has the fields needed for a GSP decoder.

Current Datoviz-side outcome:

- `DvzQueryResult` fields are defined in the local v0.4-dev headers.
- The current GSP Python environment imports Datoviz `0.3.5`, so `DvzQueryResult` is not
  Python-visible there.
- Stability should still be confirmed against Datoviz release artifacts or maintained as a GSP
  compatibility assumption.

Expected Python-visible fields or helper keys:

- request identity or correlation id;
- query status/result status;
- hit boolean;
- target kind or visual family;
- visual identity or stable application-provided visual id;
- item id for point/item hits;
- pixel or texel coordinates for image hits;
- panel/framebuffer coordinate;
- visual/data coordinate if Datoviz resolved it;
- value kind and payload bytes/scalar/vector where available;
- displayed RGBA or enough information for GSP to reconstruct it;
- diagnostic/error text for unsupported, stale/dropped, or failed results.

GSP dependency:

- GSP Datoviz adapter must not advertise full query/readback support until a decoder maps these fields into `gsp.protocol.QueryResult`.
- Once solved, GSP can enable `panel-query`, then `point-item`, then `image-texel` incrementally.

Next implementation task:

- establish a v0.4-dev Python facade/raw binding import path for GSP tests;
- add a pure decoder from `DvzQueryResult` to GSP `QueryResult`;
- add synthetic ctypes-object tests where possible;
- add runtime query tests that skip cleanly if Datoviz runtime/offscreen execution is unavailable.
