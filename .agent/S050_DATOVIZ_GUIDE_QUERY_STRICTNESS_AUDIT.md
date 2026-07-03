# S050 Datoviz guide query strictness audit

Date: 2026-07-03

Mission: M207 - S050 Datoviz guide query strictness audit

## Outcome

Completed with no guide/View2D strict promotion.

The GSP adapter has a capability-gated panel-frame guide query path, and focused tests prove the
intended contract gates: native guide hits must match the layout snapshot id, all-rendered guide
queries must share the same snapshot id, and strict review rows require native panel title evidence
plus rendered guide contributions.

Fresh real Datoviz runtime evidence does not support promotion. The S028 guide review pack crashes
the Datoviz offscreen child process for guide/View2D cases with signal 11.

## Runtime Evidence

Full S028 guide batch:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_visual_review_pack.sh \
  --suite s028 \
  --case guide/view2d_auto_grid \
  --case guide/view2d_reversed_explicit \
  --case guide/view2d_grid_clip_title_boundary \
  --out artifacts/visual_qa/s050/m207-guide-query-audit \
  --run-id s050-m207-guide-query-audit
```

Result: parent review pack completed, but all three Datoviz guide rows are `crashed` with
`Datoviz offscreen child process terminated by signal 11`.

Single-case isolation:

```bash
DATOVIZ_REPO=/Users/cyrille/GIT/Viz/datoviz \
  tools/run_datoviz_visual_review_pack.sh \
  --suite s028 \
  --case guide/view2d_auto_grid \
  --out artifacts/visual_qa/s050/m207-guide-auto-single \
  --run-id s050-m207-guide-auto-single
```

Result: the isolated Datoviz `guide/view2d_auto_grid` row also crashed with signal 11, so the
failure is not only a multi-case batching artifact.

Both runs imported Datoviz from `/Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py` at source
revision `f5b81a397e3be69ecfffbffa88754c1c227e6820`.

## Focused Test Evidence

```bash
PYTHONPATH=src python -m pytest \
  tests/test_datoviz_v04_protocol_renderer.py \
  -k 'panel_frame or guide_query or axis_provider_is_capability_gated'
```

Result: `5 passed`.

```bash
PYTHONPATH=src python -m pytest \
  tests/test_visual_qa_harness.py \
  -k 'datoviz_guide or guide_row or strict_snapshot_evidence'
```

Result: `5 passed`.

## Decision

No Datoviz guide/View2D row can narrow-promote in M207.

Reasons:

- Real Datoviz offscreen guide rendering currently crashes for the audited guide cases.
- Full guide strictness is still blocked by missing native panel-title evidence.
- The strict row classifier already requires guide identity, guide boxes, guide query,
  all-rendered guide query, layout snapshot id equality, rendered guide contributions, and native
  panel-title evidence together.

Do not change public guide query semantics. Do not claim full guide strictness from grid clipping
alone. Keep guide rows unpromoted until a future runtime proof renders cleanly and satisfies the
strict snapshot/title/query/contribution contract.
