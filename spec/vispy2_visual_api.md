# VisPy2 Visual API - Accepted S023 Baseline

Status: accepted for S023.

The `vispy2` package is the high-level protocol producer used by S023 examples. It emits formal GSP
protocol visuals and does not call backend implementation APIs directly.

Accepted producer methods:

- `Axes.scatter(...)` -> `PointVisual`;
- `Axes.markers(...)` -> `MarkerVisual`;
- `Axes.segments(...)` -> `SegmentVisual`;
- `Axes.path(...)` and `Axes.plot(...)` -> `PathVisual`;
- `Axes.imshow(...)` -> `ImageVisual`;
- semantic guide methods (`set_xlim`, `set_ylim`, labels, title, ticks, grid) update view/guide
  protocol objects.

Convenience top-level helpers mirror those methods for one-off visuals.

Out of scope:

- broad Matplotlib compatibility;
- direct Datoviz control;
- text/glyph, mesh, colorbar, legend, and layout systems;
- generated axes as user data visuals.
