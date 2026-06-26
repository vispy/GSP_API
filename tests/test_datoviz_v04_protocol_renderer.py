"""Tests for the bounded Datoviz v0.4 protocol adapter slice."""

from __future__ import annotations

import ctypes

import numpy as np
import pytest

from gsp.protocol import (
    ImageOrigin,
    ImageVisual,
    MeshColorMode,
    MeshVisual,
    MarkerShape,
    MarkerVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    TextVisual,
    StrokeCap,
    StrokeJoin,
)
from gsp.protocol import (
    AffineTransform2DResource,
    AxisProviderRequest,
    ColorbarGuide,
    ColorMapId,
    ColorMapRef,
    ColorScale,
    LinearNormalize,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryScope,
    QueryStatus,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    ScalarColorEncoding,
    ScalarColorSlot,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    TextAnchorX,
    TextAnchorY,
    TransformPlacement,
    View2D,
    VisualFamily,
    VisualTransformBinding,
)
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.capabilities import (
    DATOVIZ_V04_AXIS_PROVIDER,
    datoviz_v04_axis_provider_capability,
    datoviz_v04_capture_diagnostics,
    datoviz_v04_capture_ready,
    gsp_capability_snapshot_from_datoviz,
)
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    DatovizV04Unavailable,
    DatovizV04Unsupported,
    capability_snapshot,
    datoviz_v04_mesh_diagnostics,
    datoviz_v04_mesh_ready,
    datoviz_v04_sampled_field_diagnostics,
    datoviz_v04_sampled_field_ready,
    datoviz_v04_text_diagnostics,
    datoviz_v04_text_ready,
    is_datoviz_v04_facade,
    _image_texcoords,
)
from gsp_datoviz.query import (
    DVZ_QUERY_STATUS_DECODE_FAILED,
    DVZ_QUERY_STATUS_HIT,
    DVZ_QUERY_STATUS_MISS,
    DVZ_QUERY_STATUS_NO_CAPABLE_VISUAL,
    DVZ_QUERY_STATUS_OUTSIDE_PANEL,
    DVZ_QUERY_STATUS_STALE_DROPPED,
    DVZ_QUERY_VALUE_VEC4,
    DVZ_SCENE_VISUAL_FAMILY_IMAGE,
    DVZ_SCENE_VISUAL_FAMILY_POINT,
    decode_dvz_query_result,
    datoviz_v04_query_binding_diagnostics,
    datoviz_v04_query_binding_ready,
)


class FakeDatovizV04:
    """Small recorder for the dvz_* facade used by the adapter."""

    def __init__(self):
        self.calls = []
        self.destroyed = False

    def dvz_scene(self):
        self.calls.append(("scene",))
        return "scene"

    def dvz_figure(self, scene, width, height, flags):
        self.calls.append(("figure", scene, width, height, flags))
        return "figure"

    def dvz_panel_full(self, figure):
        self.calls.append(("panel_full", figure))
        return "panel"

    class FakeDataDomain:
        min = 0.0
        max = 0.0

    class FakePanelView2D:
        aspect = 0
        padding = 1.0

        def __init__(self):
            self.data_x = FakeDatovizV04.FakeDataDomain()
            self.data_y = FakeDatovizV04.FakeDataDomain()

    def dvz_panel_view2d(self):
        self.calls.append(("panel_view2d",))
        return self.FakePanelView2D()

    def dvz_panel_set_view2d(self, panel, view):
        self.calls.append(("set_view2d", panel, view))
        return 0

    class DvzColor(ctypes.Structure):
        _fields_ = (
            ("r", ctypes.c_uint8),
            ("g", ctypes.c_uint8),
            ("b", ctypes.c_uint8),
            ("a", ctypes.c_uint8),
        )

    def dvz_panel_set_background_color(self, panel, color):
        self.calls.append(
            ("set_background_color", panel, (color.r, color.g, color.b, color.a))
        )
        return None

    def dvz_point(self, scene, flags):
        self.calls.append(("point", scene, flags))
        return "point-visual"

    def dvz_image(self, scene, flags):
        self.calls.append(("image", scene, flags))
        return "image-visual"

    def dvz_marker(self, scene, flags):
        self.calls.append(("marker", scene, flags))
        return "marker-visual"

    def dvz_segment(self, scene, flags):
        self.calls.append(("segment", scene, flags))
        return "segment-visual"

    def dvz_path(self, scene, flags):
        self.calls.append(("path", scene, flags))
        return "path-visual"

    class DvzSegmentCap:
        DVZ_SEGMENT_CAP_ROUND = 1
        DVZ_SEGMENT_CAP_SQUARE = 4
        DVZ_SEGMENT_CAP_BUTT = 5

    def dvz_segment_set_caps(self, visual, start_cap, end_cap):
        self.calls.append(("segment_set_caps", visual, start_cap, end_cap))
        return 0

    class DvzPathJoin:
        DVZ_PATH_JOIN_MITER = 0
        DVZ_PATH_JOIN_ROUND = 1
        DVZ_PATH_JOIN_BEVEL = 2

    def dvz_path_set_subpaths(self, visual, count, subpaths):
        self.calls.append(
            ("path_set_subpaths", visual, count, np.array(subpaths, copy=True))
        )
        return 0

    def dvz_path_set_caps(self, visual, start_cap, end_cap):
        self.calls.append(("path_set_caps", visual, start_cap, end_cap))
        return 0

    def dvz_path_set_join(self, visual, join, miter_limit):
        self.calls.append(("path_set_join", visual, join, miter_limit))
        return 0

    def dvz_visual_set_data(self, visual, name, data):
        self.calls.append(("set_data", visual, name, np.array(data, copy=True)))
        return 0

    def dvz_visual_set_texture(self, visual, pixels, width, height):
        self.calls.append(
            ("set_texture", visual, np.array(pixels, copy=True), width, height)
        )
        return 0

    def dvz_visual_set_alpha_mode(self, visual, mode):
        self.calls.append(("set_alpha_mode", visual, mode))
        return 0

    def dvz_panel_add_visual(self, panel, visual, attach_desc):
        self.calls.append(("add_visual", panel, visual, attach_desc))
        return 0

    class FakePointStyle:
        stroke_width = 1.0
        aspect = 2

    def dvz_point_style_desc(self):
        self.calls.append(("point_style_desc",))
        return self.FakePointStyle()

    def dvz_point_set_style(self, visual, style):
        self.calls.append(("point_set_style", visual, style))
        return 0

    class FakeMarkerStyle:
        stroke_width_px = 0.0
        aspect = 0

        def __init__(self):
            self.edge_color = [0, 0, 0, 255]

    def dvz_marker_style(self):
        self.calls.append(("marker_style",))
        return self.FakeMarkerStyle()

    def dvz_marker_set_style(self, visual, style):
        self.calls.append(("marker_set_style", visual, style))
        return 0

    class DvzVisualAttachDesc(ctypes.Structure):
        _fields_ = (
            ("struct_size", ctypes.c_uint),
            ("flags", ctypes.c_uint),
            ("z_layer", ctypes.c_int),
            ("controller_mode", ctypes.c_int),
            ("coord_space", ctypes.c_int),
        )

    def dvz_scene_destroy(self, scene):
        self.calls.append(("destroy", scene))
        self.destroyed = True


class FakeDatovizV04WithColorPipeline(FakeDatovizV04):
    DVZ_COLOR_PIPELINE_LINEAR_SRGB = 10
    DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND = 11

    def dvz_figure_set_color_pipeline(self, figure, pipeline):
        self.calls.append(("figure_set_color_pipeline", figure, pipeline))
        return None


class FakeDatovizV04WithAxes(FakeDatovizV04):
    """Recorder exposing the verified v0.4-dev native axis symbols."""

    DVZ_DIM_X = 0
    DVZ_DIM_Y = 1

    def dvz_panel_set_domain(self, panel, dim, minimum, maximum):
        self.calls.append(("set_domain", panel, dim, minimum, maximum))
        return 0

    def dvz_panel_view2d(self):
        self.calls.append(("view2d",))
        return "view2d"

    def dvz_panel_set_view2d(self, panel, view):
        self.calls.append(("set_view2d", panel, view))
        return 0

    def dvz_panel_axis(self, panel, dim):
        self.calls.append(("panel_axis", panel, dim))
        return f"axis:{dim}"

    def dvz_axis_tick_policy(self):
        self.calls.append(("tick_policy",))
        return "tick-policy"

    def dvz_axis_set_tick_policy(self, axis, policy):
        self.calls.append(("set_tick_policy", axis, policy))
        return True

    def dvz_axis_set_grid(self, axis, visible):
        self.calls.append(("set_grid", axis, visible))
        return True

    def dvz_axis_set_label(self, axis, label):
        self.calls.append(("set_label", axis, label))
        return True


class FakeDvzCapabilitySnapshot:
    struct_size = 128
    flags = 0
    max_buffer_size = 512 * 1024 * 1024
    max_texture_dimension_2d = 8192
    max_bind_groups = 8
    max_vertex_buffers = 16
    max_color_attachments = 4
    max_color_sample_count = 8
    max_depth_sample_count = 8
    shader_format_wgsl = True
    shader_format_glsl = False
    render_target_format_rgba16float = True
    render_target_format_r16float = False
    supports_render_target_sampling = True
    supports_color_blending = True
    supports_readback = True
    min_texture_copy_bytes_per_row_alignment = 256
    max_readback_size = 64 * 1024 * 1024
    texture_format_r32uint = True
    texture_format_rg32uint = True
    render_target_format_r32uint = True
    render_target_format_rg32uint = False
    query_profile_u32_r32 = True
    query_profile_u64_rg32 = False
    query_profile_u64_2xr32 = True


