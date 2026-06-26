# M106 - S028 guide/View2D spec reconciliation

## Stage

S028 - Guide and View2D Integration

## Status

Completed.

## Summary

Reconcile guide, tick, grid, guide-query, and readout specs with accepted `View2D` semantics before
implementation work begins.

## Deliverables

- Update or add focused spec text for semantic guides consuming `View2D`.
- State reversed-axis tick ordering, labels, grid positions, guide-query hit behavior, and same
  snapshot readout expectations.
- Update Mission Control records so M107-M110 are unblocked or explicitly revised.
- Keep deferred behavior explicit: nonlinear/log/category/date axes, equal-aspect layout, guide
  collision/layout solving, public 3D camera/projection/controller, and live navigation events.

## Acceptance

- Specs no longer imply that guide ticks require increasing `View2D` limits.
- The next implementation missions have clear acceptance tests and stop conditions.
- No backend-native axis, camera, transform, or layout object becomes public GSP semantics.

## Stop Condition

Stop and create a ChatGPT Pro consultation packet if accepted guide authority conflicts with
`spec/transforms.md`, or if S028 cannot stay limited to deterministic 2D guide/view semantics.

## Result

- Added focused S028 guide/View2D rules to `spec/transforms.md`.
- Updated `spec/query.md` so guide-scoped and all-rendered guide queries consume the same `View2D`
  snapshot as rendering and return `unsupported` when that snapshot is unavailable.
- Updated `spec/vispy2/api.md` to accept reversed `set_xlim`, `set_ylim`, and `set_view2d` limits
  while preserving semantic tick identity.
- Updated Matplotlib and Datoviz backend specs for strict reference behavior and capability-gated
  Datoviz reporting.
- Updated visual QA guidance for reversed axes, grid lines, guide queries, and VisPy2 producer
  coverage.
- No ChatGPT Pro consultation was required. M107 is ready.
