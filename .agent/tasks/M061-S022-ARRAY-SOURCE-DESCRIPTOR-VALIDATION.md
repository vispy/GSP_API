# M061-S022-ARRAY-SOURCE-DESCRIPTOR-VALIDATION - Array source descriptor validation

## Mission

M061

## Goal

Add no-network validation for the first S022 array source descriptor without materializing remote
data.

## Acceptance

- Valid descriptors use `source_kind="array"`, `format="npy"`, `decoder_id="gsp.decoder.npy.v1"`,
  `locality="preconfigured-source"`, `credential_policy="none"`, opaque source refs,
  `materialization_policy="full"`, and `materialization_target="array-resource"`.
- Invalid descriptors reject `source_kind="http"`, `fetch_descriptor`, direct remote locality,
  URL-like fields, path-like fields, credentials, headers, cookies, decoder import/plugin fields,
  and unsupported cache modes.
- Diagnostics use ADR-0009/S022 codes where needed and preserve existing S020 codes where they
  already fit.
- Tests verify no network, URL parsing, DNS, file access, credential lookup, decoder execution, or
  dynamic loading occurs.

## Stop conditions

Stop if validation requires HTTP fetch, URL parsing, DNS resolution, credentials, decoder execution,
network I/O, dynamic loading, Datoviz work, or production remote-source behavior.