class FakeDatovizV04WithCapabilities(FakeDatovizV04WithAxes):
    def dvz_capability_snapshot(self):
        self.calls.append(("capability_snapshot",))
        return FakeDvzCapabilitySnapshot()


class FakeDvzQueryResultType:
    _fields_ = (("request_id", object), ("status", object), ("hit", object))


class FakeDatovizV04WithQuery(FakeDatovizV04WithCapabilities):
    DvzQueryResult = FakeDvzQueryResultType

    def dvz_query_request(self):
        self.calls.append(("query_request",))
        return "query-request"

    def dvz_panel_query(self, panel, x, y, request):
        self.calls.append(("panel_query", panel, x, y, request))
        return 0

    def dvz_scene_poll_query(self, scene, out_result):
        self.calls.append(("scene_poll_query", scene, out_result))
        return False


class FakeSampledFieldDesc:
    dim = None
    format = None
    semantic = None
    color_role = None
    width = None
    height = None
    depth = None


class FakeFieldDataView:
    data = None
    bytes_per_row = 0
    rows_per_image = 0


class FakeDatovizV04WithSampledFields(FakeDatovizV04):
    def dvz_sampled_field_desc(self):
        self.calls.append(("sampled_field_desc",))
        return FakeSampledFieldDesc()

    def dvz_field_data_view(self):
        self.calls.append(("field_data_view",))
        return FakeFieldDataView()

    def dvz_sampled_field(self, scene, desc):
        self.calls.append(("sampled_field", scene, desc))
        return "sampled-field"

    def dvz_sampled_field_set_data(self, sampled_field, view):
        self.calls.append(("sampled_field_set_data", sampled_field, view))
        return True

    def dvz_visual_set_field(self, visual, slot_name, sampled_field):
        self.calls.append(("set_field", visual, slot_name, sampled_field))
        return True


class FakeDatovizV04WithCapture(FakeDatovizV04):
    def __init__(self):
        super().__init__()
        self.app_destroyed = False

    def dvz_app(self, scene):
        self.calls.append(("app", scene))
        return "app"

    def dvz_view_offscreen(self, app, figure, width, height):
        self.calls.append(("view_offscreen", app, figure, width, height))
        return "offscreen-view"

    def dvz_app_render_once(self, app):
        self.calls.append(("render_once", app))
        return 0

    def dvz_view_capture_png(self, view, path):
        self.calls.append(("capture_png", view, path))
        with open(path, "wb") as file:
            file.write(b"\x89PNG\r\n\x1a\nfake")
        return 0

    def dvz_app_destroy(self, app):
        self.calls.append(("app_destroy", app))
        self.app_destroyed = True


class FakeDatovizV04WithInteractive(FakeDatovizV04WithCapture):
    def dvz_view(self, app, figure, desc):
        self.calls.append(("view", app, figure, desc))
        return "live-view"

    def dvz_app_run(self, app, frame_count):
        self.calls.append(("app_run", app, frame_count))
        return None


class FakeDatovizV04WithQueryCapabilities(FakeDatovizV04):
    def dvz_visual_set_query_capabilities(self, visual, capabilities):
        self.calls.append(("set_query_capabilities", visual, capabilities))
        return None


class FakeDatovizV04WithMesh(FakeDatovizV04WithQueryCapabilities):
    def dvz_mesh(self, scene, flags):
        self.calls.append(("mesh", scene, flags))
        return "mesh-visual"

    def dvz_visual_set_index_data(self, visual, indices, index_count):
        self.calls.append(
            ("set_index_data", visual, np.array(indices, copy=True), index_count)
        )
        return 0

    def dvz_visual_set_depth_test(self, visual, enabled):
        self.calls.append(("set_depth_test", visual, enabled))
        return 0


class FakeDatovizV04WithColorbar(FakeDatovizV04):
    class DvzScaleKind:
        DVZ_SCALE_CONTINUOUS = 0

    class DvzBuiltinColormap:
        DVZ_BUILTIN_COLORMAP_VIRIDIS = 1
        DVZ_BUILTIN_COLORMAP_GRAY = 7

    class DvzColorbarOrientation:
        DVZ_COLORBAR_ORIENTATION_VERTICAL = 0
        DVZ_COLORBAR_ORIENTATION_HORIZONTAL = 1

    class DvzColorbarPlacementMode:
        DVZ_COLORBAR_PLACEMENT_ATTACHED = 0

    class DvzSceneAnchor:
        DVZ_SCENE_ANCHOR_PANEL_RIGHT = 6

    class FakeScaleDesc:
        def __init__(self):
            self.kind = None
            self.label = None

    class FakeColorbarDesc:
        def __init__(self):
            self.orientation = None
            self.placement_mode = None
            self.anchor = None
            self.title = None

    def dvz_scale_desc(self):
        self.calls.append(("scale_desc",))
        return self.FakeScaleDesc()

    def dvz_scale(self, scene, desc):
        self.calls.append(("scale", scene, desc.kind, desc.label))
        return "scale"

    def dvz_scale_set_domain(self, scale, vmin, vmax):
        self.calls.append(("scale_set_domain", scale, vmin, vmax))
        return None

    def dvz_scale_set_view_range(self, scale, vmin, vmax):
        self.calls.append(("scale_set_view_range", scale, vmin, vmax))
        return None

    def dvz_colormap_builtin(self, scene, colormap):
        self.calls.append(("colormap_builtin", scene, colormap))
        return "colormap"

    def dvz_scale_set_colormap(self, scale, colormap):
        self.calls.append(("scale_set_colormap", scale, colormap))
        return None

    def dvz_colorbar_desc(self):
        self.calls.append(("colorbar_desc",))
        return self.FakeColorbarDesc()

    def dvz_colorbar(self, panel, scale, desc):
        self.calls.append(
            (
                "colorbar",
                panel,
                scale,
                desc.orientation,
                desc.placement_mode,
                desc.anchor,
                desc.title,
            )
        )
        return "colorbar"

    def dvz_colorbar_set_orientation(self, colorbar, orientation):
        self.calls.append(("colorbar_set_orientation", colorbar, orientation))
        return None

    def dvz_colorbar_set_anchor(self, colorbar, anchor):
        self.calls.append(("colorbar_set_anchor", colorbar, anchor))
        return True

    def dvz_colorbar_set_title(self, colorbar, title):
        self.calls.append(("colorbar_set_title", colorbar, title))
        return None


class FakeDatovizV04WithImageSampling(FakeDatovizV04WithQueryCapabilities):
    class DvzImageSampling:
        DVZ_IMAGE_SAMPLING_LINEAR = 0
        DVZ_IMAGE_SAMPLING_NEAREST = 1

    def dvz_image_set_sampling(self, visual, sampling):
        self.calls.append(("image_set_sampling", visual, sampling))
        return 0


class FakeDatovizV04WithText(FakeDatovizV04WithQueryCapabilities):
    class DvzTextPlacementMode:
        DVZ_TEXT_PLACEMENT_SCREEN = 0
        DVZ_TEXT_PLACEMENT_DATA = 1

    class DvzSceneAnchor:
        DVZ_SCENE_ANCHOR_DATA = 10

    class DvzTextRenderer:
        DVZ_TEXT_RENDERER_MSDF_ATLAS = 3

    class FakeTextStyle:
        def __init__(self):
            self.size_px = 0.0
            self.renderer = 0
            self.color = [0, 0, 0, 0]

    class FakeTextPlacement:
        def __init__(self):
            self.mode = 0
            self.anchor = 0
            self.position = [0.0, 0.0, 0.0]
            self.offset = [0.0, 0.0]
            self.text_anchor = [0.0, 0.0]
            self.has_text_anchor = False
            self.angle = 0.0
            self.depth_test = True

    def __init__(self):
        super().__init__()
        self.text_count = 0

    def dvz_text(self, panel, flags):
        self.text_count += 1
        text = f"text-{self.text_count}"
        self.calls.append(("text", panel, flags, text))
        return text

    def dvz_text_style(self):
        self.calls.append(("text_style",))
        return self.FakeTextStyle()

    def dvz_text_set_style(self, text, style):
        self.calls.append(
            (
                "text_set_style",
                text,
                style.size_px,
                style.renderer,
                tuple(style.color),
            )
        )
        return 0

    def dvz_text_placement(self):
        self.calls.append(("text_placement",))
        return self.FakeTextPlacement()

    def dvz_text_set_placement(self, text, placement):
        self.calls.append(
            (
                "text_set_placement",
                text,
                placement.mode,
                placement.anchor,
                tuple(placement.position),
                tuple(placement.text_anchor),
                placement.has_text_anchor,
                placement.angle,
                placement.depth_test,
            )
        )
        return None

    def dvz_text_set_string(self, text, value):
        self.calls.append(("text_set_string", text, value))
        return None


class FakeDatovizV04WithSampledFieldsAndImageSampling(
    FakeDatovizV04WithSampledFields, FakeDatovizV04WithImageSampling
):
    pass


