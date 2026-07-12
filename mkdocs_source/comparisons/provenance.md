# Screenshot provenance

The public comparison assets were generated from the current-protocol review examples. A successful
capture is visual review evidence, not automatic strict capability promotion.

| Asset | Source example | Backend | Resolution | Observed classification |
|---|---|---|---|---|
| `scatter-matplotlib.png` | `examples/review/01_scatter_basic.py` | Matplotlib | 1280×720 | rendered reference path |
| `terrain-matplotlib.png` | `examples/review/08_view3d_terrain.py` | Matplotlib | 1280×720 | adapted 3D reference raster |
| `terrain-datoviz.png` | `examples/review/08_view3d_terrain.py` | Datoviz v0.4 | 1280×720 | `review.adapted`; title and guide-query limitations |
| `lambert-matplotlib.png` | `examples/review/10_view3d_flat_lambert.py` | Matplotlib | 1280×720 | adapted 3D reference raster |
| `lambert-datoviz.png` | `examples/review/10_view3d_flat_lambert.py` | Datoviz v0.4 | 1280×720 | `review.adapted`; title and guide-query limitations |

Commands used the review runner with `--offscreen`; Datoviz used the isolated offscreen path. Exact
feature promotion is recorded in the [generated feature matrix](../support/feature-matrix.md).
