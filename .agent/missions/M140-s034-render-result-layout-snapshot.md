# M140 - S034 render result layout snapshot

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Expose Matplotlib render-result layout identity through the VisPy2 producer without changing the
existing `render_matplotlib()` tuple API.

## Deliverables

- `MatplotlibRenderResult` with `figure`, `axes`, `layout_snapshot`, and `layout_snapshot_id`.
- `Figure.render_matplotlib_with_layout(snapshot_id=...)`.
- Test showing the returned snapshot can drive resolved guide query with the same snapshot id.

## Acceptance

- Existing `render_matplotlib()` callers continue to work.
- The opt-in render result reports a concrete `layout_snapshot_id`.
- The returned `ResolvedLayoutSnapshot` uses the rendered Matplotlib figure and axes.

## Stop Condition

Stop before promoting full backend `layout_strict`; this is an API/reporting step, not a complete
strictness claim.

## Result

Completed. VisPy2 callers can now opt into a Matplotlib render result that carries resolved layout
identity.
