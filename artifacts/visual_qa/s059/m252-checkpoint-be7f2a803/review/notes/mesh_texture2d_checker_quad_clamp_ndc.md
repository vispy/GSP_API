# Texture2D checker quad with clamp probes

Case: `mesh_texture2d/checker_quad_clamp_ndc`

## Review Notes

- UVs intentionally extend outside [0,1] to fixture fixed clamp_to_edge semantics.
- Nearest/clamp probes avoid texel boundaries; full-image exact hashes are not required.

## Decision

- [ ] pass
- [ ] needs follow-up
