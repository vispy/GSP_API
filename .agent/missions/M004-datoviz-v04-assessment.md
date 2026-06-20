# M004 - Datoviz v0.4 adapter assessment

## Goal

Assess exactly how GSP point/image/query/capability concepts map to Datoviz v0.4 C/ctypes APIs and identify Datoviz API gaps before implementation.

## State

Draft.

## Expected output

- docs/datoviz_v04_gap_analysis.md
- updated spec/backends/datoviz.md
- external handoff task files for Datoviz repo if needed

## Legacy inputs

- `LEGACY_MAP.md`
- `src/gsp_datoviz/renderer/datoviz_renderer.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_points.py`
- `src/gsp_datoviz/renderer/datoviz_renderer_image.py`
- Datoviz-related examples under `examples/`

## Known observation from M002 validation

`PYTHONPATH=src python -c "import gsp; import gsp_datoviz"` failed in the current environment because `src/gsp_datoviz/renderer/datoviz_renderer.py` imports `datoviz._panel`, which is unavailable. Treat this as assessment input for the v0.4 gap analysis, not as an M002 regression.

## Scope guard

This is an assessment mission before implementation. Compare the legacy Datoviz adapter against Datoviz v0.4 public APIs, especially private imports, visual creation/update, panel mapping, offscreen screenshots, capability reporting, and query/readback feasibility.

## Stop conditions

This mission may require ChatGPT Pro consultation if a Datoviz v0.4 API break decision is needed.
