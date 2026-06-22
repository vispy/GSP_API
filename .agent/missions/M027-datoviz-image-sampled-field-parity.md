# M027 - Datoviz image sampled-field parity

## Goal

Move bounded Datoviz RGBA8 image rendering toward the explicit sampled-field path while preserving
the existing texture-wrapper fallback.

## State

Completed.

## Required reading

- `.agent/tasks/DATOVIZ-V04-IMAGE-FIELD-CONTRACT.md`
- `.agent/tasks/DATOVIZ-V04-PARITY-NEXT-PACK.md`
- `spec/backends/datoviz.md`
- `src/gsp_datoviz/protocol_renderer.py`
- `tests/test_datoviz_v04_protocol_renderer.py`
- `../datoviz/include/datoviz/scene/field.h`
- `../datoviz/src/scene/domain/field.c`
- `../datoviz/include/datoviz/scene.h`

## Expected tasks

- Add sampled-field readiness diagnostics.
- Use `dvz_sampled_field()` plus `dvz_visual_set_field()` for supported RGBA8 images when available.
- Preserve fallback to `dvz_visual_set_texture()` when sampled-field symbols are unavailable.
- Add fake-facade tests and skip-clean runtime smoke.
- Keep scalar float/color-scale semantics deferred.

## Allowed paths

- `src/gsp_datoviz/**`
- `tests/**`
- `spec/backends/datoviz.md`
- `.agent/**`

## Forbidden paths

- Scalar float image parity or color-scale semantics.
- Tiled-source support.
- Capture/offscreen parity.
- Datoviz repository edits.

## Acceptance criteria

- Fake-facade tests prove sampled-field descriptor, upload, and visual binding calls.
- Existing texture fallback tests remain compatible.
- Runtime sampled-field smoke skips cleanly when the active binding is incomplete.
- Full test suite passes.

## Result

Completed by local-main-codex. Added sampled-field readiness diagnostics, RGBA8 sampled-field image
binding, texture fallback preservation, fake-facade coverage, skip-clean runtime smoke, and spec
notes.

Verification:

```bash
PYTHONPATH=. uv run pytest
```

Result: 138 passed, 5 skipped.

## Stop conditions

Stop before scalar float/color-scale semantics, tiled-source support, capture parity, or Datoviz
repository edits.
