# M089-S025 - S025 MeshVisual query/readback and closeout

## Mission

M089

## Goal

Add accepted mesh query/readback semantics and close S025 with docs, QA notes, and next-stage recommendations.

## Status

Completed.

## Deliverables

- Implement item/face/vertex query payloads within M083 scope.
- Update docs/status and visual QA notes.
- Recommend the next stage, likely color mapping/colorbars or advanced image/data.

## Acceptance

- Mission output is committed or explicitly reported as blocked.
- Mission Control status is updated before closeout.
- Validation is proportional to the touched surface.

## Stop Conditions

- Stop if query semantics require new transform/material decisions not covered by M083.

## Completion Notes

- Added typed `MeshQueryPayload` and `MESH_QUERY_PAYLOAD_KIND`.
- Added Matplotlib/reference face-level query/readback for strict 2D `MeshVisual` with uniform or
  per-face RGBA.
- Kept vertex-colored mesh readback, edge/vertex picking, 3D query, barycentric coordinates, depth,
  normals, and interpolated RGBA deferred/capability-gated.
- Updated query, mesh, visual-family, and VisPy2 visual API specs.
- Closed S025 in Mission Control and recommended the next stage around color mapping/colorbars.
- Validation: `uv run pytest tests/test_matplotlib_protocol_query.py tests/test_protocol_spine.py
  tests/test_mesh_visual_protocol.py tests/test_matplotlib_protocol_slice.py
  tests/test_vispy2_protocol_mvp.py tests/test_visual_qa_harness.py`; `uv run ruff check
  src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_query.py
  tests/test_matplotlib_protocol_query.py`; `uv run ruff format --check
  src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_query.py
  tests/test_matplotlib_protocol_query.py`; `git diff --check`.
