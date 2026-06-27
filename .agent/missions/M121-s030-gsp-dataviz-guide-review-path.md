# M121 - S030 GSP Datoviz guide review-path wiring

## Stage

S030 - Datoviz Guide Axis Proof

## Status

Completed.

## Summary

Wire the GSP Datoviz visual review path for guide/View2D rows only if M120 proves the required
Datoviz native-axis behavior.

## Scope

- `AxisGuide` and `PanelTextGuide` review-pack rendering for Datoviz.
- S029/S030 guide rows only.

## Deliverables

- Adapter wiring with structured unsupported diagnostics for any unproven guide semantics.
- Focused tests for explicit ticks, reversed domains, grid, labels, title placement, and query
  unsupported status.
- Regenerated guide review artifacts if behavior is supported.

## Stop Condition

Stop if Datoviz cannot express exact explicit ticks/labels, reversed-domain axis placement, or panel
title layout without approximation.

## Outcome

Completed by local-main-codex. The Datoviz visual QA path now renders the two guide/View2D rows as
adapted review artifacts:

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

Implemented scope:

- `DatovizV04ProtocolRenderer.configure_view2d_axes()` accepts explicit tick values/labels and
  wires them through `dvz_axis_set_ticks` when the facade exposes it.
- The Datoviz visual QA runner configures native panel axes from `AxisGuide` state instead of
  rejecting all guide rows.
- `PanelTextGuide` titles are deliberately not approximated; skipped title state is recorded in
  `guide_diagnostics`.
- Guide and all-rendered guide query remain unsupported in structured diagnostics.
- Capability matrix rows classify rendered Datoviz guide rows as `adapted` with reason code
  `datoviz_axis_guide_adapted_review`, not `strict`.

Evidence:

- Review pack: `artifacts/visual_qa/s030/m121-guide-review-path/index.md`
- Datoviz auto/grid artifact:
  `artifacts/visual_qa/s030/m121-guide-review-path/backends/datoviz/guide_view2d_auto_grid.png`
- Datoviz reversed/explicit artifact:
  `artifacts/visual_qa/s030/m121-guide-review-path/backends/datoviz/guide_view2d_reversed_explicit.png`
- Capability matrix:
  `artifacts/visual_qa/s030/m121-guide-review-path/capability_matrix.json`

Validation:

- `PYTHONPATH=. uv run pytest tests/test_datoviz_v04_protocol_renderer.py::test_datoviz_axis_provider_is_capability_gated tests/test_datoviz_v04_protocol_renderer.py::test_configure_view2d_axes_uses_verified_datoviz_v04dev_symbols tests/test_datoviz_v04_protocol_renderer.py::test_configure_view2d_axes_rejects_unavailable_or_strict_explicit_ticks tests/test_datoviz_v04_protocol_renderer.py::test_configure_view2d_axes_wires_explicit_ticks_when_binding_is_available -q`
- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py::test_s029_datoviz_guide_view2d_rows_stay_unsupported_with_specific_blockers tests/test_visual_qa_harness.py::test_s030_rendered_datoviz_guide_rows_are_adapted_not_promoted -q`
- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py tests/test_datoviz_v04_protocol_renderer.py -q`
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`

Remaining blockers for M122:

- Strict guide promotion still requires an accepted title/query policy.
- Datoviz guide and all-rendered guide query support remain unsupported.
