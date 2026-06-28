# API review examples

These examples are intentionally small and readable. Use them to review the GSP protocol/API shape and compare Matplotlib with the Datoviz v0.4 renderer.

## Quick commands

Run one example with Matplotlib capture:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib
```

Open the same scene live in Matplotlib or Datoviz:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --live
uv run python examples/review/01_scatter_basic.py --backend datoviz --live
```

Compare captured outputs:

```bash
tools/compare-review-examples examples/review/01_scatter_basic.py
```

Artifacts are written under `artifacts/example_review/<example>/`.

## Examples

| File | Reviews |
|---|---|
| `01_scatter_basic.py` | Data-space scatter, per-point color/size, View2D, labels, grid |
| `02_image_basic.py` | Scalar image, extent, origin, interpolation, grayscale clim |
| `03_points_over_image.py` | RGBA image plus point overlay and composition order |
| `04_guides_axes_ticks.py` | Explicit ticks, tick labels, axis labels, grid, title |
| `05_color_mapping_colorbar.py` | ColorScale, ScalarColorEncoding, named colormap, colorbar |
| `06_text_labels.py` | TextVisual labels, anchors, z-order over points |

## Datoviz capture note

Datoviz live mode is the recommended interactive review path. The v0.4 adapter automatically prefers a sibling `../datoviz` source checkout when present; set `GSP_DATOVIZ_SOURCE=/path/to/datoviz` to override, or `GSP_DATOVIZ_SOURCE=none` to disable this.

Offscreen PNG capture is opt-in because native offscreen creation can abort in some local GPU/display configurations:

```bash
GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1 tools/compare-review-examples examples/review/01_scatter_basic.py
# or
uv run python examples/review/01_scatter_basic.py --backend datoviz --datoviz-offscreen
```

When Datoviz capture is not enabled or unsupported, the runner writes `datoviz.unsupported.json` rather than pretending parity.
