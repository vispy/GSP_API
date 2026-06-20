# DATOVIZ-V04-QUERY-BINDING - Expose query result decoding for Python GSP

Goal: make Datoviz v0.4 query results usable from the Python GSP adapter.

Finding from M004:

- `dvz_panel_query()`, `dvz_panel_query_now()`, and `dvz_scene_poll_query()` are exposed in the local Python facade.
- `DvzQueryRequest`, query enums, and capability flags are exposed.
- `DvzQueryResult` is exposed as a class but local introspection shows no `_fields_`, so Python code cannot decode status, hit, visual identity, resolved target/id, panel position, data position, or payload fields.

Needed Datoviz-side outcome:

- either expose `DvzQueryResult` fields in the generated ctypes binding;
- or provide a stable helper that converts `DvzQueryResult` to a Python dict/struct with documented fields.

GSP dependency:

- GSP Datoviz adapter must not advertise full query/readback support until this is solved.
