"""Tests for the bounded Datoviz v0.4 protocol adapter slice."""

from __future__ import annotations

import ctypes

import numpy as np
import pytest

from gsp.protocol import ImageOrigin, ImageVisual, PointVisual
from gsp.protocol import (
    AxisProviderRequest,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryScope,
    QueryStatus,
    View2D,
    VisualFamily,
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
    datoviz_v04_sampled_field_diagnostics,
    datoviz_v04_sampled_field_ready,
    is_datoviz_v04_facade,
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

    def dvz_point(self, scene, flags):
        self.calls.append(("point", scene, flags))
        return "point-visual"

    def dvz_image(self, scene, flags):
        self.calls.append(("image", scene, flags))
        return "image-visual"

    def dvz_visual_set_data(self, visual, name, data):
        self.calls.append(("set_data", visual, name, np.array(data, copy=True)))
        return 0

    def dvz_visual_set_texture(self, visual, pixels, width, height):
        self.calls.append(("set_texture", visual, np.array(pixels, copy=True), width, height))
        return 0

    def dvz_panel_add_visual(self, panel, visual, attach_desc):
        self.calls.append(("add_visual", panel, visual, attach_desc))
        return 0

    def dvz_scene_destroy(self, scene):
        self.calls.append(("destroy", scene))
        self.destroyed = True


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


class FakeDatovizV04WithQueryCapabilities(FakeDatovizV04):
    def dvz_visual_set_query_capabilities(self, visual, capabilities):
        self.calls.append(("set_query_capabilities", visual, capabilities))
        return None


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


def _calls(fake, name):
    return [call for call in fake.calls if call[0] == name]


def test_capability_snapshot_defers_query_support():
    caps = gsp_capability_snapshot_from_datoviz(None, dvz=None, source="static-gsp-slice")

    assert caps.server_name == "datoviz-v0.4-protocol-slice"
    assert caps.visual_families == ("point", "image")
    assert caps.texture_formats == ("rgba8",)
    assert caps.query_modes == ()
    assert caps.metadata["datoviz_api"] == "v0.4 dvz_* facade"
    assert caps.axis_providers[0].provider_id == DATOVIZ_V04_AXIS_PROVIDER


def test_datoviz_capability_translation_preserves_raw_fields_without_overclaiming_query_support():
    caps = gsp_capability_snapshot_from_datoviz(FakeDvzCapabilitySnapshot(), dvz=FakeDatovizV04WithAxes())

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
    promoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithCapture()).capabilities()
    unpromoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).capabilities()

    assert datoviz_v04_capture_ready(FakeDatovizV04WithCapture())
    assert promoted.output_formats == ("png",)
    assert promoted.metadata["capture_support"] == "offscreen PNG screenshot/export; not scientific readback"
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
    assert "DvzQueryResult" in " ".join(datoviz_v04_query_binding_diagnostics(incomplete))


def test_datoviz_capabilities_promote_panel_query_only_when_query_binding_is_ready():
    promoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithQuery()).capabilities()
    unpromoted = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithCapabilities()).capabilities()

    assert promoted.query_modes == ("panel-query", "point-item", "image-texel")
    assert promoted.supports_query_scope(QueryScope.DATA)
    assert promoted.adapt_query_request(
        QueryRequest(
            id="query:datoviz",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            coordinate_space=QueryCoordinateSpace.PANEL,
        )
    ).outcome.value == "accept"
    assert "datoviz_query_binding_diagnostics" not in promoted.metadata
    assert unpromoted.query_modes == ()
    assert "datoviz_query_binding_diagnostics" in unpromoted.metadata


def test_decode_datoviz_query_statuses_to_gsp_statuses():
    assert decode_dvz_query_result(FakeDvzQueryResult(status=DVZ_QUERY_STATUS_MISS)).status == QueryStatus.MISS
    assert (
        decode_dvz_query_result(FakeDvzQueryResult(status=DVZ_QUERY_STATUS_OUTSIDE_PANEL)).status
        == QueryStatus.OUTSIDE_PANEL
    )
    assert (
        decode_dvz_query_result(FakeDvzQueryResult(status=DVZ_QUERY_STATUS_NO_CAPABLE_VISUAL)).status
        == QueryStatus.UNSUPPORTED
    )
    assert (
        decode_dvz_query_result(FakeDvzQueryResult(status=DVZ_QUERY_STATUS_STALE_DROPPED)).status
        == QueryStatus.DROPPED
    )
    assert decode_dvz_query_result(FakeDvzQueryResult(status=DVZ_QUERY_STATUS_DECODE_FAILED)).status == QueryStatus.FAILED


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
    assert result.diagnostic == "Datoviz query produced no resolved result during bounded poll"


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
    assert names.index("panel_query") < names.index("view_render_once") < names.index("scene_poll_query")
    assert _calls(fake, "view_offscreen") == [("view_offscreen", "app", "figure", 64, 64)]


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
    data_coordinates = renderer.query_panel(QueryRequest(id="query:data", panel_id="panel:main", coordinate=(0.0, 0.0)))

    assert guides.status == QueryStatus.UNSUPPORTED
    assert "data scope only" in str(guides.diagnostic)
    assert all_hits.status == QueryStatus.UNSUPPORTED
    assert "frontmost" in str(all_hits.diagnostic)
    assert data_coordinates.status == QueryStatus.UNSUPPORTED
    assert "panel coordinates" in str(data_coordinates.diagnostic)


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


