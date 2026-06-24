# M084-S025 - S025 MeshVisual protocol dataclass and validation

## Mission

M084

## Goal

Implement the accepted MeshVisual protocol object, dtype/shape validation, and focused tests.

## Status

Draft.

## Deliverables

- Add protocol dataclass/enums only as accepted by M083.
- Validate positions, indices, colors/normals/material fields, coordinate space, and IDs.
- Add narrow unit tests.

## Acceptance

- Mission output is committed or explicitly reported as blocked.
- Mission Control status is updated before closeout.
- Validation is proportional to the touched surface.

## Stop Conditions

- Stop on any mismatch with the accepted M083 contract.
