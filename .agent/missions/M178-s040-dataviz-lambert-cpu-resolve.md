# M178 - S040 Datoviz Lambert CPU resolve implementation

## Stage

S040 - Datoviz Strict Flat Lambert Promotion

## Status

Completed by local-main-codex.

## Summary

Implement the P025/ADR-0027 CPU-resolved Datoviz strict S039 flat Lambert route and fixture-backed
capability promotion.

## Deliverables

- Datoviz adapter resolves S039 flat Lambert face colors before upload.
- Triangle-expanded or equivalent upload preserves one constant RGBA per canonical face.
- Native Datoviz lighting/material controls are not used for S039 strict support.
- Capability snapshot advertises S039 Datoviz capabilities only when prerequisites are satisfied.
- Focused positive and negative tests cover validation, upload shape, capability gates, and alpha
  diagnostics.

## Acceptance

- `flat_lambert` no longer raises `flat_lambert_unsupported` on supported CPU-resolved Datoviz path.
- Invalid S039 normals, generated normals, lights, coordinate spaces, missing `View3D`, and alpha
  cases fail before upload with structured diagnostics.
- Adjacent faces with different Lambert colors upload without shared-vertex color interpolation.
- Existing Datoviz View3D, unlit mesh, and opaque-depth behavior remains intact.

## Stop Condition

Stop if the existing Datoviz mesh facade cannot preserve constant per-face colors through triangle
expansion or an equivalent representation.

## Result

Completed. Implemented CPU-resolved S039 flat Lambert colors in the Datoviz adapter, reused
triangle-expanded per-face upload for constant face colors, promoted S040 capability metadata, added
focused tests, and closed S040.
