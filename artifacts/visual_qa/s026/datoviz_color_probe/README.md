# Datoviz v0.4 S026 Color Mapping Capability Probe

## Summary

- Runtime S026 color mapping capability gates all supported: False
- Runtime missing or unverified capability gates: 9
- Source evidence for scale/colormap/scalar-field/colorbar APIs: True
- Source evidence for query API symbols: True
- Unexpected banned legacy/private API hits: 0
- Datoviz facade imported: False
- Datoviz sibling source exists: True

## Missing or unverified runtime gates

- `color.colorbar.semantic`: missing symbols: ('dvz_colorbar', 'DvzColorbarDesc', 'DVZ_COLORBAR_ORIENTATION_VERTICAL', 'DVZ_COLORBAR_ORIENTATION_HORIZONTAL')
- `color.colormap.accepted_named`: missing symbols: ('dvz_colormap_builtin', 'DVZ_BUILTIN_COLORMAP_GRAY', 'DVZ_BUILTIN_COLORMAP_VIRIDIS', 'DVZ_BUILTIN_COLORMAP_MAGMA', 'DVZ_BUILTIN_COLORMAP_PLASMA', 'DVZ_BUILTIN_COLORMAP_INFERNO', 'DVZ_BUILTIN_COLORMAP_CIVIDIS')
- `color.colormap.custom_lut`: missing symbols: ('dvz_colormap_custom', 'dvz_colormap_set_stops')
- `color.image.scalar_field`: missing symbols: ('dvz_sampled_field', 'dvz_sampled_field_set_data', 'dvz_visual_set_field', 'dvz_visual_set_scale', 'DVZ_FIELD_DIM_2D', 'DVZ_FIELD_FORMAT_R32_FLOAT', 'DVZ_FIELD_SEMANTIC_SCALAR')
- `color.marker.scalar_fill`: No retained-scene symbol or source contract was found for MarkerVisual scalar fill colors; S026 should keep this Datoviz path unsupported or CPU-map to RGBA until verified.
- `color.mesh.face_scalar`: S026 marks MeshVisual face scalar color as capability-gated and this probe does not verify a Datoviz face-scalar readback/rendering contract.
- `color.point.scalar_attribute`: missing symbols: ('dvz_point', 'dvz_visual_set_data', 'dvz_visual_set_scale', 'dvz_scale')
- `color.query.scalar_readback`: missing symbols: ('DvzQueryResult', 'dvz_panel_query', 'dvz_panel_query_now', 'dvz_scene_poll_query')
- `color.scale.continuous`: missing symbols: ('dvz_scale', 'dvz_scale_set_domain', 'DVZ_SCALE_CONTINUOUS')

## Source evidence highlights

- `dvz_scale`: 52 hit(s)
- `dvz_colormap_builtin`: 2 hit(s)
- `dvz_sampled_field`: 33 hit(s)
- `dvz_visual_set_scale`: 14 hit(s)
- `dvz_colorbar`: 11 hit(s)
- `DvzQueryResult`: 27 hit(s)

## Recommendation

- Treat Datoviz image scalar fields, continuous scales, named/custom colormaps, point scalar colors, semantic colorbars, and query plumbing as implementation candidates based on sibling source evidence.
- Keep all S026 Datoviz color mapping paths structured unsupported in GSP until Python facade/raw runtime bindings expose the recorded symbols and semantics are verified in a retained-scene smoke.
- Keep Datoviz MarkerVisual scalar fill and MeshVisual face scalar color capability-gated until a native retained-scene contract or an explicit CPU-mapped RGBA adaptation is implemented and verified.
