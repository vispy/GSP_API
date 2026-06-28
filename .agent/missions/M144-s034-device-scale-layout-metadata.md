# M144 - S034 device-scale layout metadata

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Thread explicit `device_scale` metadata through Matplotlib resolved layout snapshots and S034 visual
QA reports.

## Deliverables

- `resolve_matplotlib_layout_snapshot(..., device_scale=...)`.
- `render_protocol_scene_with_layout(..., device_scale=...)`.
- `run_visual_qa_suite(..., device_scale=...)` with manifest/report metadata.
- Layout snapshot report fields for derived framebuffer width and height.
- Tests for resolver metadata, protocol render-result metadata, S034 QA reporting, and Matplotlib
  render-target capability posture.

## Acceptance

- Logical layout dimensions remain unchanged by `device_scale`.
- Derived framebuffer dimensions come from `RenderTarget.framebuffer_*_px`.
- Matplotlib advertises device-scale metadata support while leaving physical framebuffer-scale parity
  false.

## Stop Condition

Stop before claiming full layout strictness or Datoviz device-scale support. This is metadata
support for Matplotlib layout snapshots only.

## Result

Completed. Matplotlib resolved layout snapshots and S034 visual QA reports can now carry explicit
device-scale metadata without changing logical-pixel geometry.
