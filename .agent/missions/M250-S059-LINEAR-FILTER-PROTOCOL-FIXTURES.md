# M250 - S059 linear filter protocol and fixtures

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Completed.

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

## Result

Added the visual-owned `TextureFilter` enum and appended `MeshVisual.texture_filter` field with a
nearest default, exact applicability validation, and canonical nearest omission/linear emission.
Backend-neutral CPU fixtures pin texel centers and V orientation, bilinear interpolation,
clamp-to-edge behavior, straight-alpha channels, base-color multiplication, and distinct filters
sharing one texture. Focused protocol, artifact, numeric, Ruff, and strict mypy checks pass.
