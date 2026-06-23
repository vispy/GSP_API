# M052 - S020 no-network security validation

## Stage

S020 - Remote data and dynamic extension security pre-design

## Status

Completed by local-main-codex.

## Summary

Implemented the first runtime validation scaffolding for S020 without adding network or dynamic
extension execution. The protocol now has stable S020 security diagnostic codes, no-network source
descriptor validation, static manifest executable-field validation, deterministic redaction helpers,
and conservative capability fields.

## Deliverables

- `src/gsp/protocol/security.py`
- `src/gsp/protocol/data_sources.py`
- `src/gsp/protocol/extensions.py`
- `src/gsp/protocol/capabilities.py`
- `tests/test_s020_security_validation.py`

## Stop Condition

No real fetch, credential exchange, dynamic plugin loading, runtime shader loading, custom decoder
execution, or Datoviz remote-data requirement was added.
