# VisPy2 Visual API - Accepted S023 Baseline

Status: accepted for S023; S024 TextVisual implemented; S025 MeshVisual producer API implemented.

The `gsp_vispy2` package is the independent high-level protocol producer. It emits formal GSP
protocol visuals and does not call backend implementation APIs directly.

Accepted producer methods:

- `Axes.scatter(...)` -> `PointVisual`;
- `Axes.markers(...)` -> `MarkerVisual`;
- `Axes.segments(...)` -> `SegmentVisual`;
- `Axes.path(...)` and `Axes.plot(...)` -> `PathVisual`;
- `Axes.imshow(...)` -> `ImageVisual`;
- text/label producer -> `TextVisual`;
- `Axes.mesh(...)` -> `MeshVisual`;
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

The mesh producer emits accepted `MeshVisual` objects with explicit `positions`, `faces`,
`coordinate_space`, `color`, optional `color_mode`, and visual `order`. Textures, OBJ loading, public
materials/lights, surface grids, instancing, normals, shading, culling, and depth controls remain out
of the v1 producer API.
