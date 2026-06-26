# M109 - S028 visual QA and VisPy2 guide View2D coverage

## Stage

S028 - Guide and View2D Integration

## Status

Completed.

## Summary

Add user-facing and visual QA coverage for guide/View2D behavior after reference guide semantics are
implemented.

## Deliverables

- Visual QA cases for normal and reversed `View2D` guides, grids, labels, and overlapping data.
- VisPy2 tests showing `set_xlim`, `set_ylim`, `set_view2d`, ticks, labels, and grid emit protocol
  records that render consistently through Matplotlib.
- Example/doc updates if needed.

## Acceptance

- Visual QA artifacts include deterministic guide/View2D scenes.
- VisPy2 coverage proves guide methods mutate semantic protocol state, not data visuals.

## Stop Condition

Stop if QA requires layout/collision solving, equal aspect, or broader Matplotlib compatibility.

## Result

- Added S028 visual QA suite registration.
- Extended visual QA scenes, JSON artifacts, and Matplotlib rendering to include semantic
  `AxisGuide` and `PanelTextGuide` objects.
- Added deterministic S028 QA cases for normal auto-tick/grid guide behavior and reversed explicit
  guide ticks/labels under `View2D`.
- Added VisPy2 reversed `set_view2d` guide rendering coverage through the Matplotlib reference path.
- Validated focused QA/VisPy2 tests and nearby guide/query tests.
