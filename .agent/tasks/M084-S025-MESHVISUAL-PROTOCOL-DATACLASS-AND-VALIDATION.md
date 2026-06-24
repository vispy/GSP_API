# M084-S025 - S025 MeshVisual protocol dataclass and validation

## Mission

M084

## Goal

Implement the accepted MeshVisual protocol object, dtype/shape validation, and focused tests.

## Status

Completed.

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


## Completed

- Added S025 `MeshVisual` protocol dataclass and accepted enums.
- Implemented deterministic validation for positions, faces, color modes, normals, depth/culling/order, and degenerate triangles.
- Exported mesh protocol names from `gsp.protocol`.
- Added focused `tests/test_mesh_visual_protocol.py`.
- Validation: `uv run pytest tests/test_mesh_visual_protocol.py`; `python3 -m compileall -q src/gsp/protocol`; `git diff --check`.
