# M173 - S039 Matplotlib Lambert Reference

Implement S039 flat Lambert material math for the Matplotlib/reference path after M172.

## Required

- Use canonical `MeshVisual.shading="flat_lambert"` semantics.
- Resolve explicit or generated face normals in DATA space.
- Use `View3D.ambient_light_intensity` and optional `DirectionalLight3D`.
- Compute `output.rgb = clamp(base.rgb * clamp(A + D, 0, 1), 0, 1)` with alpha passthrough.
- Add focused tests for material math and adapted Matplotlib rendering.

## Stop Conditions

- Do not expose legacy material/light classes as public protocol API.
- Do not add vertex normals, smooth Lambert, Phong/specular, textures, UVs, or samplers.
