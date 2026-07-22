# Texture2D color multiplication and duplicated seam

Case: `mesh_texture2d/color_multiply_seam_ndc`

## Review Notes

- The seam is represented by duplicated positions with different per-vertex UVs.
- Output RGB is base.rgb * tex.rgb in normalized channel space.

## Decision

- [ ] pass
- [ ] needs follow-up
