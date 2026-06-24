# M072 - S023 closure docs and spec index

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Close S023 by converting decisions into accepted docs/tasks, updating indexes, and preparing the next
Text/Glyph or Mesh stage.

## Planned Deliverables

- Accepted ADRs/spec files indexed.
- `SPEC_INDEX.md` update.
- `LEGACY_MAP.md` update mapping legacy visuals to new families as reference only.
- `.agent/decisions/S023_visual_family_contracts.md`.
- S024 scoping note for Text/Glyph or Mesh.

## Completed

- Added accepted S023 closure specs for visual families, cross-cutting rules, visual QA, backend capabilities, Datoviz v0.4 API boundary, and VisPy2 visual API.
- Added missing SegmentVisual spec.
- Added accepted ADRs for visual family order, screen-space units, Datoviz v0.4 retained API, coordinate-space mapping, and ImageVisual scalar gray/clim.
- Updated `SPEC_INDEX.md` and `LEGACY_MAP.md`.
- Added `.agent/decisions/S023_visual_family_contracts.md`.
- Added S024 scoping task for Text/Glyph or Mesh.

## Acceptance

Closure checklist passes. All implemented fields are documented. Datoviz limitations have follow-up
tasks.

## Stop Condition

Stop if any implemented behavior exists only in code and not in spec/ADR/decision records.
