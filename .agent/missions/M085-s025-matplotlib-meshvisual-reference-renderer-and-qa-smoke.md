# M085 - S025 Matplotlib MeshVisual reference renderer and QA smoke

## Stage

S025 - Mesh and 3D Geometry Visuals v1

## Status

Completed.

## Summary

Add the Matplotlib reference slice and first visual QA smoke cases for MeshVisual.

## Planned Deliverables

- Render accepted 2D/3D mesh baseline cases in Matplotlib.
- Add QA cases for solid/indexed/per-vertex-color meshes within M083 scope.
- Emit contact-sheet/report artifacts.

## Acceptance

- Deliverables are complete, documented, and reflected in Mission Control status.
- New protocol semantics either match the accepted S025 ADR/spec baseline or remain explicitly blocked.
- Focused validation is recorded in the mission/task notes when implementation begins.

## Stop Condition

Stop if Matplotlib cannot represent a required accepted baseline without an explicit diagnostic.


## Completed

- Added `render_mesh_visual()` for the strict 2D Matplotlib reference subset.
- Added S025 visual QA suite and three strict MeshVisual smoke cases.
- Added MeshVisual scene-artifact serialization and QA runner dispatch.
- Kept Datoviz MeshVisual structured unsupported until M086/M087.
- Validation: `uv run pytest tests/test_mesh_visual_protocol.py tests/test_matplotlib_protocol_slice.py tests/test_visual_qa_harness.py`; `python3 -m compileall -q src/gsp_matplotlib src/gsp/qa/visual`; `git diff --check`.
