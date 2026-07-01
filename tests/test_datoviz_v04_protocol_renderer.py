"""Tests for the bounded Datoviz v0.4 protocol adapter slice."""

from __future__ import annotations

import ctypes
import inspect
from pathlib import Path
from types import SimpleNamespace
import sys
import types

import numpy as np
import pytest

import gsp.protocol.navigation as navigation_module
from gsp.protocol import (
    ImageOrigin,
    ImageVisual,
    MESH_MATERIAL_FLAT_LAMBERT_CAPABILITY,
    MESH_NORMALS_FACE3D_CAPABILITY,
    MESH_NORMAL_GENERATION_FACE_FLAT_CAPABILITY,
    MeshColorMode,
    MeshNormalGeneration,
    MeshNormalMode,
    MeshShading,
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
    Camera3D,
    CanvasSize,
    ColorbarGuide,
    ColorbarGuideStyle,
    ColorMapId,
    ColorMapRef,
    ColorScale,
    LinearNormalize,
    LogicalPixelRect,
    MESH3D_OPAQUE_DEPTH_CAPABILITY,
    NavigationPlacement,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryScope,
    QueryStatus,
    SCALAR_COLOR_QUERY_PAYLOAD_KIND,
    VIEW3D_QUERY_PAYLOAD_KIND,
    VIEW3D_LIGHT_AMBIENT_CAPABILITY,
    VIEW3D_LIGHT_DIRECTIONAL_CAPABILITY,
    QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
    ScalarColorEncoding,
    ScalarColorSlot,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    TextAnchorX,
    TextAnchorY,
    TransformPlacement,
    View2D,
    View3D,
    View3DDiagnosticCode,
    VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
    DirectionalLight3D,
    OrthographicProjection3D,
    VisualFamily,
    VisualTransformBinding,
    pan_view2d,
    project_view3d_data_point,
    resolve_view3d_projection_snapshot,
    zoom_view2d_about,
)
from gsp.protocol.visuals import CoordinateSpace, ImageInterpolation
from gsp_datoviz.capabilities import (
    DATOVIZ_S034_AXIS_STYLE_FIELDS,
    DATOVIZ_V04_AXIS_PROVIDER,
    datoviz_v04_axis_provider_capability,
    datoviz_v04_axis_symbols,
    datoviz_v04_capture_diagnostics,
    datoviz_v04_capture_ready,
    datoviz_v04_grid_clip_to_plot_rect_ready_for_source,
    gsp_capability_snapshot_from_datoviz,
)
from gsp_datoviz.protocol_renderer import (
    DatovizV04ProtocolRenderer,
    DatovizV04Unavailable,
    DatovizV04Unsupported,
    capability_snapshot,
    datoviz_v04_live_input_diagnostics,
    datoviz_v04_live_input_ready,
    datoviz_v04_mesh_diagnostics,
    datoviz_v04_mesh_ready,
    datoviz_v04_sampled_field_diagnostics,
    datoviz_v04_sampled_field_ready,
    datoviz_v04_text_diagnostics,
    datoviz_v04_text_ready,
    datoviz_v04_view3d_camera_diagnostics,
    datoviz_v04_view3d_live_navigation_diagnostics,
    import_datoviz_v04,
    is_datoviz_v04_facade,
    _DatovizLiveView2DNavigation,
    _image_texcoords,
    _datoviz_view_size_desc,
    _resolved_canvas_from_datoviz,
    _visual_attach_desc,
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
    datoviz_query_view3d_ray_context,
)
from gsp_matplotlib.protocol_query import query_view3d_ray_context


class FakeDatovizV04:
    """Small recorder for the dvz_* facade used by the adapter."""

    DVZ_COLOR_PIPELINE_LINEAR_SRGB = 10
    DVZ_COLOR_PIPELINE_LEGACY_SRGB_BLEND = 11

    def __init__(self):
        self.calls = []
        self.destroyed = False

    def dvz_scene(self):
        self.calls.append(("scene",))
        return "scene"

    def dvz_figure(self, scene, width, height, flags):
        self.calls.append(("figure", scene, width, height, flags))
        return "figure"

    def dvz_figure_set_color_pipeline(self, figure, pipeline):
        self.calls.append(("figure_set_color_pipeline", figure, pipeline))
        return None

    def dvz_panel_full(self, figure):
        self.calls.append(("panel_full", figure))
        return "panel"

    class DvzPanelDesc:
        x = 0.0
        y = 0.0
        width = 0.0
        height = 0.0

    def dvz_panel(self, figure, desc):
        self.calls.append(("panel", figure, desc.x, desc.y, desc.width, desc.height))
        return "panel"

    class FakeDomain:
        def __init__(self):
            self.min = -1.0
            self.max = 1.0

    class FakePanelView2D:
        def __init__(self):
            self.aspect = 0
            self.padding = 1.0

    def dvz_panel_view2d(self):
        self.calls.append(("panel_view2d",))
        return self.FakePanelView2D()

    def dvz_panel_set_view2d(self, panel, view):
        self.calls.append(("set_view2d", panel, view))
        return 0

    def dvz_panel_set_domain(self, panel, dim, minimum, maximum):
        self.calls.append(("set_domain", panel, dim, minimum, maximum))
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
            ("clip_rect", ctypes.c_int),
            ("viewport_rect", ctypes.c_int),
        )

    def dvz_scene_destroy(self, scene):
        self.calls.append(("destroy", scene))
        self.destroyed = True


class FakeDatovizV04WithColorPipeline(FakeDatovizV04):
    pass


class FakeDatovizV04WithoutColorPipeline(FakeDatovizV04):
    def __getattribute__(self, name):
        if name == "dvz_figure_set_color_pipeline":
            raise AttributeError(name)
        return super().__getattribute__(name)


class FakeDatovizV04WithAxes(FakeDatovizV04):
    """Recorder exposing the verified v0.4-dev native axis symbols."""

    DVZ_DIM_X = 0
    DVZ_DIM_Y = 1

    class FakeAxisStyle:
        def __init__(self):
            self.spine_width = 0.0
            self.major_tick_width = 0.0
            self.minor_tick_width = 0.0
            self.grid_width = 0.0
            self.major_tick_length = 0.0
            self.minor_tick_length = 0.0
            self.tick_gap_px = 0.0
            self.label_gap_px = 0.0
            self.tick_size_px = 0.0
            self.label_size_px = 0.0
            self.plot_margin_left = 0.0
            self.plot_margin_right = 0.0
            self.plot_margin_bottom = 0.0
            self.plot_margin_top = 0.0
            self.spine_color = [0, 0, 0, 0]
            self.major_tick_color = [0, 0, 0, 0]
            self.minor_tick_color = [0, 0, 0, 0]
            self.grid_color = [0, 0, 0, 0]
            self.show_spine = False
            self.show_major_ticks = False
            self.show_minor_ticks = False

    def dvz_panel_view2d(self):
        self.calls.append(("view2d",))
        return self.FakePanelView2D()

    def dvz_panel_set_view2d(self, panel, view):
        self.calls.append(("set_view2d", panel, view))
        return 0

    def dvz_panel_visible_domain(self, panel, dim, out_min, out_max):
        self.calls.append(("visible_domain", panel, dim, out_min, out_max))
        return True

    def dvz_panel_transform_point(
        self, panel, from_space, to_space, in_point, out_point
    ):
        self.calls.append(("transform_point", panel, from_space, to_space))
        return True

    def dvz_panel_axis(self, panel, dim):
        self.calls.append(("panel_axis", panel, dim))
        return f"axis:{dim}"

    def dvz_axis_tick_policy(self):
        self.calls.append(("tick_policy",))
        return "tick-policy"

    def dvz_axis_style(self):
        self.calls.append(("axis_style",))
        return self.FakeAxisStyle()

    def dvz_axis_set_style(self, axis, style):
        self.calls.append(
            (
                "set_style",
                axis,
                style.spine_width,
                style.major_tick_width,
                style.major_tick_length,
                style.tick_size_px,
                style.label_size_px,
                style.plot_margin_top,
                tuple(style.spine_color),
                tuple(style.major_tick_color),
                tuple(style.grid_color),
                style.show_major_ticks,
            )
        )
        return True

    def dvz_axis_set_tick_policy(self, axis, policy):
        self.calls.append(("set_tick_policy", axis, policy))
        return True

    def dvz_axis_clear_ticks(self, axis):
        self.calls.append(("clear_ticks", axis))
        return True

    def dvz_axis_set_grid(self, axis, visible):
        self.calls.append(("set_grid", axis, visible))
        return True

    def dvz_axis_set_label(self, axis, label):
        self.calls.append(("set_label", axis, label))
        return True

    def dvz_axis_set_plot_margins(self, axis, left, right, bottom, top):
        self.calls.append(("set_plot_margins", axis, left, right, bottom, top))
        return True


class FakeDatovizV04WithAxisTicks(FakeDatovizV04WithAxes):
    """Recorder exposing the explicit axis tick facade proven in S030."""

    def dvz_axis_set_ticks(self, axis, values, labels=None):
        self.calls.append(("set_ticks", axis, tuple(values), labels))
        return True


