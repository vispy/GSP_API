# M281 - S065 text hardening and 3D billboards

## Status

Draft; promote after M280. Target repositories: `gsp`, `vispy2`; Datoviz is read-only evidence.

## Goal

Qualify existing 2D text and implement the bounded screen-facing 3D billboard contract.

## Required scope

- Section 7 of `.agent/S065_TECHNICAL_BASELINE.md`.
- Explicit protocol validation for 3D text/View3D compatibility.
- Matplotlib and Datoviz billboard projection, anchors, rotation, logical size, color, and ordering.
- Capability IDs/diagnostics that keep depth occlusion and glyph behavior unadvertised.
- `Axes3D.text(...)`, installed-wheel examples, ASCII plus representative Unicode smoke, and visual
  artifacts across font roles/anchors/rotation.

## Acceptance

2D regressions remain green. Camera movement changes 3D anchors but not logical font size. Backend
font/raster differences are documented; neither backend claims glyph parity or depth occlusion.
Full source/wheel gates pass.

## Stop conditions

Stop on a need for public font files, glyph IDs, atlases, rich text, shaping guarantees, or hidden
backend text handles.

