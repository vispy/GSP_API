# S029 Closeout - Backend Capability Matrix and Visual Review Pack

Updated: 2026-06-26

## Final State

S029 is complete. The final review pack is:

- `artifacts/visual_qa/s029/current-review-pack`

Final capability matrix counts:

| Status | Count |
|---|---:|
| `strict` | 52 |
| `adapted` | 4 |
| `unsupported` | 2 |
| `experimental` | 0 |
| `disabled` | 0 |
| `crashed` | 0 |
| `not_run` | 0 |

## Datoviz Decisions

All Datoviz rows remain rendering-only for S029:

- `query_supported: false`

Strict Datoviz rows are bounded to the exact rendered S029 review-pack scopes for point, marker,
segment, path, image, overlay, selected color/colorbar, one text row, 2D mesh rows, and transform
rows.

Adapted Datoviz rows:

| Row | Reason |
|---|---|
| `text/basic_ndc` | Default baseline anchor semantics are not strictly verified. |
| `text/anchor_grid_ndc` | Full text-box anchor semantics need a focused fixture. |
| `text/data_vs_ndc` | DATA placement is proven only under the identity review-pack view. |
| `text/multiline_unicode_smoke` | Unicode fallback and multiline baseline anchoring remain unverified. |

Unsupported Datoviz rows:

| Row | Reason |
|---|---|
| `guide/view2d_auto_grid` | No rendered Datoviz guide artifact proves backend auto tick/grid/title alignment with the GSP `View2D` guide contract; guide query remains unsupported. |
| `guide/view2d_reversed_explicit` | Explicit tick labels, reversed-domain axis/grid placement, panel title layout, and guide query remain unverified or unsupported. |

## Validation

- `DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz tools/run_datoviz_visual_review_pack.sh --suite s028 --out artifacts/visual_qa/s029/current-review-pack --run-id current-review-pack --resolution 800x600`: passed
- `PYTHONPATH=. uv run pytest tests/test_visual_qa_harness.py -q`: 24 passed
- `PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run pytest tests/test_visual_qa_harness.py tests/test_datoviz_v04_protocol_renderer.py -q`: 94 passed
- `PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run pytest -q`: 397 passed, 2 skipped
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: success, no issues in 206 source files
- `GSP_BACKEND=matplotlib PYTHONPATH=. uv run python -c "import gsp; print('Matplotlib backend OK')"`: passed
- `GSP_BACKEND=datoviz PATH=/Users/cyrille/GIT/Viz/datoviz/.venv/bin:$PATH PYTHONPATH=/Users/cyrille/GIT/Viz/datoviz:. uv run python -c "import gsp; print('Datoviz backend OK')"`: passed

Plain `PYTHONPATH=. uv run pytest -q` failed one environment-sensitive conformance report assertion
because the parent process and subprocess saw different Datoviz importability. The Datoviz-path full
suite above is the relevant final validation environment for this review pack.

## Next Stage

S030 should be a bounded Datoviz guide-axis proof stage. It should not redesign the GSP guide
contract. The first mission should render/probe Datoviz native axes for:

- backend auto ticks, grid, labels, and title placement under normal `View2D`;
- explicit GSP tick values and labels;
- reversed finite `View2D` domains;
- explicit unsupported diagnostics for guide/all-rendered query until Datoviz guide picking exists.
