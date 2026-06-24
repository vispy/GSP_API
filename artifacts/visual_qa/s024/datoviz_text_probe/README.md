# Datoviz v0.4 TextVisual Capability Probe

## Summary

- All text renderer capability gates supported: False
- Missing capability gates: 7
- Unexpected banned legacy/private text/API hits: 0

## Missing gates

- `text.font.atlas`: missing symbols: ('dvz_text_atlas_spec', 'dvz_font_atlas_ensure_strings', 'dvz_font_atlas', 'dvz_text_atlas_field')
- `text.font.create`: missing symbols: ('dvz_font', 'dvz_font_desc')
- `text.glyph.visual`: missing symbols: ('dvz_glyph', 'dvz_glyph_set_atlas')
- `text.placement`: missing symbols: ('dvz_text_placement',)
- `text.style`: missing symbols: ('dvz_text_style',)
- `text.visual.constructor`: missing symbols: ('dvz_text',)
- `text.visual.string`: missing symbols: ('dvz_text_set_string',)

## Recommendation

- Keep Datoviz TextVisual QA as structured unsupported until M079 resolves missing gates or documents why retained text cannot satisfy S024 without deferred fields.
