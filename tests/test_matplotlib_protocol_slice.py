"""Conformance tests for the Matplotlib protocol point/image slice."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pytest

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisSide,
    Camera3D,
    CanvasSize,
    ColorMapId,
    ColorMapRef,
    ColorScale,
    ColorbarGuide,
    ColorbarGuideStyle,
    CoordinateSpace,
    DepthMode,
    DirectionalLight3D,
    FontRole,
    ImageColormap,
    ImageOrigin,
    ImageVisual,
    LogicalPixelRect,
    MeshColorMode,
    MeshNormalGeneration,
    MeshNormalMode,
    MeshShading,
    MeshUVMode,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    LinearNormalize,
    OrthographicProjection3D,
    PanByAction,
    PanelTextGuide,
    PanelTextRole,
    PathVisual,
    PerspectiveProjection3D,
    PointVisual,
    QueryCoordinateSpace,
    QueryRequest,
    QueryScope,
    QueryStatus,
    ScalarColorEncoding,
    ScalarColorSlot,
    SegmentVisual,
    StrokeCap,
    StrokeJoin,
    TextAnchorX,
    TextAnchorY,
    TextVisual,
    View2D,
    View3D,
    View3DDiagnosticCode,
    View2DNavigationController,
    VisualTransformBinding,
)
from gsp_matplotlib.color_mapping import map_scalar_values
from gsp_matplotlib.layout_query import query_resolved_layout_guides
from gsp_matplotlib.navigation import apply_view2d_navigation_action
from gsp_matplotlib.protocol_query import QueryVisualEntry, query_visuals
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
    render_protocol_scene_with_layout,
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


def test_render_protocol_scene_with_layout_reports_snapshot_id():
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(-1.0, 1.0),
        y_range=(-1.0, 1.0),
    )
    point = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([16.0], dtype=np.float32),
    )
    axis_guides = (
        AxisGuide(
            id="guide:x",
            view_id=view.id,
            dimension=AxisDimension.X,
            side=AxisSide.BOTTOM,
            label_text="x",
        ),
        AxisGuide(
            id="guide:y",
            view_id=view.id,
            dimension=AxisDimension.Y,
            side=AxisSide.LEFT,
            label_text="y",
        ),
    )
    title = PanelTextGuide(
        id="guide:title",
        panel_id=view.panel_id,
        role=PanelTextRole.TITLE,
        text="Scene layout",
    )

    result = render_protocol_scene_with_layout(
        visuals=(point,),
        view=view,
        axis_guides=axis_guides,
        panel_text_guides=(title,),
        snapshot_id="layout:scene",
        device_scale=2.0,
    )
    try:
        assert result.layout_snapshot_id == "layout:scene"
        assert result.layout_snapshot.render_target.device_scale == 2.0
        assert result.layout_snapshot.view_id == view.id
        assert result.layout_snapshot.plot_rect_px.width > 0.0
        assert result.layout_snapshot.title_boxes[0].guide_id == title.id

        title_rect = result.layout_snapshot.title_boxes[0].rect_px
        query = query_resolved_layout_guides(
            QueryRequest(
                id="query:title",
                panel_id=view.panel_id,
                coordinate=(
                    title_rect.x + title_rect.width / 2.0,
                    title_rect.y + title_rect.height / 2.0,
                ),
                coordinate_space=QueryCoordinateSpace.PANEL,
                scope=QueryScope.GUIDES,
                layout_snapshot_id=result.layout_snapshot_id,
            ),
            result.layout_snapshot,
        )
        assert query.status == QueryStatus.HIT
        assert query.layout_snapshot_id == result.layout_snapshot_id
    finally:
        plt.close(result.figure)


def test_render_protocol_scene_with_layout_accepts_view3d_mesh():
    view3d = View3D(
        id="view:main",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 1.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-1.0, 1.0),
            ylim=(-1.0, 1.0),
            near_far=(0.0, 2.0),
        ),
    )
    mesh = MeshVisual(
        id="visual:mesh",
        positions=np.array(
            [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 0, 0, 255], dtype=np.uint8),
    )

    result = render_protocol_scene_with_layout(visuals=(mesh,), view3d=view3d)

    try:
        assert len(result.axes.collections) == 1
        artist = result.axes.collections[0]
        np.testing.assert_allclose(
            artist.get_paths()[0].vertices[:3],
            np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]),
        )
    finally:
        plt.close(result.figure)


def test_render_protocol_scene_with_reference_canvas_resolves_matplotlib_size():
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(-1.0, 1.0),
        y_range=(-1.0, 1.0),
    )
    point = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
        sizes=np.array([20.0], dtype=np.float32),
    )

    result = render_protocol_scene_with_layout(
        visuals=(point,),
        view=view,
        canvas_size=CanvasSize.reference_px(960, 540, reference_dpi=96),
        output_dpi=144,
    )
    try:
        assert result.resolved_canvas.canvas_width_px == 960.0
        assert result.resolved_canvas.framebuffer_width == 1440
        assert result.resolved_canvas.framebuffer_height == 810
        assert result.resolved_canvas.framebuffer_per_canvas_px == 1.5
        np.testing.assert_allclose(
            result.figure.get_size_inches(), np.array([10.0, 5.625])
        )
        collection = result.axes.collections[0]
        np.testing.assert_allclose(
            collection.get_sizes(), np.array([225.0], dtype=np.float32)
        )
    finally:
        plt.close(result.figure)


def test_programmatic_navigation_render_and_query_share_view_snapshot():
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(0.0, 10.0),
        y_range=(0.0, 10.0),
    )
    controller = View2DNavigationController(
        id="nav:main",
        panel_id=view.panel_id,
        view_id=view.id,
        current_view2d_revision="view-rev:1",
        home_view=view,
    )
    panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=1000.0, height=1000.0)
    action = PanByAction(
        controller_id=controller.id,
        view2d_revision=controller.current_view2d_revision,
        dx_px=100.0,
        dy_px=0.0,
        layout_snapshot_id="layout:nav",
    )
    point = PointVisual(
        id="visual:points",
        positions=np.array([[5.0, 5.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([16.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )

    navigation = apply_view2d_navigation_action(
        controller,
        view,
        panel_rect,
        action,
        next_view2d_revision="view-rev:2",
        view_snapshot_id="view-snapshot:2",
        expected_layout_snapshot_id="layout:nav",
    )

    assert navigation.accepted
    assert navigation.view is not None
    assert navigation.view.x_range == pytest.approx((-1.0, 9.0))

    render = render_protocol_scene_with_layout(
        visuals=(point,),
        view=navigation.view,
        snapshot_id="layout:nav",
        view_snapshot_id=navigation.view_snapshot_id,
    )
    try:
        assert render.layout_snapshot_id == navigation.layout_snapshot_id
        assert render.view_snapshot_id == navigation.view_snapshot_id
        assert render.layout_snapshot.view_id == navigation.view.id
        assert render.axes.get_xlim() == pytest.approx(navigation.view.x_range)

        query = query_visuals(
            QueryRequest(
                id="query:nav-point",
                panel_id=view.panel_id,
                coordinate=(5.0, 5.0),
                layout_snapshot_id=render.layout_snapshot_id,
                view_snapshot_id=render.view_snapshot_id,
            ),
            [QueryVisualEntry(point)],
            view=navigation.view,
        )

        assert query.status == QueryStatus.HIT
        assert query.visual_id == point.id
        assert query.layout_snapshot_id == render.layout_snapshot_id
        assert query.view_snapshot_id == render.view_snapshot_id
    finally:
        plt.close(render.figure)


def test_programmatic_navigation_rejects_stale_view_revision():
    view = View2D(id="view:main", panel_id="panel:main")
    controller = View2DNavigationController(
        id="nav:main",
        panel_id=view.panel_id,
        view_id=view.id,
        current_view2d_revision="view-rev:2",
    )

    result = apply_view2d_navigation_action(
        controller,
        view,
        LogicalPixelRect(x=0.0, y=0.0, width=100.0, height=100.0),
        PanByAction(
            controller_id=controller.id,
            view2d_revision="view-rev:1",
            dx_px=1.0,
            dy_px=0.0,
        ),
        next_view2d_revision="view-rev:3",
    )

    assert not result.accepted
    assert "GSP_NAVIGATION_STALE_VIEW" in result.diagnostics[0]


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


def test_render_point_visual_uses_logical_dpi_when_backend_device_scales():
    """GUI backends may raise physical DPI while retaining the caller's logical DPI."""
    fig, ax = plt.subplots(dpi=200)
    try:
        setattr(fig, "_original_dpi", 100.0)
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
            sizes=np.array([20.0], dtype=np.float32),
        )

        artist = render_point_visual(ax, visual)

        np.testing.assert_allclose(
            artist.get_sizes(), np.array([207.36], dtype=np.float32)
        )
    finally:
        plt.close(fig)


