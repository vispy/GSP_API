# S046 Closeout - 3D Code Examples Pack

## Result

S046 completed the first focused 3D examples pack.

## Added

- `examples/review/12_view3d_mesh_pick.py`
  - renders overlapping DATA-space triangles;
  - prints S044 Matplotlib CPU-oracle results for frontmost hit, miss, and stale pick-scene
    snapshot handling;
  - keeps Datoviz mesh triangle picking explicitly unadvertised.
- `examples/review/13_view3d_suzanne_lambert.py`
  - loads the bundled Suzanne OBJ triangle mesh with a local parser;
  - normalizes it into accepted public View3D DATA coordinates;
  - renders S039 flat Lambert face-normal shading without OBJ materials, UVs, textures, or
    perspective.
- `examples/review/14_view3d_camera_path.py`
  - applies canonical S037 orbit, pan, and zoom actions;
  - prints accepted revisions and projection snapshot ids;
  - renders the final canonical View3D state.
- `examples/review/README.md`
  - lists the new examples;
  - adds review checklist entries and commands.

## Validation

- `tools/compare-review-examples --offscreen examples/review/12_view3d_mesh_pick.py examples/review/13_view3d_suzanne_lambert.py examples/review/14_view3d_camera_path.py`
- `uv run ruff check examples/review/12_view3d_mesh_pick.py examples/review/13_view3d_suzanne_lambert.py examples/review/14_view3d_camera_path.py`
- `uv run python -m py_compile examples/review/12_view3d_mesh_pick.py examples/review/13_view3d_suzanne_lambert.py examples/review/14_view3d_camera_path.py`
- `jq empty .agent/status.json`
- `git diff --check`

## Boundaries Preserved

- No public protocol semantics changed.
- Datoviz still must not advertise `query.view3d.mesh_triangle_pick.v1`.
- Strict opaque GPU depth, perspective, textures/UVs, Phong/smooth lighting, and public material
  resources remain out of scope.
- The sibling Datoviz repository was not edited.
