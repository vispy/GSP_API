# M250 - S059 linear filter protocol and fixtures

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Draft; depends on M249.

## Summary

Add the enum and appended MeshVisual field, validation and serialization compatibility, a test-only
CPU reference sampler, positive numeric fixtures, and negative diagnostic coverage.

## Acceptance

Old payloads remain nearest and round-trip compatibly; linear records are valid only for
`texture2d_unlit`; reference fixtures cover centers, interpolation, clamp, multiplication, alpha,
and shared-resource distinct filters.

## Stop Conditions

Stop if default omission cannot be preserved or fixtures depend on geometry edges, blending, or
unspecified perspective interpolation.