def test_render_point_visual_applies_inline_transform_and_view2d_mapping():
    """S027 DATA positions transform, then map through View2D to panel/axes coordinates."""
    fig, ax = plt.subplots()
    try:
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[1.0, 2.0]], dtype=np.float32),
            colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
            sizes=np.array([10.0], dtype=np.float32),
            coordinate_space=CoordinateSpace.DATA,
            transform=VisualTransformBinding.inline_affine(
                np.array([[1.0, 0.0, 1.0], [0.0, 1.0, -1.0], [0.0, 0.0, 1.0]])
            ),
        )
        view = View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(0.0, 4.0),
            y_range=(0.0, 2.0),
        )

        artist = render_point_visual(ax, visual, view=view)

        np.testing.assert_allclose(artist.get_offsets(), np.array([[0.5, 0.5]]))
        assert artist.get_offset_transform() == ax.transAxes
    finally:
        plt.close(fig)


def test_render_point_visual_handles_reversed_view2d_limits():
    """Reversed View2D limits are valid and reverse the panel mapping."""
    fig, ax = plt.subplots()
    try:
        visual = PointVisual(
            id="visual:points",
            positions=np.array([[1.0, 0.0]], dtype=np.float32),
            colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
            sizes=np.array([10.0], dtype=np.float32),
            coordinate_space=CoordinateSpace.DATA,
        )
        view = View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(2.0, 0.0),
            y_range=(-1.0, 1.0),
        )

        artist = render_point_visual(ax, visual, view=view)

        np.testing.assert_allclose(artist.get_offsets(), np.array([[0.5, 0.5]]))
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
            style=ColorbarGuideStyle(ramp_width_px=40.0),
        )

        colorbar = render_colorbar_guide(ax, guide, color_scales={scale.id: scale})

        assert colorbar.ax.get_gid() == "guide:colorbar"
        assert colorbar.ax.get_ylabel() == "Intensity"
        np.testing.assert_allclose(colorbar.ax.get_position().width, 40.0 / 640.0)
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


