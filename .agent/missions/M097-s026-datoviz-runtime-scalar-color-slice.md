# M097 - S026 Datoviz runtime scalar color slice

## Stage

S026 - Color Mapping, Colorbars, and Scalar Data Semantics

## Status

Completed.

## Summary

Implement or explicitly capability-gate a narrow Datoviz v0.4 runtime slice for accepted S026
scalar color behavior.

## Context

S026 public semantics are already accepted by P011/M091. M092-M096 added protocol validation,
Matplotlib reference behavior, visual QA/examples, Datoviz capability evidence, and VisPy2 producer
APIs. M095 found local Datoviz runtime candidates for scales, accepted colormaps including gray,
scalar sampled fields, visual scale binding, colorbars, point scalar colors, and query APIs.

This mission is implementation work, not protocol design.

## Outcome

- Added Datoviz adapter CPU pre-mapping for finite eager scalar `ImageVisual` color-scale rendering.
- Added Datoviz adapter CPU pre-mapping for `PointVisual` scalar color encodings.
- Moved canonical scalar color mapping helpers into `gsp.protocol.color_mapping` so Datoviz and
  Matplotlib share the same S026 LUT/normalization logic without a backend-to-backend import.
- Retained scalar source arrays and color-scale metadata for semantic scalar query payloads.
- Allowed requested `gsp.scalar-color-query@0.1` payloads through the Datoviz query wrapper and
  returns exact retained-data payloads when a point/image hit can be matched.
- Kept `ColorbarGuide` rendering/query capability-gated with structured unsupported diagnostics.
- Kept marker scalar fill capability-gated with structured unsupported diagnostics.
- Left mesh face scalar colors capability-gated.

## Validation

- `PYTHONPATH=src python -m pytest tests/test_datoviz_v04_protocol_renderer.py -q`
  - 61 passed.
- `PYTHONPATH=src python -m pytest tests/test_color_mapping_protocol.py tests/test_matplotlib_protocol_slice.py tests/test_matplotlib_protocol_query.py -q`
  - 57 passed.
- `PYTHONPATH=src python -m pytest tests -q`
  - 346 passed, 2 skipped.
- `PYTHONPATH=src python -m mypy src/gsp/protocol/color_mapping.py src/gsp_matplotlib/color_mapping.py src/gsp_datoviz/protocol_renderer.py src/gsp_datoviz/capabilities.py --strict --show-error-codes`
  - no issues in touched source files.
- `PYTHONPATH=src python -m ruff check src/gsp/protocol/color_mapping.py src/gsp_matplotlib/color_mapping.py src/gsp_datoviz/protocol_renderer.py src/gsp_datoviz/capabilities.py tests/test_datoviz_v04_protocol_renderer.py`
  - passed.
- `PYTHONPATH=src GSP_BACKEND=matplotlib python -c "import gsp; print('Matplotlib backend OK')"`
  - passed; Matplotlib used a temporary cache because `/Users/cyrille/.matplotlib` is not writable.
- `PYTHONPATH=src GSP_BACKEND=datoviz python -c "import gsp; print('DatoViz backend OK')"`
  - passed.
- `PYTHONPATH=src python -m mypy src/ --strict --show-error-codes`
  - still fails on existing repo-wide strict type debt and missing stubs outside this mission.

## Remaining Gates

- `ColorbarGuide` Datoviz rendering and `gsp.colorbar-query@0.1` remain gated until native colorbar
  layout, scale binding, tick-label, and ramp-query contracts are verified.
- Marker scalar fill remains gated until native or CPU-mapped fill-color contracts are verified.
- Mesh face scalar colors remain gated.
- Datoviz live runtime query payload parity still depends on backend query results carrying usable
  item/texel identity; when unavailable, requested scalar payloads return `unsupported` with
  `scalar_query_source_unavailable`.

## Acceptance

- Completed behavior follows `spec/color_mapping.md`, `spec/backends/datoviz.md`, and
  `spec/backend_capabilities_visuals.md`.
- No public S026 protocol/API semantics are changed.
- Marker scalar fill and mesh face scalar colors remain capability-gated unless native Datoviz
  contracts are verified inside this mission.
- Unsupported behavior emits existing structured diagnostics rather than silent fallback.
- Tests cover implemented paths and capability-gated paths.
