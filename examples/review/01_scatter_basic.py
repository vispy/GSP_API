"""API review example: basic scatter plot with data-space points."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    CoordinateSpace,
    PanelTextGuide,
    PanelTextRole,
    PointVisual,
    View2D,
)


def build_scene() -> ReviewScene:
    x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float32)
    y = np.array([1.0, 0.2, 1.4, 0.4, 1.8], dtype=np.float32)
    positions = np.column_stack([x, y]).astype(np.float32)
    colors = np.array(
        [[31, 119, 180, 255], [255, 127, 14, 255], [44, 160, 44, 255], [214, 39, 40, 255], [148, 103, 189, 255]],
        dtype=np.uint8,
    )

    view = View2D(id="view:main", panel_id="panel:main", x_range=(-2.5, 2.5), y_range=(0.0, 2.2))
    return ReviewScene(
        title="Basic scatter API review",
        view=view,
        visuals=(PointVisual(id="visual:scatter", positions=positions, colors=colors, sizes=np.array([18, 28, 38, 48, 58], dtype=np.float32), coordinate_space=CoordinateSpace.DATA),),
        axis_guides=(
            AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, label_text="x", grid_visible=True),
            AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, label_text="signal", grid_visible=True),
        ),
        panel_text_guides=(PanelTextGuide(id="guide:title", panel_id="panel:main", role=PanelTextRole.TITLE, text="Basic scatter"),),
        notes=("Reviews data-space point positions, per-point RGBA colors, pixel diameters, View2D limits, labels, and grid intent.",),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