def test_render_path_visual_applies_inline_transform_to_vertices():
    """Path vertices are transformed while stroke width remains screen-pixel based."""
    fig, ax = plt.subplots()
    try:
        visual = PathVisual(
            id="visual:path",
            positions=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32),
            path_lengths=(2,),
            colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
            widths=2.0,
            coordinate_space=CoordinateSpace.DATA,
            transform=VisualTransformBinding.inline_affine(
                np.array([[2.0, 0.0, 1.0], [0.0, 2.0, -1.0], [0.0, 0.0, 1.0]])
            ),
        )

        (artist,) = render_path_visual(ax, visual)

        np.testing.assert_allclose(
            artist.get_path().vertices, np.array([[1.0, -1.0], [3.0, -1.0]])
        )
        np.testing.assert_allclose(artist.get_linewidth(), 1.44)
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


def test_render_mesh_visual_rejects_texture2d_unlit_without_dropping_texture_fields():
    """Matplotlib must not approximate S050 Texture2D meshes as flat colors."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:textured-mesh",
            positions=np.array(
                [[-0.5, -0.5], [0.5, -0.5], [0.0, 0.5]], dtype=np.float32
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            shading=MeshShading.TEXTURE2D_UNLIT,
            texture2d_id="texture:checker",
            uv_mode=MeshUVMode.VERTEX,
            uvs=np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0]], dtype=np.float32),
        )

        with pytest.raises(
            NotImplementedError,
            match="meshvisual_material_texture2d_unlit_unsupported",
        ):
            render_mesh_visual(ax, visual)
        assert not ax.collections
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


def test_render_mesh_visual_applies_view2d_mapping():
    """Mesh vertices map through View2D when rendered in DATA coordinates."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 2.0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )
        view = View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(0.0, 4.0),
            y_range=(0.0, 4.0),
        )

        artist = render_mesh_visual(ax, visual, view=view)

        np.testing.assert_allclose(
            artist.get_paths()[0].vertices[:3],
            np.array([[0.0, 0.0], [0.5, 0.0], [0.0, 0.5]]),
        )
        assert artist.get_transform() == ax.transAxes
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_data_requires_view3d():
    """DATA MeshVisual positions3d require an explicit View3D."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
        )

        with pytest.raises(
            NotImplementedError,
            match=View3DDiagnosticCode.MESH3D_REQUIRES_VIEW3D.value,
        ):
            render_mesh_visual(ax, visual)
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_data_projects_through_view3d():
    """DATA MeshVisual positions3d project through the S036 orthographic View3D."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [0.0, 2.0, 0.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )
        view3d = View3D(
            id="view:main",
            panel_id="panel:main",
            camera=Camera3D(
                eye=(0.0, 0.0, 1.0),
                target=(0.0, 0.0, 0.0),
                up=(0.0, 1.0, 0.0),
            ),
            projection=OrthographicProjection3D(
                xlim=(0.0, 4.0),
                ylim=(0.0, 4.0),
                near_far=(0.0, 2.0),
            ),
        )

        artist = render_mesh_visual(ax, visual, view3d=view3d)

        np.testing.assert_allclose(
            artist.get_paths()[0].vertices[:3],
            np.array([[0.0, 0.0], [0.5, 0.0], [0.0, 0.5]]),
        )
        assert artist.get_transform() == ax.transAxes
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_data_projects_through_perspective_view3d():
    """DATA MeshVisual positions3d project through an S047 perspective View3D."""
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.set_position([0.0, 0.0, 1.0, 1.0])
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[0.0, 0.0, -1.0], [1.0, 0.0, -1.0], [0.0, 1.0, -1.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )
        view3d = View3D(
            id="view:main",
            panel_id="panel:main",
            camera=Camera3D(
                eye=(0.0, 0.0, 0.0),
                target=(0.0, 0.0, -1.0),
                up=(0.0, 1.0, 0.0),
            ),
            projection=PerspectiveProjection3D(
                fov_y_degrees=90.0,
                near_far=(1.0, 10.0),
            ),
        )

        artist = render_mesh_visual(ax, visual, view3d=view3d)

        np.testing.assert_allclose(
            artist.get_paths()[0].vertices[:3],
            np.array([[0.5, 0.5], [1.0, 0.5], [0.5, 1.0]]),
            rtol=1.0e-6,
            atol=1.0e-6,
        )
        assert artist.get_transform() == ax.transAxes
    finally:
        plt.close(fig)


