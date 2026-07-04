# View3D opaque depth intersecting triangles reversed order

Case: `mesh3d/opaque_depth_intersecting_triangles_reversed_view3d`

## Review Notes

- Two opaque DATA-space triangles share the same projected XY footprint and cross in depth.
- Strict per-fragment depth should show red at the left sample and blue at the right sample.
- Average-face painter sorting draws blue last across the whole overlap, so this fixture separates adapted from strict depth.
- The reversed-order companion must render the same strict-depth sample colors.

## Decision

- [ ] pass
- [ ] needs follow-up