class FakeDvzQueryResult:
    _fields_ = (("request_id", object), ("status", object), ("hit", object))

    def __init__(self, **kwargs):
        self.request_id = 7
        self.status = DVZ_QUERY_STATUS_MISS
        self.hit = False
        self.panel_position = (0.25, 0.75)
        self.framebuffer_position = (25, 75)
        self.visual_id = 0
        self.visual_family = 0
        self.item_id = 0
        self.texel_id = 0
        self.has_visual_position = False
        self.visual_position = (0.0, 0.0, 0.0)
        self.has_data_position = False
        self.data_position = (0.0, 0.0, 0.0)
        self.has_display_rgba = False
        self.display_rgba = (0.0, 0.0, 0.0, 0.0)
        self.value_kind = 0
        self.vector = (0.0, 0.0, 0.0, 0.0)
        self.scalar = 0.0
        self.category_id = 0
        self.label = b""
        for name, value in kwargs.items():
            setattr(self, name, value)


class FakeDatovizV04WithRuntimeQuery(FakeDatovizV04WithQuery):
    DvzQueryResult = FakeDvzQueryResult

    def __init__(self, result=None):
        super().__init__()
        self.result = result

    def dvz_query_request(self):
        self.calls.append(("query_request",))
        return type("FakeDvzQueryRequest", (), {})()

    def dvz_scene_poll_query(self, scene, out_result):
        self.calls.append(("scene_poll_query", scene, out_result))
        if self.result is None:
            return False
        for name, value in vars(self.result).items():
            setattr(out_result, name, value)
        return True


class FakeDatovizV04WithLiveRuntimeQuery(FakeDatovizV04WithRuntimeQuery):
    DVZ_CANVAS_FRAME_READY = 0

    def dvz_app(self, scene):
        self.calls.append(("app", scene))
        return "app"

    def dvz_view_offscreen(self, app, figure, width, height):
        self.calls.append(("view_offscreen", app, figure, width, height))
        return "offscreen-view"

    def dvz_view_render_once(self, view):
        self.calls.append(("view_render_once", view))
        return self.DVZ_CANVAS_FRAME_READY

    def dvz_app_destroy(self, app):
        self.calls.append(("app_destroy", app))
        return None


class FakeDatovizV04WithRuntimeQueryAndImageSampling(
    FakeDatovizV04WithRuntimeQuery, FakeDatovizV04WithImageSampling
):
    pass


def _calls(fake, name):
    return [call for call in fake.calls if call[0] == name]


def test_renderer_sets_datoviz_color_pipeline_when_binding_is_available():
    fake = FakeDatovizV04WithColorPipeline()

    DatovizV04ProtocolRenderer(dvz=fake, color_pipeline="legacy_srgb_blend")

    assert _calls(fake, "figure_set_color_pipeline") == [
        ("figure_set_color_pipeline", "figure", 11)
    ]


def test_renderer_defaults_to_linear_color_pipeline_when_binding_is_available():
    fake = FakeDatovizV04WithColorPipeline()

    DatovizV04ProtocolRenderer(dvz=fake)

    assert _calls(fake, "figure_set_color_pipeline") == [
        ("figure_set_color_pipeline", "figure", 10)
    ]


def test_renderer_rejects_legacy_color_pipeline_without_datoviz_binding():
    with pytest.raises(
        DatovizV04Unavailable, match="legacy sRGB blend mode is unavailable"
    ):
        DatovizV04ProtocolRenderer(
            dvz=FakeDatovizV04(), color_pipeline="legacy_srgb_blend"
        )


def test_capability_snapshot_defers_query_support():
    caps = gsp_capability_snapshot_from_datoviz(
        None, dvz=None, source="static-gsp-slice"
    )

    assert caps.server_name == "datoviz-v0.4-protocol-slice"
    assert caps.visual_families == ("point", "image")
    assert caps.texture_formats == ("rgba8",)
    assert caps.query_modes == ()
    assert caps.transform_placements == ("cpu-adapter", "unsupported")
    assert caps.supports_transform_placement(TransformPlacement.CPU_ADAPTER)
    assert caps.supports_transform_capability("gsp.transform.affine2d@0.1")
    assert "s027_transform" in caps.metadata
    assert "s028_guide_view2d" in caps.metadata
    assert "axis_guide_query_unsupported" in caps.metadata["s028_guide_view2d_diagnostics"]
    assert caps.metadata["datoviz_api"] == "v0.4 dvz_* facade"
    assert caps.axis_providers[0].provider_id == DATOVIZ_V04_AXIS_PROVIDER


def test_datoviz_capability_translation_preserves_raw_fields_without_overclaiming_query_support():
    caps = gsp_capability_snapshot_from_datoviz(
        FakeDvzCapabilitySnapshot(), dvz=FakeDatovizV04WithAxes()
    )

    assert caps.server_name == "datoviz-v0.4-protocol-slice"
    assert caps.max_buffer_bytes == 512 * 1024 * 1024
    assert caps.texture_formats == ("rgba8", "r32uint", "rg32uint")
    assert caps.output_formats == ()
    assert caps.query_modes == ()
    assert caps.query_capabilities == ()
    assert caps.metadata["datoviz_capability_source"] == "dvz_capability_snapshot"
    assert caps.metadata["datoviz_shader_formats"] == ("wgsl",)
    assert caps.metadata["datoviz_query_profiles"] == ("u32_r32", "u64_2xr32")
    assert caps.metadata["datoviz_raw_capabilities"]["max_texture_dimension_2d"] == 8192
    assert caps.axis_providers[0].provider_status == "adapted"


def test_datoviz_capabilities_promote_png_output_only_when_capture_binding_is_ready():
    promoted = DatovizV04ProtocolRenderer(
        dvz=FakeDatovizV04WithCapture()
    ).capabilities()
    unpromoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).capabilities()

    assert datoviz_v04_capture_ready(FakeDatovizV04WithCapture())
    assert promoted.output_formats == ("png",)
    assert (
        promoted.metadata["capture_support"]
        == "offscreen PNG screenshot/export; not scientific readback"
    )
    assert unpromoted.output_formats == ()
    assert "datoviz_capture_diagnostics" in unpromoted.metadata


def test_renderer_capabilities_use_runtime_datoviz_capability_snapshot_when_available():
    fake = FakeDatovizV04WithCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    caps = renderer.capabilities()

    assert _calls(fake, "capability_snapshot") == [("capability_snapshot",)]
    assert caps.max_buffer_bytes == 512 * 1024 * 1024
    assert caps.metadata["datoviz_raw_capabilities"]["supports_readback"] is True


def test_datoviz_query_binding_readiness_requires_queue_poll_and_decodable_result():
    ready = FakeDatovizV04WithQuery()
    incomplete = FakeDatovizV04WithCapabilities()

    assert datoviz_v04_query_binding_ready(ready)
    assert datoviz_v04_query_binding_diagnostics(ready) == ()
    assert "DvzQueryResult" in " ".join(
        datoviz_v04_query_binding_diagnostics(incomplete)
    )


def test_datoviz_capabilities_promote_panel_query_only_when_query_binding_is_ready():
    promoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithQuery()).capabilities()
    unpromoted = DatovizV04ProtocolRenderer(
        dvz=FakeDatovizV04WithCapabilities()
    ).capabilities()

    assert promoted.query_modes == ("panel-query", "point-item", "image-texel")
    assert promoted.supports_query_scope(QueryScope.DATA)
    assert (
        promoted.adapt_query_request(
            QueryRequest(
                id="query:datoviz",
                panel_id="panel:main",
                coordinate=(0.0, 0.0),
                coordinate_space=QueryCoordinateSpace.PANEL,
            )
        ).outcome.value
        == "accept"
    )
    assert "datoviz_query_binding_diagnostics" not in promoted.metadata
    assert unpromoted.query_modes == ()
    assert "datoviz_query_binding_diagnostics" in unpromoted.metadata


def test_decode_datoviz_query_statuses_to_gsp_statuses():
    assert (
        decode_dvz_query_result(FakeDvzQueryResult(status=DVZ_QUERY_STATUS_MISS)).status
        == QueryStatus.MISS
    )
    assert (
        decode_dvz_query_result(
            FakeDvzQueryResult(status=DVZ_QUERY_STATUS_OUTSIDE_PANEL)
        ).status
        == QueryStatus.OUTSIDE_PANEL
    )
    assert (
        decode_dvz_query_result(
            FakeDvzQueryResult(status=DVZ_QUERY_STATUS_NO_CAPABLE_VISUAL)
        ).status
        == QueryStatus.UNSUPPORTED
    )
    assert (
        decode_dvz_query_result(
            FakeDvzQueryResult(status=DVZ_QUERY_STATUS_STALE_DROPPED)
        ).status
        == QueryStatus.DROPPED
    )
    assert (
        decode_dvz_query_result(
            FakeDvzQueryResult(status=DVZ_QUERY_STATUS_DECODE_FAILED)
        ).status
        == QueryStatus.FAILED
    )


def test_decode_datoviz_point_hit_to_gsp_query_result():
    result = decode_dvz_query_result(
        FakeDvzQueryResult(
            request_id=42,
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=123,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_POINT,
            item_id=5,
            has_visual_position=True,
            visual_position=(0.1, 0.2, 0.0),
            has_data_position=True,
            data_position=(1.0, 2.0, 0.0),
        )
    )

    assert result.request_id == "query:datoviz-42"
    assert result.status == QueryStatus.HIT
    assert result.visual_id == "datoviz:visual:123"
    assert result.visual_family == VisualFamily.POINT
    assert result.item_id == 5
    assert result.visual_coordinate == (0.1, 0.2)
    assert result.data_coordinate == (1.0, 2.0)


