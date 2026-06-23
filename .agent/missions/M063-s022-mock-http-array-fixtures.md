# M063 - S022 mock HTTP array fixtures

## Stage

S022 - Remote source family selection and consultation

## Status

Pending.

## Summary

Add no-network/mock HTTP array fixtures and replay coverage after descriptor and `.npy` validation
exist.

## Planned Deliverables

- Mock configured HTTP access fixture using `gsp.fetcher.http.mock.v1` with `network_io=false`.
- Positive array materialization and optional Matplotlib rank-2 reference/query coverage.
- Negative, capability, redaction, and cache-isolation fixture records.

## Stop Condition

Do not implement live HTTP fetch, URL parsing, DNS, credentials, redirects, TLS, sockets, persistent
cache, dynamic loading, or Datoviz remote-data behavior.
