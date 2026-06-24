# Backend Visual Capabilities - Accepted S023 Baseline

Status: accepted for S023.

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

Remaining non-S023 limitations are follow-up scope, not hidden S023 failures:

- backend-native colormap registries beyond grayscale;
- text/glyph and mesh visual families;
- tiled/remote/virtual image sources in Datoviz;
- scientific readback and full query payload parity;
- all-rendered/guide query scopes.
