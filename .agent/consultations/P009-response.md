# Consultation Result: S024 Text/Glyph Protocol Semantics

## Executive recommendation

Define **TextVisual only** as the public S024 v1 visual family. Do **not** expose a public GlyphVisual in v1.

Glyphs, glyph runs, font atlases, signed-distance fields, and backend-specific text buffers should be treated as **renderer-internal realization resources**. A future GlyphVisual or GlyphResource may be added only after Datoviz v0.4 requirements, shaping requirements, atlas ownership, and query semantics are understood well enough to avoid freezing backend artifacts into the public protocol.

The first implementable slice should be:

* one public `TextVisual`;
* UTF-8 / Python `str` text items;
* finite 2D/3D anchor positions in `NDC` or `DATA`;
* screen-pixel font sizes;
* RGBA color;
* generic font roles only;
* scalar or per-item style values for common fields;
* radians for rotation;
* explicit anchor semantics;
* limited multiline support;
* ASCII as the required conformance subset, Unicode as capability-dependent;
* Matplotlib as the reference renderer;
* Datoviz v0.4 behind explicit text capability gates or structured unsupported diagnostics.

This matches the uploaded S024 consultation scope and the accepted S023 protocol style: semantic visual family first, backend-specific realization second. 

## Protocol contract draft

| Field              |                                          Type | Required |                  Scalar / per-item | Validation                                                                                                                                                                  | Units / semantics                                                                                                                                                                | Default      |
| ------------------ | --------------------------------------------: | -------: | ---------------------------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `id`               |                           `str` / protocol id |      yes |                       visual-level | Non-empty, stable, unique within scene/session scope according to existing visual id rules.                                                                                 | Public visual identity used for updates, diagnostics, and query payloads.                                                                                                        | none         |
| `texts`            |                               `Sequence[str]` |      yes |               per-item, length `N` | Each item is a Python `str`; must be UTF-8 serializable for debug/replay; no NUL; no control characters except `\n`; empty strings allowed but render as no visible glyphs. | One logical text label per item. The item index is the stable per-visual query index.                                                                                            | none         |
| `positions`        | NumPy float array, shape `(N, 2)` or `(N, 3)` |      yes |                           per-item | dtype `float32` or `float64`; all values finite; `N == len(texts)`.                                                                                                         | Anchor positions. For 3D positions, text is screen-facing after projection; glyphs are not oriented in 3D space in v1.                                                           | none         |
| `coordinate_space` |                        `CoordinateSpace` enum |      yes |                       visual-level | Must be `NDC` or `DATA`.                                                                                                                                                    | Same semantics as S023 visuals. `NDC` uses the accepted panel NDC convention; `DATA` uses panel data coordinates.                                                                | none         |
| `rgba`             |                                    RGBA array |       no | scalar `(4,)` or per-item `(N, 4)` | Same S023 RGBA validation: `uint8` in `[0,255]` or float in `[0,1]`; finite if float.                                                                                       | Text fill color including alpha. No stroke, outline, or shadow in v1.                                                                                                            | opaque black |
| `font_size_px`     |                          float or float array |       no |          scalar or per-item `(N,)` | Finite, positive, recommended lower bound `> 0`; renderer may report unsupported for extremely large values.                                                                | Logical screen-pixel font size. Not data units and not typographic points.                                                                                                       | `13.0`       |
| `font_role`        |                               `FontRole` enum |       no |                  visual-level only | Must be one accepted enum value.                                                                                                                                            | Generic font role resolved by the server/backend. No arbitrary font name in v1.                                                                                                  | `DEFAULT`    |
| `anchor_x`         |                            `TextAnchorX` enum |       no |      scalar or per-item length `N` | Must be `LEFT`, `CENTER`, or `RIGHT`.                                                                                                                                       | Horizontal anchor relative to the text layout box.                                                                                                                               | `LEFT`       |
| `anchor_y`         |                            `TextAnchorY` enum |       no |      scalar or per-item length `N` | Must be `BASELINE`, `TOP`, `CENTER`, or `BOTTOM`.                                                                                                                           | Vertical anchor. `BASELINE` refers to the first line’s typographic baseline for single-line text; for multiline, see multiline policy.                                           | `BASELINE`   |
| `rotation_rad`     |                          float or float array |       no |          scalar or per-item `(N,)` | Finite radians.                                                                                                                                                             | Counter-clockwise rotation in the panel/display plane. Rotation pivot is the resolved anchor point at `positions[i]`.                                                            | `0.0`        |
| `z_order`          |                                       integer |       no |                  visual-level only | Finite integer, no NaN because not float.                                                                                                                                   | Draw ordering hint. Higher `z_order` draws later. For equal `z_order`, use scene visual order, then item order. It does not replace depth/projection semantics for 3D positions. | `0`          |