class FakeDatovizV04WithDescriptorDomains(FakeDatovizV04WithAxes):
    """Recorder for bindings that carry View2D domains on the descriptor."""

    class FakePanelView2D(FakeDatovizV04.FakePanelView2D):
        def __init__(self):
            super().__init__()
            self.data_x = FakeDatovizV04.FakeDomain()
            self.data_y = FakeDatovizV04.FakeDomain()


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
    class DvzPointerEventType:
        DVZ_POINTER_EVENT_RELEASE = 0
        DVZ_POINTER_EVENT_PRESS = 1
        DVZ_POINTER_EVENT_MOVE = 2
        DVZ_POINTER_EVENT_DOUBLE_CLICK = 5
        DVZ_POINTER_EVENT_DRAG = 11
        DVZ_POINTER_EVENT_DRAG_STOP = 12
        DVZ_POINTER_EVENT_WHEEL = 20

    class DvzInputEventType:
        DVZ_INPUT_EVENT_POINTER = 1
        DVZ_INPUT_EVENT_RESIZE = 3
        DVZ_INPUT_EVENT_SCALE = 4

    class DvzPointerButton:
        DVZ_POINTER_BUTTON_LEFT = 1
        DVZ_POINTER_BUTTON_RIGHT = 3

    class DvzPointerEvent:
        def __init__(self):
            self.window_size = [0.0, 0.0]

    class DvzInputEvent:
        def __init__(self):
            self.content = SimpleNamespace()

    class DvzInputEventContent:
        pointer = None

    class FakePanzoomDesc:
        width = 0.0
        height = 0.0
        controller_flags = 0

    def __init__(self):
        super().__init__()
        self.pointer_callback = None
        self.pointer_user_data = None
        self.input_callback = None
        self.input_user_data = None

    def dvz_view_glfw(self, app, figure, width, height, title):
        self.calls.append(("view_glfw", app, figure, width, height, title))
        return "live-view"

    def dvz_app_run(self, app, frame_count):
        self.calls.append(("app_run", app, frame_count))
        return None

    def dvz_panzoom_desc(self):
        self.calls.append(("panzoom_desc",))
        return self.FakePanzoomDesc()

    def dvz_view_panzoom(self, view, panel, desc):
        self.calls.append(("view_panzoom", view, panel, desc.width, desc.height))
        return "panzoom"

    def dvz_view_input(self, view):
        self.calls.append(("view_input", view))
        return "input-router"

    def dvz_input_subscribe_pointer(self, router, callback, user_data):
        self.calls.append(("subscribe_pointer", router, user_data))
        self.pointer_callback = callback
        self.pointer_user_data = user_data
        return None

    def dvz_input_unsubscribe_pointer(self, router, callback, user_data):
        self.calls.append(("unsubscribe_pointer", router, callback, user_data))
        if callback == self.pointer_callback:
            self.pointer_callback = None
        return None

    def dvz_input_subscribe_event(self, router, callback, user_data):
        self.calls.append(("subscribe_event", router, user_data))
        self.input_callback = callback
        self.input_user_data = user_data
        return None

    def dvz_input_unsubscribe_event(self, router, callback, user_data):
        self.calls.append(("unsubscribe_event", router, callback, user_data))
        if callback == self.input_callback:
            self.input_callback = None
        return None

    def dvz_view_request_frame(self, view):
        self.calls.append(("request_frame", view))
        return None


class FakeDatovizV04WithInteractiveAxes(
    FakeDatovizV04WithInteractive, FakeDatovizV04WithAxes
):
    pass


class FakePointerEvent:
    def __init__(
        self,
        event_type,
        x,
        y,
        *,
        button=0,
        wheel_y=0.0,
        window_size=(800.0, 600.0),
    ):
        self.type = event_type
        self.pos = [float(x), float(y)]
        self.button = button
        self.window_size = [float(window_size[0]), float(window_size[1])]
        self.content = SimpleNamespace(w=SimpleNamespace(dir=[0.0, float(wheel_y)]))


class FakePointerEventPtr:
    def __init__(self, event):
        self.contents = event


class FakeInputEvent:
    def __init__(
        self,
        event_type,
        *,
        pointer_event=None,
        resize_event=None,
        scale_event=None,
    ):
        self.type = event_type
        self.content = SimpleNamespace(
            pointer=pointer_event,
            resize=resize_event,
            scale=scale_event,
        )


class FakeInputEventPtr:
    def __init__(self, event):
        self.contents = event


def _emit_fake_datoviz_pointer(
    fake: FakeDatovizV04WithInteractive,
    event_type,
    x: float,
    y: float,
    *,
    button: int = 0,
    wheel_y: float = 0.0,
    window_size: tuple[float, float] = (800.0, 600.0),
) -> None:
    assert fake.input_callback is not None
    fake.input_callback(
        "input-router",
        FakeInputEventPtr(
            FakeInputEvent(
                fake.DvzInputEventType.DVZ_INPUT_EVENT_POINTER,
                pointer_event=FakePointerEvent(
                    event_type,
                    x,
                    y,
                    button=button,
                    wheel_y=wheel_y,
                    window_size=window_size,
                )
            )
        ),
        None,
    )


def _emit_fake_datoviz_resize(
    fake: FakeDatovizV04WithInteractive,
    *,
    window_width: int,
    window_height: int,
    framebuffer_width: int | None = None,
    framebuffer_height: int | None = None,
    content_scale_x: float = 1.0,
    content_scale_y: float = 1.0,
) -> None:
    assert fake.input_callback is not None
    fake.input_callback(
        "input-router",
        FakeInputEventPtr(
            FakeInputEvent(
                fake.DvzInputEventType.DVZ_INPUT_EVENT_RESIZE,
                resize_event=SimpleNamespace(
                    framebuffer_width=framebuffer_width or window_width,
                    framebuffer_height=framebuffer_height or window_height,
                    window_width=window_width,
                    window_height=window_height,
                    content_scale_x=content_scale_x,
                    content_scale_y=content_scale_y,
                ),
            )
        ),
        None,
    )


def _emit_fake_datoviz_scale(
    fake: FakeDatovizV04WithInteractive,
    *,
    content_scale_x: float,
    content_scale_y: float,
) -> None:
    assert fake.input_callback is not None
    fake.input_callback(
        "input-router",
        FakeInputEventPtr(
            FakeInputEvent(
                fake.DvzInputEventType.DVZ_INPUT_EVENT_SCALE,
                scale_event=SimpleNamespace(
                    content_scale_x=content_scale_x,
                    content_scale_y=content_scale_y,
                ),
            )
        ),
        None,
    )


class FakeDatovizV04WithQueryCapabilities(FakeDatovizV04):
    def dvz_visual_set_query_capabilities(self, visual, capabilities):
        self.calls.append(("set_query_capabilities", visual, capabilities))
        return None


class FakeDatovizV04WithCurrentAttributeNames(FakeDatovizV04WithQueryCapabilities):
    def dvz_visual_set_data(self, visual, name, data):
        self.calls.append(("set_data", visual, name, np.array(data, copy=True)))
        if name in {"diameter_px", "stroke_width_px"}:
            return -1
        return 0


class FakeDatovizV04WithMesh(FakeDatovizV04WithQueryCapabilities):
    DvzCameraDesc = object
    DvzCameraView = object
    DvzCameraProjection = object
    DVZ_CAMERA_ORTHOGRAPHIC = 1

    def dvz_camera_desc(self):
        self.calls.append(("camera_desc",))
        return SimpleNamespace(
            view=SimpleNamespace(
                eye=[0.0, 0.0, 0.0],
                target=[0.0, 0.0, 0.0],
                up=[0.0, 1.0, 0.0],
            ),
            projection=SimpleNamespace(
                type=0,
                near_clip=0.0,
                far_clip=1.0,
                ortho_height=2.0,
            ),
        )

    def dvz_panel_set_camera(self, panel, desc):
        self.calls.append(
            (
                "panel_set_camera",
                panel,
                tuple(desc.view.eye),
                tuple(desc.view.target),
                tuple(desc.view.up),
                desc.projection.type,
                desc.projection.near_clip,
                desc.projection.far_clip,
                desc.projection.ortho_height,
            )
        )
        return "panel-camera"

    def dvz_camera_set_orthographic_bounds(
        self, camera, left, right, bottom, top, near, far
    ):
        self.calls.append(
            (
                "camera_set_orthographic_bounds",
                camera,
                left,
                right,
                bottom,
                top,
                near,
                far,
            )
        )
        return 0

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
        DVZ_COLORBAR_PLACEMENT_DETACHED = 1

    class DvzPlacementSpace:
        DVZ_PLACEMENT_SPACE_PANEL = 0

    class DvzHorizontalAnchor:
        DVZ_HORIZONTAL_ANCHOR_RIGHT = 2

    class DvzVerticalAnchor:
        DVZ_VERTICAL_ANCHOR_CENTER = 1

    class DvzSceneAnchor:
        DVZ_SCENE_ANCHOR_PANEL_RIGHT = 6

    class FakeScaleDesc:
        def __init__(self):
            self.kind = None
            self.label = None

    class FakePlacement:
        def __init__(self):
            self.space = None
            self.horizontal_anchor = None
            self.vertical_anchor = None
            self.offset_x_px = None
            self.offset_y_px = None
            self.width_px = None
            self.height_px = None

    class FakeColorbarDesc:
        def __init__(self):
            self.orientation = None
            self.placement_mode = None
            self.anchor = None
            self.title = None
            self.ramp_width_px = None
            self.tick_length_px = None
            self.label_gap_px = None
            self.placement = FakeDatovizV04WithColorbar.FakePlacement()

    class FakeFormatDesc:
        def __init__(self):
            self.precision = None
            self.trim_trailing_zeros = None

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
                desc.ramp_width_px,
                desc.tick_length_px,
                desc.label_gap_px,
                desc.placement.space,
                desc.placement.horizontal_anchor,
                desc.placement.vertical_anchor,
                desc.placement.width_px,
                desc.placement.height_px,
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

    def dvz_colorbar_set_ticks(self, colorbar, values, labels=None):
        self.calls.append(
            (
                "colorbar_set_ticks",
                colorbar,
                np.array(values, copy=True),
                tuple(labels) if labels is not None else None,
            )
        )
        return True

    def dvz_format_desc(self):
        self.calls.append(("format_desc",))
        return self.FakeFormatDesc()

    def dvz_colorbar_set_format(self, colorbar, format_desc):
        self.calls.append(
            (
                "colorbar_set_format",
                colorbar,
                format_desc.precision,
                format_desc.trim_trailing_zeros,
            )
        )
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


