# M249 - S059 linear filter ADR and specification baseline

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Completed.

## Summary

Convert the archived P036 response into ADR-0034 and narrowly amend the S050/current protocol,
capability, diagnostic, backend, and VisPy2 specifications before public code changes.

## Acceptance

- `TextureFilter` and `MeshVisual.texture_filter` have exact ownership, default, applicability, and
  wire semantics.
- The bilinear rule, straight-alpha numeric interpolation, multiplication order, and `2/255`
  tolerance are normative.
- Existing nearest capabilities remain unchanged and the new renderer/producer capabilities are
  separately named.
- Deferred sampler concepts remain explicit.

## Stop Conditions

Stop if the response conflicts with ADR-0029 or requires sampler resources, resource-owned state,
broader color management, or a breaking default.

## Result

Added ADR-0034 and amended the accepted detailed/current Texture2D, capability, Datoviz, and VisPy2
specifications. The baseline preserves nearest behavior and existing capability meaning, defines
the linear formula and tolerance, and keeps all broader sampler concepts deferred. Specification
traceability, profile consistency, public-doc consistency, and strict MkDocs validation pass.
