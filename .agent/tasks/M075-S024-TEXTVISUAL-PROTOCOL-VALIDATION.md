# M075-S024-TEXTVISUAL-PROTOCOL-VALIDATION - TextVisual protocol validation

## Mission

M075

## Goal

Add the accepted S024 `TextVisual` dataclass/enums and validation tests without renderer work.

## Deliverables

- Protocol enums and `TextVisual` dataclass.
- Public exports.
- Unit tests for validation and helper value expansion.

## Acceptance

`uv run pytest` for the focused protocol tests passes.

## Stop Conditions

Do not add public glyph/atlas/font-handle fields. Do not infer behavior from legacy `Texts` when it
conflicts with ADR-0016 or `spec/visuals/text.md`.