Do **not** include these as v1 fields:

| Candidate field                                      | Decision                                                                                                       |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `font_name` / `font_family_string`                   | Deferred. Non-portable without font discovery, fallback, licensing, and embedding semantics.                   |
| `glyphs`, `glyph_indices`, `atlas_id`, `atlas_uvs`   | Renderer-internal in v1.                                                                                       |
| `font_weight`, `font_style`, `stretch`               | Deferred.                                                                                                      |
| `line_spacing`, `paragraph_width`, `wrap`            | Deferred.                                                                                                      |
| `offset_px`                                          | Deferred. Useful later for annotations, but not needed to establish core text semantics.                       |
| `clip_to_panel`                                      | Defer unless a cross-visual clipping policy already exists. Do not invent a TextVisual-specific clipping rule. |
| `rotation_pivot`                                     | Not exposed. The pivot is always the anchor point.                                                             |
| `text_stroke`, `outline`, `shadow`, `background_box` | Deferred.                                                                                                      |
| `mathtext`, `TeX`, rich text, HTML                   | Deferred.                                                                                                      |

## Enums and units

### `CoordinateSpace`

Use the existing accepted values only:

| Value  | Semantics                                                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `NDC`  | Positions are in panel normalized device coordinates, consistent with S023 QA fixtures over `[-1, +1]`. Text size remains in screen pixels. |
| `DATA` | Positions are in the panel’s data coordinate system. Text size remains in screen pixels.                                                    |

### `FontRole`

Use a small generic enum, not backend font names:

| Value       |                Required? | Semantics                                                                                 |
| ----------- | -----------------------: | ----------------------------------------------------------------------------------------- |
| `DEFAULT`   |                      yes | Backend/server default UI or plotting font. Should normally resolve to a sans-serif font. |
| `SANS`      |                      yes | Generic sans-serif role.                                                                  |
| `SERIF`     | optional but recommended | Generic serif role.                                                                       |
| `MONOSPACE` | optional but recommended | Generic monospace role.                                                                   |

A renderer that cannot distinguish `DEFAULT` and `SANS` may map both to the same resolved font and should not warn. A renderer that cannot resolve `SERIF` or `MONOSPACE` should either substitute with a diagnostic warning or mark the visual unsupported, depending on the negotiated strictness.

Do not add `FAMILY_STRING` or `FONT_HANDLE` in v1.

### `TextAnchorX`

| Value    | Semantics                                                                   |
| -------- | --------------------------------------------------------------------------- |
| `LEFT`   | The anchor position lies on the left side of the text layout box.           |
| `CENTER` | The anchor position lies horizontally at the center of the text layout box. |
| `RIGHT`  | The anchor position lies on the right side of the text layout box.          |

### `TextAnchorY`

| Value      | Semantics                                                                   |
| ---------- | --------------------------------------------------------------------------- |
| `BASELINE` | The anchor position lies on the first line’s baseline. This is the default. |
| `TOP`      | The anchor position lies at the top of the text layout box.                 |
| `CENTER`   | The anchor position lies vertically at the center of the text layout box.   |
| `BOTTOM`   | The anchor position lies at the bottom of the text layout box.              |

`BASELINE` is important enough to include in v1 because Matplotlib supports it directly and scientific labels often need typographic baseline positioning. If a backend cannot implement baseline anchoring, it must report `TEXT_BASELINE_UNSUPPORTED` or `TEXT_BASELINE_APPROXIMATED`.

### Font size unit

Use **logical screen pixels**: `font_size_px`.

Rationale:

* It matches S023’s accepted screen-pixel semantics for point diameters, marker sizes, stroke widths, and line widths.
* It is natural for GPU backends.
* It avoids binding the protocol to publication point sizes or backend-native text units.
* It keeps text size independent of data coordinate scaling.

Matplotlib adaptation:

```text
matplotlib_font_size_points = font_size_px * 72 / output_dpi
```

Datoviz adaptation:

* If Datoviz accepts pixel text sizes, pass `font_size_px` directly after applying the renderer’s logical-pixel/device-pixel policy.
* If Datoviz accepts point-like or framebuffer-dependent sizes, the Datoviz backend must convert using panel DPI or framebuffer scale and advertise that `text.dpi_aware_size` is supported.
* If correct DPI behavior cannot be verified, the backend must emit `TEXT_SIZE_DPI_UNVERIFIED` and fail conformance for the size/DPI QA case.

### Rotation unit

Use **radians**, field name `rotation_rad`.

Rationale:

* S023 MarkerVisual already uses radians.
* Protocol consistency matters more than legacy compatibility.
* The field name makes accidental degree use obvious.

Semantics:

* Positive rotation is counter-clockwise in panel/display coordinates.
* Rotation is applied after resolving the anchor position.
* The pivot is the anchor point.
* Rotation is not a 3D orientation field.

### Draw order

Use visual-level `z_order`.

* Higher values draw later.
* For equal values, preserve scene visual order.
* Within one `TextVisual`, later item indices draw later.
* Do not introduce per-item `z_order` in v1; users can split text into multiple visuals if needed.

## Font and glyph atlas policy

Glyph atlas generation must be **renderer-internal** in v1.

The public protocol describes semantic text labels, not glyph buffers. The protocol should not expose:

* glyph indices;
* glyph UVs;
* atlas texture ids;
* atlas dimensions;
* SDF parameters;
* font file paths;
* font binary blobs;
* fallback chains;
* shaping engine output;
* backend glyph cache handles.

If Datoviz v0.4 requires explicit glyph atlas data, the Datoviz renderer should build and own that data internally from the `TextVisual` contract. That internal realization may be cached, invalidated, and uploaded through Datoviz-native retained resources, but none of those details should become public GSP fields in S024.

Recommended diagnostics:

| Code                            |         Severity | Meaning                                                                      |
| ------------------------------- | ---------------: | ---------------------------------------------------------------------------- |
| `TEXT_FONT_ROLE_UNRESOLVED`     | warning or error | Backend cannot resolve requested generic `font_role`.                        |
| `TEXT_FONT_SUBSTITUTED`         |          warning | Backend substituted a generic role with another generic/default font.        |
| `TEXT_GLYPH_MISSING`            | warning or error | One or more code points cannot be rendered by the resolved font/fallback.    |
| `TEXT_ATLAS_CREATION_FAILED`    |            error | Backend requires an atlas but could not build/upload it.                     |
| `TEXT_ATLAS_CAPACITY_EXCEEDED`  |            error | Backend atlas cannot hold required glyphs/items.                             |
| `TEXT_RENDERER_UNAVAILABLE`     |            error | Backend has no usable text path.                                             |
| `TEXT_FONT_METRICS_UNAVAILABLE` |            error | Backend cannot compute anchors/bounds well enough for accepted v1 semantics. |

Font discovery should be server/backend-local. S024 must not require network access, dynamic font downloads, executable font code, or font embedding.

## Unicode, shaping, and multiline policy

### Validation-level acceptance

`texts` accepts Python Unicode strings, with these restrictions:

* no NUL;
* no control characters except `\n`;
* no requirement for JSON/base64 in the in-process path;
* debug/replay serialization must use normal UTF-8 text strings.

Validation should not reject ordinary non-ASCII Unicode solely because a backend may not render it.

### Required conformance subset

The required v1 conformance subset is:

* printable ASCII `U+0020` through `U+007E`;
* newline `\n` for multiline smoke tests.

A backend that claims core `TextVisual` support must render this subset.

### Unicode beyond ASCII

Unicode beyond ASCII is accepted by the protocol but capability-dependent.

Recommended capability tiers:

| Capability                   | Meaning                                                                 |
| ---------------------------- | ----------------------------------------------------------------------- |
| `text.unicode_ascii`         | Printable ASCII plus newline. Required for v1 text support.             |
| `text.unicode_latin1`        | Common Latin-1 glyphs such as accents. Optional.                        |
| `text.unicode_symbols_basic` | Common scientific symbols such as `µ`, `Ω`, `π`, `±`. Optional.         |
| `text.unicode_bmp_basic`     | Broader BMP glyph coverage without promising complex shaping. Optional. |
| `text.emoji_color`           | Color emoji support. Deferred / optional, not part of conformance.      |
| `text.shaping_complex`       | Complex script shaping support. Deferred / optional.                    |
| `text.bidi`                  | Bidirectional text support. Deferred / optional.                        |

