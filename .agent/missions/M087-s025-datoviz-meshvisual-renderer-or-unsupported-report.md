# M087 - S025 Datoviz MeshVisual renderer or unsupported report

## Stage

S025 - Mesh and 3D Geometry Visuals v1

## Status

Draft.

## Summary

Implement the Datoviz MeshVisual adapter when evidence supports it, otherwise produce structured unsupported diagnostics.

## Planned Deliverables

- Map accepted MeshVisual fields to retained Datoviz v0.4 APIs.
- Use explicit capability gates for unsupported normals/materials/3D features.
- Add smoke coverage for PNG or unsupported reports.

## Acceptance

- Deliverables are complete, documented, and reflected in Mission Control status.
- New protocol semantics either match the accepted S025 ADR/spec baseline or remain explicitly blocked.
- Focused validation is recorded in the mission/task notes when implementation begins.

## Stop Condition

Stop if this requires legacy Datoviz paths or unverified material/ownership semantics.
