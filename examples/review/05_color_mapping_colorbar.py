"""API review example: scalar point colors with a shared color scale and colorbar."""

from __future__ import annotations

import numpy as np

from _review_runner import ReviewScene, run_review
from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    ColorMapId,
    ColorMapRef,
    ColorScale,
    ColorbarGuide,
    CoordinateSpace,
    LinearNormalize,
    PanelTextGuide,
    PanelTextRole,
    PointVisual,
    ScalarColorDomain,
    ScalarColorEncoding,
    ScalarColorSlot,
    View2D,
)


def build_scene() -> ReviewScene:
    angles = np.linspace(0.0, 2.0 * np.pi, 24, endpoint=False, dtype=np.float32)
    radius = 0.75 + 0.18 * np.sin(3.0 * angles)
    positions = np.column_stack([radius * np.cos(angles), radius * np.sin(angles)]).astype(np.float32)
    values = np.linspace(-1.0, 1.0, positions.shape[0], dtype=np.float32)
    scale = ColorScale(id="colorscale:review", colormap=ColorMapRef(ColorMapId.VIRIDIS), normalize=LinearNormalize(vmin=-1.0, vmax=1.0), description="review scalar scale")
    view = View2D(id="view:color", panel_id="panel:main", x_range=(-1.1, 1.1), y_range=(-1.1, 1.1))
    return ReviewScene(
        title="Color mapping API review",
        view=view,
        color_scales=(scale,),
        visuals=(
            PointVisual(
                id="visual:scalar-points",
                positions=positions,
                colors=None,
                sizes=42.0,
                coordinate_space=CoordinateSpace.DATA,
                color_encoding=ScalarColorEncoding(slot=ScalarColorSlot.COLOR, domain=ScalarColorDomain.ITEM, values=values, color_scale_id=scale.id, alpha=0.95),
            ),
        ),
        colorbar_guides=(ColorbarGuide(id="guide:colorbar", panel_id="panel:main", color_scale_id=scale.id, linked_visual_ids=("visual:scalar-points",), label="value", ticks=(-1.0, 0.0, 1.0), tick_labels=("low", "mid", "high")),),
        axis_guides=(
            AxisGuide(id="guide:x", view_id=view.id, dimension=AxisDimension.X, side=AxisSide.BOTTOM, label_text="x"),
            AxisGuide(id="guide:y", view_id=view.id, dimension=AxisDimension.Y, side=AxisSide.LEFT, label_text="y"),
        ),
        panel_text_guides=(PanelTextGuide(id="guide:title", panel_id="panel:main", role=PanelTextRole.TITLE, text="Scalar colors + colorbar"),),
        notes=("Reviews ColorScale, ScalarColorEncoding, named colormap, normalization, and a linked ColorbarGuide.",),
    )


if __name__ == "__main__":
    raise SystemExit(run_review(build_scene))