def test_capability_snapshot_selects_datoviz_axis_provider_when_facade_exposes_symbols():
    renderer = DatovizV04ProtocolRenderer(dvz=FakeDatovizV04WithAxes())
    provider = renderer.capabilities().select_axis_provider(AxisProviderRequest(policy="prefer_native", tick_authority="backend_resolved"))

    assert provider is not None
    assert provider.provider_id == DATOVIZ_V04_AXIS_PROVIDER


def test_add_point_visual_uses_dvz_point_attributes_and_diameter_pixels():
    fake = FakeDatovizV04WithQueryCapabilities()
    renderer = DatovizV04ProtocolRenderer(dvz=fake, width=320, height=240)
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[-0.5, 0.25], [0.5, -0.25]], dtype=np.float32),
        colors=np.array([[1.0, 0.0, 0.0, 1.0], [0.0, 0.5, 1.0, 0.5]], dtype=np.float32),
        sizes=np.array([np.pi, 4.0 * np.pi], dtype=np.float32),
    )

    dvz_visual = renderer.add_point_visual(visual)

    assert dvz_visual == "point-visual"
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "color", "diameter"]
    np.testing.assert_allclose(set_data[0][3], [[-0.5, 0.25, 0.0], [0.5, -0.25, 0.0]])
    np.testing.assert_array_equal(set_data[1][3], [[255, 0, 0, 255], [0, 128, 255, 128]])
    np.testing.assert_allclose(set_data[2][3], [2.0, 4.0], rtol=1e-6)
    assert _calls(fake, "set_query_capabilities") == [("set_query_capabilities", "point-visual", 0x02)]
    assert _calls(fake, "add_visual")[-1] == ("add_visual", "panel", "point-visual", None)


def test_add_image_visual_uses_texture_convenience_path_and_origin_texcoords():
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

    dvz_visual = renderer.add_image_visual(visual)

    assert dvz_visual == "image-visual"
    set_data = _calls(fake, "set_data")
    assert [call[2] for call in set_data] == ["position", "texcoords"]
    np.testing.assert_allclose(
        set_data[0][3],
        [[-1.0, -0.5, 0.0], [-1.0, 0.5, 0.0], [1.0, -0.5, 0.0], [1.0, 0.5, 0.0]],
    )
    np.testing.assert_allclose(set_data[1][3], [[0.0, 1.0], [0.0, 0.0], [1.0, 1.0], [1.0, 0.0]])

    texture_call = _calls(fake, "set_texture")[0]
    assert texture_call[3:] == (2, 2)
    assert texture_call[2].shape == (2, 2, 4)
    np.testing.assert_array_equal(texture_call[2][:, :, 3], 255)
    assert _calls(fake, "set_query_capabilities") == [("set_query_capabilities", "image-visual", 0x12)]


def test_add_image_visual_uses_sampled_field_path_when_available():
    fake = FakeDatovizV04WithSampledFields()
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

    assert datoviz_v04_sampled_field_ready(fake)
    assert _calls(fake, "set_texture") == []
    sampled_call = _calls(fake, "sampled_field")[0]
    desc = sampled_call[2]
    assert desc.dim == 0
    assert desc.format == 22
    assert desc.semantic == 4
    assert desc.color_role == 1
    assert (desc.width, desc.height, desc.depth) == (2, 2, 1)
    upload_view = _calls(fake, "sampled_field_set_data")[0][2]
    assert upload_view.bytes_per_row == 8
    assert upload_view.rows_per_image == 2
    assert upload_view.data.shape == (2, 2, 4)
    assert _calls(fake, "set_field") == [("set_field", "image-visual", "field", "sampled-field")]
    assert renderer.sampled_fields["visual:image"] == "sampled-field"


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
    assert _calls(fake, "view_offscreen") == [("view_offscreen", "app", "figure", 320, 240)]
    assert _calls(fake, "render_once") == [("render_once", "app")]
    capture_calls = _calls(fake, "capture_png")
    assert capture_calls[0][1] == "offscreen-view"
    assert capture_calls[0][2].endswith(".png")


