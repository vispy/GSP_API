# API review examples

These examples are intentionally small and readable. Use them to review the GSP protocol/API shape and compare Matplotlib with the Datoviz v0.4 renderer.

## Quick commands

Open one example live with Matplotlib or Datoviz:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib
uv run python examples/review/01_scatter_basic.py --backend datoviz
```

Open both live windows sequentially:

```bash
uv run python examples/review/01_scatter_basic.py --backend both
```

Capture and compare offscreen outputs:

```bash
uv run python examples/review/01_scatter_basic.py --backend both --offscreen
tools/compare-review-examples examples/review/01_scatter_basic.py --offscreen
```

Offscreen artifacts are written under `artifacts/example_review/<example>/`.

## Examples

| File | Reviews |
|---|---|
| `01_scatter_basic.py` | Data-space scatter, per-point color/size, View2D, labels, grid |
| `02_image_basic.py` | Scalar image, extent, origin, interpolation, grayscale clim |
| `03_points_over_image.py` | RGBA image plus point overlay and composition order |
| `04_guides_axes_ticks.py` | Explicit ticks, tick labels, axis labels, grid, title |
| `05_color_mapping_colorbar.py` | ColorScale, ScalarColorEncoding, named colormap, colorbar |
| `06_text_labels.py` | TextVisual labels, anchors, z-order over points |

## Offscreen Capture Note

Live mode is the default interactive review path. The Datoviz v0.4 adapter automatically prefers a sibling `../datoviz` source checkout when present; set `GSP_DATOVIZ_SOURCE=/path/to/datoviz` to override, or `GSP_DATOVIZ_SOURCE=none` to disable this.

Offscreen PNG capture is opt-in for both Matplotlib and Datoviz:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --offscreen
uv run python examples/review/01_scatter_basic.py --backend datoviz --offscreen
tools/compare-review-examples examples/review/01_scatter_basic.py --offscreen
```

Datoviz offscreen creation can abort in some local GPU/display configurations. If Datoviz capture is unsupported, the runner writes `datoviz.unsupported.json` rather than pretending parity.
