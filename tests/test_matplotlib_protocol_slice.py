"""Conformance tests for the Matplotlib protocol point/image slice."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from gsp.protocol import ImageOrigin, ImageVisual, PointVisual
from gsp.protocol.visuals import ImageInterpolation
from gsp_matplotlib.protocol_renderer import render_image_visual, render_point_visual


def test_render_point_visual_creates_path_collection():
    """Protocol points render as a Matplotlib PathCollection."""
    fig, ax = plt.subplots()
    try:
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
            colors=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
            sizes=np.array([16.0, 36.0], dtype=np.float32),
        )

        artist = render_point_visual(ax, visual)

        np.testing.assert_allclose(artist.get_offsets(), visual.positions)
        np.testing.assert_allclose(artist.get_sizes(), visual.sizes)
        np.testing.assert_allclose(artist.get_facecolors()[0], np.array([1.0, 0.0, 0.0, 1.0]))
        assert artist.get_gid() == "visual:points"
    finally:
        plt.close(fig)


def test_render_image_visual_creates_axes_image():
    """Protocol images render as a Matplotlib AxesImage with explicit extent and origin."""
    fig, ax = plt.subplots()
    try:
        image_data = np.array(
            [
                [[255, 0, 0, 255], [0, 255, 0, 255]],
                [[0, 0, 255, 255], [255, 255, 255, 255]],
            ],
            dtype=np.uint8,
        )
        visual = ImageVisual(
            id="visual:image",
            image=image_data,
            extent=(-1.0, 1.0, -0.5, 0.5),
            interpolation=ImageInterpolation.NEAREST,
            origin=ImageOrigin.UPPER,
        )

        artist = render_image_visual(ax, visual)

        np.testing.assert_array_equal(artist.get_array(), image_data)
        assert artist.get_extent() == [-1.0, 1.0, -0.5, 0.5]
        assert artist.get_interpolation() == "nearest"
        assert artist.origin == "upper"
        assert artist.get_gid() == "visual:image"
    finally:
        plt.close(fig)


def test_protocol_visual_validation_rejects_shape_mismatch():
    """Formal visual models reject mismatched first-slice attributes."""
    positions = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    colors = np.array([[255, 255, 255, 255]], dtype=np.uint8)

    try:
        PointVisual("visual:bad", positions, colors, np.array([1.0, 2.0], dtype=np.float32))
    except ValueError as exc:
        assert "colors length" in str(exc)
    else:
        raise AssertionError("PointVisual accepted mismatched colors")