### Complex shaping

Complex shaping is **not required** in v1.

Scripts requiring shaping, bidirectional layout, contextual forms, ligature control, or complex combining behavior must not be silently misrepresented under a strict conformance mode. The renderer should report:

| Code                             |         Severity | Meaning                                                             |
| -------------------------------- | ---------------: | ------------------------------------------------------------------- |
| `TEXT_SHAPING_UNSUPPORTED`       | warning or error | Text likely requires shaping that the backend does not support.     |
| `TEXT_BIDI_UNSUPPORTED`          | warning or error | Text likely requires bidirectional layout.                          |
| `TEXT_COMBINING_MARK_UNVERIFIED` |          warning | Combining marks are present but backend behavior is not guaranteed. |

For non-strict exploratory rendering, the backend may attempt best-effort rendering with diagnostics.

### Multiline

Multiline text is represented by `\n` inside each string. No separate field is needed.

V1 multiline semantics:

* line breaks are explicit only;
* no wrapping;
* no paragraph layout;
* no rich text spans;
* one font role, size, color, anchor, and rotation applies to the whole item;
* `anchor_x` applies to the multiline layout box;
* `anchor_y=BASELINE` anchors the first line’s baseline;
* `TOP`, `CENTER`, and `BOTTOM` anchor the multiline layout box;
* exact line spacing is reference-renderer-defined in v1 and should not be used for pixel-perfect cross-backend assertions.

Capability gate:

| Capability       | Meaning                                        |
| ---------------- | ---------------------------------------------- |
| `text.multiline` | Backend supports `\n` as explicit line breaks. |

If unsupported, emit `TEXT_MULTILINE_UNSUPPORTED`.

## Guide relationship

Guides should remain **semantic guides**, not public TextVisual emitters.

`AxisGuide`, tick labels, axis labels, and `PanelTextGuide` titles should continue to exist as guide-level semantic objects. They may be realized by a backend using:

* native Matplotlib axis/title/tick APIs;
* internal text primitives;
* internal TextVisual-like structures;
* future layout systems.

But guide-generated labels should not automatically become public user-authored `TextVisual` objects in S024.

Rules:

1. `TextVisual` is for explicit user-authored labels, annotations, and text marks.
2. `AxisGuide` and `PanelTextGuide` remain higher-level semantic guide contracts.
3. Guide realization artifacts are backend-private unless an explicit debug/inspection mode exposes them.
4. Guide query payloads may include text values, but that does not make guide labels public TextVisual items.
5. Future specs may define a shared `TextStyle` subset used by both guides and `TextVisual`, but S024 should not require guide refactoring before TextVisual lands.
6. Matplotlib may keep using native guide APIs for axis labels, tick labels, and titles.
7. Datoviz may realize guides through the same internal text engine as TextVisual if convenient, but this must not leak into the public protocol.

## Backend mapping guidance

### Matplotlib

Matplotlib should be the S024 reference renderer.

Mapping:

| GSP field                               | Matplotlib mapping                                                                                             |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `texts[i]`                              | `Text` artist string                                                                                           |
| `positions[i]`, `coordinate_space=DATA` | data transform                                                                                                 |
| `positions[i]`, `coordinate_space=NDC`  | panel NDC to axes/panel transform; do not confuse with raw Matplotlib `[0,1]` axes fraction without conversion |
| `rgba[i]`                               | normalized Matplotlib RGBA color                                                                               |
| `font_size_px[i]`                       | points via `px * 72 / figure_dpi`                                                                              |
| `font_role`                             | Matplotlib generic family: sans-serif, serif, monospace, or default                                            |
| `anchor_x`                              | `ha`: left, center, right                                                                                      |
| `anchor_y`                              | `va`: baseline, top, center, bottom                                                                            |
| `rotation_rad`                          | degrees via `rad * 180 / pi`                                                                                   |
| rotation pivot                          | `rotation_mode='anchor'` or equivalent anchor-preserving behavior                                              |
| `z_order`                               | Matplotlib `zorder`                                                                                            |

Matplotlib conformance expectations:

* Must pass ASCII text cases.
* Must pass anchor grid cases.
* Must pass rotation pivot cases.
* Must pass alpha blending cases.
* Must pass pixel-size conversion at known output DPI.
* Should pass basic Unicode smoke tests where local fonts support glyphs.
* May emit diagnostics for font substitution or missing glyphs.
* Query/readback can be implemented by drawing once and using artist bounding boxes, but interactive text query is not required unless the capability is advertised.

Matplotlib should not be used as justification for adding TeX, MathText, arbitrary font names, or rich text to v1. Those are deferred even though Matplotlib can support some of them.

### Datoviz v0.4

Datoviz v0.4 should be treated as a retained C-first scene backend with explicit capability discovery.

The Datoviz backend must not assume v0.3 Python plotting APIs. It should probe or hard-code against verified v0.4 retained visual/text/glyph APIs only.

Minimum capability gate for claiming S024 TextVisual support:

| Capability               |                         Required for core? | Meaning                                                                          |
| ------------------------ | -----------------------------------------: | -------------------------------------------------------------------------------- |
| `visual.text`            |                                        yes | Backend has a usable text rendering path.                                        |
| `text.items`             |                                        yes | Can render multiple text items in one visual or equivalent retained realization. |
| `text.positions.ndc`     |                                        yes | Supports NDC-positioned text.                                                    |
| `text.positions.data`    | yes for full support; optional for partial | Supports data-positioned text.                                                   |
| `text.font_size_px`      |                                        yes | Supports or can faithfully convert screen-pixel font size.                       |
| `text.rgba`              |                                        yes | Supports RGBA text color.                                                        |
| `text.alpha`             |                                        yes | Supports alpha blending.                                                         |
| `text.anchor_x`          |                                        yes | Supports left/center/right horizontal anchoring.                                 |
| `text.anchor_y_basic`    |                                        yes | Supports top/center/bottom vertical anchoring.                                   |
| `text.anchor_y_baseline` |  recommended; required if claiming full v1 | Supports baseline anchoring.                                                     |
| `text.rotation`          |                       yes for full support | Supports per-item or scalar screen-plane rotation in radians after conversion.   |
| `text.font_roles`        |                                        yes | Can map generic font roles.                                                      |
| `text.unicode_ascii`     |                                        yes | Renders printable ASCII.                                                         |
| `text.multiline`         |                                   optional | Supports explicit `\n`.                                                          |
| `text.per_item_color`    |                                recommended | Supports per-item colors or can split into internal batches.                     |
| `text.per_item_size`     |                                recommended | Supports per-item sizes or can split into internal batches.                      |
| `text.per_item_rotation` |                                recommended | Supports per-item rotation or can split into internal batches.                   |
| `text.query`             |                                   optional | Supports text hit testing/readback.                                              |
| `text.bounds`            |                                   optional | Can report text bounds.                                                          |

If Datoviz cannot support a per-item style directly, the backend may split one public `TextVisual` into multiple internal Datoviz visuals, provided public ids and query item indices remain stable.

Structured unsupported diagnostics should include:

| Code                              | Meaning                                                                    |
| --------------------------------- | -------------------------------------------------------------------------- |
| `TEXT_UNSUPPORTED`                | No usable Datoviz v0.4 text path.                                          |
| `TEXT_API_UNVERIFIED`             | Backend implementation would require unverified or legacy API assumptions. |
| `TEXT_ANCHOR_UNSUPPORTED`         | Requested anchor cannot be represented.                                    |
| `TEXT_BASELINE_UNSUPPORTED`       | Baseline anchoring unavailable.                                            |
| `TEXT_ROTATION_UNSUPPORTED`       | Rotation unavailable or only globally supported when per-item requested.   |
| `TEXT_PER_ITEM_STYLE_UNSUPPORTED` | Requested per-item color/size/rotation cannot be implemented or batched.   |
| `TEXT_SIZE_DPI_UNVERIFIED`        | Pixel-size mapping cannot be verified.                                     |
| `TEXT_MULTILINE_UNSUPPORTED`      | Text contains `\n`, but backend lacks multiline support.                   |
| `TEXT_GLYPH_MISSING`              | One or more glyphs unavailable.                                            |
| `TEXT_ATLAS_CREATION_FAILED`      | Required internal atlas creation failed.                                   |
| `TEXT_QUERY_UNSUPPORTED`          | Query requested but text query capability absent.                          |

If Datoviz requires explicit atlas/glyph data, the Datoviz renderer may maintain an internal cache keyed by resolved font role, size bucket, glyph set, DPI scale, and backend context. This cache remains non-protocol.

