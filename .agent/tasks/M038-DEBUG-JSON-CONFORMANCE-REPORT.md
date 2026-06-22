# M038-DEBUG-JSON-CONFORMANCE-REPORT - Debug-json conformance report

## Mission

M038

## Goal

Continue S018 with a minimal debug-json report that serializes semantic conformance replay results
without introducing NumPy/base64 array transport.

## Acceptance

- Report is JSON-safe with `json.dumps()`.
- Report includes backend pass/skip outcomes.
- Matplotlib replay query summaries are flattened into JSON-safe dictionaries.
- Datoviz skip reason is visible.
- Report explicitly marks itself as non-authoritative and omits array transport.

## Stop conditions

Stop before adding JSON schema authority, base64 array encoding, transport fixture files, pixel
comparison, or Datoviz runtime conformance replay.

## Result

Completed. `fixtures.conformance.debug_report.conformance_debug_report()` emits a non-authoritative
debug-json report for the current S018 conformance matrix.
