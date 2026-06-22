# DATOVIZ-V04-CAPABILITY-PARITY - Translate Datoviz v0.4 capability snapshot

Goal: replace the Datoviz adapter's static capability surface with a bounded translation from
`dvz_capability_snapshot()`.

Finding:

- Local `../datoviz` on `v0.4-dev` exposes `dvz_capability_snapshot()`.
- Current `src/gsp_datoviz/protocol_renderer.py` returns a static `CapabilitySnapshot`.
- M018 found that the current GSP virtual environment imports Datoviz `0.3.5`, which does not expose
  `dvz_capability_snapshot()` or `DvzCapabilitySnapshot`.

Required GSP behavior:

- first establish a v0.4-dev Python facade/raw binding import path for runtime tests;
- translate Datoviz resource, texture, readback, shader, and query-profile flags into GSP
  `CapabilitySnapshot` fields where the mapping is clear;
- keep unknown/ambiguous Datoviz fields in `metadata` rather than overclaiming support;
- advertise `query_modes` only after `DATOVIZ-V04-QUERY-BINDING` and `DATOVIZ-V04-QUERY-PARITY`
  tests pass;
- advertise extension/tiled-source support only after explicit Datoviz implementation exists.

Acceptance:

- capability translation tests use a fake/synthetic Datoviz snapshot object;
- real `dvz_capability_snapshot()` smoke test skips cleanly if Datoviz is unavailable;
- no old v0.3 Datoviz API assumptions are introduced.
