# M214 - S050 Datoviz coordinate-space enum compatibility

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Ready.

## Summary

Audit and fix the GSP Datoviz adapter's use of `DvzVisualCoordSpace` against the current local
Datoviz Python facade so isolated offscreen review packs can reach the actual colorbar and retained
View3D rendering paths.

## Required Context

- `.agent/S050_DATOVIZ_OFFSCREEN_CRASH_ISOLATION.md`
- `.agent/S050_DATOVIZ_COLORBAR_EXPLICIT_TICK_PROOF.md`
- `.agent/S050_DATOVIZ_RETAINED_VIEW3D_DEPTH_PROOF.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `tests/test_visual_qa_harness.py`

## Deliverables

- Identify the current Datoviz facade coordinate-space enum names or integer values.
- Update GSP adapter compatibility code if this can be done without changing Datoviz itself.
- Add focused tests for DATA and VIEW/NDC coordinate-space selection.
- Rerun the M206 colorbar and M210 strict-depth isolated review-pack cases.

## Stop Conditions

- Stop before editing `/home/cyrille/GIT/Viz/datoviz`.
- Stop before promoting colorbar strictness or strict opaque depth without completed runtime evidence.
- Stop if the current Datoviz facade lacks enough public API to express the required coordinate
  spaces without private internals.