## Query/readback guidance

Text query support should be capability-gated.

Recommended capability flags:

| Capability              | Meaning                                                      |
| ----------------------- | ------------------------------------------------------------ |
| `query.text`            | Text items participate in panel query hit testing.           |
| `query.text.bounds`     | Query can report text bounding boxes in panel/screen pixels. |
| `query.text.item_index` | Query can resolve the public `texts[i]` item index.          |
| `query.text.label`      | Query payload includes the source text string.               |
| `query.text.glyph`      | Glyph-level hit testing; deferred, not required.             |

Recommended query payload for a text hit:

| Field              |                               Type |    Required | Meaning                                                                                          |
| ------------------ | ---------------------------------: | ----------: | ------------------------------------------------------------------------------------------------ |
| `kind`             |                        enum/string |         yes | `"text"`                                                                                         |
| `visual_id`        |                        protocol id |         yes | Public `TextVisual.id`.                                                                          |
| `item_index`       |                            integer |         yes | Index into `texts`.                                                                              |
| `text`             |                             string | recommended | The matched text item. May be omitted in privacy/minimal modes if the query model supports that. |
| `position`         | float array shape `(2,)` or `(3,)` | recommended | Original anchor position.                                                                        |
| `coordinate_space` |                               enum | recommended | Original coordinate space.                                                                       |
| `anchor_x`         |                               enum |    optional | Resolved horizontal anchor.                                                                      |
| `anchor_y`         |                               enum |    optional | Resolved vertical anchor.                                                                        |
| `bounds_px`        |                 `[x0, y0, x1, y1]` |    optional | Axis-aligned screen/panel bounding box after layout and rotation if available.                   |
| `distance_px`      |                              float |    optional | Distance from query point to text bounds or anchor.                                              |
| `z_order`          |                            integer |    optional | Draw-order value used during hit resolution.                                                     |

Hit testing should be item-level, not glyph-level, in v1.

If `query.text` is absent, text visuals may render but should not produce query hits. The server should report this through capability discovery rather than silently returning misleading partial hits.

Guides remain guide-query objects. A tick label or title query may return guide-specific payloads containing text values without pretending to be a public `TextVisual` hit.

## Visual QA plan

S024 should add Matplotlib reference images, optional Datoviz images where supported, contact sheets, and manual review notes.

| Case                      | Purpose                                                                                                                        | Expected review criteria                                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `text_basic_ndc`          | Single ASCII label at panel center.                                                                                            | Text appears at expected NDC position, correct color, correct approximate size, no clipping surprises.                                 |
| `text_anchor_grid`        | Labels at a 3 × 4 anchor grid: `LEFT/CENTER/RIGHT` × `TOP/CENTER/BOTTOM/BASELINE`, with crosshair markers at anchor positions. | Anchor point visibly matches each requested anchor. Baseline case is distinguishable and documented.                                   |
| `text_rotation_anchor`    | Several labels at same/similar anchors with rotations `0`, `π/6`, `π/4`, `π/2`, `-π/4`.                                        | Rotation is in radians, counter-clockwise, and pivots around the anchor.                                                               |
| `text_alpha_overlap`      | Semi-transparent text over points/image/background.                                                                            | RGBA alpha blends correctly; draw order is visible and stable.                                                                         |
| `text_size_dpi`           | Labels at `8`, `13`, `24`, `40` px rendered at at least two output DPIs.                                                       | Matplotlib conversion preserves intended pixel sizes for raster output; Datoviz reports pass or `TEXT_SIZE_DPI_UNVERIFIED`.            |
| `text_data_vs_ndc`        | DATA labels attached to plotted data points plus NDC labels in panel corners.                                                  | DATA labels follow data transform; NDC labels remain panel-relative.                                                                   |
| `text_z_order`            | Text above and below points/segments/images using different `z_order`.                                                         | Higher `z_order` draws later; equal order respects scene/item order.                                                                   |
| `text_multiline_smoke`    | `"line 1\nline 2"` with several anchors.                                                                                       | Explicit newline works where capability is present; line spacing need not be pixel-identical across backends.                          |
| `text_unicode_smoke`      | Strings such as `café`, `µm`, `Ω`, `π`, `±`.                                                                                   | Matplotlib should usually render; Datoviz may render or emit structured glyph/Unicode diagnostics. This is not core ASCII conformance. |
| `text_missing_glyph_diag` | Deliberately hard glyph or unsupported script under strict mode.                                                               | Backend reports missing glyph/shaping diagnostic instead of silent corruption.                                                         |
| `text_guide_integration`  | Axis labels, tick labels, title guide, plus explicit TextVisual.                                                               | Guides remain guides; explicit TextVisual remains independently queryable and identifiable.                                            |
| `text_query_smoke`        | Click/query on text item if backend advertises `query.text`.                                                                   | Payload includes `visual_id`, `item_index`, and preferably `text` and `bounds_px`.                                                     |