def _calls_from(calls, name):
    return [call for call in calls if call[0] == name]


def _canonical_view3d_for_datoviz_query() -> View3D:
    return View3D(
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


def test_renderer_sets_datoviz_color_pipeline_when_binding_is_available():
    fake = FakeDatovizV04WithColorPipeline()

    DatovizV04ProtocolRenderer(dvz=fake, color_pipeline="legacy_srgb_blend")

    assert _calls(fake, "figure_set_color_pipeline") == [
        ("figure_set_color_pipeline", "figure", 11)
    ]


def test_renderer_can_create_custom_panel_bounds_for_review_layout():
    fake = FakeDatovizV04()

    DatovizV04ProtocolRenderer(dvz=fake, panel_bounds=(0.0, 0.07, 1.0, 0.93))

    assert _calls(fake, "panel") == [("panel", "figure", 0.0, 0.07, 1.0, 0.93)]
    assert _calls(fake, "panel_full") == []


def test_renderer_defaults_to_legacy_color_pipeline_when_binding_is_available():
    fake = FakeDatovizV04WithColorPipeline()

    DatovizV04ProtocolRenderer(dvz=fake)

    assert _calls(fake, "figure_set_color_pipeline") == [
        ("figure_set_color_pipeline", "figure", 11)
    ]


def test_renderer_accepts_explicit_linear_color_pipeline_without_datoviz_binding():
    fake = FakeDatovizV04WithoutColorPipeline()

    DatovizV04ProtocolRenderer(dvz=fake, color_pipeline="linear_srgb")

    assert _calls(fake, "figure_set_color_pipeline") == []


def test_renderer_rejects_legacy_color_pipeline_without_datoviz_binding():
    fake = FakeDatovizV04WithoutColorPipeline()

    with pytest.raises(DatovizV04Unavailable, match="legacy sRGB blend mode"):
        DatovizV04ProtocolRenderer(dvz=fake, color_pipeline="legacy_srgb_blend")

    assert _calls(fake, "figure_set_color_pipeline") == []


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
    assert caps.supports_navigation_placement(NavigationPlacement.RETAINED_GPU_STATE)
    assert caps.supports_navigation_capability("interaction.view2d.navigation.v1")
    assert "s027_transform" in caps.metadata
    assert "s035_navigation" in caps.metadata
    assert "s028_guide_view2d" in caps.metadata
    assert "s034_guide_layout_audit" in caps.metadata
    audit = caps.metadata["s034_guide_layout_audit"]
    assert audit["layout_strict"] is False
    assert audit["resolved_layout_produce"] == "none"
    assert audit["panel_text_title"] == "adapted: panel_text_guide_as_screen_text"
    assert audit["axis_style_fields"] == DATOVIZ_S034_AXIS_STYLE_FIELDS
    assert audit["grid_clip_to_plot_rect"] == "unsupported"
    assert "grid_clip_not_enforced" in audit["diagnostics"]
    assert "grid_clip_native_api_unverified" in audit["diagnostics"]
    assert (
        "axis_guide_query_unsupported" in caps.metadata["s028_guide_view2d_diagnostics"]
    )
    assert "grid_clip_not_enforced" in caps.guide_layout_capability.diagnostics
    assert "axis_style_mapping_partial" in caps.layout_capability.diagnostics
    assert caps.metadata["datoviz_api"] == "v0.4 dvz_* facade"


def test_capability_snapshot_promotes_native_datoviz_grid_clip_when_source_is_fixed(
    tmp_path: Path,
) -> None:
    source = _write_datoviz_grid_clip_source(tmp_path)
    fake_dvz = SimpleNamespace(__file__=str(source / "datoviz" / "__init__.py"))

    caps = gsp_capability_snapshot_from_datoviz(None, dvz=fake_dvz)

    assert datoviz_v04_grid_clip_to_plot_rect_ready_for_source(source)
    audit = caps.metadata["s034_guide_layout_audit"]
    assert audit["grid_clip_to_plot_rect"] == "native-verified"
    assert "grid_clip_native_verified" in audit["diagnostics"]
    assert "grid_clip_not_enforced" not in audit["diagnostics"]
    assert caps.guide_layout_capability.axis_grid_clip_to_plot_rect is True
    assert "grid_clip_native_verified" in caps.guide_layout_capability.diagnostics


def test_retained_view2d_navigation_update_does_not_reupload_visual_buffers():
    fake = FakeDatovizV04WithQueryCapabilities()
    initial_view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(0.0, 10.0),
        y_range=(0.0, 10.0),
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view=initial_view)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[5.0, 5.0]], dtype=np.float32),
        colors=np.array([[255, 0, 0, 255]], dtype=np.uint8),
        sizes=np.array([8.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )
    renderer.add_point_visual(visual)
    baseline_call_count = len(fake.calls)

    next_view = pan_view2d(
        initial_view,
        LogicalPixelRect(x=0.0, y=0.0, width=1000.0, height=1000.0),
        dx_px=100.0,
        dy_px=0.0,
    )
    renderer.apply_retained_view2d_navigation(next_view)

    new_calls = fake.calls[baseline_call_count:]
    assert _calls_from(new_calls, "set_domain") == [
        ("set_domain", "panel", 0, -1.0, 9.0),
        ("set_domain", "panel", 1, 0.0, 10.0),
    ]
    assert _calls_from(new_calls, "panel_view2d")
    assert _calls_from(new_calls, "set_view2d")
    assert not _calls_from(new_calls, "set_data")
    assert not _calls_from(new_calls, "set_texture")
    assert not _calls_from(new_calls, "set_index_data")
    assert not _calls_from(new_calls, "sampled_field_set_data")
    assert not _calls_from(new_calls, "point")
    assert not _calls_from(new_calls, "image")
    assert not _calls_from(new_calls, "mesh")
    assert not _calls_from(new_calls, "add_visual")
    assert renderer.view == next_view


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


def test_datoviz_capabilities_promote_view3d_ray_when_camera_binding_is_ready():
    promoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithMesh()).capabilities()
    unpromoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).capabilities()

    assert promoted.query_modes == ("view3d-ray",)
    assert promoted.supports_view3d_capability(VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY)
    assert promoted.supports_view3d_capability(QUERY_VIEW3D_RAY_READBACK_CAPABILITY)
    assert promoted.adapt_query_mode("view3d-ray").outcome.value == "accept"
    assert "datoviz_view3d_binding_diagnostics" not in promoted.metadata
    assert "view3d-ray" not in unpromoted.query_modes
    assert "datoviz_view3d_binding_diagnostics" in unpromoted.metadata


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


def test_datoviz_view3d_ray_context_matches_matplotlib_reference():
    view = _canonical_view3d_for_datoviz_query()
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    request = QueryRequest(
        id="query:ray",
        panel_id="panel:main",
        coordinate=(75.0, 25.0),
        coordinate_space=QueryCoordinateSpace.PANEL,
        layout_snapshot_id=snapshot.layout_snapshot_id,
        view_snapshot_id=snapshot.view_projection_snapshot_id,
    )

    datoviz_result = datoviz_query_view3d_ray_context(
        request,
        view,
        snapshot,
        panel_bounds=(0.0, 100.0, 0.0, 100.0),
    )
    matplotlib_result = query_view3d_ray_context(
        request,
        view,
        snapshot,
        panel_bounds=(0.0, 100.0, 0.0, 100.0),
    )

    assert datoviz_result == matplotlib_result
    assert datoviz_result.extension_payload_kind == VIEW3D_QUERY_PAYLOAD_KIND


def test_datoviz_renderer_view3d_ray_context_uses_current_view_and_bounds():
    view = _canonical_view3d_for_datoviz_query()
    renderer = DatovizV04ProtocolRenderer(
        dvz=FakeDatovizV04WithMesh(),
        width=200,
        height=100,
        panel_bounds=(0.0, 0.0, 0.5, 1.0),
        view3d=view,
    )

    result = renderer.query_view3d_ray_context(
        QueryRequest(
            id="query:ray",
            panel_id="panel:main",
            coordinate=(50.0, 50.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
        ),
        layout_snapshot_id="layout:datoviz",
    )

    assert result.status == QueryStatus.HIT
    assert result.extension_payload_kind == VIEW3D_QUERY_PAYLOAD_KIND
    assert result.visual_coordinate == (0.0, 0.0)
    assert result.layout_snapshot_id == "layout:datoviz"
    assert result.view_snapshot_id is not None
    assert result.view_snapshot_id.startswith("view3d-projection:")


def test_datoviz_renderer_view3d_ray_context_rejects_missing_or_stale_view():
    no_view = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithQueryCapabilities())

    unsupported = no_view.query_view3d_ray_context(
        QueryRequest(
            id="query:ray",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
        ),
        layout_snapshot_id="layout:datoviz",
    )

    view = _canonical_view3d_for_datoviz_query()
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithMesh(), view3d=view)
    stale = renderer.query_view3d_ray_context(
        QueryRequest(
            id="query:stale",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
            layout_snapshot_id="layout:stale",
        ),
        layout_snapshot_id="layout:datoviz",
    )

    assert unsupported.status == QueryStatus.UNSUPPORTED
    assert View3DDiagnosticCode.VIEW3D_NOT_SUPPORTED.value in str(
        unsupported.diagnostic
    )
    assert stale.status == QueryStatus.STALE
    assert stale.diagnostic == View3DDiagnosticCode.QUERY_3D_SNAPSHOT_MISMATCH.value


def test_facade_shape_rejects_missing_v04_functions():
    class IncompleteDatoviz:
        pass

    assert is_datoviz_v04_facade(IncompleteDatoviz()) is False

    with pytest.raises(DatovizV04Unavailable, match="missing v0.4 functions"):
        DatovizV04ProtocolRenderer(dvz=IncompleteDatoviz())