def test_decode_datoviz_image_hit_to_gsp_query_result():
    result = decode_dvz_query_result(
        FakeDvzQueryResult(
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=456,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_IMAGE,
            texel_id=9,
            has_display_rgba=True,
            display_rgba=(0.25, 0.5, 0.75, 1.0),
            value_kind=DVZ_QUERY_VALUE_VEC4,
            vector=(1.0, 0.5, 0.25, 1.0),
        )
    )

    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.IMAGE
    assert result.texel == (0, 9)
    assert result.displayed_rgba == (0.25, 0.5, 0.75, 1.0)
    assert result.value == (1.0, 0.5, 0.25, 1.0)


def test_decode_datoviz_query_accepts_ctypes_array_fields():
    result = decode_dvz_query_result(
        FakeDvzQueryResult(
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=456,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_IMAGE,
            has_display_rgba=True,
            display_rgba=(ctypes.c_double * 4)(0.25, 0.5, 0.75, 1.0),
            value_kind=DVZ_QUERY_VALUE_VEC4,
            vector=(ctypes.c_double * 4)(1.0, 0.5, 0.25, 1.0),
        )
    )

    assert result.displayed_rgba == (0.25, 0.5, 0.75, 1.0)
    assert result.value == (1.0, 0.5, 0.25, 1.0)


def test_query_panel_queues_polls_and_decodes_datoviz_result():
    fake = FakeDatovizV04WithRuntimeQuery(
        FakeDvzQueryResult(
            request_id=99,
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=123,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_POINT,
            item_id=5,
        )
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    request = QueryRequest(
        id="query:runtime",
        panel_id="panel:main",
        coordinate=(12.0, 34.0),
        coordinate_space=QueryCoordinateSpace.PANEL,
    )

    result = renderer.query_panel(request)

    assert result.request_id == "query:runtime"
    assert result.status == QueryStatus.HIT
    assert result.visual_family == VisualFamily.POINT
    assert result.item_id == 5
    query_request = _calls(fake, "panel_query")[0][4]
    assert query_request.request_id > 0
    assert query_request.target == 2
    assert query_request.hit_policy == 0
    assert query_request.profile == 0
    assert _calls(fake, "panel_query")[0][:4] == ("panel_query", "panel", 12.0, 34.0)
    assert _calls(fake, "scene_poll_query")[0][1] == "scene"


def test_query_panel_returns_dropped_when_bounded_poll_has_no_result():
    fake = FakeDatovizV04WithRuntimeQuery()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    request = QueryRequest(
        id="query:runtime",
        panel_id="panel:main",
        coordinate=(12.0, 34.0),
        coordinate_space=QueryCoordinateSpace.PANEL,
    )

    result = renderer.query_panel(request)

    assert result.status == QueryStatus.DROPPED
    assert (
        result.diagnostic
        == "Datoviz query produced no resolved result during bounded poll"
    )


def test_query_panel_renders_offscreen_frame_before_poll_when_available():
    fake = FakeDatovizV04WithLiveRuntimeQuery(
        FakeDvzQueryResult(
            request_id=99,
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=123,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_POINT,
            item_id=5,
        )
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=64, height=64)

    result = renderer.query_panel(
        QueryRequest(
            id="query:runtime",
            panel_id="panel:main",
            coordinate=(32.0, 32.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
        )
    )

    names = [call[0] for call in fake.calls]
    assert result.status == QueryStatus.HIT
    assert (
        names.index("panel_query")
        < names.index("view_render_once")
        < names.index("scene_poll_query")
    )
    assert _calls(fake, "view_offscreen") == [
        ("view_offscreen", "app", "figure", 64, 64)
    ]


def test_query_panel_rejects_unadvertised_scopes_and_policies():
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithRuntimeQuery())

    guides = renderer.query_panel(
        QueryRequest(
            id="query:guides",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            scope=QueryScope.GUIDES,
        )
    )
    all_hits = renderer.query_panel(
        QueryRequest(
            id="query:all",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            hit_policy=QueryHitPolicy.ALL,
        )
    )
    all_rendered = renderer.query_panel(
        QueryRequest(
            id="query:all-rendered",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            scope=QueryScope.ALL_RENDERED,
        )
    )
    data_coordinates = renderer.query_panel(
        QueryRequest(id="query:data", panel_id="panel:main", coordinate=(0.0, 0.0))
    )

    assert guides.status == QueryStatus.UNSUPPORTED
    assert "axis-guide-query-unsupported" in str(guides.diagnostic)
    assert all_hits.status == QueryStatus.UNSUPPORTED
    assert "frontmost" in str(all_hits.diagnostic)
    assert all_rendered.status == QueryStatus.UNSUPPORTED
    assert "all-rendered-guides-unsupported" in str(all_rendered.diagnostic)
    assert data_coordinates.status == QueryStatus.UNSUPPORTED
    assert "panel coordinates" in str(data_coordinates.diagnostic)

    transform_payload = renderer.query_panel(
        QueryRequest(
            id="query:transform",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            requested_extension_payload_kinds=(TRANSFORM_QUERY_PAYLOAD_KIND,),
        )
    )

    assert transform_payload.status == QueryStatus.UNSUPPORTED
    assert "GSP_QUERY_INVERSE_UNSUPPORTED" in str(transform_payload.diagnostic)


def test_facade_shape_rejects_missing_v04_functions():
    class IncompleteDatoviz:
        pass

    assert is_datoviz_v04_facade(IncompleteDatoviz()) is False

    with pytest.raises(DatovizV04Unavailable, match="missing v0.4 functions"):
        DatovizV04ProtocolRenderer(dvz=IncompleteDatoviz())


def test_datoviz_axis_provider_is_capability_gated():
    unsupported = datoviz_v04_axis_provider_capability(FakeDatovizV04())
    supported = datoviz_v04_axis_provider_capability(FakeDatovizV04WithAxes())

    assert unsupported.provider_status == "unsupported"
    assert supported.provider_status == "adapted"
    assert supported.supports_backend_auto_ticks
    assert not supported.supports_explicit_ticks
    assert not supported.supports_guide_query
    assert "axis-guide-query-unsupported" in " ".join(supported.diagnostics)
    assert "strict-reversed-view2d-unverified" in " ".join(supported.diagnostics)


def test_capability_snapshot_selects_datoviz_axis_provider_when_facade_exposes_symbols():
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithAxes())
    provider = renderer.capabilities().select_axis_provider(
        AxisProviderRequest(policy="prefer_native", tick_authority="backend_resolved")
    )

    assert provider is not None
    assert provider.provider_id == DATOVIZ_V04_AXIS_PROVIDER


def test_add_point_visual_uses_dvz_point_attributes_and_diameter_pixels():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        colors=np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.5]], dtype=np.float32),
        sizes=np.array([2.0, 4.0], dtype=np.float32),
    )

    dvz_visual = renderer.add_point_visual(visual)

    assert dvz_visual == "point-visual"
    style_call = _calls(fake, "point_set_style")[0]
    assert style_call[1] == "point-visual"
    assert style_call[2].stroke_width == 0.0
    assert style_call[2].aspect == 0
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "color", "diameter_px"]
    np.testing.assert_allclose(set_data[0][3], [[-0.5, 0.25, 0.0], [0.5, -0.25, 0.0]])
    np.testing.assert_array_equal(
        set_data[1][3], [[255, 0, 0, 255], [0, 128, 255, 128]]
    )
    np.testing.assert_allclose(set_data[2][3], [2.0, 4.0], rtol=1e-6)
    assert _calls(fake, "set_alpha_mode") == [("set_alpha_mode", "point-visual", 1)]
    assert _calls(fake, "set_query_capabilities") == [
        ("set_query_capabilities", "point-visual", 0x02)
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[:3] == ("add_visual", "panel", "point-visual")
    attach_desc = add_visual_call[3]
    assert isinstance(attach_desc, FakeDatovizV04.DvzVisualAttachDesc)
    assert attach_desc.z_layer == 0
    assert attach_desc.coord_space == 1


def test_add_point_visual_cpu_adapts_inline_affine_transform():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255], [0, 0, 255, 255]], dtype=np.uint8),
        sizes=np.array([2.0, 4.0], dtype=np.float32),
        transform=VisualTransformBinding.inline_affine(
            np.array([[1.0, 0.0, 0.25], [0.0, 1.0, -0.5], [0.0, 0.0, 1.0]])
        ),
    )

    renderer.add_point_visual(visual)

    position_upload = _calls(fake, "set_data")[0]
    assert position_upload[2] == "position"
    np.testing.assert_allclose(
        position_upload[3],
        [[0.25, -0.5, 0.0], [1.25, 0.5, 0.0]],
    )
    assert renderer.transform_adaptations["visual:points"] == (
        "cpu_adapter_affine2d_eager_ndc",
        "query_inverse_unsupported",
    )


