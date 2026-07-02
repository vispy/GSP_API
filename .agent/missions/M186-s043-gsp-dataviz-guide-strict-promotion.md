# M186 - S043 GSP Datoviz guide strict promotion

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Completed.

## Summary

Promote Datoviz guide rows from adapted to strict only where Datoviz provides full guide
layout/query/readback/all-rendered snapshot evidence.

## Deliverables

- Capability matrix updates promote Datoviz guide rows only when native guide identity, guide box,
  guide query, all-rendered guide query, rendered contribution, and layout snapshot id equality
  diagnostics are all native-verified.
- Visual QA Datoviz reports now probe a real guide box center and record row-specific guide
  query/readback diagnostics for review packs.
- Datoviz protocol renderer now routes guide/all-rendered guide queries through panel frame
  guide hit/readback and rejects stale layout snapshot ids.
- Tests cover guide identity, guide boxes, hit/readback payloads, contribution enumeration,
  `layout_snapshot_id` equality, stale snapshot rejection, and the native-grid-clip-only adapted
  boundary.

## Acceptance

- Every promoted row requires guide identity, guide box, hit/readback, contribution, and snapshot
  id evidence.
- Native grid clipping proof is credited without implying full guide strictness.
- Adapted rows remain adapted with precise blockers when the full guide evidence set is absent.

## Validation

- `uv run pytest tests/test_datoviz_v04_protocol_renderer.py tests/test_visual_qa_harness.py tests/test_axis_provider_capabilities.py -q`
- `uv run mypy src/ --strict --show-error-codes`
- `uv run ruff check src tests`
- `uv run pytest tests/ -q`
- `GSP_BACKEND=matplotlib uv run python -c "import gsp; print('Matplotlib backend OK')"`
- `GSP_BACKEND=datoviz uv run python -c "import gsp; print('DatoViz backend OK')"`
- `git diff --check`

## Stop Conditions

- Stop if any promoted row lacks guide identity, guide box, hit/readback, contribution, or snapshot
  id.
- Stop if grid clipping proof depends on overlay masking.