def test_datoviz_axis_provider_is_capability_gated():
    unsupported = datoviz_v04_axis_provider_capability(FakeDatovizV04())
    supported = datoviz_v04_axis_provider_capability(FakeDatovizV04WithAxes())
    explicit_supported = datoviz_v04_axis_provider_capability(
        FakeDatovizV04WithAxisTicks()
    )

    assert unsupported.provider_status == "unsupported"
    assert supported.provider_status == "adapted"
    assert supported.supports_backend_auto_ticks
    assert not supported.supports_explicit_ticks
    assert explicit_supported.supports_explicit_ticks
    assert not supported.supports_guide_query
    assert "axis-guide-query-unsupported" in " ".join(supported.diagnostics)
    assert "strict-guide-title-query-unverified" in " ".join(supported.diagnostics)


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
    assert attach_desc.coord_space == 0
    assert attach_desc.clip_rect == 0
    assert attach_desc.viewport_rect == 0


def test_visual_attach_desc_rejects_stale_binding_missing_clip_and_viewport_rect():
    class StaleAttachDesc(ctypes.Structure):
        _fields_ = (
            ("struct_size", ctypes.c_uint32),
            ("flags", ctypes.c_uint32),
            ("z_layer", ctypes.c_int32),
            ("controller_mode", ctypes.c_int),
            ("coord_space", ctypes.c_int),
        )

    def stale_factory():
        desc = StaleAttachDesc()
        desc.struct_size = ctypes.sizeof(StaleAttachDesc)
        desc.controller_mode = 0
        desc.coord_space = 1
        return desc

    fake = SimpleNamespace(
        DvzVisualAttachDesc=StaleAttachDesc,
        dvz_visual_attach_desc=stale_factory,
    )

    with pytest.raises(DatovizV04Unavailable, match="Regenerate Datoviz bindings"):
        _visual_attach_desc(fake, coord_space="data", z_layer=3)


def test_add_point_visual_scales_canvas_pixels_for_resolved_datoviz_framebuffer():
    fake = FakeDatovizV04WithQueryCapabilities()
    canvas_size = CanvasSize.reference_px(320, 240).with_requested_device_scale(2.0)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, canvas_size=canvas_size)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
        sizes=np.array([12.0], dtype=np.float32),
    )

    renderer.add_point_visual(visual)

    assert renderer.resolved_canvas.canvas_width_px == 320.0
    assert renderer.resolved_canvas.framebuffer_width == 640
    assert _calls(fake, "figure") == [("figure", "scene", 640, 480, 0)]
    set_data = _calls(fake, "set_data")
    np.testing.assert_allclose(set_data[2][3], [24.0], rtol=1e-6)


def test_resolved_canvas_from_datoviz_fills_missing_physical_metrics():
    native = SimpleNamespace(
        canvas_width_px=1280.0,
        canvas_height_px=720.0,
        host_logical_width=1280,
        host_logical_height=720,
        framebuffer_width=1280,
        framebuffer_height=720,
        device_scale_x=1.0,
        device_scale_y=1.0,
        canvas_to_host_scale_x=1.0,
        canvas_to_host_scale_y=1.0,
        framebuffer_per_canvas_px_x=1.0,
        framebuffer_per_canvas_px_y=1.0,
        target_width_mm=0.0,
        target_height_mm=0.0,
        estimated_width_mm=0.0,
        estimated_height_mm=0.0,
    )

    resolved = _resolved_canvas_from_datoviz(CanvasSize.pixel_exact(1280, 720), native)

    assert resolved.target_width_mm > 0.0
    assert resolved.estimated_width_mm == resolved.target_width_mm
    assert resolved.target_width_mm == pytest.approx(1280.0 / 96.0 * 25.4)


def test_datoviz_view_size_desc_sets_current_monitor_dpi_override_fields():
    class FakeDatovizWithSizeDesc:
        class Desc:
            monitor_dpi_x_override = 0.0
            monitor_dpi_y_override = 0.0

        def dvz_view_size_desc_reference_px(self, width, height, reference_dpi):
            self.args = (width, height, reference_dpi)
            return self.Desc()

    fake = FakeDatovizWithSizeDesc()
    canvas_size = CanvasSize.reference_px(1280, 720).with_monitor_dpi_override(139.2)

    desc = _datoviz_view_size_desc(fake, canvas_size)

    assert fake.args == (1280, 720, 96.0)
    assert desc is not None
    assert desc.monitor_dpi_x_override == 139.2
    assert desc.monitor_dpi_y_override == 139.2


def test_add_point_visual_retries_current_datoviz_diameter_attribute_name():
    fake = FakeDatovizV04WithCurrentAttributeNames()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[1.0, 0.0, 0.0, 1.0]], dtype=np.float32),
        sizes=np.array([6.0], dtype=np.float32),
    )

    renderer.add_point_visual(visual)

    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == [
        "position",
        "color",
        "diameter_px",
        "diameter",
    ]
    np.testing.assert_allclose(set_data[-1][3], [6.0], rtol=1e-6)


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


def test_add_point_visual_keeps_data_coordinates_with_native_view2d_domain():
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
        [[-8.0, -4.0, 0.0], [0.0, 0.0, 0.0], [8.0, 4.0, 0.0]],
        atol=1e-6,
    )
    assert _calls(fake, "set_domain")[:4] == [
        ("set_domain", "panel", 0, -1.0, 1.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
        ("set_domain", "panel", 0, 10.0, -10.0),
        ("set_domain", "panel", 1, -5.0, 5.0),
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[3].coord_space == 1


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

    color_upload = [call for call in _calls(fake, "set_data") if call[2] == "color"][0]
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


def test_add_segment_visual_retries_current_datoviz_stroke_width_attribute_name():
    fake = FakeDatovizV04WithCurrentAttributeNames()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = SegmentVisual(
        id="visual:segments",
        start_positions=np.array([[0.0, 0.0]], dtype=np.float32),
        end_positions=np.array([[0.5, 0.5]], dtype=np.float32),
        colors=np.array([[1.0, 0.0, 0.0, 1.0]], dtype=np.float32),
        widths=np.array([3.0], dtype=np.float32),
    )

    renderer.add_segment_visual(visual)

    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == [
        "position_start",
        "position_end",
        "color",
        "stroke_width_px",
        "stroke_width",
    ]
    np.testing.assert_allclose(set_data[-1][3], [3.0], rtol=1e-6)


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
    assert _calls(fake, "set_domain") == [
        ("set_domain", "panel", 0, -1.0, 1.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
    ]


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


def test_add_image_visual_renders_when_datoviz_sampler_api_is_absent():
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

    renderer.add_image_visual(visual)

    assert _calls(fake, "image") == [("image", "scene", 0)]
    assert _calls(fake, "set_texture")


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
    assert _calls(fake, "scale_set_domain") == [("scale_set_domain", "scale", 0.0, 1.0)]
    assert _calls(fake, "scale_set_view_range") == [
        ("scale_set_view_range", "scale", 0.0, 1.0)
    ]
    assert _calls(fake, "colormap_builtin") == [("colormap_builtin", "scene", 1)]
    assert _calls(fake, "scale_set_colormap") == [
        ("scale_set_colormap", "scale", "colormap")
    ]
    assert _calls(fake, "colorbar") == [
        (
            "colorbar",
            "panel",
            "scale",
            0,
            1,
            6,
            b"value",
            36.0,
            6.0,
            6.0,
            0,
            2,
            1,
            36.0,
            372.0,
        )
    ]
    assert _calls(fake, "colorbar_set_orientation") == [
        ("colorbar_set_orientation", "colorbar", 0)
    ]
    assert _calls(fake, "colorbar_set_anchor") == [
        ("colorbar_set_anchor", "colorbar", 6)
    ]
    assert _calls(fake, "colorbar_set_format") == [
        ("colorbar_set_format", "colorbar", 2, True)
    ]
    tick_calls = _calls(fake, "colorbar_set_ticks")
    assert len(tick_calls) == 1
    _, colorbar_id, tick_values, tick_labels = tick_calls[0]
    assert colorbar_id == "colorbar"
    np.testing.assert_array_equal(tick_values, np.array([0.0, 0.5, 1.0]))
    assert tick_labels == ("low", "mid", "high")
    assert _calls(fake, "colorbar_set_title") == [
        ("colorbar_set_title", "colorbar", b"value")
    ]
    assert renderer.colorbars[guide.id] == "colorbar"


def test_add_colorbar_guide_scales_style_width_for_datoviz_framebuffer():
    fake = FakeDatovizV04WithColorbar()
    scale = _test_color_scale(colormap_id=ColorMapId.VIRIDIS)
    canvas_size = CanvasSize.reference_px(320, 240).with_requested_device_scale(2.0)
    renderer = DatovizV04ProtocolRenderer(
        dvz=fake,
        color_scales={scale.id: scale},
        canvas_size=canvas_size,
    )
    guide = ColorbarGuide(
        id="guide:colorbar",
        panel_id="panel:main",
        color_scale_id=scale.id,
        style=ColorbarGuideStyle(ramp_width_px=22.0, min_length_px=80.0),
    )

    renderer.add_colorbar_guide(guide)

    colorbar_call = _calls(fake, "colorbar")[0]
    assert colorbar_call[7] == 44.0
    assert colorbar_call[13] == 44.0
    assert colorbar_call[14] == max(160.0, 480.0 * 0.62)


def test_add_colorbar_guide_rejects_missing_explicit_tick_facade():
    fake = FakeDatovizV04WithColorbar()
    fake.dvz_colorbar_set_ticks = None
    scale = _test_color_scale(colormap_id=ColorMapId.VIRIDIS)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, color_scales={scale.id: scale})

    with pytest.raises(DatovizV04Unsupported, match="explicit ticks"):
        renderer.add_colorbar_guide(
            ColorbarGuide(
                id="guide:colorbar",
                panel_id="panel:main",
                color_scale_id=scale.id,
                ticks=(0.0, 1.0),
            )
        )


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


def test_capture_png_bytes_rejects_null_ctypes_app_handle():
    class FakeDatovizV04WithNullApp(FakeDatovizV04WithCapture):
        def dvz_app(self, scene):
            self.calls.append(("app", scene))
            return ctypes.POINTER(ctypes.c_int)()

    fake = FakeDatovizV04WithNullApp()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    with pytest.raises(DatovizV04Unavailable, match="offscreen app creation failed"):
        renderer.capture_png_bytes()

    assert _calls(fake, "view_offscreen") == []


def test_capture_png_bytes_rejects_null_ctypes_offscreen_view_handle():
    class FakeDatovizV04WithNullOffscreenView(FakeDatovizV04WithCapture):
        def dvz_view_offscreen(self, app, figure, width, height):
            self.calls.append(("view_offscreen", app, figure, width, height))
            return ctypes.POINTER(ctypes.c_int)()

    fake = FakeDatovizV04WithNullOffscreenView()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    with pytest.raises(DatovizV04Unavailable, match="offscreen view creation failed"):
        renderer.capture_png_bytes()

    assert _calls(fake, "render_once") == []


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


def test_add_mesh_visual_accepts_default_data_domain_and_requires_view3d_for_data3d():
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
        positions=np.array(
            [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]], dtype=np.float32
        ),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
    )

    renderer.add_mesh_visual(data_visual)
    position_upload = _calls(renderer.dvz, "set_data")[0]
    np.testing.assert_allclose(
        position_upload[3],
        [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]],
    )
    with pytest.raises(
        DatovizV04Unsupported,
        match=View3DDiagnosticCode.MESH3D_REQUIRES_VIEW3D.value,
    ):
        renderer.add_mesh_visual(mesh_3d)