def test_add_point_visual_resolves_named_transform_ref_with_resource_map():
    fake = FakeDatovizV04WithQueryCapabilities()
    matrix = np.array(
        [[1.0, 0.0, 0.25], [0.0, 1.0, -0.5], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    renderer = DatovizV04ProtocolRenderer(
        dvz=fake,
        transform_resources={
            "transform:model": AffineTransform2DResource(
                id="transform:model", matrix=matrix
            )
        },
    )
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([2.0], dtype=np.float32),
        transform=VisualTransformBinding.from_ref("transform:model"),
    )

    renderer.add_point_visual(visual)

    position_upload = _calls(fake, "set_data")[0]
    assert position_upload[2] == "position"
    np.testing.assert_allclose(position_upload[3], [[0.25, -0.5, 0.0]])


def test_add_point_visual_rejects_unresolved_named_transform_ref():
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithQueryCapabilities())
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([2.0], dtype=np.float32),
        transform=VisualTransformBinding.from_ref("transform:model"),
    )

    with pytest.raises(DatovizV04Unsupported, match="GSP_TRANSFORM_MISSING_REF"):
        renderer.add_point_visual(visual)


def test_add_point_visual_maps_data_coordinates_through_view2d():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(
        dvz=fake,
        view=View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(10.0, -10.0),
            y_range=(-5.0, 5.0),
        ),
    )
    visual = PointVisual(
        id="visual:data-points",
        positions=np.array([[-8.0, -4.0], [0.0, 0.0], [8.0, 4.0]], dtype=np.float32),
        colors=np.zeros((3, 4), dtype=np.uint8),
        sizes=np.array([2.0, 4.0, 6.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )

    renderer.add_point_visual(visual)

    position_upload = _calls(fake, "set_data")[0]
    np.testing.assert_allclose(
        position_upload[3],
        [[0.8, -0.8, 0.0], [0.0, 0.0, 0.0], [-0.8, 0.8, 0.0]],
        atol=1e-6,
    )


def test_add_point_visual_cpu_premaps_scalar_color_encoding_to_canonical_rgba8():
    fake = FakeDatovizV04WithQueryCapabilities()
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})
    visual = PointVisual(
        id="visual:scalar-points",
        positions=np.array([[-0.5, 0.0], [0.5, 0.0]], dtype=np.float32),
        sizes=np.array([5.0, 7.0], dtype=np.float32),
        color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.COLOR,
            values=np.array([-1.0, 0.5], dtype=np.float32),
            color_scale_id=scale.id,
            alpha=0.5,
        ),
    )

    renderer.add_point_visual(visual)

    color_upload = _calls(fake, "set_data")[1]
    assert color_upload[2] == "color"
    np.testing.assert_array_equal(
        color_upload[3], [[0, 0, 0, 128], [128, 128, 128, 128]]
    )
    assert renderer.scalar_visuals["visual:scalar-points"].visual_id == visual.id
    assert renderer.scalar_visuals["visual:scalar-points"].color_scale == scale


def test_add_marker_visual_uses_dvz_marker_attributes_shape_angle_and_style():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = MarkerVisual(
        id="visual:markers",
        positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        shape=(MarkerShape.DISC, MarkerShape.DIAMOND),
        fill_colors=np.array(
            [[1.0, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.5]], dtype=np.float32
        ),
        sizes=np.array([12.0, 24.0], dtype=np.float32),
        angle=np.array([0.0, 0.5], dtype=np.float32),
        stroke_color=np.array([0, 0, 0, 255], dtype=np.uint8),
        stroke_width=2.0,
    )

    dvz_visual = renderer.add_marker_visual(visual)

    assert dvz_visual == "marker-visual"
    style_call = _calls(fake, "marker_set_style")[0]
    assert style_call[1] == "marker-visual"
    assert style_call[2].stroke_width_px == 2.0
    assert style_call[2].aspect == 2
    assert style_call[2].edge_color == [0, 0, 0, 255]
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == [
        "position",
        "color",
        "diameter_px",
        "angle",
        "shape",
    ]
    np.testing.assert_allclose(set_data[0][3], [[-0.5, 0.25, 0.0], [0.5, -0.25, 0.0]])
    np.testing.assert_array_equal(
        set_data[1][3], [[255, 0, 0, 255], [0, 128, 255, 128]]
    )
    np.testing.assert_allclose(set_data[2][3], [12.0, 24.0], rtol=1e-6)
    np.testing.assert_allclose(set_data[3][3], [0.0, 0.5], rtol=1e-6)
    np.testing.assert_array_equal(set_data[4][3], [0, 3])
    assert _calls(fake, "set_alpha_mode") == [("set_alpha_mode", "marker-visual", 1)]
    assert _calls(fake, "set_query_capabilities") == [
        ("set_query_capabilities", "marker-visual", 0x02)
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[:3] == ("add_visual", "panel", "marker-visual")


def test_add_marker_visual_cpu_premaps_scalar_fill_to_canonical_rgba8():
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})
    visual = MarkerVisual(
        id="visual:scalar-markers",
        positions=np.array([[-0.25, 0.0], [0.25, 0.0]], dtype=np.float32),
        shape=MarkerShape.DISC,
        sizes=np.array([9.0, 11.0], dtype=np.float32),
        fill_color_encoding=ScalarColorEncoding(
            slot=ScalarColorSlot.FILL,
            values=np.array([0.25, 1.5], dtype=np.float32),
            color_scale_id=scale.id,
            alpha=0.5,
        ),
    )

    renderer.add_marker_visual(visual)

    color_upload = [
        call for call in _calls(fake, "set_data") if call[2] == "color"
    ][0]
    np.testing.assert_array_equal(
        color_upload[3], [[64, 64, 64, 128], [255, 255, 255, 128]]
    )
    metadata = renderer.scalar_visuals["visual:scalar-markers"]
    assert metadata.visual_id == visual.id
    assert metadata.visual_family == "marker"
    assert metadata.item_kind == "marker"
    assert metadata.color_slot == ScalarColorSlot.FILL
    assert metadata.color_scale == scale
    assert metadata.alpha == 0.5


def test_add_marker_visual_passes_marker_angles_through_to_datoviz():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = MarkerVisual(
        id="visual:triangles",
        positions=np.array([[-0.5, 0.0], [0.5, 0.0]], dtype=np.float32),
        shape=(MarkerShape.TRIANGLE, MarkerShape.SQUARE),
        fill_colors=np.array([[0, 137, 123, 255], [30, 136, 229, 255]], dtype=np.uint8),
        sizes=np.array([20.0, 20.0], dtype=np.float32),
        angle=np.array([0.25, 0.5], dtype=np.float32),
    )

    renderer.add_marker_visual(visual)

    set_data = _calls(fake, "set_data")
    np.testing.assert_allclose(set_data[3][3], [0.25, 0.5], rtol=1e-6)


