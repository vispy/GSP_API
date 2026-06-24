# ADR-0016 - TextVisual v1 without public GlyphVisual

## Status

Accepted

## Context

S024 adds general text/label support after S023 accepted Point, Marker, Segment, Path, and Image.
Text rendering risks leaking backend-specific font, glyph-atlas, shaping, and Datoviz realization
artifacts into the public protocol if not bounded before implementation.

## Decision

S024 accepts `TextVisual` as the only public text/glyph visual family for v1.

- `GlyphVisual`, glyph runs, glyph indices, atlas ids/UVs, SDF/MSDF parameters, and font cache
  handles are renderer-internal realization details.
- `TextVisual` stores one `texts: Sequence[str]` item per position.
- Positions are finite float32/float64 `(N, 2)` or `(N, 3)` arrays in existing `CoordinateSpace.NDC`
  or `CoordinateSpace.DATA`.
- Text color uses the existing RGBA validation rules.
- `font_size_px` is a logical screen-pixel size, scalar or per item.
- `font_role` is a visual-level generic enum: `DEFAULT`, `SANS`, `SERIF`, `MONOSPACE`.
- Anchoring uses `anchor_x={LEFT,CENTER,RIGHT}` and
  `anchor_y={BASELINE,TOP,CENTER,BOTTOM}`; default is `LEFT`/`BASELINE`.
- `rotation_rad` is scalar or per item, counter-clockwise in the panel/display plane, pivoting
  around the resolved anchor point.
- `z_order` is visual-level only; per-item order follows item index.
- Printable ASCII plus explicit newline is the required conformance subset. Other Unicode is
  protocol-valid but capability- and diagnostic-gated.
- Explicit `\n` multiline is the only v1 multiline/layout feature.
- Complex shaping, bidi, rich text, TeX/MathText, arbitrary font names, font handles, font embedding,
  outlines/shadows/background boxes, label placement, legends, and colorbars are deferred.
- Axis and panel text guides remain semantic guide objects. They are not automatically public
  `TextVisual` objects, though backends may realize them with internal text primitives.
- Text query/readback is item-level and capability-gated.

## Consequences

Matplotlib is the reference text renderer and converts pixels to points using output DPI. Datoviz
v0.4 text support must be verified against retained v0.4 APIs and capability gates; otherwise it must
return structured unsupported diagnostics rather than exposing glyph/atlas details or relying on
legacy/private APIs.
