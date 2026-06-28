"""API review example: View2D guides with explicit ticks."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import AxisDimension, AxisGuide, AxisSide, CoordinateSpace, PanelTextGuide, PanelTextRole, PointVisual, TickSpec, TickSpecKind, View2D


def build_scene() -> ReviewScene:
    x = np.linspace(0.0, 10.0, 9, dtype=np.float32)
    y = np.sqrt(x).astype(np.float32)
    view = View2D(id="view:guide-review", panel_id="panel:main", x_range=(0.0, 10.0), y_range=(0.0, 3.5))
    return ReviewScene(
        title="Guide and tick API review",
        view=view,
        visuals=(PointVisual(id="visual:sqrt-points", positions=np.column_stack([x, y]).astype(np.float32), colors=np.repeat(np.array([[52, 101, 164, 255]], dtype=np.uint8), x.shape[0], axis=0), sizes=30.0, coordinate_space=CoordinateSpace.DATA),),
        axis_guides=(
            AxisGuide(id="guide:x-explicit", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, label_text="time (s)", grid_visible=True, tick_spec=TickSpec(kind=TickSpecKind.EXPLICIT, explicit_values=(0.0, 2.5, 5.0, 7.5, 10.0), explicit_labels=("0", "2.5", "5", "7.5", "10"), target_count=None)),
            AxisGuide(id="guide:y-explicit", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, label_text="sqrt(time)", grid_visible=True, tick_spec=TickSpec(kind=TickSpecKind.EXPLICIT, explicit_values=(0.0, 1.0, 2.0, 3.0), explicit_labels=("0", "1", "2", "3"), target_count=None)),
        ),
        panel_text_guides=(PanelTextGuide(id="guide:explicit-title", panel_id="panel:main", role=PanelTextRole.TITLE, text="Explicit ticks + grid"),),
        notes=("Reviews View2D limits, explicit tick values/labels, axis labels, grid visibility, and panel title semantics.",),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
