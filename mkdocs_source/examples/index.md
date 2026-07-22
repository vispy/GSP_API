# Examples

Start with the [executable first scene](../getting-started/first-scene.md). Its checked-in source is
`examples/docs/first_scene.py`, and the documentation includes that file directly.

The numbered review examples are the maintained current-protocol demonstrations.

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --offscreen
uv run python examples/review/03_points_over_image.py --backend both --offscreen
uv run python examples/review/07_view3d_cube.py --backend matplotlib --offscreen
```

| Range | Subject |
|---|---|
| 01-06 | Scatter, images, guides, color mapping, and View2D interaction |
| 07-09 | Static View3D, terrain, and depth |
| 10-13 | Lambert shading, navigation, and nontrivial mesh geometry |
| 14 | Deterministic View3D camera navigation path |

Datoviz runs require a compatible local v0.4 build. Each generated `summary.json` records whether a backend rendered, adapted, rejected, or failed. Do not interpret a PNG alone as a capability claim.

The maintained scripts live in `examples/review/`; each is directly executable with the same runner
options shown above.

The bounded experimental Datoviz session example is separate from the review runner:

```bash
uv run python examples/vispy2_datoviz_session.py
uv run python examples/vispy2_datoviz_session.py --poll
```

The current-protocol Texture2D example compares nearest and linear field-slot filtering. It first
inspects the separate material and linear-filter capabilities; `--show` opens the bounded Datoviz
display. Matplotlib intentionally rejects textured meshes rather than substituting flat color.

```bash
uv run python examples/vispy2_datoviz_texture2d.py
uv run python examples/vispy2_datoviz_texture2d.py --show
```

## Backend comparison

| Matplotlib reference | Datoviz v0.4 |
|---|---|
| ![A faceted mesh with flat Lambert shading rendered by Matplotlib](../comparisons/lambert-matplotlib.png) | ![The same mesh rendered by Datoviz](../comparisons/lambert-datoviz.png) |
| Adapted 3D raster reference for the accepted flat-Lambert color semantics. | `review.adapted`: mesh rendering succeeds, while title layout and guide-query geometry are not strict. |

Both images were regenerated from `10_view3d_flat_lambert.py` at 1280x720 for this documentation review. See [screenshot provenance](../comparisons/provenance.md) for the recorded classifications.
