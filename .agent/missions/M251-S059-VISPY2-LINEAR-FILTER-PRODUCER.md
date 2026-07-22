# M251 - S059 VisPy2 linear filter producer

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Completed.

## Summary

Add only the keyword-only `texture_filter="nearest"` argument to `Axes.mesh()`, lower it to protocol
state, validate invalid/inapplicable values, and advertise the producer-only linear capability.

## Acceptance

Existing calls emit nearest records unchanged; linear lowers exactly; invalid strings and linear
without both texture and UVs fail; no backend or general sampler vocabulary leaks into VisPy2.

## Stop Conditions

Stop if implementation requires another public sampler keyword or a renderer-specific object.

## Result

Added the single keyword-only `texture_filter` argument to `Axes.mesh()` with a nearest default,
lowering of string or protocol-enum values, and exact invalid/inapplicable failures. Existing mesh
calls retain nearest protocol output; linear textured calls emit `TextureFilter.LINEAR`. The
producer-only linear capability constant is exported separately from renderer support. Focused
VisPy2/protocol tests, Ruff, and strict mypy pass.