Manual review should avoid pixel-perfect glyph raster comparison across backends. The accepted checks should focus on semantic placement, size class, anchor behavior, alpha, rotation, and diagnostics.

## Deferred features

Explicit S024 non-goals:

* public `GlyphVisual`;
* public glyph atlas resources;
* SDF/MSDF glyph cache semantics;
* arbitrary font family strings;
* server-resolved persistent font handles;
* font embedding;
* remote font download;
* executable font/plugin loading;
* font fallback chain specification;
* font weight/style/stretch;
* kerning control;
* ligature control;
* complex text shaping as a required feature;
* bidirectional text as a required feature;
* Arabic/Indic/Thai shaping conformance;
* emoji/color font conformance;
* rich text spans;
* HTML text;
* Markdown text;
* TeX/LaTeX;
* Matplotlib MathText;
* superscript/subscript protocol;
* text outline/stroke;
* shadow/glow;
* background boxes;
* text along path;
* paragraph wrapping;
* layout boxes;
* collision avoidance;
* automatic label placement;
* legends and colorbars;
* annotation arrows/callouts;
* editable text;
* selection handles/carets;
* glyph-level query;
* exact cross-backend text metrics;
* 3D oriented text;
* data-unit font sizes;
* per-item font role;
* per-item z-order;
* protocol-level clipping semantics unless already defined cross-visually.

## ADR draft

* **Decision**: S024 accepts `TextVisual` as the only public text/glyph visual family for v1.
* **Decision**: `GlyphVisual` is not public in v1. Glyphs, atlases, shaping output, and SDF resources are renderer-internal realization details.
* **Decision**: Text item storage is `texts: Sequence[str]`, one string per item, paired with finite float `positions`.
* **Decision**: `coordinate_space` is required and uses only existing `NDC` and `DATA`.
* **Decision**: Font size uses logical screen pixels via `font_size_px`.
* **Decision**: Rotation uses radians via `rotation_rad`, consistent with MarkerVisual.
* **Decision**: Rotation is screen-plane rotation around the resolved anchor point.
* **Decision**: Anchoring uses `anchor_x={LEFT,CENTER,RIGHT}` and `anchor_y={BASELINE,TOP,CENTER,BOTTOM}`.
* **Decision**: Default anchor is `LEFT` / `BASELINE`.
* **Decision**: Color uses existing S023 RGBA validation.
* **Decision**: `font_role` is a generic enum: `DEFAULT`, `SANS`, `SERIF`, `MONOSPACE`.
* **Decision**: Arbitrary font names, font handles, font embedding, and font fallback chains are deferred.
* **Decision**: Printable ASCII plus newline is the required v1 conformance subset.
* **Decision**: Unicode strings are protocol-valid but rendering beyond ASCII is capability-dependent and diagnostic-driven.
* **Decision**: Complex shaping and bidirectional text are not required in v1.
* **Decision**: Multiline is represented only by explicit `\n`.
* **Decision**: Guides remain semantic guides and are not automatically converted into public `TextVisual` objects.
* **Decision**: Text query/readback is item-level and capability-gated.
* **Decision**: Matplotlib is the reference implementation.
* **Decision**: Datoviz v0.4 support requires explicit capability gates; otherwise it must return structured unsupported diagnostics.
* **Consequence**: S024 provides useful labels, annotations, titles-adjacent validation, and visual QA without committing to a full typography engine.
* **Consequence**: Some Datoviz paths may initially report unsupported or partial support, which is preferable to protocol leakage.
* **Consequence**: Exact glyph metrics are not a cross-backend guarantee in v1.

## Spec/task changes

Proposed new spec files:

