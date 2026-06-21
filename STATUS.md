# Project Status

Canonical machine-readable status lives in `.agent/status.json`.

Use:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
```

Current state:

- Completed through M011 extensions and virtual data-source architecture proof.
- Current stage: M001-M011 foundation complete.
- Recommended next action: review the completed foundation and decide the next mission pack focus.

Notes:

- M006 accepted ADR-0003 as the GSP v0.1 vertical-slice mini-contract.
- The v0.1 conformance baseline lives under `fixtures/conformance/`.
- The local in-process path remains direct Python objects/NumPy/memoryview and does not require JSON/base64.
- M007 added a bounded Datoviz v0.4 protocol renderer using the local C-shaped `dvz_*` facade.
- Datoviz query support remains deferred until Python can decode `DvzQueryResult`.
- M008 added an experimental VisPy2 producer MVP that emits GSP protocol point/image visuals and renders through the Matplotlib reference backend.
- M009 hardened query statuses, query capability checks, and Datoviz query handoff tasks.
- M010 refreshed safe aisw provider inventory: Codex profiles `adikia`/`ibl` and Claude profile `main` are available as enabled providers. No credentials or tokens are recorded.
- M011 accepted ADR-0004, added static extension/data-source models, and proved a local fake tiled-image Matplotlib mosaic/query path without network or credentials.
