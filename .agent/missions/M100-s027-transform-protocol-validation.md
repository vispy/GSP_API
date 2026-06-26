# M100 - S027 transform protocol dataclasses and validation

## Stage

S027 - Transform, View, Camera, and Navigation Semantics

## Status

Completed.

## Summary

Implement the accepted S027 protocol-owned dataclasses, enums, validation, and diagnostics for
2D affine transforms, `View2D`, visual transform bindings, placement vocabulary, and transform query
payload shells.

## Deliverables

- Protocol enums for transform kind, view kind, placement, and inverse status.
- `AffineTransform2DResource`, inline affine transform, transform reference/binding, and `View2D`
  models.
- Validation diagnostics for bad shape, non-finite matrix values, non-affine matrices, singular
  transforms, unsupported kinds, invalid view limits, and unsupported deferred semantics.
- Focused unit tests for positive and negative validation cases.
- No Matplotlib, Datoviz, or VisPy2 implementation beyond protocol imports required for tests.

## Acceptance

- Focused protocol validation tests pass.
- New models follow `spec/transforms.md` and ADR-0019.
- Deferred public 3D camera/projection/controller behavior is rejected with structured diagnostics.

## Stop Condition

Stop if existing public source code already exposes incompatible transform/camera/view semantics.
Report the conflict instead of reconciling by invention.

## Completion Notes

- Added `gsp.protocol.transforms` with accepted S027 enums, resources, bindings, matrix validation,
  placement vocabulary, inverse statuses, and diagnostic codes.
- Tightened `View2D` validation to allow reversed finite limits and reject equal-aspect S027
  semantics.
- Added optional transform bindings to positional visual families without renderer application.
- Added `gsp.transform-query@0.1` payload shell and capability helpers.
- Added focused protocol tests.
