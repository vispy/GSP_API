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
- Post-S011 roadmap accepted from `.agent/consultations/P003-response.md`.
- Current stage: S012 Matplotlib strict guide/tick provider baseline.
- M012 strict tick resolver and guide-provider foundation is complete.
- Next mission: M013 Matplotlib AxisGuide and PanelTextGuide rendering.
- Parallel planning priority: Datoviz v0.4 Python binding evidence and handoff.

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
- ADR-0005 defines semantic axis intent with capability-resolved realization providers.
- M012 added deterministic `auto-linear-nice-v0` tick resolution, explicit tick pass-through, and resolver tests.
