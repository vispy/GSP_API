# S030 Continuation Handoff

## Current State

S030 is closed. M120, M121, and M122 are complete.

Authoritative closeout:

- `.agent/S030_CLOSEOUT.md`
- `.agent/S030_DATOVIZ_GUIDE_AXIS_PROOF.md`
- `artifacts/visual_qa/s030/final-review-pack/index.md`
- `artifacts/visual_qa/s030/final-review-pack/capability_matrix.json`

## Final Decision

Datoviz guide/View2D rows are rendered review artifacts but remain `adapted`, not `strict`:

| Case | Datoviz status | Reason code |
| --- | --- | --- |
| `guide/view2d_auto_grid` | `adapted` | `datoviz_axis_guide_adapted_review` |
| `guide/view2d_reversed_explicit` | `adapted` | `datoviz_axis_guide_adapted_review` |

The full S028 visual QA suite was regenerated for S030 closeout. The focused M121 guide-only review
pack remains useful evidence, but the final S030 review pack is the authoritative current artifact.

## What Is Proven

- Native Datoviz panel axes render backend auto ticks, grid, axis labels, and finite `View2D`
  domains.
- Native Datoviz panel axes render reversed finite domains.
- Explicit tick values/labels are wired through `dvz_axis_set_ticks` and render in the
  `guide/view2d_reversed_explicit` review case.
- The visual QA runner records skipped `PanelTextGuide` title state and guide-query gaps in
  structured `guide_diagnostics`.

## Remaining Blockers

Do not claim strict Datoviz guide parity yet. Remaining blockers:

- Datoviz panel title API is not exposed/proven: no `dvz_panel_set_title` or `dvz_panel_title`.
- Datoviz guide/all-rendered query support is not exposed/proven.
- Strict GSP auto tick identity is not claimed for backend-native Datoviz auto ticks.

## Validation

- `PYTHONPATH=. uv run pytest tests/ -q`: 396 passed, 8 skipped.
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: success.
- `git diff --check`: clean.
- Backend import checks passed for `GSP_BACKEND=matplotlib` and `GSP_BACKEND=datoviz`.

## External Checkout State

Sibling Datoviz checkout `/Users/cyrille/GIT/Viz/datoviz` had unrelated local changes at the start
of S030 work. Do not revert or edit them unless explicitly asked.
