# Project Status

Canonical machine-readable status lives in `.agent/status.json`.

Use:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
```

Current state:

- Completed through M007 Datoviz v0.4 point/image adapter slice.
- Current stage: S008 planning / next mission selection.
- Recommended next mission: M008 VisPy2 producer MVP.

Notes:

- M006 accepted ADR-0003 as the GSP v0.1 vertical-slice mini-contract.
- The v0.1 conformance baseline lives under `fixtures/conformance/`.
- The local in-process path remains direct Python objects/NumPy/memoryview and does not require JSON/base64.
- M007 added a bounded Datoviz v0.4 protocol renderer using the local C-shaped `dvz_*` facade.
- Datoviz query support remains deferred until Python can decode `DvzQueryResult`.