def test_add_segment_visual_uses_dvz_segment_attributes_widths_and_caps():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = SegmentVisual(
        id="visual:segments",
        start_positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        end_positions=np.array([[0.0, 0.5], [0.75, 0.25]], dtype=np.float32),
        colors=np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.5]], dtype=np.float32),
        widths=np.array([12.0, 24.0], dtype=np.float32),
        cap=StrokeCap.SQUARE,
    )

    dvz_visual = renderer.add_segment_visual(visual)

    assert dvz_visual == "segment-visual"
    assert _calls(fake, "segment_set_caps") == [
        ("segment_set_caps", "segment-visual", 4, 4)
    ]
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == [
        "position_start",
        "position_end",
        "color",
        "stroke_width_px",
    ]
    np.testing.assert_allclose(set_data[0][3], [[-0.5, 0.25, 0.0], [0.5, -0.25, 0.0]])
    np.testing.assert_allclose(set_data[1][3], [[0.0, 0.5, 0.0], [0.75, 0.25, 0.0]])
    np.testing.assert_array_equal(
        set_data[2][3], [[255, 0, 0, 255], [0, 128, 255, 128]]
    )
    np.testing.assert_allclose(set_data[3][3], [12.0, 24.0], rtol=1e-6)
    assert _calls(fake, "set_alpha_mode") == [("set_alpha_mode", "segment-visual", 1)]
    assert _calls(fake, "set_query_capabilities") == [
        ("set_query_capabilities", "segment-visual", 0x02)
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[:3] == ("add_visual", "panel", "segment-visual")


def test_add_path_visual_uses_dvz_path_subpaths_styles_and_expanded_attributes():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = PathVisual(
        id="visual:paths",
        positions=np.array(
            [[-0.5, 0.25], [0.0, 0.5], [0.5, -0.25], [0.75, 0.25]],
            dtype=np.float32,
        ),
        path_lengths=(2, 2),
        colors=np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.5]], dtype=np.float32),
        widths=np.array([12.0, 24.0], dtype=np.float32),
        cap=StrokeCap.ROUND,
        join=StrokeJoin.BEVEL,
        miter_limit=8.0,
    )

    dvz_visual = renderer.add_path_visual(visual)

    assert dvz_visual == "path-visual"
    assert _calls(fake, "path_set_caps") == [("path_set_caps", "path-visual", 1, 1)]
    assert _calls(fake, "path_set_join") == [("path_set_join", "path-visual", 2, 8.0)]
    subpaths_call = _calls(fake, "path_set_subpaths")[0]
    assert subpaths_call[:3] == ("path_set_subpaths", "path-visual", 2)
    np.testing.assert_array_equal(subpaths_call[3], [2, 2])
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "color", "stroke_width_px"]
    np.testing.assert_allclose(
        set_data[0][3],
        [[-0.5, 0.25, 0.0], [0.0, 0.5, 0.0], [0.5, -0.25, 0.0], [0.75, 0.25, 0.0]],
    )
    np.testing.assert_array_equal(
        set_data[1][3],
        [[255, 0, 0, 255], [255, 0, 0, 255], [0, 128, 255, 128], [0, 128, 255, 128]],
    )
    np.testing.assert_allclose(set_data[2][3], [12.0, 12.0, 24.0, 24.0], rtol=1e-6)
    assert _calls(fake, "set_alpha_mode") == [("set_alpha_mode", "path-visual", 1)]
    assert _calls(fake, "set_query_capabilities") == [
        ("set_query_capabilities", "path-visual", 0x02)
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[:3] == ("add_visual", "panel", "path-visual")


def test_renderer_configures_equal_aspect_ndc_panel_when_available():
    fake = FakeDatovizV04()
    DatovizV04ProtocolRenderer(dvz=fake)

    assert _calls(fake, "set_background_color") == [
        ("set_background_color", "panel", (255, 255, 255, 255))
    ]
    view_call = _calls(fake, "set_view2d")[0]
    assert view_call[1] == "panel"
    assert view_call[2].aspect == 1
    assert view_call[2].padding == 0.0
    assert view_call[2].data_x.min == -1.0
    assert view_call[2].data_x.max == 1.0
    assert view_call[2].data_y.min == -1.0
    assert view_call[2].data_y.max == 1.0


def test_add_image_visual_uses_sampling_api_and_texture_upload():
    fake = FakeDatovizV04WithImageSampling()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    image = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 255]],
        ],
        dtype=np.uint8,
    )
    visual = ImageVisual(
        id="visual:image",
        image=image,
        extent=(-1.0, 1.0, -0.5, 0.5),
        origin=ImageOrigin.UPPER,
    )

    dvz_visual = renderer.add_image_visual(visual)

    assert dvz_visual == "image-visual"
    assert _calls(fake, "image_set_sampling") == [
        ("image_set_sampling", "image-visual", 1)
    ]
    assert [call[2] for call in _calls(fake, "set_data")] == ["position", "texcoords"]
    texture_call = _calls(fake, "set_texture")[0]
    assert texture_call[1] == "image-visual"
    np.testing.assert_array_equal(texture_call[2][..., :3], image)
    np.testing.assert_array_equal(
        texture_call[2][..., 3], np.full((2, 2), 255, dtype=np.uint8)
    )
    assert texture_call[3:] == (2, 2)
    assert _calls(fake, "set_query_capabilities") == [
        ("set_query_capabilities", "image-visual", 0x12)
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[:3] == ("add_visual", "panel", "image-visual")


def test_add_image_visual_maps_linear_sampling():
    fake = FakeDatovizV04WithImageSampling()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = ImageVisual(
        id="visual:image-linear",
        image=np.zeros((2, 2, 4), dtype=np.uint8),
        extent=(-1.0, 1.0, -0.5, 0.5),
        interpolation=ImageInterpolation.LINEAR,
    )

    renderer.add_image_visual(visual)

    assert _calls(fake, "image_set_sampling") == [
        ("image_set_sampling", "image-visual", 0)
    ]


def test_add_image_visual_rejects_nearest_without_datoviz_sampler_api():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    image = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 255]],
        ],
        dtype=np.uint8,
    )
    visual = ImageVisual(
        id="visual:image",
        image=image,
        extent=(-1.0, 1.0, -0.5, 0.5),
        origin=ImageOrigin.UPPER,
    )

    with pytest.raises(DatovizV04Unsupported, match="dvz_image_set_sampling"):
        renderer.add_image_visual(visual)

    assert _calls(fake, "image") == [("image", "scene", 0)]
    assert _calls(fake, "set_texture") == []


def test_add_image_visual_uses_sampled_field_path_with_sampling_api():
    fake = FakeDatovizV04WithSampledFieldsAndImageSampling()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    image = np.array(
        [
            [[255, 0, 0], [0, 255, 0]],
            [[0, 0, 255], [255, 255, 255]],
        ],
        dtype=np.uint8,
    )
    visual = ImageVisual(
        id="visual:image",
        image=image,
        extent=(-1.0, 1.0, -0.5, 0.5),
        origin=ImageOrigin.UPPER,
    )

    dvz_visual = renderer.add_image_visual(visual)

    assert dvz_visual == "image-visual"
    assert datoviz_v04_sampled_field_ready(fake)
    assert _calls(fake, "image_set_sampling") == [
        ("image_set_sampling", "image-visual", 1)
    ]
    assert _calls(fake, "sampled_field")
    assert _calls(fake, "set_field") == [
        ("set_field", "image-visual", "field", "sampled-field")
    ]
    assert _calls(fake, "set_texture") == []
    assert renderer.sampled_fields == {"visual:image": "sampled-field"}


def test_add_image_visual_converts_scalar_image_to_rgba8_texture():
    fake = FakeDatovizV04WithImageSampling()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = ImageVisual(
        id="visual:scalar-image",
        image=np.array([[0.0, 0.5], [1.0, 2.0]], dtype=np.float32),
        extent=(-1.0, 1.0, -0.5, 0.5),
        clim=(0.0, 1.0),
    )

    renderer.add_image_visual(visual)

    texture_call = _calls(fake, "set_texture")[0]
    np.testing.assert_array_equal(
        texture_call[2],
        [
            [[0, 0, 0, 255], [128, 128, 128, 255]],
            [[255, 255, 255, 255], [255, 255, 255, 255]],
        ],
    )


def test_add_image_visual_cpu_premaps_scalar_color_scale_to_canonical_rgba8():
    fake = FakeDatovizV04WithImageSampling()
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})
    visual = ImageVisual(
        id="visual:scalar-image",
        image=np.array([[0.0, 0.5], [1.0, 2.0]], dtype=np.float32),
        extent=(-1.0, 1.0, -0.5, 0.5),
        color_scale_id=scale.id,
    )

    renderer.add_image_visual(visual)

    texture_call = _calls(fake, "set_texture")[0]
    np.testing.assert_array_equal(
        texture_call[2],
        [
            [[0, 0, 0, 255], [128, 128, 128, 255]],
            [[255, 255, 255, 255], [255, 255, 255, 255]],
        ],
    )
    assert renderer.scalar_visuals["visual:scalar-image"].visual_id == visual.id


