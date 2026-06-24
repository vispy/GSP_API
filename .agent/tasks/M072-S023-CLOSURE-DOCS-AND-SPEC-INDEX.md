# M072-S023-CLOSURE-DOCS-AND-SPEC-INDEX - S023 closure docs and spec index

## Mission

M072

## Goal

Finish S023 by making the visual-family contracts durable and discoverable.

## Required Documentation Work

Create or update, based on what earlier S023 missions actually implemented:

- `spec/visual_families_v1.md`
- `spec/visual_cross_cutting_rules.md`
- `spec/visual_qa_harness.md`
- `spec/backend_capabilities_visuals.md`
- `spec/datoviz_v04_api_boundary.md`
- `spec/vispy2_visual_api.md`
- accepted ADR for visual family order;
- accepted ADR for screen-space units;
- accepted ADR for Datoviz v0.4 retained scene API;
- accepted ADR for coordinate-space mapping;
- accepted ADR for image sampled-field/colormap/clim if M070 completed that scope;
- `LEGACY_MAP.md`;
- `.agent/decisions/S023_visual_family_contracts.md`.

## Acceptance

- `SPEC_INDEX.md` points to all accepted S023 specs.
- Mission/task/status records reflect completed or deferred scope.
- Follow-up tasks exist for every Datoviz limitation that remains structured unsupported.
- Text/Glyph and Mesh are scoped for a later stage, not silently left ambiguous.

## Stop Conditions

- Stop if docs assert support that the QA report does not prove.
- Stop if closure tries to complete unfinished visual families without artifacts.

## Completion Notes

- Created closure specs:
  - `spec/visual_families_v1.md`
  - `spec/visual_cross_cutting_rules.md`
  - `spec/visual_qa_harness.md`
  - `spec/backend_capabilities_visuals.md`
  - `spec/datoviz_v04_api_boundary.md`
  - `spec/vispy2_visual_api.md`
  - `spec/visuals/segment.md`
- Created ADRs `ADR-0011` through `ADR-0015`.
- Updated `SPEC_INDEX.md`, `LEGACY_MAP.md`, `.agent/decisions/S023_visual_family_contracts.md`, and S024 scoping.
- S023 is closed with Text/Glyph and Mesh explicitly deferred.
