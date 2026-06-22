# M039-DIAGNOSTIC-CONFORMANCE-REPORT-HARDENING - Diagnostic conformance report hardening

## Mission

M039

## Goal

Keep debug-json diagnostic and harden it with deterministic output plus a small tool entry point.

## Acceptance

- `conformance_debug_report_json()` returns sorted, indented, newline-terminated JSON.
- `tools/conformance_debug_report.py` prints the same deterministic report.
- Tests verify deterministic output and CLI parity.
- Docs/spec state that this remains non-authoritative and is not an array transport contract.

## Stop conditions

Stop before adding a versioned fixture schema, JSON/base64 array transport, Datoviz runtime
conformance pass requirements, or compatibility certification claims.

## Result

Completed. The diagnostic debug-json path is deterministic and tool-accessible while remaining
explicitly non-authoritative.
