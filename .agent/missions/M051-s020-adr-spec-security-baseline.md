# M051 - S020 ADR/spec security baseline

## Stage

S020 - Remote data and dynamic extension security pre-design

## Status

Completed by local-main-codex.

## Summary

Recorded the P006 response and translated it into durable S020 governance artifacts. The resulting
baseline keeps v0.2 remote data limited to synthetic, in-memory, and optional preconfigured-source
handles; rejects arbitrary fetch by default; defers dynamic extension loading; and requires
redaction/negative conformance before runtime implementation.

## Deliverables

- `.agent/consultations/P006-response.md`
- `adr/ADR-0008-remote-data-dynamic-extension-security.md`
- `spec/data_sources.md`
- `spec/extensions.md`
- `spec/capabilities.md`
- `spec/conformance-fixtures.md`
- `docs/security/remote-data-and-extensions.md`

## Stop Condition

No runtime remote fetch, credential exchange, dynamic extension loading, or Datoviz remote-data work
was added.