def test_add_mesh_visual_projects_data_positions3d_to_panel_ndc_for_datoviz_mesh():
    fake = FakeDatovizV04WithMesh()
    view3d = View3D(
        id="view:main",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(1.0, 2.0, 3.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(2.0, -2.0),
            ylim=(-1.0, 3.0),
            near_far=(0.1, 100.0),
        ),
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view3d=view3d)
    visual = MeshVisual(
        id="visual:mesh-3d",
        positions=np.array(
            [[0.0, 0.0, 0.0], [0.5, 0.0, 0.25], [0.0, 0.5, 0.5]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 255], dtype=np.uint8),
    )

    renderer.add_mesh_visual(visual)

    assert _calls(fake, "panel_set_camera") == [
        (
            "panel_set_camera",
            "panel",
            (1.0, 2.0, 3.0),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            1,
            0.1,
            100.0,
            4.0,
        )
    ]
    assert _calls(fake, "camera_set_orthographic_bounds") == [
        (
            "camera_set_orthographic_bounds",
            "panel-camera",
            2.0,
            -2.0,
            -1.0,
            3.0,
            0.1,
            100.0,
        )
    ]
    expected_positions = np.array(
        [project_view3d_data_point(view3d, tuple(point)) for point in visual.positions],
        dtype=np.float32,
    )
    np.testing.assert_allclose(
        _calls(fake, "set_data")[0][3],
        expected_positions,
        rtol=1.0e-6,
        atol=1.0e-6,
    )
    assert _calls(fake, "set_depth_test") == [("set_depth_test", "mesh-visual", False)]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[3].coord_space == 0
    assert add_visual_call[3].controller_mode == 1


def test_add_mesh_visual_orders_ndc3_faces_for_adapted_datoviz_depth():
    fake = FakeDatovizV04WithMesh()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = MeshVisual(
        id="visual:mesh-ndc-depth",
        positions=np.array(
            [
                [-0.72, -0.62, 0.0],
                [0.72, -0.62, 0.0],
                [0.0, 0.72, 0.0],
                [-0.58, 0.58, 0.75],
                [0.58, 0.58, 0.75],
                [0.0, -0.74, 0.75],
            ],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.NDC,
        color=np.array([[230, 57, 70, 255], [69, 123, 157, 255]], dtype=np.uint8),
        color_mode=MeshColorMode.FACE,
    )

    renderer.add_mesh_visual(visual)

    set_data = _calls(fake, "set_data")
    expected_positions = np.array(
        [
            [-0.58, 0.58, 0.75],
            [0.58, 0.58, 0.75],
            [0.0, -0.74, 0.75],
            [-0.72, -0.62, 0.0],
            [0.72, -0.62, 0.0],
            [0.0, 0.72, 0.0],
        ],
        dtype=np.float32,
    )
    np.testing.assert_allclose(
        set_data[0][3],
        expected_positions,
        rtol=1.0e-6,
        atol=1.0e-6,
    )
    np.testing.assert_array_equal(
        set_data[1][3],
        np.array(
            [
                [69, 123, 157, 255],
                [69, 123, 157, 255],
                [69, 123, 157, 255],
                [230, 57, 70, 255],
                [230, 57, 70, 255],
                [230, 57, 70, 255],
            ],
            dtype=np.uint8,
        ),
    )
    assert _calls(fake, "set_depth_test") == [("set_depth_test", "mesh-visual", False)]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[3].coord_space == 0
    assert add_visual_call[3].controller_mode == 1


def test_add_mesh_visual_cpu_resolves_s039_flat_lambert_face_colors():
    fake = FakeDatovizV04WithMesh()
    view3d = View3D(
        id="view:main",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 2.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(near_far=(0.0, 4.0)),
        ambient_light_intensity=0.25,
        directional_light=DirectionalLight3D(
            direction_to_light=(0.0, 0.0, 1.0),
            intensity=0.5,
        ),
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view3d=view3d)
    visual = MeshVisual(
        id="visual:mesh-lambert",
        positions=np.array(
            [
                [0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0],
                [0.0, 0.5, 0.0],
                [0.0, 0.0, 0.5],
                [0.0, 0.5, 0.5],
                [0.5, 0.0, 0.5],
            ],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([[200, 100, 50, 255], [40, 80, 120, 255]], dtype=np.uint8),
        color_mode=MeshColorMode.FACE,
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )

    renderer.add_mesh_visual(visual)

    set_data = _calls(fake, "set_data")
    expected_positions = np.array(
        [project_view3d_data_point(view3d, tuple(point)) for point in visual.positions],
        dtype=np.float32,
    )
    np.testing.assert_allclose(set_data[0][3], expected_positions)
    np.testing.assert_array_equal(
        set_data[1][3],
        np.array(
            [
                [150, 75, 38, 255],
                [150, 75, 38, 255],
                [150, 75, 38, 255],
                [10, 20, 30, 255],
                [10, 20, 30, 255],
                [10, 20, 30, 255],
            ],
            dtype=np.uint8,
        ),
    )
    np.testing.assert_array_equal(
        _calls(fake, "set_index_data")[0][2],
        np.arange(6, dtype=np.uint32),
    )
    assert _calls(fake, "set_depth_test") == [("set_depth_test", "mesh-visual", False)]


def test_add_mesh_visual_rejects_s039_flat_lambert_alpha_as_non_strict():
    fake = FakeDatovizV04WithMesh()
    view3d = View3D(
        id="view:main",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 2.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(near_far=(0.0, 4.0)),
        ambient_light_intensity=1.0,
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view3d=view3d)
    visual = MeshVisual(
        id="visual:mesh-lambert-alpha",
        positions=np.array(
            [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.5, 0.0]],
            dtype=np.float32,
        ),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        coordinate_space=CoordinateSpace.DATA,
        color=np.array([255, 255, 255, 128], dtype=np.uint8),
        shading=MeshShading.FLAT_LAMBERT,
        normal_mode=MeshNormalMode.FACE,
        normal_generation=MeshNormalGeneration.FACE_FLAT,
    )

    with pytest.raises(
        DatovizV04Unsupported,
        match=View3DDiagnosticCode.MESH3D_ALPHA_NOT_STRICT.value,
    ):
        renderer.add_mesh_visual(visual)

    assert _calls(fake, "mesh") == []


def test_datoviz_capabilities_advertise_s040_lambert_cpu_resolve_when_view3d_ready():
    caps = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithMesh()).capabilities()

    assert MESH3D_OPAQUE_DEPTH_CAPABILITY not in caps.view3d_capabilities
    assert MESH_MATERIAL_FLAT_LAMBERT_CAPABILITY in caps.view3d_capabilities
    assert MESH_NORMALS_FACE3D_CAPABILITY in caps.view3d_capabilities
    assert MESH_NORMAL_GENERATION_FACE_FLAT_CAPABILITY in caps.view3d_capabilities
    assert VIEW3D_LIGHT_AMBIENT_CAPABILITY in caps.view3d_capabilities
    assert VIEW3D_LIGHT_DIRECTIONAL_CAPABILITY in caps.view3d_capabilities
    assert "flat_lambert_cpu_resolved_strict" in caps.metadata["s040_flat_lambert"]


def test_datoviz_capabilities_do_not_advertise_s040_lambert_without_view3d_binding():
    caps = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).capabilities()

    assert MESH_MATERIAL_FLAT_LAMBERT_CAPABILITY not in caps.view3d_capabilities


