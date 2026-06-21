# DATOVIZ-V04-PARITY-NEXT-PACK - Recommended next mission pack

Goal: define the next Datoviz-focused work after M001-M011.

Current state:

- GSP has protocol spine, Matplotlib reference slice, query semantics, VisPy2 MVP, and extension/data-source proof.
- Datoviz adapter has only a bounded v0.4 point/RGBA8 image slice.
- Local `../datoviz` on `v0.4-dev` now exposes `DvzQueryResult._fields_`, unblocking query decode work that was previously deferred.

Recommended mission order:

1. Datoviz capability parity:
   - translate `dvz_capability_snapshot()` to GSP `CapabilitySnapshot`;
   - keep ambiguous fields in metadata;
   - advertise only proven features.
2. Datoviz query decode parity:
   - pure `DvzQueryResult` to GSP `QueryResult` decoder;
   - status/family/target/value mapping tests;
   - skip-clean runtime query smoke.
3. Datoviz image sampled-field parity:
   - use `dvz_sampled_field`, `dvz_sampled_field_set_data`, `dvz_visual_set_field`;
   - resolve scalar/float images, origin, interpolation, and color-scale semantics.
4. Datoviz capture/offscreen parity:
   - bounded PNG capture smoke using local v0.4 APIs;
   - no scientific readback claim.
5. Datoviz tiled-source follow-up:
   - only after sampled-field/capability/query foundations are stable;
   - map GSP tiled source materialization to Datoviz texture/field update path.

Non-goals:

- no old `datoviz.App` or `datoviz.visuals` API;
- no Datoviz repository edits from this GSP branch;
- no production remote fetch or credentials;
- no broad renderer rewrite before query/capability proof.
