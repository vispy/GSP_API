# Linear Texture2D minification at a quadrant boundary

Case: `mesh_texture2d/linear_minification_ndc`

## Review Notes

- A 256x256 base-level texture maps to a small viewport footprint, forcing minification.
- The center probe lies on the four-quadrant boundary and must bilinearly average the adjacent texels without mipmaps.

## Decision

- [ ] pass
- [ ] needs follow-up
