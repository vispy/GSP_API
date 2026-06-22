"""Tests for the minimal VisPy2 GSP producer API."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import vispy2 as vp
from gsp.protocol import CoordinateSpace, ImageOrigin, ImageVisual, PointVisual, View2D


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
