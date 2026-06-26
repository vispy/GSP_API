# M105 - S028 Guide/View2D integration scoping

## Stage

S028 - Guide and View2D Integration

## Status

Completed.

## Summary

Open S028 around the remaining guide/view integration work after S027 accepted deterministic
`View2D`. Reconcile semantic axis guides, ticks, grids, labels, guide queries, and readouts with
the accepted transform/view contract before implementation workers are launched.

## Deliverables

- Audit existing guide, tick, grid, scoped-query, VisPy2 guide API, and visual QA behavior against
  `spec/transforms.md`.
- Identify whether existing guide specs need a focused S028 spec update or whether implementation
  can proceed from accepted S012/S013/S015/S027 semantics.
- Produce a mission-sized implementation plan for guide rendering/query/readout behavior under
  explicit `View2D`, including reversed axes.
- Define acceptance tests and visual QA coverage for deterministic ticks, grids, labels, guide
  queries, and readouts tied to the same `View2D` snapshot as data visuals.

## Acceptance

- Mission Control has a concrete next mission batch or a documented blocker.
- The plan keeps S028 limited to semantic guides consuming `View2D` state.
- Any spec conflict is reported instead of resolved by inventing a third design.
- No public 3D camera/projection/controller, nonlinear transform, layout engine, or guide collision
  semantics are added.

## Stop Condition

Stop if existing guide authority documents conflict with accepted `View2D` semantics in
`spec/transforms.md`, or if the work requires public 3D camera/projection/controller, nonlinear
view, equal-aspect layout, or automatic guide layout/collision semantics.

## Result

- Audited guide/tick/grid/query authority in `spec/vispy2/api.md`, `spec/query.md`,
  `spec/transforms.md`, ADR-0019, and S027 decision records.
- Audited current Matplotlib guide rendering/query tests, scoped-query tests, VisPy2 guide API
  tests, and Datoviz guide capability notes.
- Found no conflict requiring ChatGPT Pro consultation.
- Identified the main implementation gap: accepted `View2D` permits reversed limits, but the
  deterministic tick resolver and guide coverage still treat reversed domains as invalid or
  untested.
- Opened the S028 mission batch M106-M110 with M106 as the next ready local Mission Control task.
