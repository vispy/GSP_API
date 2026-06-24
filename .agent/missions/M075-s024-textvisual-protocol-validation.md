# M075 - S024 TextVisual protocol dataclass and validation

## Stage

S024 - Text/Glyph Visuals v1

## Status

Ready.

## Summary

Implement the accepted `TextVisual` protocol model and validation surface from ADR-0016 and
`spec/visuals/text.md`.

## Planned Deliverables

- Add `TextVisual`, `FontRole`, `TextAnchorX`, and `TextAnchorY` to `gsp.protocol.visuals` exports.
- Validate texts, positions, RGBA scalar/per-item values, positive `font_size_px`, anchors,
  `rotation_rad`, `font_role`, and visual-level `z_order`.
- Add focused unit tests for accepted and rejected inputs.

## Acceptance

Tests prove scalar/per-item broadcasting and validation semantics. No renderer behavior or Datoviz
API assumptions are added in this mission.

## Stop Condition

Stop if implementation needs fields not accepted by ADR-0016/spec, such as arbitrary font names,
font handles, public glyph ids, atlas ids, rich text, TeX/MathText, or layout fields.
