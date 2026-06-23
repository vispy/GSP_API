# M062 - S022 `.npy` decoder policy validation

## Stage

S022 - Remote source family selection and consultation

## Status

Pending.

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