def test_capture_png_bytes_rejects_missing_capture_binding():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    assert not datoviz_v04_capture_ready(fake)
    assert "dvz_view_capture_png" in " ".join(datoviz_v04_capture_diagnostics(fake))
    with pytest.raises(DatovizV04Unavailable, match="offscreen PNG capture is unavailable"):
        renderer.capture_png_bytes()


def test_lower_origin_texcoords_are_not_flipped():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)
    visual = ImageVisual(
        id="visual:image",
        image=np.zeros((1, 1, 4), dtype=np.uint8),
        extent=(0.0, 1.0, 0.0, 1.0),
        origin=ImageOrigin.LOWER,
    )

    renderer.add_image_visual(visual)

    texcoords = _calls(fake, "set_data")[1][3]
    np.testing.assert_allclose(texcoords, [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])


def test_image_slice_rejects_unlocked_semantics():
    fake = FakeDatovizV04()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    with pytest.raises(DatovizV04Unsupported, match="uint8 RGB/RGBA"):
        renderer.add_image_visual(
            ImageVisual(
                id="visual:float-image",
                image=np.zeros((2, 2), dtype=np.float32),
                extent=(0.0, 1.0, 0.0, 1.0),
            )
        )

    with pytest.raises(DatovizV04Unsupported, match="interpolation"):
        renderer.add_image_visual(
            ImageVisual(
                id="visual:linear-image",
                image=np.zeros((2, 2, 4), dtype=np.uint8),
                extent=(0.0, 1.0, 0.0, 1.0),
                interpolation=ImageInterpolation.LINEAR,
            )
        )

    with pytest.raises(DatovizV04Unsupported, match="NDC point"):
        renderer.add_point_visual(
            PointVisual(
                id="visual:data-points",
                positions=np.zeros((1, 2), dtype=np.float32),
                colors=np.zeros((1, 4), dtype=np.uint8),
                sizes=1.0,
                coordinate_space=CoordinateSpace.DATA,
            )
        )


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


def test_configure_view2d_axes_uses_verified_datoviz_v04dev_symbols():
    fake = FakeDatovizV04WithAxes()
    renderer = DatovizV04ProtocolRenderer(dvz=fake)

    renderer.configure_view2d_axes(View2D(id="view:main", panel_id="panel:main", x_range=(-1.0, 2.0), y_range=(-3.0, 4.0)), x_label="x", y_label="y", grid=True)

    assert _calls(fake, "set_domain") == [
        ("set_domain", "panel", 0, -1.0, 2.0),
        ("set_domain", "panel", 1, -3.0, 4.0),
    ]
    assert _calls(fake, "set_view2d") == [("set_view2d", "panel", "view2d")]
    assert _calls(fake, "panel_axis") == [("panel_axis", "panel", 0), ("panel_axis", "panel", 1)]
    assert _calls(fake, "set_tick_policy") == [("set_tick_policy", "axis:0", "tick-policy"), ("set_tick_policy", "axis:1", "tick-policy")]
    assert _calls(fake, "set_grid") == [("set_grid", "axis:0", True), ("set_grid", "axis:1", True)]
    assert _calls(fake, "set_label") == [("set_label", "axis:0", "x"), ("set_label", "axis:1", "y")]


def test_configure_view2d_axes_rejects_unavailable_or_strict_explicit_ticks():
    with pytest.raises(DatovizV04Unavailable, match="missing v0.4-dev axis symbols"):
        DatovizV04ProtocolRenderer(dvz=FakeDatovizV04()).configure_view2d_axes(View2D(id="view:main", panel_id="panel:main"))

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
        pytest.skip("installed Datoviz binding does not expose decodable DvzQueryResult fields")

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
        pytest.skip("installed Datoviz binding does not expose sampled-field image symbols")

    assert datoviz_v04_sampled_field_diagnostics(dvz) == ()


def test_imported_datoviz_capture_binding_smoke_when_available():
    dvz = pytest.importorskip("datoviz")
    if not datoviz_v04_capture_ready(dvz):
        pytest.skip("installed Datoviz binding does not expose offscreen PNG capture symbols")

    assert datoviz_v04_capture_diagnostics(dvz) == ()
