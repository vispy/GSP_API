# M013-MPL-AXISGUIDE-RENDER - Render semantic AxisGuide in Matplotlib

## Mission

M013

## Goal

Render x/y `AxisGuide` objects with Matplotlib native axes using GSP-resolved ticks.

## Acceptance

- Tick values and labels come from `resolve_ticks()`.
- Axis labels come from `AxisGuide.label_text`.
- Hidden guides hide the corresponding Matplotlib axis/spine.
- No generated guide objects enter `Figure.visuals()`.

## Stop conditions

Stop if implementation depends on Matplotlib native locators as the conformance source.

