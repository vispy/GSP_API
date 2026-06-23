# M062 - S022 `.npy` decoder policy validation

## Stage

S022 - Remote source family selection and consultation

## Status

Completed by local-main-codex.

## Summary

Implement bounded no-network `.npy` decoder policy validation for trusted `gsp.decoder.npy.v1`.

## Planned Deliverables

- Safe `.npy` metadata/header validation for allowed version, dtype, rank, shape, C-order,
  declared byte length, and decoded byte limit.
- Rejections for pickle/object dtype, structured dtype, strings, void dtype, Fortran order, invalid
  magic/header, shape mismatch, trailing bytes, and oversized payloads.
- Tests over in-memory bytes only.

## Stop Condition

Do not implement HTTP fetch, URL parsing, DNS, credentials, network I/O, dynamic decoder plugins, or
production remote-source behavior.

## Result

Completed. Added no-network in-memory validation for trusted `gsp.decoder.npy.v1` policy. The
validator parses `.npy` header metadata without materializing arrays and rejects invalid magic,
unsupported versions, oversized headers, object/pickle payloads, structured/string/void dtypes,
Fortran order, big-endian dtype, shape/dtype mismatch, trailing bytes, excessive elements, and
decoded-byte limit violations.