def test_add_mesh_visual_keeps_data_coordinates_with_native_view2d_domain():
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
        [[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [0.0, 10.0, 0.0]],
    )
    assert _calls(fake, "set_domain")[:4] == [
        ("set_domain", "panel", 0, -1.0, 1.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
        ("set_domain", "panel", 0, 0.0, 10.0),
        ("set_domain", "panel", 1, 0.0, 10.0),
    ]
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[3].coord_space == 1


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
            0,
            5,
            (-150.0, -75.0, 1.0),
            (0.0, 0.0),
            True,
            0.0,
            False,
        ),
        (
            "text_set_placement",
            "text-2",
            0,
            5,
            (150.0, 75.0, 1.0),
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
    assert _calls(fake, "view_glfw") == [
        ("view_glfw", "app", "figure", 800, 600, b"GSP Datoviz review")
    ]
    assert _calls(fake, "app_run") == [("app_run", "app", 1)]


def test_renderer_enable_native_panzoom_creates_live_view_and_controller():
    fake = FakeDatovizV04WithInteractive()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    panzoom = renderer.enable_native_panzoom()

    assert panzoom == "panzoom"
    assert renderer.native_panzoom == "panzoom"
    assert _calls(fake, "view_glfw") == [
        ("view_glfw", "app", "figure", 800, 600, b"GSP Datoviz review")
    ]
    assert _calls(fake, "panzoom_desc") == [("panzoom_desc",)]
    assert _calls(fake, "view_panzoom") == [
        ("view_panzoom", "live-view", "panel", 800.0, 600.0)
    ]


def test_datoviz_live_input_readiness_requires_correct_binding_layout():
    assert datoviz_v04_live_input_ready(FakeDatovizV04WithInteractive())

    diagnostics = datoviz_v04_live_input_diagnostics(FakeDatovizV04())

    assert "missing DvzInputEventContent" in diagnostics


def test_renderer_enable_gsp_view2d_navigation_subscribes_to_live_pointer_input():
    fake = FakeDatovizV04WithInteractive()
    view = View2D(id="view:main", panel_id="panel:main")
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view=view)

    session = renderer.enable_gsp_view2d_navigation()

    assert session.view == view
    assert _calls(fake, "view_input") == [("view_input", "live-view")]
    assert _calls(fake, "subscribe_event") == [
        ("subscribe_event", "input-router", None)
    ]
    assert fake.input_callback == session.handle_input_event


def test_datoviz_live_pointer_events_apply_retained_gsp_view2d_navigation():
    fake = FakeDatovizV04WithInteractive()
    view = View2D(id="view:main", panel_id="panel:main")
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view=view)
    renderer.enable_gsp_view2d_navigation()
    assert fake.input_callback is not None

    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
        350.0,
        300.0,
        button=fake.DvzPointerButton.DVZ_POINTER_BUTTON_LEFT,
    )
    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_MOVE,
        390.0,
        300.0,
    )
    assert renderer.view == view
    assert _calls(fake, "request_frame") == []

    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG,
        430.0,
        300.0,
    )

    assert renderer.view is not None
    assert renderer.view.x_range == pytest.approx((-1.2, 0.8))
    assert renderer.view.y_range == pytest.approx((-1.0, 1.0))
    assert _calls(fake, "set_domain")[-2:] == [
        ("set_domain", "panel", 0, -1.2, 0.8),
        ("set_domain", "panel", 1, -1.0, 1.0),
    ]
    assert _calls(fake, "request_frame") == [("request_frame", "live-view")]


def test_datoviz_live_right_drag_zooms_view2d_x_and_y_axes():
    fake = FakeDatovizV04WithInteractive()
    view = View2D(id="view:main", panel_id="panel:main")
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view=view)
    renderer.enable_gsp_view2d_navigation()
    assert fake.input_callback is not None

    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
        400.0,
        300.0,
        button=fake.DvzPointerButton.DVZ_POINTER_BUTTON_RIGHT,
    )
    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG,
        440.0,
        270.0,
    )

    expected_factor_x, expected_factor_y = (
        navigation_module._DatovizPanzoomProfile.for_platform().drag_zoom_factor(
            LogicalPixelRect(x=0.0, y=0.0, width=800.0, height=600.0),
            40.0,
            30.0,
        )
    )
    expected_view = zoom_view2d_about(
        view,
        LogicalPixelRect(x=0.0, y=0.0, width=800.0, height=600.0),
        (400.0, 300.0),
        expected_factor_x,
        expected_factor_y,
    )

    assert renderer.view is not None
    assert renderer.view.x_range == pytest.approx(expected_view.x_range)
    assert renderer.view.y_range == pytest.approx(expected_view.y_range)
    x_domain, y_domain = _calls(fake, "set_domain")[-2:]
    assert x_domain[:3] == ("set_domain", "panel", 0)
    assert y_domain[:3] == ("set_domain", "panel", 1)
    assert x_domain[3:] == pytest.approx(expected_view.x_range)
    assert y_domain[3:] == pytest.approx(expected_view.y_range)
    assert _calls(fake, "request_frame") == [("request_frame", "live-view")]


def test_datoviz_live_double_click_resets_to_home_view2d():
    fake = FakeDatovizV04WithInteractive()
    view = View2D(id="view:main", panel_id="panel:main")
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view=view)
    renderer.enable_gsp_view2d_navigation()
    assert fake.input_callback is not None

    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
        350.0,
        300.0,
        button=fake.DvzPointerButton.DVZ_POINTER_BUTTON_LEFT,
    )
    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG,
        430.0,
        300.0,
    )
    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_DOUBLE_CLICK,
        430.0,
        300.0,
    )

    assert renderer.view == view
    assert _calls(fake, "set_domain")[-2:] == [
        ("set_domain", "panel", 0, -1.0, 1.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
    ]
    assert _calls(fake, "request_frame") == [
        ("request_frame", "live-view"),
        ("request_frame", "live-view"),
    ]


def test_datoviz_live_pointer_y_coordinates_are_converted_from_window_origin():
    fake = FakeDatovizV04WithInteractive()
    renderer = DatovizV04ProtocolRenderer(
        dvz=fake, view=View2D(id="view:main", panel_id="panel:main")
    )
    renderer.enable_gsp_view2d_navigation()
    assert fake.input_callback is not None

    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
        350.0,
        300.0,
        button=fake.DvzPointerButton.DVZ_POINTER_BUTTON_LEFT,
    )
    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG,
        350.0,
        240.0,
    )

    assert renderer.view is not None
    assert renderer.view.x_range == pytest.approx((-1.0, 1.0))
    assert renderer.view.y_range == pytest.approx((-1.2, 0.8))


def test_datoviz_live_resize_updates_navigation_panel_rect_and_refreshes_axes():
    fake = FakeDatovizV04WithInteractiveAxes()
    view = View2D(id="view:main", panel_id="panel:main")
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    renderer.configure_view2d_axes(view, x_label="x", y_label="y", grid=True)
    session = renderer.enable_gsp_view2d_navigation(view)
    baseline_call_count = len(fake.calls)

    _emit_fake_datoviz_resize(fake, window_width=1600, window_height=1200)

    assert session.panel_rect == LogicalPixelRect(
        x=0.0, y=0.0, width=1600.0, height=1200.0
    )
    assert session.adapter.panel_rect == session.panel_rect
    resize_calls = fake.calls[baseline_call_count:]
    assert _calls_from(resize_calls, "clear_ticks") == [
        ("clear_ticks", "axis:0"),
        ("clear_ticks", "axis:1"),
    ]
    assert _calls_from(resize_calls, "set_tick_policy") == [
        ("set_tick_policy", "axis:0", "tick-policy"),
        ("set_tick_policy", "axis:1", "tick-policy"),
    ]
    assert _calls_from(resize_calls, "request_frame") == [
        ("request_frame", "live-view")
    ]

    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
        800.0,
        600.0,
        button=fake.DvzPointerButton.DVZ_POINTER_BUTTON_LEFT,
        window_size=(1600.0, 1200.0),
    )
    _emit_fake_datoviz_pointer(
        fake,
        fake.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG,
        960.0,
        600.0,
        window_size=(1600.0, 1200.0),
    )

    assert renderer.view is not None
    assert renderer.view.x_range == pytest.approx((-1.2, 0.8))
    assert renderer.view.y_range == pytest.approx((-1.0, 1.0))


def test_datoviz_live_scale_refreshes_axes_without_changing_panel_rect_or_view():
    fake = FakeDatovizV04WithInteractiveAxes()
    view = View2D(id="view:main", panel_id="panel:main")
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    renderer.configure_view2d_axes(view, x_label="x", y_label="y", grid=True)
    session = renderer.enable_gsp_view2d_navigation(view)
    baseline_rect = session.panel_rect
    baseline_call_count = len(fake.calls)

    _emit_fake_datoviz_scale(fake, content_scale_x=2.0, content_scale_y=2.0)

    assert session.panel_rect == baseline_rect
    assert renderer.view == view
    scale_calls = fake.calls[baseline_call_count:]
    assert _calls_from(scale_calls, "clear_ticks") == [
        ("clear_ticks", "axis:0"),
        ("clear_ticks", "axis:1"),
    ]
    assert _calls_from(scale_calls, "request_frame") == [
        ("request_frame", "live-view")
    ]


def test_datoviz_live_navigation_unsubscribes_on_close():
    fake = FakeDatovizV04WithInteractive()

    with DatovizV04ProtocolRenderer(
        dvz=fake, view=View2D(id="view:main", panel_id="panel:main")
    ) as renderer:
        renderer.enable_gsp_view2d_navigation()

    assert _calls(fake, "unsubscribe_event")
    assert fake.input_callback is None


def test_datoviz_view3d_live_navigation_reports_cpu_projected_mesh_boundary():
    fake = FakeDatovizV04WithMesh()
    view3d = _canonical_view3d_for_datoviz_query()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, view3d=view3d)

    diagnostics = datoviz_v04_view3d_live_navigation_diagnostics(fake)

    assert any("CPU-projected panel-NDC mesh positions" in item for item in diagnostics)
    with pytest.raises(DatovizV04Unavailable, match="CPU-projected panel-NDC"):
        renderer.enable_gsp_view3d_navigation()


