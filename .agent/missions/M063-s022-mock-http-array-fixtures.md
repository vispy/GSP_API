# M063 - S022 mock HTTP array fixtures

## Stage

S022 - Remote source family selection and consultation

## Status

Completed.

## Summary

Add no-network/mock HTTP array fixtures and replay coverage after descriptor and `.npy` validation
exist.

## Planned Deliverables

- Mock configured HTTP access fixture using `gsp.fetcher.http.mock.v1` with `network_io=false`.
- Positive array materialization and optional Matplotlib rank-2 reference/query coverage.
- Negative, capability, redaction, and cache-isolation fixture records.

## Result

Completed. Added `fixtures/conformance/s022_http_mock_array.json` and replay validation for the
configured/mock HTTP `.npy` array proof. The fixture keeps network I/O disabled, uses only opaque
handles and generated in-memory `.npy` bytes, validates materialized shape/dtype/values plus bounded
array-value query, and covers descriptor negatives, mock response negatives, capability posture,
redaction, and session cache isolation.

Validation passed:

- `uv run ruff check`
- `uv run pytest -q`
- `uv run mypy src/ --strict --show-error-codes`
- `python -m json.tool .agent/status.json >/dev/null`
- `git diff --check`

## Stop Condition

Do not implement live HTTP fetch, URL parsing, DNS, credentials, redirects, TLS, sockets, persistent
cache, dynamic loading, or Datoviz remote-data behavior.
