"""Protocol color mapping example.

This example builds accepted S026 protocol objects directly: a shared ColorScale,
scalar image/point/marker encodings, and a semantic ColorbarGuide rendered by the
Matplotlib reference backend.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from gsp.protocol import (
    ColorMapId,
    ColorMapRef,
    ColorScale,
    ColorbarGuide,
    CoordinateSpace,
    ImageOrigin,
    ImageVisual,
    LinearNormalize,
    MarkerShape,
    MarkerVisual,
    PointVisual,
    ScalarColorEncoding,
    ScalarColorSlot,
)
from gsp_matplotlib.protocol_renderer import (
    render_colorbar_guide,
    render_image_visual,
    render_marker_visual,
    render_point_visual,
)


def main() -> None:
    """Render scalar color mappings into examples/output."""
    y, x = np.mgrid[0:24, 0:36].astype(np.float32)
    field = np.sin(x / 5.0) * 0.45 + np.cos(y / 6.0) * 0.35 + x / 72.0

    scale = ColorScale(
        id="scale:example",
        colormap=ColorMapRef(ColorMapId.VIRIDIS),
        normalize=LinearNormalize(vmin=-0.75, vmax=1.25),
    )
    color_scales = {scale.id: scale}

    image = ImageVisual(
        id="visual:scalar-image",
        image=np.ascontiguousarray(field.astype(np.float32)),
        extent=(-0.92, 0.28, -0.68, 0.68),
        coordinate_space=CoordinateSpace.NDC,
        origin=ImageOrigin.UPPER,
        color_scale_id=scale.id,
    )

    point_values = np.array([-0.75, -0.25, 0.25, 0.75, 1.25], dtype=np.float32)
    points = PointVisual(
        id="visual:scalar-points",
        positions=np.array(
            [[0.50, -0.52], [0.68, -0.26], [0.80, 0.02], [0.68, 0.30], [0.50, 0.56]],
            dtype=np.float32,
        ),
        sizes=np.array([26.0, 34.0, 42.0, 50.0, 58.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.NDC,
        color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.COLOR,
            values=point_values,
            color_scale_id=scale.id,
        ),
    )

    marker_values = np.array([-0.25, 0.25, 0.75], dtype=np.float32)
    markers = MarkerVisual(
        id="visual:scalar-markers",
        positions=np.array(
            [[0.42, -0.02], [0.62, 0.18], [0.84, -0.02]], dtype=np.float32
        ),
        shape=(MarkerShape.SQUARE, MarkerShape.TRIANGLE, MarkerShape.DIAMOND),
        sizes=np.array([48.0, 54.0, 48.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.NDC,
        fill_color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.FILL,
            values=marker_values,
            color_scale_id=scale.id,
            alpha=0.76,
        ),
    )

    guide = ColorbarGuide(
        id="guide:color-scale",
        panel_id="panel:example",
        color_scale_id=scale.id,
        linked_visual_ids=(image.id, points.id, markers.id),
        label="example value",
        ticks=(-0.75, 0.25, 1.25),
        tick_labels=("low", "mid", "high"),
    )

    fig, ax = plt.subplots(figsize=(7.0, 4.0), dpi=120)
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-0.8, 0.8)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    render_image_visual(ax, image, color_scales=color_scales)
    render_point_visual(ax, points, color_scales=color_scales)
    render_marker_visual(ax, markers, color_scales=color_scales)
    render_colorbar_guide(ax, guide, color_scales=color_scales)

    output = Path("examples/output/protocol_color_mapping.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print(output)


if __name__ == "__main__":
    main()
