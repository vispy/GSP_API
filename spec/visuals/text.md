# Text Visual - Accepted S024 Baseline

Status: accepted protocol baseline for S024; implementation pending.

Semantic purpose: render explicit user-authored labels, annotations, and text marks. Axis labels,
tick labels, and panel titles remain semantic guide objects unless a future spec changes that.

## Public model

S024 defines `TextVisual` only. There is no public `GlyphVisual` in v1. Glyphs, glyph runs, atlases,
SDFs, shaping output, and backend text buffers are renderer-internal realization details.

| Attribute | Type | Required | Scalar/per-item | Default | Semantics |
|---|---|---:|---|---|---|
| `id` | protocol id string | yes | visual | none | Stable public visual id. |
| `texts` | sequence of `str` | yes | per item `N` | none | One logical label per item; item index is the public query index. |
| `positions` | float32/float64 `(N,2)` or `(N,3)` | yes | per item | none | Anchor positions. 3D text is screen-facing after projection in v1. |
| `coordinate_space` | `CoordinateSpace.NDC` or `.DATA` | yes | visual | none | Same coordinate-space semantics as S023 visuals. |
| `rgba` | RGBA `(4,)` or `(N,4)` | no | scalar/per item | opaque black | Text fill color and alpha. |
| `font_size_px` | positive float or float array `(N,)` | no | scalar/per item | `13.0` | Logical screen-pixel font size, never data units. |
| `font_role` | `FontRole` | no | visual | `DEFAULT` | Generic server/backend-resolved role. |
| `anchor_x` | `TextAnchorX` or tuple | no | scalar/per item | `LEFT` | Horizontal anchor on the text layout box. |
| `anchor_y` | `TextAnchorY` or tuple | no | scalar/per item | `BASELINE` | Vertical anchor; `BASELINE` is first-line baseline. |
| `rotation_rad` | finite float or float array `(N,)` | no | scalar/per item | `0.0` | Counter-clockwise display-plane rotation around the anchor. |
| `z_order` | integer | no | visual | `0` | Higher values draw later; ties use scene order then item order. |

## Enums

- `FontRole`: `DEFAULT`, `SANS`, `SERIF`, `MONOSPACE`.
- `TextAnchorX`: `LEFT`, `CENTER`, `RIGHT`.
- `TextAnchorY`: `BASELINE`, `TOP`, `CENTER`, `BOTTOM`.

`font_role` intentionally avoids arbitrary font-family strings, font file paths, font handles, and
fallback-chain declarations. Missing or substituted font roles are diagnostics.

## Validation and units

- `texts` entries must be Python strings, UTF-8 serializable for debug/replay, without NUL, and
  without control characters except `\n`. Empty strings are valid but render no visible glyphs.
- `positions` must be finite float32/float64 with length matching `texts`.
- RGBA uses S023 color validation: uint8 `[0,255]` or finite float `[0,1]`.
- `font_size_px` values must be finite and positive.
- `rotation_rad` values must be finite radians; legacy degree fields are not accepted.
- Per-item anchors, color, size, and rotation must have length `N` when arrays/tuples are used.

## Unicode, shaping, and multiline

Required conformance subset: printable ASCII `U+0020..U+007E` plus explicit newline `\n`.

Unicode beyond ASCII is protocol-valid but capability-dependent. Backends must render it or emit
structured diagnostics such as missing glyph, unsupported shaping, unsupported bidi, or unverified
combining mark behavior. Complex shaping and bidirectional text are not required in v1.

Multiline text is represented only with explicit `\n`. There is no wrapping, rich text, paragraph
layout, or per-line styling in v1. For multiline, `BASELINE` anchors the first line baseline; other
vertical anchors apply to the multiline layout box. Exact line spacing is not a cross-backend
conformance guarantee.

## Query payload

Text query/readback is item-level and capability-gated. A text hit payload should include:

- `kind="text"`;
- `visual_id`;
- `item_index`;
- preferably `text`, `position`, `coordinate_space`, and `bounds_px` when available.

Glyph-level query is deferred.

## Backend mapping

Matplotlib is the reference renderer. It maps `font_size_px` to points as
`font_size_px * framebuffer_per_canvas_px * 72 / output_dpi`, maps anchors to `ha`/`va`, converts
`rotation_rad` to degrees, and uses anchor-preserving rotation.

Datoviz v0.4 support must be based only on verified retained v0.4 APIs. If text/glyph APIs,
font-size mapping, anchors, baseline, rotation, atlas creation, or per-item styles cannot be verified,
the Datoviz adapter must return structured unsupported diagnostics rather than relying on v0.3 or
private APIs.

## Deferred

Public GlyphVisual, glyph atlases, arbitrary font names, font handles, font embedding, fallback-chain
specification, weight/style/stretch, kerning/ligature control, complex shaping requirements, bidi
requirements, emoji conformance, rich text/HTML/Markdown, TeX/MathText, text stroke/outline/shadow,
background boxes, text along path, paragraph wrapping, automatic label placement, legends,
colorbars, editable text, glyph-level query, exact cross-backend text metrics, 3D-oriented text,
data-unit font sizes, per-item font role, and per-item z-order are out of S024 v1.
