"""Tests for the minimal VisPy2 GSP producer API."""

from pathlib import Path
import runpy

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

import vispy2 as vp
from gsp.protocol import (
    AxisDimension,
    ColorMapId,
    ColorbarOrientation,
    CoordinateSpace,
    FontRole,
    ImageOrigin,
    ImageVisual,
    MeshColorMode,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    PanelTextRole,
    PathVisual,
    PointVisual,
    ScalarColorSlot,
    SegmentVisual,
    StrokeCap,
    StrokeJoin,
    TextAnchorX,
    TextAnchorY,
    TextVisual,
    TickSpecKind,
    View2D,
)


def test_subplots_scatter_emits_point_visual():
    fig, ax = vp.subplots()

    visual = ax.scatter(
        np.array([-0.5, 0.5], dtype=np.float32),
        np.array([0.25, -0.25], dtype=np.float32),
        color=np.array([255, 0, 0, 255], dtype=np.uint8),
        size=np.array([16.0, 36.0], dtype=np.float32),
        id="visual:points",
    )

    assert isinstance(visual, PointVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert fig.visuals() == (visual,)
    np.testing.assert_allclose(visual.positions, [[-0.5, 0.25], [0.5, -0.25]])
    np.testing.assert_array_equal(visual.colors, [[255, 0, 0, 255], [255, 0, 0, 255]])
    np.testing.assert_allclose(visual.sizes, [16.0, 36.0])


def test_subplots_imshow_emits_image_visual():
    fig, ax = vp.subplots()
    image = np.zeros((2, 3, 4), dtype=np.uint8)

    visual = ax.imshow(image, origin="lower", id="visual:image")

    assert isinstance(visual, ImageVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert fig.visuals() == (visual,)
    assert visual.origin == ImageOrigin.LOWER
    assert visual.extent == (-0.5, 2.5, -0.5, 1.5)
    np.testing.assert_array_equal(visual.image, image)


def test_vispy2_scalar_image_uses_explicit_color_scale():
    fig, ax = vp.subplots()

    visual = ax.imshow(
        np.array([[0.0, 0.5], [1.0, 1.5]], dtype=np.float32),
        cmap="viridis",
        clim=(0.0, 1.0),
        id="visual:image",
    )

    scale = fig.color_scales()[0]
    assert scale.colormap.id == ColorMapId.VIRIDIS
    assert scale.normalize.vmin == 0.0
    assert scale.normalize.vmax == 1.0
    assert visual.color_scale_id == scale.id
    assert visual.colormap is None
    assert visual.clim is None


def test_subplots_markers_emits_marker_visual():
    fig, ax = vp.subplots()

    visual = ax.markers(
        np.array([-0.5, 0.5], dtype=np.float32),
        np.array([0.25, -0.25], dtype=np.float32),
        shape=("square", MarkerShape.TRIANGLE),
        fill_color=np.array([255, 0, 0, 255], dtype=np.uint8),
        size=np.array([16.0, 36.0], dtype=np.float32),
        angle=np.array([0.0, 0.5], dtype=np.float32),
        stroke_color=np.array([0, 0, 0, 255], dtype=np.uint8),
        stroke_width=1.5,
        id="visual:markers",
    )

    assert isinstance(visual, MarkerVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert fig.visuals() == (visual,)
    assert visual.shape_values() == (MarkerShape.SQUARE, MarkerShape.TRIANGLE)
    np.testing.assert_allclose(visual.positions, [[-0.5, 0.25], [0.5, -0.25]])
    np.testing.assert_array_equal(
        visual.fill_colors, [[255, 0, 0, 255], [255, 0, 0, 255]]
    )
    np.testing.assert_allclose(visual.sizes, [16.0, 36.0])
    np.testing.assert_allclose(visual.angle_values(), [0.0, 0.5])
    np.testing.assert_array_equal(visual.stroke_color, [0, 0, 0, 255])
    assert visual.stroke_width == 1.5


def test_vispy2_point_and_marker_scalar_colors_emit_protocol_encodings():
    fig, ax = vp.subplots()
    scale = ax.color_scale(cmap="magma", clim=(0.0, 10.0), id="scale:magma")

    points = ax.scatter(
        [0.0, 1.0],
        [0.0, 1.0],
        c=[0.0, 10.0],
        color_scale=scale,
        alpha=0.5,
        id="visual:points",
    )
    markers = ax.markers(
        [0.0, 1.0],
        [1.0, 0.0],
        fill_color=[2.5, 7.5],
        color_scale="scale:magma",
        id="visual:markers",
    )

    assert fig.color_scales() == (scale,)
    assert points.colors is None
    assert points.color_encoding is not None
    assert points.color_encoding.slot == ScalarColorSlot.COLOR
    assert points.color_encoding.color_scale_id == "scale:magma"
    assert points.color_encoding.alpha == 0.5
    np.testing.assert_allclose(points.color_encoding.values, [0.0, 10.0])
    assert markers.fill_colors is None
    assert markers.fill_color_encoding is not None
    assert markers.fill_color_encoding.slot == ScalarColorSlot.FILL
    assert markers.fill_color_encoding.color_scale_id == "scale:magma"
    np.testing.assert_allclose(markers.fill_color_encoding.values, [2.5, 7.5])


def test_vispy2_colorbar_emits_semantic_guide_and_renders():
    fig, ax = vp.subplots()
    scale = ax.color_scale(cmap="cividis", clim=(-1.0, 1.0), id="scale:cividis")
    guide = ax.colorbar(
        scale,
        label="Value",
        orientation="horizontal",
        ticks=[-1.0, 0.0, 1.0],
        tick_labels=["low", "zero", "high"],
        linked_visual_ids=["visual:image"],
        id="guide:colorbar",
    )

    assert fig.colorbar_guides() == (guide,)
    assert guide.color_scale_id == "scale:cividis"
    assert guide.orientation == ColorbarOrientation.HORIZONTAL
    assert guide.linked_visual_ids == ("visual:image",)

    ax.imshow(
        np.array([[0.0, 1.0]], dtype=np.float32),
        color_scale=scale,
        id="visual:image",
    )
    mpl_fig, _ = fig.render_matplotlib()
    try:
        colorbar_axes = [
            axes for axes in mpl_fig.axes if axes.get_gid() == "guide:colorbar"
        ]
        assert len(colorbar_axes) == 1
        assert colorbar_axes[0].get_xlabel() == "Value"
        assert [label.get_text() for label in colorbar_axes[0].get_xticklabels()] == [
            "low",
            "zero",
            "high",
        ]
    finally:
        plt.close(mpl_fig)


def test_vispy2_scalar_color_requires_explicit_normalization():
    _, ax = vp.subplots()

    with pytest.raises(ValueError, match="cmap and clim"):
        ax.scatter([0.0, 1.0], [0.0, 1.0], c=[0.0, 1.0], cmap="viridis")

    with pytest.raises(ValueError, match="clim is required"):
        ax.imshow(np.zeros((2, 2), dtype=np.float32), cmap="viridis")


def test_subplots_segments_emits_segment_visual():
    fig, ax = vp.subplots()

    visual = ax.segments(
        np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        np.array([[0.0, 0.5], [0.75, 0.25]], dtype=np.float32),
        color=np.array([255, 0, 0, 255], dtype=np.uint8),
        width=np.array([16.0, 36.0], dtype=np.float32),
        cap="round",
        id="visual:segments",
    )

    assert isinstance(visual, SegmentVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert fig.visuals() == (visual,)
    np.testing.assert_allclose(visual.start_positions, [[-0.5, 0.25], [0.5, -0.25]])
    np.testing.assert_allclose(visual.end_positions, [[0.0, 0.5], [0.75, 0.25]])
    np.testing.assert_array_equal(visual.colors, [[255, 0, 0, 255], [255, 0, 0, 255]])
    np.testing.assert_allclose(visual.width_values(), [16.0, 36.0])
    assert visual.cap == StrokeCap.ROUND


def test_subplots_path_and_plot_emit_path_visuals():
    fig, ax = vp.subplots()

    visual = ax.path(
        np.array(
            [[-0.5, 0.25], [0.0, 0.5], [0.5, -0.25], [0.75, 0.25]],
            dtype=np.float32,
        ),
        path_lengths=(2, 2),
        color=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
        width=np.array([16.0, 36.0], dtype=np.float32),
        cap="round",
        join="bevel",
        id="visual:paths",
    )

    assert isinstance(visual, PathVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert fig.visuals() == (visual,)
    assert visual.path_lengths == (2, 2)
    assert visual.cap == StrokeCap.ROUND
    assert visual.join == StrokeJoin.BEVEL

    plotted = ax.plot([0.0, 1.0], [1.0, 0.0], id="visual:plot")
    assert isinstance(plotted, PathVisual)
    assert plotted.path_lengths == (2,)


def test_subplots_text_emits_text_visual():
    fig, ax = vp.subplots()

    visual = ax.text(
        np.array([-0.5, 0.5], dtype=np.float32),
        np.array([0.25, -0.25], dtype=np.float32),
        ["left", "right"],
        color=np.array([255, 0, 0, 255], dtype=np.uint8),
        font_size_px=np.array([16.0, 24.0], dtype=np.float32),
        font_role="monospace",
        anchor_x=("left", TextAnchorX.RIGHT),
        anchor_y=TextAnchorY.CENTER,
        rotation_rad=np.array([0.0, 0.5], dtype=np.float32),
        z_order=3,
        id="visual:text",
    )

    assert isinstance(visual, TextVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert fig.visuals() == (visual,)
    assert fig.attachments()[0].visual_id == "visual:text"
    assert visual.texts == ("left", "right")
    np.testing.assert_allclose(visual.positions, [[-0.5, 0.25], [0.5, -0.25]])
    np.testing.assert_array_equal(visual.rgba, [[255, 0, 0, 255], [255, 0, 0, 255]])
    np.testing.assert_allclose(visual.font_size_values(), [16.0, 24.0])
    assert visual.font_role == FontRole.MONOSPACE
    assert visual.anchor_x_values() == (TextAnchorX.LEFT, TextAnchorX.RIGHT)
    assert visual.anchor_y_values() == (TextAnchorY.CENTER, TextAnchorY.CENTER)
    np.testing.assert_allclose(visual.rotation_values(), [0.0, 0.5])
    assert visual.z_order == 3


def test_subplots_mesh_emits_mesh_visual():
    fig, ax = vp.subplots()

    visual = ax.mesh(
        np.array(
            [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]],
            dtype=np.float32,
        ),
        np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
        color=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
        color_mode="face",
        order=2.0,
        id="visual:mesh",
    )

    assert isinstance(visual, MeshVisual)
    assert visual.coordinate_space == CoordinateSpace.DATA
    assert visual.resolved_color_mode() == MeshColorMode.FACE
    assert fig.visuals() == (visual,)
    assert fig.attachments()[0].visual_id == "visual:mesh"
    np.testing.assert_allclose(
        visual.positions, [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]]
    )
    np.testing.assert_array_equal(visual.faces, [[0, 1, 2], [0, 2, 3]])
    np.testing.assert_array_equal(visual.color, [[255, 0, 0, 255], [0, 0, 255, 255]])
    assert visual.order == 2.0


def test_text_rejects_deferred_font_and_mismatched_texts():
    _, ax = vp.subplots()

    with pytest.raises(ValueError, match="texts length"):
        ax.text([0.0, 1.0], [0.0, 1.0], ["one"])

    with pytest.raises(ValueError):
        ax.text([0.0], [0.0], "one", font_role="Helvetica")

    with pytest.raises(ValueError, match="font_size_px"):
        ax.text([0.0], [0.0], "one", font_size_px=0.0)


def test_vispy2_text_renders_through_matplotlib_protocol_backend():
    fig, ax = vp.subplots()
    ax.text(
        [0.0], [0.0], "center", anchor_x="center", anchor_y="center", id="visual:text"
    )

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert len(mpl_axes.texts) == 1
        assert mpl_axes.texts[0].get_text() == "center"
        assert mpl_axes.texts[0].get_gid() == "visual:text"
        assert mpl_axes.texts[0].get_ha() == "center"
    finally:
        plt.close(mpl_fig)


def test_vispy2_mesh_renders_through_matplotlib_protocol_backend():
    fig, ax = vp.subplots()
    ax.mesh(
        [[-0.5, -0.5], [0.5, -0.5], [0.0, 0.5]],
        [[0, 1, 2]],
        color=[255, 0, 0, 255],
        id="visual:mesh",
    )

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert len(mpl_axes.collections) == 1
        assert mpl_axes.collections[0].get_gid() == "visual:mesh"
    finally:
        plt.close(mpl_fig)


def test_vispy2_output_renders_through_matplotlib_protocol_backend():
    fig, ax = vp.subplots()
    ax.imshow(
        np.zeros((2, 2, 4), dtype=np.uint8),
        extent=(-1.0, 1.0, -1.0, 1.0),
        id="visual:image",
    )
    ax.scatter(
        np.array([[0.0, 0.0], [0.5, 0.5]], dtype=np.float32),
        color=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
        id="visual:points",
    )

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert len(mpl_axes.images) == 1
        assert len(mpl_axes.collections) == 1
        assert mpl_axes.images[0].get_gid() == "visual:image"
        assert mpl_axes.collections[0].get_gid() == "visual:points"
    finally:
        plt.close(mpl_fig)


def test_view2d_is_separate_from_data_visual_stream():
    fig, ax = vp.subplots()
    ax.set_xlim(-1.0, 2.0)
    ax.set_ylim(-3.0, 4.0)
    point = ax.scatter(np.array([[0.0, 0.0]], dtype=np.float32), id="visual:points")

    assert fig.visuals() == (point,)
    assert fig.panels()[0].id == "panel:1"
    assert fig.attachments()[0].visual_id == "visual:points"
    assert fig.attachments()[0].view_id == fig.views()[0].id
    assert fig.views() == (
        View2D(
            id="view:1", panel_id="panel:1", x_range=(-1.0, 2.0), y_range=(-3.0, 4.0)
        ),
    )
    assert ax.get_xlim() == (-1.0, 2.0)
    assert ax.get_ylim() == (-3.0, 4.0)


def test_matplotlib_render_honors_view2d_limits():
    fig, ax = vp.subplots()
    ax.set_xlim(-1.0, 2.0)
    ax.set_ylim(-3.0, 4.0)
    ax.imshow(
        np.zeros((2, 2, 4), dtype=np.uint8),
        extent=(-10.0, 10.0, -10.0, 10.0),
        id="visual:image",
    )
    ax.scatter(np.array([[0.0, 0.0]], dtype=np.float32), id="visual:points")

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert mpl_axes.get_xlim() == (-1.0, 2.0)
        assert mpl_axes.get_ylim() == (-3.0, 4.0)
    finally:
        plt.close(mpl_fig)


def test_top_level_helpers_emit_protocol_visuals():
    point = vp.scatter(np.array([[0.0, 0.0]], dtype=np.float32))
    marker = vp.markers(np.array([[0.0, 0.0]], dtype=np.float32))
    segment = vp.segments(
        np.array([[0.0, 0.0]], dtype=np.float32),
        np.array([[1.0, 0.0]], dtype=np.float32),
    )
    path = vp.path(np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32))
    image = vp.imshow(np.zeros((1, 1), dtype=np.float32))
    label = vp.text([0.0], [0.0], "label")
    mesh = vp.mesh(
        [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]],
        [[0, 1, 2]],
        color=[255, 0, 0, 255],
    )

    assert isinstance(point, PointVisual)
    assert isinstance(marker, MarkerVisual)
    assert isinstance(segment, SegmentVisual)
    assert isinstance(path, PathVisual)
    assert isinstance(image, ImageVisual)
    assert isinstance(label, TextVisual)
    assert isinstance(mesh, MeshVisual)


def test_vispy2_guide_apis_emit_semantic_protocol_guides():
    fig, ax = vp.subplots()

    ax.set_xlabel("time")
    ax.set_ylabel("value")
    ax.set_title("Demo")
    ax.set_xticks([0.0, 0.5, 1.0], labels=["zero", "half", "one"])
    ax.set_yticks([-1.0, 0.0, 1.0])
    ax.grid(True, axis="x")

    x_guide, y_guide = fig.axis_guides()
    title = fig.panel_text_guides()[0]

    assert x_guide.dimension == AxisDimension.X
    assert x_guide.label_text == "time"
    assert x_guide.grid_visible is True
    assert x_guide.tick_spec.kind == TickSpecKind.EXPLICIT
    assert x_guide.tick_spec.explicit_values == (0.0, 0.5, 1.0)
    assert x_guide.tick_spec.explicit_labels == ("zero", "half", "one")
    assert y_guide.dimension == AxisDimension.Y
    assert y_guide.label_text == "value"
    assert y_guide.grid_visible is False
    assert y_guide.tick_spec.explicit_values == (-1.0, 0.0, 1.0)
    assert title.role == PanelTextRole.TITLE
    assert title.text == "Demo"
    assert fig.visuals() == ()


def test_vispy2_guide_api_getters_and_clear_title():
    fig, ax = vp.subplots()

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Temporary")
    ax.set_title(None)
    ax.set_xticks([])

    assert ax.get_xlabel() == "x"
    assert ax.get_ylabel() == "y"
    assert ax.get_title() is None
    assert ax.get_xticks() == ()
    assert fig.panel_text_guides() == ()
    assert fig.axis_guides()[0].tick_spec.kind == TickSpecKind.NONE


def test_vispy2_guide_apis_render_through_matplotlib_reference():
    fig, ax = vp.subplots()
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlabel("time")
    ax.set_ylabel("value")
    ax.set_title("Demo")
    ax.set_xticks([0.0, 0.5, 1.0], labels=["zero", "half", "one"])
    ax.grid(True)
    point = ax.scatter(np.array([[0.5, 0.0]], dtype=np.float32), id="visual:points")

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert fig.visuals() == (point,)
        assert list(mpl_axes.get_xticks()) == [0.0, 0.5, 1.0]
        assert [label.get_text() for label in mpl_axes.get_xticklabels()] == [
            "zero",
            "half",
            "one",
        ]
        assert mpl_axes.get_xlabel() == "time"
        assert mpl_axes.get_ylabel() == "value"
        assert mpl_axes.get_title() == "Demo"
        assert any(line.get_visible() for line in mpl_axes.get_xgridlines())
        assert any(line.get_visible() for line in mpl_axes.get_ygridlines())
    finally:
        plt.close(mpl_fig)


def test_vispy2_guide_example_covers_public_guide_surface():
    namespace = runpy.run_path(str(Path("examples/vispy2_protocol_guides.py")))
    fig = namespace["fig"]
    ax = namespace["ax"]

    assert ax.get_xlim() == (-1.0, 1.0)
    assert ax.get_ylim() == (-1.0, 1.0)
    assert ax.get_xlabel() == "x position"
    assert ax.get_ylabel() == "y position"
    assert ax.get_title() == "VisPy2 guide API"
    assert ax.get_xticks() == (-1.0, 0.0, 1.0)
    assert ax.get_yticks() == (-1.0, 0.0, 1.0)

    x_guide, y_guide = fig.axis_guides()
    assert x_guide.grid_visible is True
    assert y_guide.grid_visible is True
    assert x_guide.tick_spec.kind == TickSpecKind.EXPLICIT
    assert x_guide.tick_spec.explicit_labels == ("left", "center", "right")
    assert len(fig.visuals()) == 2
    assert len(fig.panel_text_guides()) == 1


@pytest.mark.parametrize(
    "example",
    [
        "examples/vispy2_protocol_scatter.py",
        "examples/vispy2_protocol_imshow.py",
        "examples/vispy2_protocol_point_over_image.py",
        "examples/vispy2_protocol_guides.py",
        "examples/vispy2_protocol_mesh.py",
    ],
)
def test_vispy2_protocol_examples_are_runnable(example):
    namespace = runpy.run_path(str(Path(example)))
    fig = namespace["fig"]

    assert fig.visuals()
    assert fig.panels()
    assert fig.views()
