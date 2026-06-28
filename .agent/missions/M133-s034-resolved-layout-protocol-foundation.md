# M133 - S034 resolved layout protocol foundation

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Implement the first bounded slice from the P016 `ANSWER`: create the resolved-layout specification
and protocol/capability foundation before backend layout-strict implementation work.

## Deliverables

- `spec/layout.md` with conformance tiers, `RenderTarget`, `ResolvedLayoutSnapshot`, logical pixel
  semantics, guide geometry, capability surface, and QA classification.
- Protocol models in `src/gsp/protocol/layout.py`.
- Capability schema expansion for layout, guides, fonts, render targets, and layout-aware query.
- Query request/result `layout_snapshot_id` fields.
- Conservative Matplotlib and Datoviz capability postures.
- Focused tests covering validation and capability adaptation.

## Acceptance

- Protocol tests pass for layout dataclasses, query snapshot identity, and capability adaptation.
- Existing protocol/capability tests remain compatible with conservative defaults.
- No backend claims `layout_strict` until a resolved layout snapshot implementation exists.
- Mission records identify follow-up work for Matplotlib, Datoviz, QA, and query/readback.

## Stop Condition

Stop before implementing backend strict layout if the protocol model or spec needs another
architecture decision. Stop before changing release state.

## Result

Completed. Added `spec/layout.md`, protocol layout models, layout-aware query snapshot ids,
capability records for layout/guide/font/render-target/query-layout support, conservative Matplotlib
and Datoviz capability posture, and focused validation tests.

Validation performed:

- `uv run python -m py_compile src/gsp/protocol/layout.py src/gsp/protocol/capabilities.py src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/capabilities.py src/gsp_datoviz/capabilities.py tests/test_layout_protocol.py`
- `uv run pytest tests/test_layout_protocol.py tests/test_protocol_spine.py tests/test_transform_protocol.py tests/test_axis_provider_capabilities.py -q`
- `uv run pytest -q` (`419 passed, 2 skipped`)

Remaining follow-up:

- Matplotlib resolved-layout reference implementation.
- Guide style field integration and resolved readback.
- Datoviz guide capability audit, grid clipping investigation, and diagnostics hardening.
- Tiered visual QA fixtures and layout-aware guide query/readback.
