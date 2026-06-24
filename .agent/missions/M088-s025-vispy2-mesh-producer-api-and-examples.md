# M088 - S025 VisPy2 mesh producer API and examples

## Stage

S025 - Mesh and 3D Geometry Visuals v1

## Status

Completed.

## Summary

Expose a minimal VisPy2 producer for accepted mesh scenes without backend-specific calls.

## Planned Deliverables

- Add high-level mesh creation API according to M083.
- Add examples that emit formal GSP protocol scenes.
- Keep advanced materials/shading deferred unless accepted.

## Acceptance

- Deliverables are complete, documented, and reflected in Mission Control status.
- New protocol semantics either match the accepted S025 ADR/spec baseline or remain explicitly blocked.
- Focused validation is recorded in the mission/task notes when implementation begins.

## Stop Condition

Stop if the API starts exposing Datoviz draw calls or private renderer knobs.

## Completion Notes

- Added bounded VisPy2 mesh producer APIs that emit protocol `MeshVisual` objects without exposing
  Datoviz calls, private renderer knobs, materials, lights, textures, transforms, normals, culling, or
  depth state.
- Added a strict 2D protocol mesh example and API documentation.
- Added focused tests covering object emission, attachments, top-level helper behavior, example
  execution, and Matplotlib protocol rendering.
- Validation passed: 54 focused pytest cases, `ruff check`, `ruff format --check`, and
  `git diff --check`.
