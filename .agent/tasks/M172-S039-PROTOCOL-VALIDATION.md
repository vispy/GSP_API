# M172 - S039 Protocol Validation

Implement accepted S039 protocol dataclasses/enums/validation after M171.

## Required

- Add canonical `unlit_rgba` and `flat_lambert` protocol shading semantics without silently treating
  legacy `lambert` as canonical.
- Add or normalize `DirectionalLight3D`, `View3D.ambient_light_intensity`, and
  `View3D.directional_light`.
- Validate explicit face normals and deterministic `face_flat` generated normals.
- Reject vertex normals, NDC Lambert, `(N,2)` Lambert, missing `View3D`, and invalid light values.
- Add focused protocol tests.

## Stop Conditions

- Stop if implementation would require public material objects.
- Stop if implementation would require textures/UVs or Phong/specular semantics.