def test_renderer_show_uses_resolved_host_logical_size_for_reference_canvas():
    fake = FakeDatovizV04WithInteractive()
    canvas_size = CanvasSize.reference_px(320, 240).with_requested_device_scale(2.0)
    renderer = DatovizV04ProtocolRenderer(dvz=fake, canvas_size=canvas_size)

    renderer.show(frame_count=1)

    assert _calls(fake, "view_glfw") == [
        ("view_glfw", "app", "figure", 320, 240, b"GSP Datoviz review")
    ]


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
        ("set_domain", "panel", 0, -1.0, 1.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
        ("set_domain", "panel", 0, -1.0, 2.0),
        ("set_domain", "panel", 1, -3.0, 4.0),
    ]
    view_call = _calls(fake, "set_view2d")[-1]
    panel_view = view_call[2]
    assert view_call[:2] == ("set_view2d", "panel")
    assert panel_view.padding == 0.0
    assert renderer.last_view2d_carrier_diagnostics == {
        "datoviz_view2d_carrier": "dvz_panel_set_domain+DvzPanelView2D policy",
        "ordered_ranges_preserved": True,
        "reversed_x": False,
        "reversed_y": False,
        "legacy_panel_domain_sync": True,
        "datoviz_visible_domain_readback": "available",
        "datoviz_transform_point": "available",
    }
    assert _calls(fake, "panel_axis") == [
        ("panel_axis", "panel", 0),
        ("panel_axis", "panel", 1),
    ]
    assert _calls(fake, "set_style") == [
        (
            "set_style",
            "axis:0",
            1.75,
            1.5,
            7.0,
            15.0,
            17.0,
            0.08,
            (32, 32, 32, 255),
            (32, 32, 32, 255),
            (150, 150, 150, 190),
            True,
        ),
        (
            "set_style",
            "axis:1",
            1.75,
            1.5,
            7.0,
            15.0,
            17.0,
            0.08,
            (32, 32, 32, 255),
            (32, 32, 32, 255),
            (150, 150, 150, 190),
            True,
        ),
    ]
    assert _calls(fake, "set_plot_margins") == [
        ("set_plot_margins", "axis:0", 0.0, 0.0, 0.0, 0.08),
        ("set_plot_margins", "axis:1", 0.0, 0.0, 0.0, 0.08),
    ]
    assert _calls(fake, "clear_ticks") == [
        ("clear_ticks", "axis:0"),
        ("clear_ticks", "axis:1"),
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
        ("set_label", "axis:0", b"x"),
        ("set_label", "axis:1", b"y"),
    ]


def test_configure_view2d_axes_keeps_data_visuals_in_native_data_coordinates():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    renderer.configure_view2d_axes(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(-2.5, 2.5),
            y_range=(0.0, 2.0),
        )
    )
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[-2.5, 0.0], [0.0, 1.0], [2.5, 2.0]], dtype=np.float32),
        colors=np.repeat(np.array([[255, 255, 255, 255]], dtype=np.uint8), 3, axis=0),
        sizes=np.array([6.0, 6.0, 6.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )

    renderer.add_point_visual(visual)

    position_upload = _calls(fake, "set_data")[0]
    assert position_upload[2] == "position"
    np.testing.assert_allclose(
        position_upload[3],
        [[-2.5, 0.0, 0.0], [0.0, 1.0, 0.0], [2.5, 2.0, 0.0]],
    )
    add_visual_call = _calls(fake, "add_visual")[-1]
    assert add_visual_call[3].coord_space == 1


def test_retained_view2d_navigation_with_axes_does_not_reupload_data_points():
    fake = FakeDatovizV04WithAxes()
    initial_view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(-2.5, 2.5),
        y_range=(0.0, 2.0),
    )
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    renderer.configure_view2d_axes(initial_view)
    renderer.add_point_visual(
        PointVisual(
            id="visual:points",
            positions=np.array([[0.0, 1.0]], dtype=np.float32),
            colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
            sizes=np.array([6.0], dtype=np.float32),
            coordinate_space=CoordinateSpace.DATA,
        )
    )
    baseline_call_count = len(fake.calls)

    renderer.apply_retained_view2d_navigation(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(-5.0, 5.0),
            y_range=(0.0, 4.0),
        )
    )

    new_calls = fake.calls[baseline_call_count:]
    assert _calls_from(new_calls, "set_domain") == [
        ("set_domain", "panel", 0, -5.0, 5.0),
        ("set_domain", "panel", 1, 0.0, 4.0),
    ]
    assert _calls_from(new_calls, "set_view2d")
    assert _calls_from(new_calls, "clear_ticks") == [
        ("clear_ticks", "axis:0"),
        ("clear_ticks", "axis:1"),
    ]
    assert _calls_from(new_calls, "set_tick_policy") == [
        ("set_tick_policy", "axis:0", "tick-policy"),
        ("set_tick_policy", "axis:1", "tick-policy"),
    ]
    assert _calls_from(new_calls, "set_grid") == [
        ("set_grid", "axis:0", False),
        ("set_grid", "axis:1", False),
    ]
    assert not _calls_from(new_calls, "set_data")
    assert not _calls_from(new_calls, "point")
    assert not _calls_from(new_calls, "add_visual")


def test_adapted_cpu_remap_navigation_reuploads_derived_data_points():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    renderer.configure_view2d_axes(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(-2.5, 2.5),
            y_range=(0.0, 2.0),
        )
    )
    renderer._cpu_map_data_visuals_to_view = True
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 1.0]], dtype=np.float32),
        colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
        sizes=np.array([6.0], dtype=np.float32),
        coordinate_space=CoordinateSpace.DATA,
    )
    renderer.add_point_visual(visual)
    baseline_call_count = len(fake.calls)

    renderer.apply_adapted_view2d_navigation_cpu_remap(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(-5.0, 5.0),
            y_range=(0.0, 4.0),
        )
    )

    new_calls = fake.calls[baseline_call_count:]
    assert _calls_from(new_calls, "set_domain") == [
        ("set_domain", "panel", 0, -5.0, 5.0),
        ("set_domain", "panel", 1, 0.0, 4.0),
    ]
    position_upload = _calls_from(new_calls, "set_data")[0]
    assert position_upload[2] == "position"
    np.testing.assert_allclose(position_upload[3], [[0.0, -0.5, 0.0]])


def test_apply_datoviz_data_view2d_preserves_reversed_ordered_endpoints():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    panel_view = renderer.apply_datoviz_data_view2d(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(1.0, -1.0),
            y_range=(2.0, -2.0),
        )
    )

    assert _calls(fake, "set_domain") == [
        ("set_domain", "panel", 0, -1.0, 1.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
        ("set_domain", "panel", 0, 1.0, -1.0),
        ("set_domain", "panel", 1, 2.0, -2.0),
    ]
    assert _calls(fake, "set_view2d")[-1] == ("set_view2d", "panel", panel_view)
    assert renderer.last_view2d_carrier_diagnostics == {
        "datoviz_view2d_carrier": "dvz_panel_set_domain+DvzPanelView2D policy",
        "ordered_ranges_preserved": True,
        "reversed_x": True,
        "reversed_y": True,
        "legacy_panel_domain_sync": True,
        "datoviz_visible_domain_readback": "available",
        "datoviz_transform_point": "available",
    }


def test_apply_datoviz_data_view2d_calls_legacy_domain_sync_before_view2d_setter():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    baseline_call_count = len(fake.calls)

    renderer.apply_datoviz_data_view2d(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(-2.0, 2.0),
            y_range=(-1.0, 1.0),
        )
    )

    new_calls = fake.calls[baseline_call_count:]
    assert [call[0] for call in new_calls] == [
        "set_domain",
        "set_domain",
        "view2d",
        "set_view2d",
    ]
    assert new_calls[:2] == [
        ("set_domain", "panel", 0, -2.0, 2.0),
        ("set_domain", "panel", 1, -1.0, 1.0),
    ]
    assert new_calls[-1][2].padding == 0.0


def test_apply_datoviz_data_view2d_populates_descriptor_domains_when_available():
    fake = FakeDatovizV04WithDescriptorDomains()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    panel_view = renderer.apply_datoviz_data_view2d(
        View2D(
            id="view:main",
            panel_id="panel:main",
            x_range=(1.0, -1.0),
            y_range=(2.0, -2.0),
        )
    )

    assert panel_view.data_x.min == 1.0
    assert panel_view.data_x.max == -1.0
    assert panel_view.data_y.min == 2.0
    assert panel_view.data_y.max == -2.0
    assert renderer.last_view2d_carrier_diagnostics["datoviz_view2d_carrier"] == (
        "DvzPanelView2D.data_x/data_y"
    )


def test_datoviz_axis_symbol_report_includes_latest_readback_helpers():
    symbols = datoviz_v04_axis_symbols(FakeDatovizV04WithAxisTicks())

    assert symbols["dvz_panel_view2d"]
    assert symbols["dvz_panel_set_view2d"]
    assert symbols["dvz_panel_set_domain"]
    assert symbols["dvz_panel_visible_domain"]
    assert symbols["dvz_panel_transform_point"]
    assert symbols["dvz_axis_set_ticks"]


def test_configure_view2d_axes_rejects_unavailable_axis_symbols():
    with pytest.raises(DatovizV04Unavailable, match="missing v0.4-dev axis symbols"):
        DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).configure_view2d_axes(
            View2D(id="view:main", panel_id="panel:main")
        )


def test_configure_view2d_axes_adapts_explicit_ticks_to_backend_policy_when_tick_binding_is_absent():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    renderer.configure_view2d_axes(
        View2D(id="view:main", panel_id="panel:main"),
        backend_auto_ticks=False,
        x_tick_values=(0.0, 1.0),
    )

    assert _calls(fake, "set_ticks") == []
    assert _calls(fake, "clear_ticks") == []
    assert _calls(fake, "set_tick_policy") == [
        ("set_tick_policy", "axis:0", "tick-policy"),
        ("set_tick_policy", "axis:1", "tick-policy"),
    ]


