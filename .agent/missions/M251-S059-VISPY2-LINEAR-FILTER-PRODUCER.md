# M251 - S059 VisPy2 linear filter producer

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Approved; M250 completed.

## Summary

Add only the keyword-only `texture_filter="nearest"` argument to `Axes.mesh()`, lower it to protocol
state, validate invalid/inapplicable values, and advertise the producer-only linear capability.

## Acceptance

Existing calls emit nearest records unchanged; linear lowers exactly; invalid strings and linear
without both texture and UVs fail; no backend or general sampler vocabulary leaks into VisPy2.

## Stop Conditions

Stop if implementation requires another public sampler keyword or a renderer-specific object.
