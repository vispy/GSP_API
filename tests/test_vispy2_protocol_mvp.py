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
    CoordinateSpace,
    ImageOrigin,
    ImageVisual,
    PanelTextRole,
    PointVisual,
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


def test_vispy2_output_renders_through_matplotlib_protocol_backend():
    fig, ax = vp.subplots()
    ax.imshow(np.zeros((2, 2, 4), dtype=np.uint8), extent=(-1.0, 1.0, -1.0, 1.0), id="visual:image")
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
    assert fig.views() == (View2D(id="view:1", panel_id="panel:1", x_range=(-1.0, 2.0), y_range=(-3.0, 4.0)),)
    assert ax.get_xlim() == (-1.0, 2.0)
    assert ax.get_ylim() == (-3.0, 4.0)


def test_matplotlib_render_honors_view2d_limits():
    fig, ax = vp.subplots()
    ax.set_xlim(-1.0, 2.0)
    ax.set_ylim(-3.0, 4.0)
    ax.imshow(np.zeros((2, 2, 4), dtype=np.uint8), extent=(-10.0, 10.0, -10.0, 10.0), id="visual:image")
    ax.scatter(np.array([[0.0, 0.0]], dtype=np.float32), id="visual:points")

    mpl_fig, mpl_axes = fig.render_matplotlib()
    try:
        assert mpl_axes.get_xlim() == (-1.0, 2.0)
        assert mpl_axes.get_ylim() == (-3.0, 4.0)
    finally:
        plt.close(mpl_fig)


def test_top_level_helpers_emit_protocol_visuals():
    point = vp.scatter(np.array([[0.0, 0.0]], dtype=np.float32))
    image = vp.imshow(np.zeros((1, 1), dtype=np.float32))

    assert isinstance(point, PointVisual)
    assert isinstance(image, ImageVisual)


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
        assert [label.get_text() for label in mpl_axes.get_xticklabels()] == ["zero", "half", "one"]
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
    ],
)
def test_vispy2_protocol_examples_are_runnable(example):
    namespace = runpy.run_path(str(Path(example)))
    fig = namespace["fig"]

    assert fig.visuals()
    assert fig.panels()
    assert fig.views()
