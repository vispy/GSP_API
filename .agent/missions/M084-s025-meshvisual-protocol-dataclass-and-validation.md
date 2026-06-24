# M084 - S025 MeshVisual protocol dataclass and validation

## Stage

S025 - Mesh and 3D Geometry Visuals v1

## Status

Draft.

## Summary

Implement the accepted MeshVisual protocol object, dtype/shape validation, and focused tests.

## Planned Deliverables

- Add protocol dataclass/enums only as accepted by M083.
- Validate positions, indices, colors/normals/material fields, coordinate space, and IDs.
- Add narrow unit tests.

## Acceptance

- Deliverables are complete, documented, and reflected in Mission Control status.
- New protocol semantics either match the accepted S025 ADR/spec baseline or remain explicitly blocked.
- Focused validation is recorded in the mission/task notes when implementation begins.

## Stop Condition

Stop on any mismatch with the accepted M083 contract.
