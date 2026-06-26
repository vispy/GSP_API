# M103 - S027 VisPy2 transform/view producer API

## Stage

S027 - Transform, View, Camera, and Navigation Semantics

## Status

Completed.

## Summary

Expose bounded VisPy2 producer conveniences for accepted S027 affine transforms and `View2D`
without exposing backend-native transform, camera, or controller objects.

## Deliverables

- VisPy2 affine2d constructor/convenience surface.
- Visual `transform=` support for accepted positional visual producers.
- View2D producer updates or aliases aligned with accepted `set_view2d` semantics.
- Focused tests proving VisPy2 emits GSP protocol records only.

## Acceptance

- VisPy2 emits `VisualTransformBinding`, `InlineAffineTransform2D`, or transform refs according to
  `spec/transforms.md`.
- Existing x/y limit methods continue to emit deterministic `View2D`.
- No Matplotlib transform object, Datoviz slot, shader handle, or public camera/controller object
  enters the API.

## Stop Condition

Stop if API design requires public 3D camera/projection/controller semantics or transform graphs.

## Completion Notes

- Added `vispy2.affine2d()` producer convenience for inline S027 affine transform bindings.
- Added `transform=` support to point, marker, segment, path/plot, text, and mesh producer methods.
- Added explicit `Axes.set_view2d()` convenience while preserving existing x/y limit APIs.
- Added focused VisPy2 tests proving protocol transform records are emitted.
