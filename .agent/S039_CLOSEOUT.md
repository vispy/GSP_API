# S039 Closeout

## Result

S039 completed the minimal flat Lambert face-normal slice.

Accepted public semantics:

- `MeshVisual.shading="flat_lambert"`;
- face normals only, explicit `(F,3)` or deterministic `face_flat` generation;
- DATA-space `(N,3)` meshes in a resolved `View3D`;
- scalar `View3D.ambient_light_intensity`;
- one optional DATA-space `DirectionalLight3D`;
- `output.rgb = base.rgb * clamp(A + D, 0, 1)`;
- alpha passthrough with non-opaque 3D alpha still non-strict.

## Implemented

- Protocol dataclasses/enums/validation and public exports.
- Matplotlib/reference CPU material math with adapted 3D raster boundary preserved.
- Datoviz capability gate: explicit `flat_lambert_unsupported` until exact S039 support exists.
- VisPy2-style producer mesh helper fields for canonical S039 protocol emission.
- Review example: `examples/review/10_view3d_flat_lambert.py`.

## Validation

Latest validation during M175:

- `uv run ruff check ...`
- `uv run mypy src/ --strict --show-error-codes`
- `uv run python -m pytest tests/ -q`
- backend import smoke for Matplotlib and Datoviz.

## Deferred

- Vertex normals and smooth Lambert.
- Phong/specular/shininess.
- Textures, UVs, samplers, normal maps.
- Multiple lights, colored lights, point/spot lights, attenuation, scene graph.
- Datoviz strict S039 Lambert until exact protocol semantics are implemented and tested.