def test_query_panel_adds_scalar_point_payload_from_retained_scene_data():
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    fake = FakeDatovizV04WithRuntimeQuery(
        FakeDvzQueryResult(
            request_id=99,
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=123,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_POINT,
            item_id=1,
        )
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})
    renderer.add_point_visual(
        PointVisual(
            id="visual:scalar-points",
            positions=np.array([[0.0, 0.0], [1.0, 0.0]], dtype=np.float32),
            sizes=np.array([4.0, 4.0], dtype=np.float32),
            color_encoding=ScalarColorEncoding(
                slot=ScalarColorSlot.COLOR,
                values=np.array([0.0, 2.0], dtype=np.float32),
                color_scale_id=scale.id,
            ),
        )
    )

    result = renderer.query_panel(
        QueryRequest(
            id="query:scalar-point",
            panel_id="panel:main",
            coordinate=(32.0, 32.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            requested_extension_payload_kinds=(SCALAR_COLOR_QUERY_PAYLOAD_KIND,),
        )
    )

    assert result.status == QueryStatus.HIT
    assert result.extension_payload_kind == SCALAR_COLOR_QUERY_PAYLOAD_KIND
    assert result.extension_payload.visual_id == "visual:scalar-points"
    assert result.extension_payload.item_kind == "point"
    assert result.extension_payload.lut_index == 255
    assert result.value == 2.0
    assert result.displayed_rgba == (1.0, 1.0, 1.0, 1.0)


def test_query_panel_adds_scalar_image_payload_from_flat_datoviz_texel_id():
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    fake = FakeDatovizV04WithRuntimeQueryAndImageSampling(
        FakeDvzQueryResult(
            request_id=99,
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=456,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_IMAGE,
            texel_id=3,
        )
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})
    renderer.add_image_visual(
        ImageVisual(
            id="visual:scalar-image",
            image=np.array([[0.0, 0.25], [0.5, 0.75]], dtype=np.float32),
            extent=(-1.0, 1.0, -1.0, 1.0),
            color_scale_id=scale.id,
        )
    )

    result = renderer.query_panel(
        QueryRequest(
            id="query:scalar-image",
            panel_id="panel:main",
            coordinate=(32.0, 32.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            requested_extension_payload_kinds=(SCALAR_COLOR_QUERY_PAYLOAD_KIND,),
        )
    )

    assert result.status == QueryStatus.HIT
    assert result.extension_payload_kind == SCALAR_COLOR_QUERY_PAYLOAD_KIND
    assert result.extension_payload.visual_id == "visual:scalar-image"
    assert result.extension_payload.texel == (1, 1)
    assert result.extension_payload.source_value == 0.75
    assert result.extension_payload.lut_index == 192


def test_query_panel_reports_unsupported_when_scalar_payload_cannot_be_matched():
    fake = FakeDatovizV04WithRuntimeQuery(
        FakeDvzQueryResult(
            request_id=99,
            status=DVZ_QUERY_STATUS_HIT,
            hit=True,
            visual_id=123,
            visual_family=DVZ_SCENE_VISUAL_FAMILY_POINT,
            item_id=0,
        )
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    result = renderer.query_panel(
        QueryRequest(
            id="query:scalar-unmatched",
            panel_id="panel:main",
            coordinate=(32.0, 32.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            requested_extension_payload_kinds=(SCALAR_COLOR_QUERY_PAYLOAD_KIND,),
        )
    )

    assert result.status == QueryStatus.UNSUPPORTED
    assert "scalar_query_source_unavailable" in str(result.diagnostic)


def test_add_colorbar_guide_reports_missing_native_colorbar_facade():
    scale = _test_color_scale(colormap_id=ColorMapId.GRAY)
    renderer = DatovizV04ProtocolRenderer(
        dvz=FakeDatovizV04(), color_scales={scale.id: scale}
    )

    with pytest.raises(DatovizV04Unsupported, match="colorbar_render_unsupported"):
        renderer.add_colorbar_guide(
            ColorbarGuide(
                id="guide:colorbar",
                panel_id="panel:main",
                color_scale_id=scale.id,
            )
        )


def test_add_colorbar_guide_creates_native_datoviz_scale_colormap_and_colorbar():
    fake = FakeDatovizV04WithColorbar()
    scale = _test_color_scale(colormap_id=ColorMapId.VIRIDIS)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})
    guide = ColorbarGuide(
        id="guide:colorbar",
        panel_id="panel:main",
        color_scale_id=scale.id,
        label="value",
        ticks=(0.0, 0.5, 1.0),
        tick_labels=("low", "mid", "high"),
    )

    colorbar = renderer.add_colorbar_guide(guide)

    assert colorbar == "colorbar"
    assert _calls(fake, "scale") == [("scale", "scene", 0, b"value")]
    assert _calls(fake, "scale_set_domain") == [
        ("scale_set_domain", "scale", 0.0, 1.0)
    ]
    assert _calls(fake, "scale_set_view_range") == [
        ("scale_set_view_range", "scale", 0.0, 1.0)
    ]
    assert _calls(fake, "colormap_builtin") == [
        ("colormap_builtin", "scene", 1)
    ]
    assert _calls(fake, "scale_set_colormap") == [
        ("scale_set_colormap", "scale", "colormap")
    ]
    assert _calls(fake, "colorbar") == [
        ("colorbar", "panel", "scale", 0, 0, 6, b"value")
    ]
    assert _calls(fake, "colorbar_set_orientation") == [
        ("colorbar_set_orientation", "colorbar", 0)
    ]
    assert _calls(fake, "colorbar_set_anchor") == [
        ("colorbar_set_anchor", "colorbar", 6)
    ]
    assert _calls(fake, "colorbar_set_title") == [
        ("colorbar_set_title", "colorbar", b"value")
    ]
    assert renderer.colorbars[guide.id] == "colorbar"


def test_sampled_field_readiness_reports_missing_symbols():
    fake = FakeDatovizV04()

    assert not datoviz_v04_sampled_field_ready(fake)
    assert "dvz_sampled_field" in " ".join(datoviz_v04_sampled_field_diagnostics(fake))


def test_capture_png_bytes_uses_offscreen_view_and_returns_png_bytes():
    fake = FakeDatovizV04WithCapture()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)

    png = renderer.capture_png_bytes()

    assert png.startswith(b"\x89PNG")
    assert _calls(fake, "app") == [("app", "scene")]
    assert _calls(fake, "view_offscreen") == [
        ("view_offscreen", "app", "figure", 320, 240)
    ]
    assert _calls(fake, "render_once") == [("render_once", "app")]
    capture_calls = _calls(fake, "capture_png")
    assert capture_calls[0][1] == "offscreen-view"
    assert capture_calls[0][2].endswith(b".png")


def test_capture_png_bytes_rejects_missing_capture_binding():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    assert not datoviz_v04_capture_ready(fake)
    assert "dvz_view_capture_png" in " ".join(datoviz_v04_capture_diagnostics(fake))
    with pytest.raises(
        DatovizV04Unavailable, match="offscreen PNG capture is unavailable"
    ):
        renderer.capture_png_bytes()


def test_lower_origin_texcoords_are_not_flipped():
    texcoords = _image_texcoords(ImageOrigin.LOWER)
    np.testing.assert_allclose(
        texcoords, [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]]
    )




def test_add_mesh_visual_uploads_uniform_indexed_triangles():
    fake = FakeDatovizV04WithMesh()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = MeshVisual(
        id="visual:mesh",
        positions=np.array(
            [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.NDC,
        color=np.array([42, 157, 143, 192], dtype=np.uint8),
        order=2.0,
    )

    result = renderer.add_mesh_visual(visual)

    assert result == "mesh-visual"
    assert datoviz_v04_mesh_ready(fake) is True
    assert _calls(fake, "mesh") == [("mesh", "scene", 0)]
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "color"]
    np.testing.assert_allclose(
        set_data[0][3],
        [
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.5, 0.5, 0.0],
            [-0.5, 0.5, 0.0],
        ],
    )
    np.testing.assert_array_equal(
        set_data[1][3],
        np.tile(np.array([[42, 157, 143, 192]], dtype=np.uint8), (4, 1)),
    )
    assert _calls(fake, "set_index_data")[0][3] == 6
    np.testing.assert_array_equal(
        _calls(fake, "set_index_data")[0][2],
        np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32),
    )
    assert _calls(fake, "set_depth_test") == [("set_depth_test", "mesh-visual", False)]
    assert _calls(fake, "set_alpha_mode")


def test_add_mesh_visual_duplicates_face_colors_for_datoviz_vertex_color_mesh():
    fake = FakeDatovizV04WithMesh()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = MeshVisual(
        id="visual:mesh-face-color",
        positions=np.array(
            [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2], [0, 2, 3]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.NDC,
        color=np.array(
            [[255, 0, 0, 255], [0, 0, 255, 255]],
            dtype=np.uint8,
        ),
        color_mode=MeshColorMode.FACE,
    )

    renderer.add_mesh_visual(visual)

    set_data = _calls(fake, "set_data")
    np.testing.assert_allclose(
        set_data[0][3],
        [
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.5, 0.5, 0.0],
            [-0.5, -0.5, 0.0],
            [0.5, 0.5, 0.0],
            [-0.5, 0.5, 0.0],
        ],
    )
    np.testing.assert_array_equal(
        set_data[1][3],
        np.array(
            [
                [255, 0, 0, 255],
                [255, 0, 0, 255],
                [255, 0, 0, 255],
                [0, 0, 255, 255],
                [0, 0, 255, 255],
                [0, 0, 255, 255],
            ],
            dtype=np.uint8,
        ),
    )
    np.testing.assert_array_equal(
        _calls(fake, "set_index_data")[0][2],
        np.arange(6, dtype=np.uint32),
    )


