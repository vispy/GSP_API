# Project Status

Canonical machine-readable status lives in `.agent/status.json`.

Use:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
```

Current state:

- Completed through M006 protocol hardening and conformance baseline.
- Current stage: S007 planning / next mission selection.
- Recommended next mission: M007 Datoviz v0.4 point/image adapter slice.

Notes:

- M006 accepted ADR-0003 as the GSP v0.1 vertical-slice mini-contract.
- The v0.1 conformance baseline lives under `fixtures/conformance/`.
- The local in-process path remains direct Python objects/NumPy/memoryview and does not require JSON/base64.
