"""Conformance tests for the Matplotlib protocol point/image slice."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from gsp.protocol import (
    ColorMapId,
    ColorMapRef,
    ColorScale,
    ColorbarGuide,
    CoordinateSpace,
    FontRole,
    ImageColormap,
    ImageOrigin,
    ImageVisual,
    MeshColorMode,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    LinearNormalize,
    PathVisual,
    PointVisual,
    ScalarColorEncoding,
    ScalarColorSlot,
    SegmentVisual,
    StrokeCap,
    StrokeJoin,
    TextAnchorX,
    TextAnchorY,
    TextVisual,
)
from gsp_matplotlib.color_mapping import map_scalar_values
from gsp.protocol.visuals import ImageInterpolation
from gsp_matplotlib.protocol_renderer import (
    _marker_areas_from_pixel_diameters,
    _marker_path,
    render_colorbar_guide,
    render_image_visual,
    render_marker_visual,
    render_mesh_visual,
    render_path_visual,
    render_point_visual,
    render_segment_visual,
    render_text_visual,
)


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
        np.testing.assert_allclose(
            artist.get_sizes(), _marker_areas_from_pixel_diameters(ax, visual.sizes)
        )
        np.testing.assert_allclose(
            artist.get_facecolors()[0], np.array([1.0, 0.0, 0.0, 1.0])
        )
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

        np.testing.assert_allclose(
            artist.get_sizes(), np.array([100.0], dtype=np.float32)
        )
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


def test_render_scalar_image_visual_applies_gray_colormap_and_clim():
    """Scalar images render with explicit scalar colormap/clim semantics."""
    fig, ax = plt.subplots()
    try:
        image_data = np.array([[0.0, 1.0], [2.0, 3.0]], dtype=np.float32)
        visual = ImageVisual(
            id="visual:scalar-image",
            image=image_data,
            extent=(-1.0, 1.0, -0.5, 0.5),
            colormap=ImageColormap.GRAY,
            clim=(0.5, 2.5),
        )

        artist = render_image_visual(ax, visual)

        assert artist.get_cmap().name == "gray"
        assert artist.get_clim() == (0.5, 2.5)
    finally:
        plt.close(fig)


def test_render_scalar_image_visual_maps_color_scale_to_rgba():
    """S026 scalar images use the accepted color scale sampling rule."""
    fig, ax = plt.subplots()
    try:
        scale = _test_color_scale()
        image_data = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
        visual = ImageVisual(
            id="visual:scalar-image",
            image=image_data,
            extent=(0.0, 3.0, 0.0, 1.0),
            color_scale_id=scale.id,
        )

        artist = render_image_visual(ax, visual, color_scales={scale.id: scale})

        np.testing.assert_allclose(
            np.asarray(artist.get_array()), map_scalar_values(image_data, scale)
        )
        assert artist.get_cmap().name == "viridis"
    finally:
        plt.close(fig)


def test_render_point_visual_maps_scalar_color_encoding():
    """PointVisual scalar colors render through canonical S026 mapping."""
    fig, ax = plt.subplots()
    try:
        scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32),
            sizes=np.array([10.0, 10.0], dtype=np.float32),
            color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.COLOR,
                values=np.array([0.0, 0.5], dtype=np.float32),
                color_scale_id=scale.id,
            ),
        )

        artist = render_point_visual(ax, visual, color_scales={scale.id: scale})

        np.testing.assert_allclose(
            artist.get_facecolors(),
            map_scalar_values(visual.color_encoding.values, scale),
        )
    finally:
        plt.close(fig)


def test_render_marker_visual_maps_scalar_fill_encoding():
    """MarkerVisual fill scalars render while stroke styling remains explicit."""
    fig, ax = plt.subplots()
    try:
        scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
        visual = MarkerVisual(
            id="visual:markers",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            shape=MarkerShape.DISC,
            sizes=np.array([12.0], dtype=np.float32),
            stroke_color=np.array([255, 0, 0, 255], dtype=np.uint8),
            stroke_width=2.0,
            fill_color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.FILL,
                values=np.array([1.0], dtype=np.float32),
                color_scale_id=scale.id,
                alpha=0.5,
            ),
        )

        (artist,) = render_marker_visual(ax, visual, color_scales={scale.id: scale})

        np.testing.assert_allclose(
            artist.get_facecolors()[0],
            map_scalar_values(visual.fill_color_encoding.values, scale, alpha=0.5)[0],
        )
        np.testing.assert_allclose(artist.get_edgecolors()[0], [1.0, 0.0, 0.0, 1.0])
    finally:
        plt.close(fig)


def test_render_scalar_visual_requires_declared_color_scale():
    """Scalar color encodings fail loudly when their scale resource is absent."""
    fig, ax = plt.subplots()
    try:
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.COLOR,
                values=np.array([0.0], dtype=np.float32),
                color_scale_id="scale:missing",
            ),
        )

        with pytest.raises(ValueError, match="missing color scale"):
            render_point_visual(ax, visual, color_scales={})
    finally:
        plt.close(fig)


def test_render_colorbar_guide_uses_semantic_scale_and_ticks():
    """ColorbarGuide renders from semantic color scale data."""
    fig, ax = plt.subplots()
    try:
        scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
        guide = ColorbarGuide(
            id="guide:colorbar",
            panel_id="panel:main",
            color_scale_id=scale.id,
            label="Intensity",
            ticks=(0.0, 0.5, 1.0),
            tick_labels=("low", "mid", "high"),
        )

        colorbar = render_colorbar_guide(ax, guide, color_scales={scale.id: scale})

        assert colorbar.ax.get_gid() == "guide:colorbar"
        assert colorbar.ax.get_ylabel() == "Intensity"
        np.testing.assert_allclose(colorbar.get_ticks(), [0.0, 0.5, 1.0])
        assert [tick.get_text() for tick in colorbar.ax.get_yticklabels()] == [
            "low",
            "mid",
            "high",
        ]
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
        np.testing.assert_allclose(
            artists[1].get_sizes(),
            np.array([_marker_areas_from_pixel_diameters(ax, visual.sizes)[1]]),
        )
        np.testing.assert_allclose(
            artists[0].get_facecolors()[0], np.array([1.0, 0.0, 0.0, 1.0])
        )
        np.testing.assert_allclose(
            artists[0].get_edgecolors()[0], np.array([0.0, 0.0, 0.0, 1.0])
        )
        np.testing.assert_allclose(artists[0].get_linewidths(), np.array([1.08]))
    finally:
        plt.close(fig)


def test_render_segment_visual_creates_line_collection_with_pixel_widths():
    """Protocol segments render as a Matplotlib LineCollection."""
    fig, ax = plt.subplots(dpi=144)
    try:
        visual = SegmentVisual(
            id="visual:segments",
            start_positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
            end_positions=np.array([[0.0, 0.5], [0.75, 0.25]], dtype=np.float32),
            colors=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
            widths=np.array([10.0, 20.0], dtype=np.float32),
            cap=StrokeCap.ROUND,
        )

        artist = render_segment_visual(ax, visual)

        assert artist.get_gid() == "visual:segments"
        np.testing.assert_allclose(artist.get_segments()[0], [[-0.5, 0.25], [0.0, 0.5]])
        np.testing.assert_allclose(artist.get_linewidths(), np.array([5.0, 10.0]))
        np.testing.assert_allclose(
            artist.get_colors()[0], np.array([1.0, 0.0, 0.0, 1.0])
        )
        assert artist.get_capstyle() == "round"
    finally:
        plt.close(fig)


def test_render_path_visual_creates_open_path_patches_with_pixel_widths():
    """Protocol paths render as open Matplotlib PathPatches."""
    fig, ax = plt.subplots(dpi=144)
    try:
        visual = PathVisual(
            id="visual:paths",
            positions=np.array(
                [[-0.5, 0.0], [0.0, 0.5], [0.5, 0.0], [0.6, -0.2], [0.8, 0.2]],
                dtype=np.float32,
            ),
            path_lengths=(3, 2),
            colors=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
            widths=np.array([10.0, 20.0], dtype=np.float32),
            cap=StrokeCap.ROUND,
            join=StrokeJoin.BEVEL,
        )

        artists = render_path_visual(ax, visual)

        assert len(artists) == 2
        assert all(artist.get_gid() == "visual:paths" for artist in artists)
        np.testing.assert_allclose(
            artists[0].get_path().vertices, [[-0.5, 0.0], [0.0, 0.5], [0.5, 0.0]]
        )
        np.testing.assert_allclose(artists[0].get_linewidth(), 5.0)
        np.testing.assert_allclose(artists[1].get_linewidth(), 10.0)
        assert artists[0].get_capstyle() == "round"
        assert artists[0].get_joinstyle() == "bevel"
        assert artists[0].get_fill() is False
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


def test_marker_diamond_path_uses_bbox_diameter_semantics():
    """Protocol diamonds use bbox diameter, not Matplotlib's larger rotated-square marker."""
    path = _marker_path(MarkerShape.DIAMOND, 0.0)
    bbox = path.get_extents()

    np.testing.assert_allclose(
        [bbox.x0, bbox.x1, bbox.y0, bbox.y1], [-0.5, 0.5, -0.5, 0.5]
    )


