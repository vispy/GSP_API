# Backend Visual Capabilities - Accepted S023 Baseline

Status: accepted for S023; S024 text capability gates accepted.

S023 validates two backend paths:

| Backend | Role | S023 guarantee |
|---|---|---|
| Matplotlib | reference/publication backend | renders all S023 visual families and QA cases |
| Datoviz v0.4 | high-performance retained-scene adapter | renders all S023 QA cases when the v0.4 facade exposes required symbols |

## Capability-gated behavior

Datoviz v0.4 support is facade-symbol gated. Missing symbols must produce structured unsupported
reports rather than fallback approximations. Required visual families use:

- points: `dvz_point`, `position`, `color`, `diameter_px`;
- markers: `dvz_marker`, `position`, `color`, `diameter_px`, `angle`, `shape`, marker style helpers;
- segments: `dvz_segment`, `position_start`, `position_end`, `color`, `stroke_width_px`, caps;
- paths: `dvz_path`, `position`, `color`, `stroke_width_px`, subpaths, caps, joins;
- images: `dvz_image`, `position`, `texcoords`, sampled-field binding or texture fallback,
  image sampling controls.
- text: verified v0.4 retained text/glyph path only; no legacy/private text APIs.

Remaining non-S023 limitations are follow-up scope, not hidden S023 failures:

- backend-native colormap registries beyond grayscale;
- public glyph and mesh visual families;
- tiled/remote/virtual image sources in Datoviz;
- scientific readback and full query payload parity;
- all-rendered/guide query scopes.

## S024 TextVisual capability gates

A backend may claim core `TextVisual` support only when it can render printable ASCII text with
positions, RGBA alpha, logical pixel font sizes, horizontal anchors, basic vertical anchors, generic
font roles, and NDC positioning. Full support additionally includes DATA positioning, baseline
anchoring, rotation, multiline, and per-item color/size/rotation either natively or through internal
batching.

Recommended capability names include `visual.text`, `text.positions.ndc`, `text.positions.data`,
`text.font_size_px`, `text.rgba`, `text.alpha`, `text.anchor_x`, `text.anchor_y_basic`,
`text.anchor_y_baseline`, `text.rotation`, `text.font_roles`, `text.unicode_ascii`,
`text.multiline`, `text.per_item_color`, `text.per_item_size`, and `text.per_item_rotation`.

Structured diagnostics include `TEXT_UNSUPPORTED`, `TEXT_API_UNVERIFIED`,
`TEXT_ANCHOR_UNSUPPORTED`, `TEXT_BASELINE_UNSUPPORTED`, `TEXT_ROTATION_UNSUPPORTED`,
`TEXT_PER_ITEM_STYLE_UNSUPPORTED`, `TEXT_SIZE_DPI_UNVERIFIED`, `TEXT_MULTILINE_UNSUPPORTED`,
`TEXT_GLYPH_MISSING`, `TEXT_ATLAS_CREATION_FAILED`, `TEXT_FONT_ROLE_UNRESOLVED`,
`TEXT_FONT_SUBSTITUTED`, `TEXT_SHAPING_UNSUPPORTED`, and `TEXT_BIDI_UNSUPPORTED`.
