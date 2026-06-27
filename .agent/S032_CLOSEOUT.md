# S032 Closeout - Datoviz v0.4 Compatibility Refresh

## Result

M127 refreshed GSP_API for the latest Datoviz v0.4-dev policy-only `DvzPanelView2D` contract.

Implemented changes:

- Datoviz panel data limits now flow through `dvz_panel_set_domain()`.
- `dvz_panel_set_view2d()` is used as fitting/aspect/padding policy rather than the data-domain
  carrier.
- Datoviz DATA visuals keep native DATA coordinates; NDC visuals attach as Datoviz VIEW
  coordinates.
- Stale `dvz_panel_data_to_visual_positions()` capability/docs references were removed or marked
  historical.
- S031 review packs were regenerated for both legacy and linear Datoviz color pipelines.

## Review Artifacts

- Legacy review pack: `artifacts/visual_qa/s031/full-review-pack-legacy`
- Legacy all-cases sheet:
  `artifacts/visual_qa/s031/full-review-pack-legacy/contact_sheets/s028_all_cases.png`
- Linear review pack: `artifacts/visual_qa/s031/full-review-pack-linear`
- Linear all-cases sheet:
  `artifacts/visual_qa/s031/full-review-pack-linear/contact_sheets/s028_all_cases.png`

Both regenerated packs report Datoviz status counts:

| Status | Count |
|---|---:|
| strict | 23 |
| adapted | 6 |
| unsupported | 0 |
| crashed/disabled/not_run | 0 |

The combined backend matrix remains `strict=52`, `adapted=6`, `unsupported=0`.

## Visual Agreement

Manual review of the regenerated all-cases sheet and changed transform sheets shows Matplotlib and
Datoviz remain aligned. The changed transform rows match their Matplotlib references at the expected
layout level:

- `transform/view2d_data_ndc_overlay`: mean RGB diff 1.66, p95 0.0 in the legacy pack.
- `transform/family_affine_view2d`: mean RGB diff 6.59, p95 21.0 in the legacy pack.
- Guide rows remain adapted, not strict, because guide query/title semantics are still outside the
  accepted strict Datoviz contract.

## Validation

- `PATH=/home/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. uv run pytest tests/test_datoviz_v04_protocol_renderer.py tests/test_visual_qa_harness.py -q`: 107 passed.
- `PATH=/home/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. uv run pytest -q`: 411 passed, 2 skipped.
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: clean.
- `GSP_BACKEND=matplotlib PYTHONPATH=. uv run python -c "import gsp; print('Matplotlib backend OK')"`: passed.
- `GSP_BACKEND=datoviz PATH=/home/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/home/cyrille/GIT/Viz/datoviz:. uv run python -c "import gsp; print('Datoviz backend OK')"`: passed.
- `git diff --check`: clean.

## Remaining Limits

Datoviz guide rows remain adapted until title layout and guide/all-rendered query semantics are
strictly specified and implemented. Query support for the visual-review rows remains unchanged by
this compatibility refresh.
