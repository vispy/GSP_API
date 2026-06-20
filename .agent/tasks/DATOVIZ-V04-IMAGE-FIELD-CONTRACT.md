# DATOVIZ-V04-IMAGE-FIELD-CONTRACT - Confirm image sampled-field details for GSP

Goal: clarify image semantics before implementing the GSP Datoviz image adapter.

Finding from M004:

- `dvz_image()` is available.
- Datoviz examples upload image geometry through `position` and `texcoords`.
- `dvz_visual_set_texture()` exists but is documented as a transitional RGBA8 convenience wrapper.
- `dvz_sampled_field()`, `dvz_sampled_field_set_data()`, and `dvz_visual_set_field()` are available and are the preferred direction for sampled fields.

Needed decision or documentation:

- exact mapping for GSP `ImageOrigin.UPPER/LOWER` to Datoviz `texcoords`;
- exact interpolation/filter control for sampled fields/images;
- whether first GSP Datoviz image slice should support only RGBA8, or also scalar float sampled fields with color scales;
- whether `dvz_visual_set_texture()` remains acceptable for first-slice RGBA8 conformance tests.

GSP dependency:

- The first implementation can render RGBA8 images, but should not claim complete image semantics until these details are fixed.

M007 update:

- `src/gsp_datoviz/protocol_renderer.py` implements the bounded RGBA8 convenience path with explicit `texcoords` for `ImageOrigin.UPPER/LOWER`.
- The adapter rejects scalar, grayscale, floating-point, non-nearest, and non-NDC image cases until the sampled-field contract is confirmed.
