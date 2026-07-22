# Shared Texture2D with nearest and linear field slots

Case: `mesh_texture2d/shared_nearest_linear_ndc`

## Review Notes

- Both visuals reference one protocol Texture2D and differ only by field-slot filtering.
- Constant UV=(0.5,0.5) avoids geometry edges and perspective interpolation.
- Nearest selects the lower-right texel; linear averages all four straight-alpha texels before base-color multiplication.

## Decision

- [ ] pass
- [ ] needs follow-up
