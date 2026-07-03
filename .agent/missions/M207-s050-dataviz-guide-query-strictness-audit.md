# M207 - S050 Datoviz guide query strictness audit

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Audit current Datoviz panel frame snapshot, guide-hit, and rendered-contribution evidence to decide
whether any guide/View2D row can narrow-promote without overclaiming full guide strictness.

## Stop Conditions

- Stop before claiming full guide strictness from grid clipping alone.
- Stop before treating screen-text panel titles as native Datoviz title strictness.
- Stop if title/query/contribution snapshot identity cannot be proven together.
- Stop before changing public guide query semantics without a consultation packet.

## Result

Completed with no guide/View2D strict promotion. See
`.agent/S050_DATOVIZ_GUIDE_QUERY_STRICTNESS_AUDIT.md`.

Fresh real Datoviz offscreen review evidence under
`artifacts/visual_qa/s050/m207-guide-query-audit/` reports all audited Datoviz guide rows as
`crashed` because the offscreen child process terminated with signal 11. A single-case retry under
`artifacts/visual_qa/s050/m207-guide-auto-single/` also crashed for
`guide/view2d_auto_grid`, so no narrow guide promotion is accepted.

Focused tests still prove the strict gates: panel-frame guide hits must match layout snapshot ids,
all-rendered guide queries must match the same snapshot id, rendered guide contributions must be
reported, and native panel-title evidence remains required for strict rows.
