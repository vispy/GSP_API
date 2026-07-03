# M209 - S050 strict opaque depth fixture plan

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Design the minimal GSP-local fixture and acceptance plan for strict opaque View3D mesh depth. This is
a protocol/test planning mission, not a backend promotion mission.

## Required Context

- `.agent/S050_STRICT_3D_DEPTH_MESH_SCOPING.md`
- `spec/view3d.md`
- `spec/view3d_mesh_triangle_picking.md`
- `src/gsp/protocol/view3d.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `tests/test_matplotlib_protocol_renderer.py`
- `tests/test_visual_qa_harness.py`

## Deliverables

- Define a small overlapping-geometry fixture that distinguishes strict fragment-depth behavior from
  average-face CPU sorting.
- Identify which checks are protocol-only, Matplotlib adapted-reference checks, and Datoviz runtime
  checks.
- Record exact promotion criteria for `meshvisual.positions3d.opaque_depth.v1`.
- Leave backend capability advertisements unchanged.

## Stop Conditions

- Stop before claiming any backend provides `meshvisual.positions3d.opaque_depth.v1`.
- Stop before adding culling, transparency, barycentric, or multi-hit semantics.
- Stop if the fixture design requires Datoviz mesh-pick identity; that is blocked by M200/M205.

## Result

Completed locally. See `.agent/S050_STRICT_OPAQUE_DEPTH_FIXTURE_PLAN.md`.

Outcome: defined an overlapping opaque-triangle fixture that distinguishes strict per-fragment
depth from average-face painter sorting, plus protocol-only, Matplotlib adapted-reference, Datoviz
fake-adapter, and Datoviz runtime acceptance checks. No capability advertisements changed.
