# S030 Closeout - Datoviz Guide Axis Proof

## Outcome

S030 is closed. Datoviz guide/View2D rows are now rendered review artifacts, but they remain
`adapted`, not `strict`.

Final review pack:

- `artifacts/visual_qa/s030/final-review-pack/index.md`
- `artifacts/visual_qa/s030/final-review-pack/capability_matrix.json`
- `artifacts/visual_qa/s030/final-review-pack/summary.json`

Final S030 review-pack counts:

| Scope | Strict | Adapted | Unsupported | Crashed/disabled/not run |
| --- | ---: | ---: | ---: | ---: |
| All backend rows | 52 | 6 | 0 | 0 |
| Datoviz rows | 23 | 6 | 0 | 0 |

The full S028 review suite was regenerated for S030 closeout. The M121 guide-only pack remains useful
as focused evidence, but the final pack is the authoritative S030 review artifact.

## Guide Row Decisions

| Case | Datoviz status | Reason |
| --- | --- | --- |
| `guide/view2d_auto_grid` | `adapted` | Native Datoviz panel axes render backend-native ticks, grid, labels, and View2D domains, but GSP strict auto tick identity, panel title placement, and guide query remain unsupported. |
| `guide/view2d_reversed_explicit` | `adapted` | Native Datoviz panel axes render reversed domains and explicit tick values/labels via `dvz_axis_set_ticks`, but panel title placement and guide query remain unsupported. |

## Remaining Gaps

- Datoviz panel title APIs are not exposed/proven (`dvz_panel_set_title` / `dvz_panel_title` absent).
- Datoviz guide and all-rendered guide query support remains unsupported.
- Strict Datoviz guide parity remains deferred unless title/query semantics are proven or explicitly
  excluded from a future guide-row contract.

## Validation

- `PYTHONPATH=. uv run pytest tests/ -q`: 396 passed, 8 skipped.
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: success.
- `git diff --check`: clean.
- Backend import checks passed for `GSP_BACKEND=matplotlib` and `GSP_BACKEND=datoviz`.
