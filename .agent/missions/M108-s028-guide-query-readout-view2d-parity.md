# M108 - S028 guide query/readout View2D parity

## Stage

S028 - Guide and View2D Integration

## Status

Completed.

## Summary

Align guide-scoped and all-rendered query/readout behavior with deterministic `View2D` state,
including reversed axes.

## Deliverables

- Add guide query tests for reversed x/y ranges.
- Ensure guide query payloads report tick values and labels from the same resolver/view snapshot
  used for rendering.
- Add or update scoped-query tests where guide/data hits overlap under `View2D`.

## Acceptance

- Guide and all-rendered query tests pass for normal and reversed `View2D`.
- Unsupported behavior remains `unsupported`, not miss or backend-adapted success.

## Stop Condition

Stop if guide query/readout semantics require broader rendered-order or layout semantics than S015
and S027 accepted.

## Result

- Fixed guide spine hit testing for reversed `View2D` bounds.
- Added guide query coverage for reversed x-axis auto ticks, reversed y-axis explicit ticks, and
  reversed-bound spine hits.
- Added scoped query coverage proving guide-scoped and all-rendered queries use the reversed
  `View2D` snapshot and preserve reference ordering.
- Validated focused guide-query/scoped-query tests and nearby protocol/conformance tests.
