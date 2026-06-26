# M101 - S027 Matplotlib transform/view reference behavior

## Stage

S027 - Transform, View, Camera, and Navigation Semantics

## Status

Completed.

## Summary

Implement strict Matplotlib/reference behavior for accepted S027 2D affine visual transforms,
linear `View2D`, family-specific transform application, clipping, and query inverse payloads.

## Deliverables

- Reference transform application for DATA/NDC positional visuals in the Matplotlib renderer.
- Deterministic `View2D` mapping, including reversed limits.
- Query/readback inverse payloads using `gsp.transform-query@0.1`.
- Focused render/query tests for point, marker, segment/path, text anchors, and mesh2d where
  existing reference code supports them.

## Acceptance

- Matplotlib strict reference behavior matches `spec/transforms.md`.
- Focused tests pass and existing Matplotlib visual/query tests remain green.
- No public 3D camera/projection/controller semantics are introduced.

## Stop Condition

Stop if applying transforms requires changing accepted transform order, coordinate reporting,
aspect/layout policy, or 3D/depth semantics.

## Completion Notes

- Added Matplotlib reference transform helpers for visual-local affine transforms, View2D mapping,
  NDC-to-axes conversion, and query payload identity.
- Added optional `view` and `transform_resources` parameters to accepted positional visual renderers.
- Added transformed CPU query support for point, marker, text, and strict 2D mesh query paths.
- Added `gsp.transform-query@0.1` payload output when transformed query context is active.
- Added focused Matplotlib renderer/query tests.
