# M088 - S025 VisPy2 mesh producer API and examples

## Stage

S025 - Mesh and 3D Geometry Visuals v1

## Status

Draft.

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
