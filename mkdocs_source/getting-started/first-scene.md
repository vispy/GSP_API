# First scene

This example uses current protocol records and the Matplotlib reference path. It deliberately does
not claim to demonstrate the full target session lifecycle: the repository exposes the session
contracts, but its review runner currently lowers records to reference renderer functions directly.

```python
import numpy as np

from gsp.protocol import CoordinateSpace, PointVisual, View2D

view = View2D(
    id="view:main",
    panel_id="panel:main",
    x_range=(-2.5, 2.5),
    y_range=(0.0, 2.2),
)

points = PointVisual(
    id="visual:scatter",
    positions=np.array(
        [[-2.0, 1.0], [-1.0, 0.2], [0.0, 1.4], [1.0, 0.4], [2.0, 1.8]],
        dtype=np.float32,
    ),
    colors=np.array(
        [[31, 119, 180, 255], [255, 127, 14, 255], [44, 160, 44, 255],
         [214, 39, 40, 255], [148, 103, 189, 255]],
        dtype=np.uint8,
    ),
    sizes=np.array([18, 28, 38, 48, 58], dtype=np.float32),
    coordinate_space=CoordinateSpace.DATA,
)
```

`View2D` defines the data-to-panel mapping. `PointVisual` describes semantic points rather than a
Matplotlib artist or GPU pipeline. The maintained executable example adds axes and a title:

```bash
uv run python examples/review/01_scatter_basic.py --backend matplotlib --offscreen
```

Next, read [Architecture and roles](../concepts/architecture.md) to see how these records fit into
the target session lifecycle.
