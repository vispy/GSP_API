# M062-S022-NPY-DECODER-POLICY-VALIDATION - `.npy` decoder policy validation

## Mission

M062

## Goal

Add no-network, in-memory validation for trusted `.npy` decoder policy before any HTTP fetcher is
implemented.

## Acceptance

- `gsp.decoder.npy.v1` accepts only bounded, non-pickle `.npy` arrays with allowed dtype, rank,
  shape, C-order, and byte limits.
- Object, structured, string, unicode, void, Fortran-order, invalid-header, shape-mismatched,
  trailing-byte, and oversized payloads reject with stable diagnostics.
- Tests use deterministic in-memory bytes and do not perform network, file, URL, DNS, credential, or
  dynamic loading work.

## Stop conditions

Stop if decoder validation needs pickle, object dtype, dynamic imports, external plugins, HTTP,
network I/O, local file reads, credentials, or unbounded allocation.
