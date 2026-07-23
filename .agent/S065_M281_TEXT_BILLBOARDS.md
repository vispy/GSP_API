# S065 M281 text hardening and 3D billboards completion

Date: 2026-07-23

Status: completed and independently accepted.

## Integrated commits

- GSP implementation: `3fd39f0` (`feat: harden text and add 3D billboards`)
- GSP Mission Control specification correction: `5ddc722`
  (`docs: register 3D billboard text contract`)
- VisPy2: `ed31905` (`feat: add 3D billboard text producers and gallery`)

## Result

- Existing 2D DATA/View2D and viewless 2D NDC text behavior remains supported.
- `(N, 3)` text is DATA-only, transform-free, screen-facing, and requires View3D.
- Matplotlib and Datoviz project 3D anchors through the resolved panel geometry while preserving
  logical size, anchors, rotation, color, item order, and stable visual z-order.
- Retained Datoviz camera navigation reprojects placement without reallocating text or repeating
  string/style/font-size uploads.
- Datoviz text and billboard capabilities require its public text ABI. Generic font roles adapt to
  its configured/default font; no glyph parity, shaping, font selection, or depth occlusion is
  advertised.
- VisPy2 exposes restricted `Axes3D.text(...)` without glyph, atlas, font-file, rich-text, shaping,
  backend, or native-handle escape hatches.

## Validation

- GSP source and installed-wheel suites: 660 tests passed.
- VisPy2 source and installed-wheel suites: 59 tests passed.
- Strict mypy, Ruff, and `git diff --check` passed.
- Four fresh Hatchling wheels built and installed together under CPython 3.13.4.
- Installed-wheel Matplotlib gallery was visually accepted with separated sans, serif, and
  monospace labels, Unicode, anchors, rotation, and ordering.
- Independent supervisor review accepted without blockers.

## Deferred checkpoint

The file-output gallery is Matplotlib-only. Native Datoviz capture, glyph parity, and depth
occlusion remain outside M281; native runtime review remains assigned to M284.

M282 minimal public query entry point is approved next.