* `specs/visuals/text_visual_v1.md`
* `specs/capabilities/text_capabilities_v1.md`
* `specs/query/text_query_payload_v1.md`
* `specs/rendering/text_reference_matplotlib_v1.md`
* `specs/rendering/text_datoviz_v04_mapping.md`
* `specs/qa/text_visual_qa_v1.md`

Proposed ADR:

* `adrs/ADR-00xx-textvisual-v1-no-public-glyphvisual.md`

Proposed updates:

* Update `SPEC_INDEX` to list TextVisual v1 as accepted only after ADR/spec approval.
* Update the visual-family index to add `TextVisual`.
* Update capability schema to include text capability gates and diagnostics.
* Update query schema to include item-level text query payloads.
* Update guide documentation to clarify that guides remain semantic and may internally realize text.
* Update Matplotlib renderer documentation with pixel-to-point conversion.
* Update Datoviz backend notes to forbid v0.3-style text API assumptions.
* Update visual QA harness to include text contact sheets and manual review notes.

Mission-sized tasks:

1. **S024-A ADR/spec baseline**
   Draft and accept the TextVisual ADR, protocol spec, enum definitions, validation rules, capability names, and diagnostic codes.

2. **S024-B protocol dataclass and validation**
   Add frozen dataclass/enums for `TextVisual`; validate `texts`, `positions`, scalar/per-item broadcasting, RGBA, anchors, font size, rotation, and `z_order`.

3. **S024-C Matplotlib reference renderer**
   Implement Matplotlib Text artist mapping, NDC/DATA transforms, pixel-to-point conversion, anchors, rotation, RGBA, multiline, and reference diagnostics.

4. **S024-D visual QA fixtures**
   Add deterministic NDC fixtures and contact sheets for basic text, anchors, rotation, alpha, size/DPI, DATA vs NDC, multiline, Unicode smoke, z-order, and guide integration.

5. **S024-E Datoviz v0.4 capability probe**
   Probe verified v0.4 retained text/glyph APIs only. Produce a capability report before implementing renderer behavior.

6. **S024-F Datoviz renderer path or unsupported report**
   Implement TextVisual only where capabilities are verified. Otherwise return structured unsupported diagnostics without inventing fields.

7. **S024-G query/readback integration**
   Add item-level text query payloads behind `query.text` capability. Matplotlib may compute bounds after draw; Datoviz may report unsupported initially.

8. **S024-H VisPy2 producer API**
   Add a high-level text/labels producer that maps to `TextVisual` without exposing glyphs, font atlases, or backend-specific names.

9. **S024-I guide relationship note**
   Document how `AxisGuide` and `PanelTextGuide` coexist with TextVisual and how guide text may be internally realized.

## Risks and stop conditions

### Risks

* Datoviz v0.4 text APIs may not support anchors, baseline, rotation, or per-item styling.
* Datoviz may expose glyph/atlas primitives but not semantic text primitives, tempting workers to leak atlas details into GSP.
* Font metrics can differ substantially between Matplotlib and GPU backends.
* Pixel-size behavior can be wrong on HiDPI displays or publication raster exports if DPI conversion is not explicit.
* Unicode rendering may vary by installed fonts.
* Complex scripts may render incorrectly without shaping.
* Baseline anchoring may be approximated in some backends.
* Multiline metrics may differ across renderers.
* Query bounding boxes may be expensive or unavailable on GPU backends.
* Guide text and TextVisual may accidentally diverge stylistically if no shared style subset is later introduced.

### Stop conditions

Workers must stop and report instead of inventing semantics if:

* accepted project authority documents conflict with the proposed TextVisual contract;
* implementation requires relying on Datoviz v0.3/private/legacy text APIs;
* Datoviz v0.4 requires public glyph atlas fields to proceed;
* no reliable way exists to map `font_size_px` to backend output size;
* anchor or baseline behavior cannot be implemented or honestly diagnosed;
* rotation pivot semantics cannot be preserved;
* Unicode text would be silently corrupted instead of rendered or diagnosed;
* complex shaping is needed for a test or user case but no shaping capability is present;
* query/readback cannot preserve public `visual_id` and `item_index`;
* guide implementation would require converting guides into public TextVisuals without an accepted guide-spec change;
* visual QA reveals systematic Matplotlib/Datoviz semantic disagreement not covered by an explicit capability gate;
* a worker is about to add arbitrary font names, font handles, glyph ids, atlas ids, MathText, TeX, rich text, or layout fields to v1 without a new ADR.