def test_add_mesh_visual_accepts_default_data_domain_and_rejects_3d_before_diagnostics():
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithMesh())
    data_visual = MeshVisual(
        id="visual:data-mesh",
        positions=np.array([[0.0, 0.0], [0.5, 0.0], [0.0, 0.5]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
    )
    mesh_3d = MeshVisual(
        id="visual:mesh-3d",
        positions=np.array([[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.NDC,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
    )

    renderer.add_mesh_visual(data_visual)
    position_upload = _calls(renderer.dvz, "set_data")[0]
    np.testing.assert_allclose(
        position_upload[3],
        [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]],
    )
    with pytest.raises(DatovizV04Unsupported, match="2D positions"):
        renderer.add_mesh_visual(mesh_3d)


def test_add_mesh_visual_maps_data_coordinates_through_view2d():
    fake = FakeDatovizV04WithMesh()
    renderer = DatovizV04ProtocolRenderer(
        dvz=fake,
        view=View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(0.0, 10.0),
            y_range=(0.0, 10.0),
        ),
    )
    visual = MeshVisual(
        id="visual:data-mesh",
        positions=np.array([[0.0, 0.0], [10.0, 0.0], [0.0, 10.0]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
    )

    renderer.add_mesh_visual(visual)

    position_upload = _calls(fake, "set_data")[0]
    np.testing.assert_allclose(
        position_upload[3],
        [[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [-1.0, 1.0, 0.0]],
    )


def test_datoviz_mesh_diagnostics_name_missing_and_unverified_symbols():
    fake = FakeDatovizV04()

    diagnostics = datoviz_v04_mesh_diagnostics(fake)

    assert "missing dvz_mesh" in diagnostics
    assert "missing dvz_visual_set_index_data" in diagnostics
    assert "missing dvz_visual_set_depth_test" in diagnostics
    assert datoviz_v04_mesh_ready(fake) is False


def test_add_text_visual_uses_retained_text_style_placement_and_strings():
    fake = FakeDatovizV04WithText()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = TextVisual(
        id="visual:text",
        texts=("left", "café"),
        positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        coordinate_space=CoordinateSpace.NDC,
        rgba=np.array([[10, 20, 30, 255], [200, 150, 100, 128]], dtype=np.uint8),
        font_size_px=np.array([16.0, 24.0], dtype=np.float32),
        anchor_x=(TextAnchorX.LEFT, TextAnchorX.RIGHT),
        anchor_y=(TextAnchorY.TOP, TextAnchorY.BOTTOM),
        rotation_rad=np.array([0.0, 0.5], dtype=np.float32),
        z_order=4,
    )

    texts = renderer.add_text_visual(visual)

    assert texts == ("text-1", "text-2")
    assert datoviz_v04_text_ready(fake) is True
    assert _calls(fake, "text") == [
        ("text", "panel", 0, "text-1"),
        ("text", "panel", 0, "text-2"),
    ]
    assert _calls(fake, "text_set_style") == [
        ("text_set_style", "text-1", 16.0, 3, (10, 20, 30, 255)),
        ("text_set_style", "text-2", 24.0, 3, (200, 150, 100, 128)),
    ]
    assert _calls(fake, "text_set_placement") == [
        (
            "text_set_placement",
            "text-1",
            1,
            10,
            (-0.5, 0.25, 4.0),
            (0.0, 0.0),
            True,
            0.0,
            False,
        ),
        (
            "text_set_placement",
            "text-2",
            1,
            10,
            (0.5, -0.25, 4.0),
            (1.0, 1.0),
            True,
            0.5,
            False,
        ),
    ]
    assert _calls(fake, "text_set_string") == [
        ("text_set_string", "text-1", b"left"),
        ("text_set_string", "text-2", "café".encode("utf-8")),
    ]
    assert renderer.visuals["visual:text"] == ("text-1", "text-2")


def test_add_text_visual_reports_structured_unsupported_until_semantics_verified():
    fake = FakeDatovizV04()
    fake.dvz_text = lambda panel, flags: "text"
    fake.dvz_text_set_string = lambda text, value: None
    fake.dvz_text_style = lambda: object()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = TextVisual(
        id="visual:text",
        texts=("hello",),
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.NDC,
    )

    with pytest.raises(
        DatovizV04Unsupported, match="TextVisual support is unavailable"
    ) as exc_info:
        renderer.add_text_visual(visual)

    message = str(exc_info.value)
    assert "missing dvz_text_set_style" in message
    assert "missing dvz_text_set_placement" in message
    assert datoviz_v04_text_ready(fake) is False


def test_add_text_visual_reports_missing_text_facade_for_data_coordinates():
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04())
    visual = TextVisual(
        id="visual:data-text",
        texts=("data",),
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )

    with pytest.raises(DatovizV04Unsupported, match="missing dvz_text"):
        renderer.add_text_visual(visual)


def test_datoviz_text_diagnostics_name_missing_and_unverified_symbols():
    fake = FakeDatovizV04()

    diagnostics = datoviz_v04_text_diagnostics(fake)

    assert "missing dvz_text" in diagnostics
    assert "missing dvz_text_set_style" in diagnostics
    assert "missing dvz_text_set_placement" in diagnostics
    assert datoviz_v04_text_ready(fake) is False


def test_image_slice_rejects_data_extents_but_point_data_uses_default_domain():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    with pytest.raises(DatovizV04Unsupported, match="NDC image"):
        renderer.add_image_visual(
            ImageVisual(
                id="visual:data-image",
                image=np.zeros((2, 2, 4), dtype=np.uint8),
                extent=(0.0, 1.0, 0.0, 1.0),
                coordinate_space=CoordinateSpace.DATA,
            )
        )

    renderer.add_point_visual(
        PointVisual(
            id="visual:data-points",
            positions=np.array([[0.25, -0.5]], dtype=np.float32),
            colors=np.zeros((1, 4), dtype=np.uint8),
            sizes=1.0,
            coordinate_space=CoordinateSpace.DATA,
        )
    )
    position_upload = _calls(fake, "set_data")[0]
    np.testing.assert_allclose(position_upload[3], [[0.25, -0.5, 0.0]])


def test_renderer_close_uses_scene_destroy_when_available():
    fake = FakeDatovizV04()

    with DatovizV04ProtocolRenderer(dvz=fake) as renderer:
        assert renderer.scene == "scene"

    assert fake.destroyed is True
    assert _calls(fake, "destroy") == [("destroy", "scene")]


def test_renderer_close_destroys_lazy_capture_app_when_available():
    fake = FakeDatovizV04WithCapture()

    with DatovizV04ProtocolRenderer(dvz=fake) as renderer:
        renderer.capture_png_bytes()

    assert fake.app_destroyed is True
    assert _calls(fake, "app_destroy") == [("app_destroy", "app")]
    assert _calls(fake, "destroy") == [("destroy", "scene")]


def test_renderer_show_creates_live_view_and_runs_app():
    fake = FakeDatovizV04WithInteractive()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    renderer.show(frame_count=1)

    assert _calls(fake, "app") == [("app", "scene")]
    assert _calls(fake, "view") == [("view", "app", "figure", None)]
    assert _calls(fake, "app_run") == [("app_run", "app", 1)]


def test_renderer_show_returns_in_test_mode(monkeypatch):
    fake = FakeDatovizV04WithInteractive()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    monkeypatch.setenv("GSP_TEST", "True")
    renderer.show()

    assert _calls(fake, "app") == []
    assert _calls(fake, "app_run") == []


def test_configure_view2d_axes_uses_verified_datoviz_v04dev_symbols():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    renderer.configure_view2d_axes(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(-1.0, 2.0),
            y_range=(-3.0, 4.0),
        ),
        x_label="x",
        y_label="y",
        grid=True,
    )

    assert _calls(fake, "set_domain") == [
        ("set_domain", "panel", 0, -1.0, 2.0),
        ("set_domain", "panel", 1, -3.0, 4.0),
    ]
    assert _calls(fake, "set_view2d")[-1] == ("set_view2d", "panel", "view2d")
    assert _calls(fake, "panel_axis") == [
        ("panel_axis", "panel", 0),
        ("panel_axis", "panel", 1),
    ]
    assert _calls(fake, "set_tick_policy") == [
        ("set_tick_policy", "axis:0", "tick-policy"),
        ("set_tick_policy", "axis:1", "tick-policy"),
    ]
    assert _calls(fake, "set_grid") == [
        ("set_grid", "axis:0", True),
        ("set_grid", "axis:1", True),
    ]
    assert _calls(fake, "set_label") == [
        ("set_label", "axis:0", "x"),
        ("set_label", "axis:1", "y"),
    ]


def test_configure_view2d_axes_rejects_unavailable_or_strict_explicit_ticks():
    with pytest.raises(DatovizV04Unavailable, match="missing v0.4-dev axis symbols"):
        DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).configure_view2d_axes(
            View2D(id="view:main", panel_id="panel:main")
        )

    with pytest.raises(DatovizV04Unsupported, match="explicit GSP ticks"):
        DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithAxes()).configure_view2d_axes(
            View2D(id="view:main", panel_id="panel:main"),
            backend_auto_ticks=False,
        )


def test_imported_datoviz_binding_has_expected_v04_shape_when_available():
    dvz = pytest.importorskip("datoviz")
    if not is_datoviz_v04_facade(dvz):
        pytest.skip("installed Datoviz binding is not the v0.4 facade")

    assert is_datoviz_v04_facade(dvz)


def test_imported_datoviz_capability_snapshot_translates_when_available():
    dvz = pytest.importorskip("datoviz")
    if not hasattr(dvz, "dvz_capability_snapshot"):
        pytest.skip("installed Datoviz binding does not expose dvz_capability_snapshot")

    caps = gsp_capability_snapshot_from_datoviz(dvz.dvz_capability_snapshot(), dvz=dvz)

    assert caps.server_name == "datoviz-v0.4-protocol-slice"
    assert "datoviz_raw_capabilities" in caps.metadata
    if datoviz_v04_query_binding_ready(dvz):
        assert caps.query_modes == ("panel-query", "point-item", "image-texel")
    else:
        assert caps.query_modes == ()


def test_imported_datoviz_query_result_binding_is_decodable_when_available():
    dvz = pytest.importorskip("datoviz")
    query_result_type = getattr(dvz, "DvzQueryResult", None)
    if query_result_type is None or not hasattr(query_result_type, "_fields_"):
        pytest.skip(
            "installed Datoviz binding does not expose decodable DvzQueryResult fields"
        )

    raw = query_result_type()
    raw.request_id = 1
    raw.status = DVZ_QUERY_STATUS_MISS
    raw.hit = False

    result = decode_dvz_query_result(raw)

    assert result.request_id == "query:datoviz-1"
    assert result.status == QueryStatus.MISS


def test_imported_datoviz_query_capability_promotes_when_binding_is_ready():
    dvz = pytest.importorskip("datoviz")
    if not datoviz_v04_query_binding_ready(dvz):
        pytest.skip("installed Datoviz binding does not expose the v0.4 query binding")

    caps = capability_snapshot()

    assert caps.supports_query_mode("panel-query")
    assert caps.supports_query_mode("point-item")
    assert caps.supports_query_mode("image-texel")


def test_imported_datoviz_sampled_field_binding_smoke_when_available():
    dvz = pytest.importorskip("datoviz")
    if not datoviz_v04_sampled_field_ready(dvz):
        pytest.skip(
            "installed Datoviz binding does not expose sampled-field image symbols"
        )

    assert datoviz_v04_sampled_field_diagnostics(dvz) == ()


def test_imported_datoviz_capture_binding_smoke_when_available():
    dvz = pytest.importorskip("datoviz")
    if not datoviz_v04_capture_ready(dvz):
        pytest.skip(
            "installed Datoviz binding does not expose offscreen PNG capture symbols"
        )

    assert datoviz_v04_capture_diagnostics(dvz) == ()


def _test_color_scale(*, colormap_id: ColorMapId = ColorMapId.VIRIDIS) -> ColorScale:
    return ColorScale(
        id=f"scale:{colormap_id.value}",
        colormap=ColorMapRef(colormap_id),
        normalize=LinearNormalize(vmin=0.0, vmax=1.0),
    )