def test_configure_view2d_axes_wires_explicit_ticks_when_binding_is_available():
    fake = FakeDatovizV04WithAxisTicks()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    renderer.configure_view2d_axes(
        View2D(id="view:main", panel_id="panel:main"),
        backend_auto_ticks=False,
        x_tick_values=(1.0, 0.0, -1.0),
        x_tick_labels=("right", "center", "left"),
        y_tick_values=(1.0, -1.0),
        y_tick_labels=("top", "bottom"),
    )

    assert _calls(fake, "set_ticks") == [
        ("set_ticks", "axis:0", (1.0, 0.0, -1.0), (b"right", b"center", b"left")),
        ("set_ticks", "axis:1", (1.0, -1.0), (b"top", b"bottom")),
    ]


def test_imported_datoviz_binding_has_expected_v04_shape_when_available():
    dvz = pytest.importorskip("datoviz")
    if not is_datoviz_v04_facade(dvz):
        pytest.skip("installed Datoviz binding is not the v0.4 facade")

    assert is_datoviz_v04_facade(dvz)


def test_imported_datoviz_binding_exposes_view2d_and_axis_tick_contract_when_available():
    dvz = pytest.importorskip("datoviz")
    required = (
        "dvz_panel_set_domain",
        "dvz_panel_view2d",
        "dvz_panel_set_view2d",
        "dvz_panel_visible_domain",
        "dvz_panel_transform_point",
        "dvz_axis_set_ticks",
    )
    missing = [name for name in required if not hasattr(dvz, name)]
    if missing:
        pytest.skip(f"installed Datoviz binding is missing latest symbols: {missing}")

    panel_view = dvz.dvz_panel_view2d()
    descriptor_fields_present = True
    for field_name, expected in (
        ("data_x", (1.0, -1.0)),
        ("data_y", (2.0, -2.0)),
    ):
        domain = getattr(panel_view, field_name, None)
        if domain is None:
            descriptor_fields_present = False
            continue
        assert hasattr(domain, "min")
        assert hasattr(domain, "max")
        domain.min = expected[0]
        domain.max = expected[1]
        assert domain.min == expected[0]
        assert domain.max == expected[1]
    if not descriptor_fields_present:
        assert hasattr(dvz, "dvz_panel_set_domain")
    if hasattr(panel_view, "padding"):
        panel_view.padding = 0.0
        assert panel_view.padding == 0.0

    signature = inspect.signature(dvz.dvz_axis_set_ticks)
    assert tuple(signature.parameters) == ("axis", "values", "labels")
    assert signature.parameters["labels"].default is None


def test_imported_datoviz_binding_exposes_live_input_contract_when_available():
    dvz = pytest.importorskip("datoviz")
    if not is_datoviz_v04_facade(dvz):
        pytest.skip("installed Datoviz binding is not the v0.4 facade")

    diagnostics = datoviz_v04_live_input_diagnostics(dvz)

    assert diagnostics == ()


def test_imported_datoviz_union_input_stream_drives_live_view2d_navigation_when_available():
    dvz = pytest.importorskip("datoviz")
    required = (
        "dvz_input_router",
        "dvz_input_router_destroy",
        "dvz_input_subscribe_event",
        "dvz_input_emit_event",
        "DvzInputEvent",
        "DvzInputEventType",
        "DvzPointerEventType",
        "DvzPointerButton",
    )
    missing = [name for name in required if not hasattr(dvz, name)]
    if missing:
        pytest.skip(f"installed Datoviz binding is missing input symbols: {missing}")

    class DvzWithoutRequestFrame:
        def __init__(self, raw_dvz):
            self.raw_dvz = raw_dvz

        def __getattr__(self, name):
            if name == "dvz_view_request_frame":
                raise AttributeError(name)
            return getattr(self.raw_dvz, name)

    class RendererRecorder:
        def __init__(self, raw_dvz):
            self.dvz = DvzWithoutRequestFrame(raw_dvz)
            self.resolved_canvas = SimpleNamespace(
                host_logical_width=800,
                host_logical_height=600,
            )
            self.view = None
            self.applied_views = []
            self.axis_updates = []

        def apply_retained_view2d_navigation(self, view):
            self.view = view
            self.applied_views.append(view)
            return None

        def update_view2d_axes(self, view):
            self.axis_updates.append(view)

    def emit_pointer(router, event_type, x, y, *, button=None, wheel_y=0.0):
        input_event = dvz.DvzInputEvent()
        input_event.type = dvz.DvzInputEventType.DVZ_INPUT_EVENT_POINTER
        pointer = input_event.content.pointer
        pointer.type = event_type
        pointer.pos[0] = float(x)
        pointer.pos[1] = float(y)
        pointer.window_size[0] = 800.0
        pointer.window_size[1] = 600.0
        pointer.button = (
            int(button)
            if button is not None
            else int(dvz.DvzPointerButton.DVZ_POINTER_BUTTON_NONE)
        )
        pointer.content.w.dir[1] = float(wheel_y)
        dvz.dvz_input_emit_event(router, input_event)

    view = View2D(id="view:main", panel_id="panel:main")
    renderer = RendererRecorder(dvz)
    router = dvz.dvz_input_router()
    try:
        session = _DatovizLiveView2DNavigation(
            renderer=renderer,
            router=router,
            live_view=None,
            view=view,
            controller_id="nav:datoviz-live",
            layout_snapshot_id="layout:datoviz-live",
        )
        dvz.dvz_input_subscribe_event(router, session.handle_input_event, None)

        emit_pointer(
            router,
            dvz.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
            350.0,
            300.0,
            button=dvz.DvzPointerButton.DVZ_POINTER_BUTTON_LEFT,
        )
        emit_pointer(
            router, dvz.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG, 430.0, 300.0
        )
        assert renderer.applied_views[-1].x_range == pytest.approx((-1.2, 0.8))

        emit_pointer(
            router,
            dvz.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG_STOP,
            430.0,
            300.0,
        )
        emit_pointer(
            router,
            dvz.DvzPointerEventType.DVZ_POINTER_EVENT_PRESS,
            400.0,
            300.0,
            button=dvz.DvzPointerButton.DVZ_POINTER_BUTTON_RIGHT,
        )
        emit_pointer(
            router, dvz.DvzPointerEventType.DVZ_POINTER_EVENT_DRAG, 440.0, 270.0
        )
        right_drag_view = renderer.applied_views[-1]
        assert right_drag_view.x_range != pytest.approx((-1.2, 0.8))

        emit_pointer(
            router,
            dvz.DvzPointerEventType.DVZ_POINTER_EVENT_WHEEL,
            460.0,
            315.0,
            wheel_y=1.0,
        )
        assert renderer.applied_views[-1] != right_drag_view

        emit_pointer(
            router,
            dvz.DvzPointerEventType.DVZ_POINTER_EVENT_DOUBLE_CLICK,
            460.0,
            315.0,
        )
        assert renderer.applied_views[-1] == view
        session.close()
    finally:
        dvz.dvz_input_router_destroy(router)


def test_import_datoviz_v04_wraps_facade_load_runtime_error(monkeypatch):
    class ExplodingDatoviz(types.ModuleType):
        def __getattr__(self, name):
            raise RuntimeError("unable to load libdatoviz")

    monkeypatch.setitem(sys.modules, "datoviz", ExplodingDatoviz("datoviz"))

    with pytest.raises(DatovizV04Unavailable, match="Datoviz is not importable"):
        import_datoviz_v04()


def test_imported_datoviz_capability_snapshot_translates_when_available():
    dvz = pytest.importorskip("datoviz")
    if not hasattr(dvz, "dvz_capability_snapshot"):
        pytest.skip("installed Datoviz binding does not expose dvz_capability_snapshot")

    caps = gsp_capability_snapshot_from_datoviz(dvz.dvz_capability_snapshot(), dvz=dvz)

    assert caps.server_name == "datoviz-v0.4-protocol-slice"
    assert "datoviz_raw_capabilities" in caps.metadata
    expected_modes: tuple[str, ...] = ()
    if datoviz_v04_query_binding_ready(dvz):
        expected_modes = ("panel-query", "point-item", "image-texel")
    if not datoviz_v04_view3d_camera_diagnostics(dvz):
        expected_modes = (*expected_modes, "view3d-ray")
    assert caps.query_modes == expected_modes


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


def _write_datoviz_grid_clip_source(root: Path) -> Path:
    source = root / "datoviz-source"
    (source / "datoviz").mkdir(parents=True)
    (source / "datoviz" / "__init__.py").write_text("", encoding="utf-8")
    axis_visual = source / "src" / "scene" / "annotation" / "axis_visual.c"
    axis_visual.parent.mkdir(parents=True)
    axis_visual.write_text(
        "\n".join(
            (
                "source_x0 = _axis_inverse_panzoom_coord(extent, 0, 1, x0);",
                "source_x1 = _axis_inverse_panzoom_coord(extent, 0, 1, x1);",
                "source_y0 = _axis_inverse_panzoom_coord(extent, 2, 3, y0);",
                "source_y1 = _axis_inverse_panzoom_coord(extent, 2, 3, y1);",
            )
        ),
        encoding="utf-8",
    )
    axis_tests = source / "src" / "scene" / "tests" / "axis.c"
    axis_tests.parent.mkdir(parents=True)
    axis_tests.write_text("test_axis_grid_uses_style_plot_margins", encoding="utf-8")
    return source


def _test_color_scale(*, colormap_id: ColorMapId = ColorMapId.VIRIDIS) -> ColorScale:
    return ColorScale(
        id=f"scale:{colormap_id.value}",
        colormap=ColorMapRef(colormap_id),
        normalize=LinearNormalize(vmin=0.0, vmax=1.0),
    )
