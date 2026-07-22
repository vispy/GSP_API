# Texture2D alpha non-strict diagnostic

Case: `mesh_texture2d/alpha_diagnostic_ndc`

## Review Notes

- Texture alpha participates in output alpha multiplication.
- Any alpha byte below 255 prevents strict opaque-depth claims for 3D textured meshes.

## Decision

- [ ] pass
- [ ] needs follow-up
