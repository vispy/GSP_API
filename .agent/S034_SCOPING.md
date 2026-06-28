# S034 - Resolved Layout and Guide Geometry Foundation

## State

Opened by local-main-codex after P016/ADR-0020.

## Purpose

Turn the P016 hybrid guide/layout decision into a protocol foundation before attempting Matplotlib
or Datoviz layout-strict implementation work.

## Scope

- Define `spec/layout.md` as the authority for resolved layout, logical pixels, render targets,
  layout snapshots, and tiered conformance.
- Add protocol dataclasses/enums for `RenderTarget`, `ResolvedLayoutSnapshot`, guide boxes,
  diagnostics, layout resolve request/result records, and logical-pixel conversion.
- Add optional `layout_snapshot_id` to query request/result models.
- Expand capability snapshots with layout, guide-layout, font-layout, render-target, and
  query-layout capability records.
- Set conservative Matplotlib and Datoviz capability postures.
- Add validation tests for the protocol model and capability posture.

## Out Of Scope

- Full Matplotlib resolved-layout reference implementation.
- Datoviz grid clipping proof or strict guide promotion.
- Guide query geometry implementation.
- Visual QA fixture expansion beyond spec hooks.
- Release/tag/publish operations.

## Stop Conditions

Stop before claiming `layout_strict` for any backend until render, query, readback, and review
artifacts all share a concrete `layout_snapshot_id`.

Stop before adding backend-specific layout hacks as strict behavior. Adapted review artifacts must
remain classified as adapted.

## Follow-Up Mission Batch

1. Matplotlib resolved-layout reference implementation. Completed in M134 for snapshot production;
   render API snapshot reporting and full guide-geometry query/readback remain pending.
2. Guide style fields and resolved readback. Style fields and Matplotlib rendering completed in
   M135; full resolved style readback remains pending.
3. Datoviz guide capability audit and diagnostics hardening.
4. Grid clipping proof or explicit unsupported diagnostic.
5. Tiered visual QA fixtures and review report classification.
6. Layout-aware guide query/readback.
