"""Conformance tests for the Matplotlib protocol point/image slice."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from gsp.protocol import ImageOrigin, ImageVisual, MarkerShape, MarkerVisual, PointVisual
from gsp.protocol.visuals import ImageInterpolation
from gsp_matplotlib.protocol_renderer import _marker_areas_from_pixel_diameters, render_image_visual, render_marker_visual, render_point_visual


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
        np.testing.assert_allclose(artist.get_sizes(), _marker_areas_from_pixel_diameters(ax, visual.sizes))
        np.testing.assert_allclose(artist.get_facecolors()[0], np.array([1.0, 0.0, 0.0, 1.0]))
        assert artist.get_gid() == "visual:points"
    finally:
        plt.close(fig)


def test_render_point_visual_converts_pixel_diameters_using_figure_dpi():
    """Protocol point sizes are screen-pixel diameters, not Matplotlib scatter areas."""
    fig, ax = plt.subplots(dpi=144)
    try:
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
            sizes=np.array([20.0], dtype=np.float32),
        )

        artist = render_point_visual(ax, visual)

        np.testing.assert_allclose(artist.get_sizes(), np.array([100.0], dtype=np.float32))
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


def test_render_marker_visual_creates_marker_collections():
    """Protocol markers render as shaped Matplotlib PathCollections."""
    fig, ax = plt.subplots()
    try:
        visual = MarkerVisual(
            id="visual:markers",
            positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
            shape=(MarkerShape.SQUARE, MarkerShape.TRIANGLE),
            fill_colors=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
            sizes=np.array([16.0, 36.0], dtype=np.float32),
            angle=np.array([0.0, np.pi / 4.0], dtype=np.float32),
            stroke_color=np.array([0, 0, 0, 255], dtype=np.uint8),
            stroke_width=1.5,
        )

        artists = render_marker_visual(ax, visual)

        assert len(artists) == 2
        assert all(artist.get_gid() == "visual:markers" for artist in artists)
        np.testing.assert_allclose(artists[0].get_offsets(), np.array([[-0.5, 0.25]]))
        np.testing.assert_allclose(artists[1].get_sizes(), np.array([_marker_areas_from_pixel_diameters(ax, visual.sizes)[1]]))
        np.testing.assert_allclose(artists[0].get_facecolors()[0], np.array([1.0, 0.0, 0.0, 1.0]))
        np.testing.assert_allclose(artists[0].get_edgecolors()[0], np.array([0.0, 0.0, 0.0, 1.0]))
        np.testing.assert_allclose(artists[0].get_linewidths(), np.array([1.08]))
    finally:
        plt.close(fig)


def test_render_marker_visual_does_not_renormalize_rotated_marker_paths():
    """Rotated marker paths keep the requested marker-space scale."""
    fig, ax = plt.subplots()
    try:
        visual = MarkerVisual(
            id="visual:rotated-markers",
            positions=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32),
            shape=MarkerShape.TRIANGLE,
            fill_colors=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
            sizes=np.array([40.0, 40.0], dtype=np.float32),
            angle=np.array([0.0, np.pi / 4.0], dtype=np.float32),
        )

        artists = render_marker_visual(ax, visual)

        np.testing.assert_allclose(artists[0].get_sizes(), artists[1].get_sizes())
        unrotated_bbox = artists[0].get_paths()[0].get_extents()
        rotated_bbox = artists[1].get_paths()[0].get_extents()
        assert rotated_bbox.width > unrotated_bbox.width
        assert rotated_bbox.height > unrotated_bbox.height
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


def test_marker_visual_validation_covers_shapes_angles_and_stroke():
    """MarkerVisual validates scalar and per-item marker-specific attributes."""
    positions = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    colors = np.array([[255, 255, 255, 255], [0, 0, 0, 255]], dtype=np.uint8)

    visual = MarkerVisual(
        "visual:markers",
        positions,
        MarkerShape.DISC,
        colors,
        np.array([12.0, 14.0], dtype=np.float32),
        angle=np.array([0.0, 0.5], dtype=np.float32),
    )

    assert visual.shape_values() == (MarkerShape.DISC, MarkerShape.DISC)
    np.testing.assert_allclose(visual.angle_values(), np.array([0.0, 0.5], dtype=np.float32))

    with pytest.raises(ValueError, match="shape length"):
        MarkerVisual("visual:bad-shape", positions, (MarkerShape.DISC,), colors, 4.0)

    with pytest.raises(ValueError, match="angle length"):
        MarkerVisual("visual:bad-angle", positions, MarkerShape.DISC, colors, 4.0, angle=np.array([0.0], dtype=np.float32))

    with pytest.raises(ValueError, match="stroke_color"):
        MarkerVisual("visual:bad-stroke-color", positions, MarkerShape.DISC, colors, 4.0, stroke_color=np.zeros((1, 4), dtype=np.uint8))

    with pytest.raises(ValueError, match="stroke_width must be non-negative"):
        MarkerVisual("visual:bad-stroke-width", positions, MarkerShape.DISC, colors, 4.0, stroke_width=-1.0)


def test_protocol_visual_validation_rejects_non_finite_point_fields():
    """Formal point visuals reject NaN/Inf protocol values."""
    colors = np.array([[255, 255, 255, 255]], dtype=np.uint8)
    finite_positions = np.array([[0.0, 0.0]], dtype=np.float32)

    with pytest.raises(ValueError, match="positions must be finite"):
        PointVisual("visual:bad-positions", np.array([[np.nan, 0.0]], dtype=np.float32), colors, 1.0)

    with pytest.raises(ValueError, match="sizes must be finite"):
        PointVisual("visual:bad-sizes", finite_positions, colors, np.array([np.inf], dtype=np.float32))

    with pytest.raises(ValueError, match="floating point colors must be finite"):
        PointVisual(
            "visual:bad-colors",
            finite_positions,
            np.array([[0.0, np.nan, 0.0, 1.0]], dtype=np.float32),
            1.0,
        )
