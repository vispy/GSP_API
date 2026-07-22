# Linear Texture2D straight-alpha and base-color multiplication

Case: `mesh_texture2d/linear_alpha_multiply_ndc`

## Review Notes

- Straight-alpha texture channels are bilinearly interpolated before multiplication by base RGBA.
- The expected capture value applies ordinary source-over compositing to the white offscreen background.

## Decision

- [ ] pass
- [ ] needs follow-up
