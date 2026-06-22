# GSP Conformance Fixtures - Draft

Conformance fixtures define stable semantic behavior for the v0.1 reference path.

## M036 in-process replay harness

The first S018 replay layer is Python/in-process only. It replays existing conformance fixtures
without JSON/base64 serialization and returns semantic results for:

- capability snapshot identity and advertised extension surface;
- point-over-image query frontmost behavior;
- guide tick hit and guide miss behavior;
- local tiled-source clipped mosaic and typed query payload behavior.

This harness is not a transport encoding and is not a schema authority. JSON/base64 fixture files,
debug-json replay, backend matrices, and pixel/image comparison remain follow-up S018 work.

## M037 backend conformance matrix

The backend matrix is still Python/in-process. It records expected replay outcomes explicitly:

- `matplotlib`: `pass`, using the deterministic reference replay harness;
- `datoviz`: `skip`, with a diagnostic reason derived from the active Python binding state.

The Datoviz entry is intentionally present even before it can pass. This keeps conformance reports
honest: Datoviz is visible in the matrix, but skipped until a backend replay adapter can map stable
application visual IDs and define guide/tiled-source expectations.

This matrix is not a runtime certification suite and does not add JSON/base64 fixtures.

## M038 debug-json report

The debug-json report serializes the current semantic replay summary into JSON-safe dictionaries.
It is intended for inspection and lightweight report comparison only.

Required properties:

- includes backend outcomes from the conformance matrix;
- includes Matplotlib semantic replay query summaries;
- includes the Datoviz skip reason;
- omits NumPy arrays and memory buffers;
- sets `schema_authority=false`.

This report is not the versioned fixture schema and is not a base64 array transport.

## M039 diagnostic report hardening

`conformance_debug_report_json()` and `tools/conformance_debug_report.py` provide deterministic,
sorted, newline-terminated JSON output for diagnostics.

The report remains diagnostic:

- `schema_authority` stays `false`;
- output is stable enough for local inspection and CI logs;
- consumers must not treat the report shape as the versioned compatibility schema;
- array/base64 transport remains deferred.