def test_render_mesh_visual_creates_poly_collection_for_uniform_color():
    """Strict 2D MeshVisual renders as filled Matplotlib polygons."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-0.5, -0.5], [0.5, -0.5], [0.0, 0.5]], dtype=np.float32
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )

        artist = render_mesh_visual(ax, visual)

        assert artist.get_gid() == "visual:mesh"
        assert len(artist.get_paths()) == 1
        np.testing.assert_allclose(
            artist.get_facecolors()[0], np.array([1.0, 0.0, 0.0, 1.0])
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_preserves_per_face_colors():
    """Per-face MeshVisual colors map one RGBA value to each triangle."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([[255, 0, 0, 255], [0, 0, 255, 128]], dtype=np.uint8),
            color_mode=MeshColorMode.FACE,
        )

        artist = render_mesh_visual(ax, visual)

        assert len(artist.get_paths()) == 2
        np.testing.assert_allclose(
            artist.get_facecolors(),
            np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.0, 1.0, 128 / 255.0]]),
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_rejects_3d_reference_path():
    """S025 Matplotlib strict reference is 2D only."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
        )

        with pytest.raises(NotImplementedError, match="2D positions"):
            render_mesh_visual(ax, visual)
    finally:
        plt.close(fig)


def test_render_text_visual_maps_protocol_fields_to_text_artists():
    """TextVisual renders as Matplotlib Text with accepted S024 mappings."""
    from gsp.protocol import CoordinateSpace

    fig, ax = plt.subplots(dpi=144)
    try:
        visual = TextVisual(
            "visual:text",
            ("left", "right\nline"),
            np.array([[-1.0, -1.0], [1.0, 1.0]], dtype=np.float32),
            CoordinateSpace.NDC,
            rgba=np.array([[255, 0, 0, 128], [0, 0, 255, 255]], dtype=np.uint8),
            font_size_px=np.array([20.0, 30.0], dtype=np.float32),
            font_role=FontRole.MONOSPACE,
            anchor_x=(TextAnchorX.LEFT, TextAnchorX.RIGHT),
            anchor_y=(TextAnchorY.BASELINE, TextAnchorY.TOP),
            rotation_rad=np.array([0.0, np.pi / 2.0], dtype=np.float32),
            z_order=7,
        )

        artists = render_text_visual(ax, visual)

        assert len(artists) == 2
        assert artists[0].get_text() == "left"
        assert artists[1].get_text() == "right\nline"
        assert artists[0].get_gid() == "visual:text"
        assert artists[1].get_url() == "visual:text#1"
        np.testing.assert_allclose(artists[0].get_color(), (1.0, 0.0, 0.0, 128 / 255))
        np.testing.assert_allclose(artists[1].get_color(), (0.0, 0.0, 1.0, 1.0))
        np.testing.assert_allclose([a.get_fontsize() for a in artists], [10.0, 15.0])
        assert artists[0].get_fontfamily() == ["monospace"]
        assert artists[0].get_ha() == "left"
        assert artists[1].get_ha() == "right"
        assert artists[0].get_va() == "baseline"
        assert artists[1].get_va() == "top"
        np.testing.assert_allclose(artists[1].get_rotation(), 90.0)
        assert artists[0].get_rotation_mode() == "anchor"
        assert artists[0].get_zorder() == 7
        np.testing.assert_allclose(
            artists[0].get_transform().transform((-1.0, -1.0)),
            ax.transAxes.transform((0.0, 0.0)),
        )
    finally:
        plt.close(fig)


def _test_color_scale(*, colormap_id: ColorMapId = ColorMapId.VIRIDIS) -> ColorScale:
    return ColorScale(
        id="scale:main",
        colormap=ColorMapRef(colormap_id),
        normalize=LinearNormalize(vmin=0.0, vmax=1.0),
    )


def test_render_text_visual_uses_data_transform_for_data_coordinates():
    """DATA text positions use Matplotlib data coordinates directly."""
    from gsp.protocol import CoordinateSpace

    fig, ax = plt.subplots()
    try:
        visual = TextVisual(
            "visual:data-text",
            ("data",),
            np.array([[2.0, 3.0]], dtype=np.float32),
            CoordinateSpace.DATA,
        )

        (artist,) = render_text_visual(ax, visual)

        assert artist.get_transform() is ax.transData
        assert artist.get_position() == (2.0, 3.0)
    finally:
        plt.close(fig)


def test_protocol_visual_validation_rejects_shape_mismatch():
    """Formal visual models reject mismatched first-slice attributes."""
    positions = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    colors = np.array([[255, 255, 255, 255]], dtype=np.uint8)

    try:
        PointVisual(
            "visual:bad", positions, colors, np.array([1.0, 2.0], dtype=np.float32)
        )
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
    np.testing.assert_allclose(
        visual.angle_values(), np.array([0.0, 0.5], dtype=np.float32)
    )

    with pytest.raises(ValueError, match="shape length"):
        MarkerVisual("visual:bad-shape", positions, (MarkerShape.DISC,), colors, 4.0)

    with pytest.raises(ValueError, match="angle length"):
        MarkerVisual(
            "visual:bad-angle",
            positions,
            MarkerShape.DISC,
            colors,
            4.0,
            angle=np.array([0.0], dtype=np.float32),
        )

    with pytest.raises(ValueError, match="stroke_color"):
        MarkerVisual(
            "visual:bad-stroke-color",
            positions,
            MarkerShape.DISC,
            colors,
            4.0,
            stroke_color=np.zeros((1, 4), dtype=np.uint8),
        )

    with pytest.raises(ValueError, match="stroke_width must be non-negative"):
        MarkerVisual(
            "visual:bad-stroke-width",
            positions,
            MarkerShape.DISC,
            colors,
            4.0,
            stroke_width=-1.0,
        )


def test_segment_visual_validation_covers_positions_widths_and_colors():
    """SegmentVisual validates independent line segment attributes."""
    starts = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    ends = np.array([[0.5, 0.0], [1.5, 1.0]], dtype=np.float32)
    colors = np.array([[255, 255, 255, 255], [0, 0, 0, 255]], dtype=np.uint8)

    visual = SegmentVisual(
        "visual:segments",
        starts,
        ends,
        colors,
        np.array([2.0, 4.0], dtype=np.float32),
        cap=StrokeCap.SQUARE,
    )

    np.testing.assert_allclose(
        visual.width_values(), np.array([2.0, 4.0], dtype=np.float32)
    )

    with pytest.raises(ValueError, match="end_positions length"):
        SegmentVisual("visual:bad-end-count", starts, ends[:1], colors, 2.0)

    with pytest.raises(ValueError, match="colors"):
        SegmentVisual("visual:bad-colors", starts, ends, colors[:1], 2.0)

    with pytest.raises(ValueError, match="widths must be non-negative"):
        SegmentVisual("visual:bad-width", starts, ends, colors, -1.0)


def test_path_visual_validation_covers_path_lengths_widths_and_colors():
    """PathVisual validates open subpath partitioning and per-path attributes."""
    positions = np.array(
        [[0.0, 0.0], [0.5, 0.5], [1.0, 0.0], [1.5, 0.5]], dtype=np.float32
    )
    colors = np.array([[255, 255, 255, 255], [0, 0, 0, 255]], dtype=np.uint8)

    visual = PathVisual(
        "visual:paths",
        positions,
        (2, 2),
        colors,
        np.array([2.0, 4.0], dtype=np.float32),
        join=StrokeJoin.ROUND,
    )

    np.testing.assert_allclose(
        visual.width_values(), np.array([2.0, 4.0], dtype=np.float32)
    )

    with pytest.raises(ValueError, match="path_lengths sum"):
        PathVisual("visual:bad-length-sum", positions, (3,), colors[:1], 2.0)

    with pytest.raises(ValueError, match="at least 2"):
        PathVisual("visual:bad-short-subpath", positions, (1, 3), colors, 2.0)

    with pytest.raises(ValueError, match="colors"):
        PathVisual("visual:bad-colors", positions, (2, 2), colors[:1], 2.0)

    with pytest.raises(ValueError, match="miter_limit must be non-negative"):
        PathVisual("visual:bad-miter", positions, (2, 2), colors, 2.0, miter_limit=-1.0)


def test_text_visual_validation_and_value_expansion():
    """TextVisual validates S024 scalar/per-item protocol attributes."""
    from gsp.protocol import CoordinateSpace

    positions = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)
    rgba = np.array([1.0, 0.5, 0.0, 1.0], dtype=np.float32)

    visual = TextVisual(
        "visual:text",
        ("hello", "multi\nline"),
        positions,
        CoordinateSpace.NDC,
        rgba=rgba,
        font_size_px=np.array([12.0, 18.0], dtype=np.float32),
        font_role=FontRole.MONOSPACE,
        anchor_x=(TextAnchorX.LEFT, TextAnchorX.RIGHT),
        anchor_y=TextAnchorY.CENTER,
        rotation_rad=np.array([0.0, 0.5], dtype=np.float32),
        z_order=2,
    )

    np.testing.assert_allclose(
        visual.rgba_values(),
        np.array([[1.0, 0.5, 0.0, 1.0], [1.0, 0.5, 0.0, 1.0]], dtype=np.float32),
    )
    np.testing.assert_allclose(
        visual.font_size_values(), np.array([12.0, 18.0], dtype=np.float32)
    )
    assert visual.anchor_x_values() == (TextAnchorX.LEFT, TextAnchorX.RIGHT)
    assert visual.anchor_y_values() == (TextAnchorY.CENTER, TextAnchorY.CENTER)
    np.testing.assert_allclose(
        visual.rotation_values(), np.array([0.0, 0.5], dtype=np.float32)
    )


def test_text_visual_validation_rejects_invalid_inputs():
    """TextVisual rejects fields outside the accepted S024 baseline."""
    from gsp.protocol import CoordinateSpace

    positions = np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)

    with pytest.raises(ValueError, match="positions length"):
        TextVisual("visual:bad-positions", ("one",), positions, CoordinateSpace.NDC)

    with pytest.raises(ValueError, match="control characters"):
        TextVisual(
            "visual:bad-text", ("bad\ttext",), positions[:1], CoordinateSpace.NDC
        )

    with pytest.raises(ValueError, match="rgba"):
        TextVisual(
            "visual:bad-rgba",
            ("one", "two"),
            positions,
            CoordinateSpace.NDC,
            rgba=np.zeros((1, 4), dtype=np.uint8),
        )

    with pytest.raises(ValueError, match="font_size_px must be positive"):
        TextVisual(
            "visual:bad-size",
            ("one",),
            positions[:1],
            CoordinateSpace.NDC,
            font_size_px=0.0,
        )

    with pytest.raises(ValueError, match="anchor_x length"):
        TextVisual(
            "visual:bad-anchor",
            ("one", "two"),
            positions,
            CoordinateSpace.NDC,
            anchor_x=(TextAnchorX.LEFT,),
        )

    with pytest.raises(ValueError, match="rotation_rad must be finite"):
        TextVisual(
            "visual:bad-rotation",
            ("one",),
            positions[:1],
            CoordinateSpace.NDC,
            rotation_rad=np.nan,
        )

    with pytest.raises(TypeError, match="font_role"):
        TextVisual(
            "visual:bad-font-role",
            ("one",),
            positions[:1],
            CoordinateSpace.NDC,
            font_role="monospace",
        )

    with pytest.raises(TypeError, match="z_order"):
        TextVisual(
            "visual:bad-z",
            ("one",),
            positions[:1],
            CoordinateSpace.NDC,
            z_order=1.5,
        )


def test_protocol_visual_validation_rejects_non_finite_point_fields():
    """Formal point visuals reject NaN/Inf protocol values."""
    colors = np.array([[255, 255, 255, 255]], dtype=np.uint8)
    finite_positions = np.array([[0.0, 0.0]], dtype=np.float32)

    with pytest.raises(ValueError, match="positions must be finite"):
        PointVisual(
            "visual:bad-positions",
            np.array([[np.nan, 0.0]], dtype=np.float32),
            colors,
            1.0,
        )

    with pytest.raises(ValueError, match="sizes must be finite"):
        PointVisual(
            "visual:bad-sizes",
            finite_positions,
            colors,
            np.array([np.inf], dtype=np.float32),
        )

    with pytest.raises(ValueError, match="floating point colors must be finite"):
        PointVisual(
            "visual:bad-colors",
            finite_positions,
            np.array([[0.0, np.nan, 0.0, 1.0]], dtype=np.float32),
            1.0,
        )


def test_image_visual_validation_covers_scalar_colormap_and_clim_rules():
    """ImageVisual validates v1 scalar/RGB/RGBA image constraints."""
    scalar = np.array([[0.0, 2.0], [np.nan, 4.0]], dtype=np.float32)
    rgb = np.zeros((2, 2, 3), dtype=np.float32)

    with pytest.raises(ValueError, match="finite"):
        ImageVisual("visual:bad-scalar", scalar, (-1.0, 1.0, -1.0, 1.0))

    with pytest.raises(ValueError, match="RGB/RGBA"):
        ImageVisual("visual:bad-rgb-range", rgb + 2.0, (-1.0, 1.0, -1.0, 1.0))

    with pytest.raises(ValueError, match="scalar images only"):
        ImageVisual(
            "visual:bad-colormap",
            np.zeros((2, 2, 4), dtype=np.uint8),
            (-1.0, 1.0, -1.0, 1.0),
            colormap=ImageColormap.GRAY,
        )

    with pytest.raises(ValueError, match="clim minimum"):
        ImageVisual(
            "visual:bad-clim",
            rgb[..., 0],
            (-1.0, 1.0, -1.0, 1.0),
            clim=(1.0, 1.0),
        )
