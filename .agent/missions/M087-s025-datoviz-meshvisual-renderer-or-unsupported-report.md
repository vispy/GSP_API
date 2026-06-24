# M087 - S025 Datoviz MeshVisual renderer or unsupported report

## Stage

S025 - Mesh and 3D Geometry Visuals v1

## Status

Completed.

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


## Completed

- Added Datoviz MeshVisual adapter entry point with explicit S025 structured unsupported diagnostics.
- Added `datoviz_v04_mesh_diagnostics()` and `datoviz_v04_mesh_ready()` gates.
- Routed visual QA MeshVisual Datoviz attempts through the adapter instead of ad-hoc runner rejection.
- Added focused Datoviz adapter tests for mesh unsupported/data/3D diagnostics.
- Validation: `uv run pytest tests/test_datoviz_v04_protocol_renderer.py tests/test_visual_qa_harness.py -q`; `python3 -m compileall -q src/gsp_datoviz/protocol_renderer.py src/gsp/qa/visual/runner.py`; `git diff --check`.
