# M061 - S022 array source descriptor validation

## Stage

S022 - Remote source family selection and consultation

## Status

Completed by local-main-codex.

## Summary

Implement no-network validation for the first-proof array source descriptor shape accepted by
ADR-0009.

## Planned Deliverables

- Protocol validation for `source_kind="array"`, `format="npy"`, `decoder_id`,
  `materialization_target`, opaque `preconfigured-source` handles, and forbidden fields.
- Stable diagnostics for source-contract, decoder-id, credential, fetch-descriptor, URL-like,
  path-like, cache-policy, and metadata violations.
- Tests proving validation performs no HTTP, URL parsing, DNS, file, credential, or dynamic loading
  work.

## Stop Condition

Do not implement HTTP fetch, URL parsing, DNS, credentials, decoder execution, network I/O, dynamic
loading, real resolver access, or production remote-source behavior.

## Result

Completed. Added `DataSourceKind.ARRAY`, stable S022 diagnostic codes, and
`validate_s022_http_array_source_descriptor()` for no-network descriptor validation. Added tests for
accepted descriptors and rejection of wrong source contract, direct remote fetch, credentials,
headers, decoder plugin attempts, bad contract details, and unsupported cache modes.
