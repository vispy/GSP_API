# Datoviz v0.4 S026 Color Mapping Capability Probe

## Summary

- Runtime S026 color mapping capability gates all supported: False
- Runtime missing or unverified capability gates: 2
- Source evidence for scale/colormap/scalar-field/colorbar APIs: True
- Source evidence for query API symbols: True
- Unexpected banned legacy/private API hits: 0
- Datoviz facade imported: True
- Datoviz package path: /Users/cyrille/GIT/Viz/datoviz/datoviz/__init__.py
- Datoviz sibling source exists: True

## Missing or unverified runtime gates

- `color.marker.scalar_fill`: No retained-scene symbol or source contract was found for MarkerVisual scalar fill colors; S026 should keep this Datoviz path unsupported or CPU-map to RGBA until verified.
- `color.mesh.face_scalar`: S026 marks MeshVisual face scalar color as capability-gated and this probe does not verify a Datoviz face-scalar readback/rendering contract.

## Source evidence highlights

- `dvz_scale`: 52 hit(s)
- `dvz_colormap_builtin`: 2 hit(s)
- `dvz_sampled_field`: 33 hit(s)
- `dvz_visual_set_scale`: 14 hit(s)
- `dvz_colorbar`: 11 hit(s)
- `DvzQueryResult`: 27 hit(s)

## Recommendation

- Datoviz runtime bindings expose image scalar fields, continuous scales, named/custom colormaps, point scalar colors, semantic colorbars, and query plumbing as implementation candidates.
- Keep Datoviz MarkerVisual scalar fill and MeshVisual face scalar color capability-gated until a native retained-scene contract or an explicit CPU-mapped RGBA adaptation is implemented and verified.
- Add a retained-scene smoke before enabling S026 Datoviz rendering/query paths in GSP.
