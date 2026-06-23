# M063-S022-MOCK-HTTP-ARRAY-FIXTURES - Mock HTTP array fixtures

## Mission

M063

## Goal

Create no-network conformance fixtures for the configured/mock HTTP `.npy` array proof.

## Acceptance

- Fixtures advertise HTTP only as configured mock access with `network_io=false`.
- Positive fixture covers opaque handle, deterministic `.npy` bytes, materialized array shape/dtype
  and values, and optional Matplotlib rank-2 rendering/query.
- Negative fixtures cover forbidden descriptor fields, unknown handles, unsupported source
  contract, credential material, decoder plugin attempts, content-type/encoding failures, invalid
  `.npy`, oversized payloads, and query bounds.
- Redaction fixtures prove URLs, hostnames, headers, credentials, DNS results, cache keys, digests,
  raw bodies, and resolver private config are omitted or redacted.

## Stop conditions

Stop if fixtures require live network I/O, raw URLs in tracked fixtures, credentials, URL parsing,
DNS, redirects, TLS, persistent/shared cache, dynamic loading, or Datoviz remote-data behavior.

## Result

Completed. Added a packaged S022 mock HTTP array fixture and validator. The committed fixture
contains no raw response bodies, raw URLs, credentials, DNS results, cache keys, digests, or resolver
private config; deterministic `.npy` payloads are generated in memory during replay. Tests cover the
positive materialization/query case, descriptor and response rejection cases, capability metadata,
redaction placeholders, and cache-session isolation.
