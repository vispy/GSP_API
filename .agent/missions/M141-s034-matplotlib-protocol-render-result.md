# M141 - S034 Matplotlib protocol render result

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Expose layout snapshot identity from the lower-level Matplotlib protocol renderer, not only from
the VisPy2 producer convenience API.

## Deliverables

- `MatplotlibProtocolRenderResult` with `figure`, `axes`, `layout_snapshot`, and
  `layout_snapshot_id`.
- `render_protocol_scene_with_layout(...)` for protocol visuals, semantic guides, and colorbars.
- VisPy2 `render_matplotlib_with_layout()` delegates to the lower-level Matplotlib helper.
- Matplotlib capability diagnostics no longer mark render API snapshot reporting as pending.

## Acceptance

- Lower-level Matplotlib render results report a concrete `layout_snapshot_id`.
- Returned snapshots can drive resolved guide queries with matching snapshot identity.
- Matplotlib still does not claim full `layout_strict`.

## Stop Condition

Stop before promoting full backend `layout_strict`; readback and review-pack closure remain separate
requirements.

## Result

Completed. Matplotlib protocol rendering can now return the resolved layout snapshot used by the
render result, while preserving the conservative layout-strict posture.