def test_render_mesh_visual_s039_flat_lambert_explicit_normals():
    """Matplotlib resolves S039 flat Lambert material math before 3D adaptation."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [1.0, 1.0, 0.0],
                    [0.0, 1.0, 0.0],
                ],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array(
                [[255, 128, 0, 255], [255, 128, 0, 255]],
                dtype=np.uint8,
            ),
            color_mode=MeshColorMode.FACE,
            shading=MeshShading.FLAT_LAMBERT,
            normals=np.array([[0.0, 0.0, 2.0], [0.0, 0.0, -1.0]], dtype=np.float32),
            normal_mode=MeshNormalMode.FACE,
            depth_test=DepthMode.DISABLED,
        )
        view3d = View3D(
            id="view:main",
            panel_id="panel:main",
            camera=Camera3D(
                eye=(0.0, 0.0, 2.0),
                target=(0.0, 0.0, 0.0),
                up=(0.0, 1.0, 0.0),
            ),
            projection=OrthographicProjection3D(
                xlim=(-1.0, 2.0),
                ylim=(-1.0, 2.0),
                near_far=(0.0, 4.0),
            ),
            ambient_light_intensity=0.25,
            directional_light=DirectionalLight3D(
                direction_to_light=(0.0, 0.0, 1.0),
                intensity=0.5,
            ),
        )

        artist = render_mesh_visual(ax, visual, view3d=view3d)

        np.testing.assert_allclose(
            artist.get_facecolors(),
            np.array(
                [
                    [0.75, (128 / 255.0) * 0.75, 0.0, 1.0],
                    [0.25, (128 / 255.0) * 0.25, 0.0, 1.0],
                ],
                dtype=np.float32,
            ),
            rtol=1.0e-6,
            atol=1.0e-6,
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_s039_generated_normals_follow_winding():
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 2, 1]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 255], dtype=np.uint8),
            shading=MeshShading.FLAT_LAMBERT,
            normal_mode=MeshNormalMode.FACE,
            normal_generation=MeshNormalGeneration.FACE_FLAT,
        )
        view3d = View3D(
            id="view:main",
            panel_id="panel:main",
            camera=Camera3D(
                eye=(0.0, 0.0, 2.0),
                target=(0.0, 0.0, 0.0),
                up=(0.0, 1.0, 0.0),
            ),
            projection=OrthographicProjection3D(near_far=(0.0, 4.0)),
            ambient_light_intensity=0.2,
            directional_light=DirectionalLight3D(
                direction_to_light=(0.0, 0.0, 1.0),
                intensity=0.8,
            ),
        )

        artist = render_mesh_visual(ax, visual, view3d=view3d)

        np.testing.assert_allclose(
            artist.get_facecolors()[0],
            np.array([0.2, 0.2, 0.2, 1.0], dtype=np.float32),
            rtol=1.0e-6,
            atol=1.0e-6,
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_s039_flat_lambert_alpha_remains_non_strict():
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.DATA,
            color=np.array([255, 255, 255, 128], dtype=np.uint8),
            shading=MeshShading.FLAT_LAMBERT,
            normal_mode=MeshNormalMode.FACE,
            normal_generation=MeshNormalGeneration.FACE_FLAT,
        )
        view3d = View3D(
            id="view:main",
            panel_id="panel:main",
            camera=Camera3D(
                eye=(0.0, 0.0, 2.0),
                target=(0.0, 0.0, 0.0),
                up=(0.0, 1.0, 0.0),
            ),
            projection=OrthographicProjection3D(near_far=(0.0, 4.0)),
            directional_light=DirectionalLight3D(direction_to_light=(0.0, 0.0, 1.0)),
        )

        with pytest.raises(
            NotImplementedError,
            match=View3DDiagnosticCode.MESH3D_ALPHA_NOT_STRICT.value,
        ):
            render_mesh_visual(ax, visual, view3d=view3d)
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_ndc_uses_panel_xy_directly():
    """NDC MeshVisual positions3d use panel NDC x/y directly."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.5], [-1.0, 1.0, 1.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )

        artist = render_mesh_visual(ax, visual)

        np.testing.assert_allclose(
            artist.get_paths()[0].vertices[:3],
            np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]),
        )
        assert artist.get_transform() == ax.transAxes
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_orders_opaque_faces_far_to_near():
    """Opaque 3D MeshVisual faces are ordered so nearer faces are drawn last."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [
                    [-1.0, -1.0, 0.0],
                    [1.0, -1.0, 0.0],
                    [-1.0, 1.0, 0.0],
                    [-1.0, -1.0, 0.8],
                    [1.0, -1.0, 0.8],
                    [-1.0, 1.0, 0.8],
                ],
                dtype=np.float32,
            ),
            faces=np.array([[3, 4, 5], [0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array(
                [[0, 0, 255, 255], [255, 0, 0, 255]],
                dtype=np.uint8,
            ),
        )

        artist = render_mesh_visual(ax, visual)

        np.testing.assert_allclose(
            artist.get_facecolors(),
            np.array([[0.0, 0.0, 1.0, 1.0], [1.0, 0.0, 0.0, 1.0]]),
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_coalesces_coplanar_cube_triangles_for_painter_sort():
    """A triangulated cube draws logical sides atomically in the Matplotlib 3D fallback."""
    fig, ax = plt.subplots()
    try:
        positions = np.array(
            [
                [-1.0, -1.0, -1.0],
                [1.0, -1.0, -1.0],
                [1.0, 1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, -1.0, 1.0],
                [1.0, -1.0, 1.0],
                [1.0, 1.0, 1.0],
                [-1.0, 1.0, 1.0],
            ],
            dtype=np.float32,
        )
        faces = np.array(
            [
                [0, 1, 2],
                [0, 2, 3],
                [4, 6, 5],
                [4, 7, 6],
                [0, 4, 5],
                [0, 5, 1],
                [1, 5, 6],
                [1, 6, 2],
                [2, 6, 7],
                [2, 7, 3],
                [3, 7, 4],
                [3, 4, 0],
            ],
            dtype=np.uint32,
        )
        colors = np.repeat(
            np.array(
                [
                    [69, 123, 157, 255],
                    [42, 157, 143, 255],
                    [230, 57, 70, 255],
                    [244, 162, 97, 255],
                    [38, 70, 83, 255],
                    [131, 197, 190, 255],
                ],
                dtype=np.uint8,
            ),
            2,
            axis=0,
        )
        visual = MeshVisual(
            id="visual:cube",
            positions=positions,
            faces=faces,
            coordinate_space=CoordinateSpace.NDC,
            color=colors,
            color_mode=MeshColorMode.FACE,
        )

        artist = render_mesh_visual(ax, visual)

        assert len(artist.get_paths()) == 6
        assert all(path.vertices.shape == (5, 2) for path in artist.get_paths())
        assert artist.get_facecolors().shape == (6, 4)
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_depth_disabled_preserves_face_order():
    """Disabled depth uses declared face order for 3D MeshVisual rendering."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [
                    [-1.0, -1.0, 0.0],
                    [1.0, -1.0, 0.0],
                    [-1.0, 1.0, 0.0],
                    [-1.0, -1.0, 0.8],
                    [1.0, -1.0, 0.8],
                    [-1.0, 1.0, 0.8],
                ],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array(
                [[255, 0, 0, 255], [0, 0, 255, 255]],
                dtype=np.uint8,
            ),
            depth_test=DepthMode.DISABLED,
        )

        artist = render_mesh_visual(ax, visual)

        np.testing.assert_allclose(
            artist.get_facecolors(),
            np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.0, 1.0, 1.0]]),
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_keeps_reversed_winding_visible_without_culling():
    """FaceCulling.NONE keeps reversed-winding 3D faces visible."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 2, 1]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
        )

        artist = render_mesh_visual(ax, visual)

        assert len(artist.get_paths()) == 1
        np.testing.assert_allclose(
            artist.get_paths()[0].vertices[:3],
            np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0]]),
        )
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_rejects_alpha_for_strict_depth_path():
    """Translucent 3D mesh colors are not strict opaque-depth fixtures."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 128], dtype=np.uint8),
        )

        with pytest.raises(
            NotImplementedError,
            match=View3DDiagnosticCode.MESH3D_ALPHA_NOT_STRICT.value,
        ):
            render_mesh_visual(ax, visual)
    finally:
        plt.close(fig)


def test_render_mesh_visual_3d_rejects_2d_affine_transform():
    """S036 does not apply existing 2D visual transforms to 3D mesh geometry."""
    fig, ax = plt.subplots()
    try:
        visual = MeshVisual(
            id="visual:mesh",
            positions=np.array(
                [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]],
                dtype=np.float32,
            ),
            faces=np.array([[0, 1, 2]], dtype=np.uint32),
            coordinate_space=CoordinateSpace.NDC,
            color=np.array([255, 0, 0, 255], dtype=np.uint8),
            transform=VisualTransformBinding.inline_affine(np.eye(3, dtype=np.float32)),
        )

        with pytest.raises(
            NotImplementedError,
            match=View3DDiagnosticCode.MESH3D_TRANSFORM_UNSUPPORTED.value,
        ):
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
        assert artists[0].get_position() == (0.0, 0.0)
        np.testing.assert_allclose(
            artists[0].get_transform().transform(artists[0].get_position()),
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
