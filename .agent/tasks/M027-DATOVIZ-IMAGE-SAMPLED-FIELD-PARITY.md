# M027-DATOVIZ-IMAGE-SAMPLED-FIELD-PARITY - Datoviz image sampled-field parity

## Mission

M027

## Goal

Use Datoviz v0.4 sampled fields for bounded RGBA8 image rendering when the binding exposes the
required symbols.

## Acceptance

- Sampled-field readiness reports missing symbols.
- RGBA8 images use `dvz_sampled_field`, `dvz_sampled_field_set_data`, and `dvz_visual_set_field`
  when available.
- Existing `dvz_visual_set_texture` fallback remains available.
- Scalar float/color-scale semantics stay deferred.

## Stop conditions

Stop before scalar image parity, color-scale semantics, tiled sources, capture/offscreen parity, or
Datoviz repository edits.
