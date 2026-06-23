# M053 - S020 security negative fixtures

## Stage

S020 - Remote data and dynamic extension security pre-design

## Status

Completed by local-main-codex.

## Summary

Added JSON conformance fixture records for S020 no-network security diagnostics and wired them into
fixture validation tooling. The fixture checks source descriptor rejection, executable manifest
rejection, redaction output, and conservative capability metadata without network I/O or dynamic
loading.

## Deliverables

- `fixtures/conformance/s020_security_negative.json`
- `fixtures/conformance/security_fixture.py`
- `tests/test_s020_security_fixtures.py`

## Stop Condition

No real fetch, credential exchange, dynamic plugin loading, runtime shader loading, custom decoder
execution, or Datoviz remote-data requirement was added.
