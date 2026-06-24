# VisPy2 Visual API - Accepted S023 Baseline

Status: accepted for S023; S024 TextVisual implemented; S025 MeshVisual producer API pending implementation.

The `vispy2` package is the high-level protocol producer used by S023 examples. It emits formal GSP
protocol visuals and does not call backend implementation APIs directly.

Accepted producer methods:

- `Axes.scatter(...)` -> `PointVisual`;
- `Axes.markers(...)` -> `MarkerVisual`;
- `Axes.segments(...)` -> `SegmentVisual`;
- `Axes.path(...)` and `Axes.plot(...)` -> `PathVisual`;
- `Axes.imshow(...)` -> `ImageVisual`;
- text/label producer -> `TextVisual`;
- S025 planned: simple mesh producer -> `MeshVisual`;
- semantic guide methods (`set_xlim`, `set_ylim`, labels, title, ticks, grid) update view/guide
  protocol objects.

Convenience top-level helpers mirror those methods for one-off visuals.

Out of scope:

- broad Matplotlib compatibility;
- direct Datoviz control;
- public glyphs, mesh features beyond accepted S025 `MeshVisual`, colorbar, legend, and layout systems;
- arbitrary font names, font handles, rich text, TeX/MathText, and glyph atlas controls;
- generated axes as user data visuals.

## S025 Mesh producer note

The first mesh producer should emit accepted `MeshVisual` objects with explicit `positions`, `faces`,
`coordinate_space`, `color`, and `color_mode`. Convenience unindexed triangles may be accepted by the
producer only if it creates explicit faces before producing protocol. Textures, OBJ loading, public
materials/lights, surface grids, and instancing remain out of the v1 producer API.
