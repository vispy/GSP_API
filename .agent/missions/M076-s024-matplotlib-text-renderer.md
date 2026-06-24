# M076 - S024 Matplotlib TextVisual reference renderer

## Stage

S024 - Text/Glyph Visuals v1

## Status

completed

## Summary

Render `TextVisual` through the Matplotlib reference backend after M075 lands.

## Planned Deliverables

- Matplotlib Text artist mapping for DATA/NDC positions, RGBA, pixel-to-point font size conversion,
  anchors, radians rotation, multiline, and z-order.
- Focused renderer tests.
- Diagnostics for missing glyph/font substitution where practical.

## Stop Condition

Stop if Matplotlib support would require adding deferred protocol fields such as arbitrary font names,
MathText, TeX, outlines, or layout boxes.
