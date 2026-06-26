# M102 - S027 Datoviz transform capability gates

## Stage

S027 - Transform, View, Camera, and Navigation Semantics

## Status

Completed.

## Summary

Add Datoviz S027 capability gates and explicit adaptation/unsupported diagnostics for accepted 2D
affine transforms, `View2D`, placement reporting, and query inverse support without hidden fallback.

## Deliverables

- Datoviz capability reporting for accepted transform placements and semantic transform support.
- Structured unsupported diagnostics for public 3D camera/projection/controller, image affine,
  virtual-source materialization, and missing query inverse support.
- Bounded CPU pre-transform adaptation only where finite eager arrays and retained source data make
  semantics explicit.
- Focused tests that prove no unsupported transform behavior is silently accepted.

## Acceptance

- Datoviz reports render support, query inverse support, and placement separately.
- Finite eager CPU adaptation, if implemented, is explicit in metadata/diagnostics.
- Virtual or huge source transforms are rejected/deferred rather than materialized.

## Stop Condition

Stop if Datoviz support requires changing accepted S027 semantics, adding public 3D camera behavior,
or silently materializing virtual/remote data.

## Completion Notes

- Added Datoviz S027 transform capability metadata and CPU-adapter placement reporting.
- Added bounded CPU pre-transform adaptation for finite eager NDC Point/Marker/Segment/PathVisual
  inline affine transforms.
- Added explicit unsupported behavior for named transform refs, transform query inverse payloads,
  mesh/text transforms, and deferred semantics.
- Added focused Datoviz tests.
