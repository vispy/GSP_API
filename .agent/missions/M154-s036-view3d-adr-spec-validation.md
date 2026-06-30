# M154 - S036 View3D ADR/spec and validation baseline

## Stage

S036 - Static View3D, Orthographic Projection, and 3D Mesh Baseline

## Status

Ready for local-main-codex.

## Summary

Convert the accepted P020 response into durable ADR/spec authority and add the first protocol
validation baseline for static orthographic `View3D`.

## Deliverables

- ADR for minimal static `View3D`, camera, orthographic projection, depth, and query boundary.
- `spec/view3d.md` or equivalent authoritative spec section.
- SPEC_INDEX update.
- S036 decision record under `.agent/decisions/`.
- Protocol dataclasses/enums/diagnostics for `Camera3D`, `OrthographicProjection3D`, `View3D`, and
  related capability/diagnostic vocabulary.
- Focused validation tests for valid camera/projection state and negative fixtures:
  degenerate camera, zero/parallel up, equal x/y bounds, invalid near/far, non-finite values, and
  unsupported projection kind.

## Acceptance

- Public authoring is camera-parameter-first: no public arbitrary view/projection matrix input.
- S036 supports orthographic projection only.
- Existing `CoordinateSpace.DATA` and `CoordinateSpace.NDC` remain the only public authoring spaces.
- Public 3D navigation, perspective, materials/lights, scene graph, and 3D picking are explicitly
  deferred.
- Focused protocol validation tests pass.

## Stop Condition

Stop if the ADR/spec would require public Datoviz camera objects, public perspective semantics,
matrix-first authoring, or changes to existing `(N, 2)` mesh/`View2D` semantics.

