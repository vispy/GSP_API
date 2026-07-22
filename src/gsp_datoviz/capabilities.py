"""Datoviz v0.4-dev protocol capability declarations."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
import subprocess
from types import ModuleType
from typing import Any, Literal, cast

from gsp.protocol import (
    AxisProviderCapability,
    CapabilitySnapshot,
    FontLayoutCapability,
    GuideLayoutCapability,
    LayoutCapability,
    MESH3D_DATA_VIEW3D_CAPABILITY,
    MESH3D_NDC_CAPABILITY,
    MESH3D_OPAQUE_DEPTH_CAPABILITY,
    MESH_MATERIAL_FLAT_LAMBERT_CAPABILITY,
    MESH_MATERIAL_TEXTURE2D_UNLIT_CAPABILITY,
    MESH_TEXTURE_FILTER_LINEAR_CAPABILITY,
    MESH_NORMALS_FACE3D_CAPABILITY,
    MESH_NORMAL_GENERATION_FACE_FLAT_CAPABILITY,
    NavigationPlacement,
    QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY,
    QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryLayoutCapability,
    QueryOrderingGuarantee,
    QueryPayload,
    QueryScope,
    QueryScopeCapability,
    QueryTargetCapability,
    QueryTargetKind,
    RenderTargetCapability,
    TransportKind,
    TransformPlacement,
    VIEW3D_LIGHT_AMBIENT_CAPABILITY,
    VIEW3D_LIGHT_DIRECTIONAL_CAPABILITY,
    VIEW3D_NAVIGATION_ORBIT_PAN_ZOOM_CAPABILITY,
    VIEW3D_RETAINED_DATA_SPACE_VISUALS_CAPABILITY,
    VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
    VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
)
from gsp_datoviz.query import datoviz_v04_query_binding_diagnostics
from gsp_datoviz.v04_import import bootstrap_datoviz_v04_source


DATOVIZ_V04_AXIS_PROVIDER = "datoviz.v04.panel_axis.wip"
DATOVIZ_GRID_CLIP_TO_PLOT_RECT_COMMIT = "9ba820489fae8b1da4a3debd5d19decd0a8c2533"
DATOVIZ_EXPERIMENTAL_VIEW3D_NAV_ENV = "GSP_DATOVIZ_ENABLE_EXPERIMENTAL_VIEW3D_NAV"
DATOVIZ_S034_AXIS_STYLE_FIELDS = (
    "tick_size_px",
    "label_size_px",
    "major_tick_length",
    "minor_tick_length",
    "major_tick_width",
    "minor_tick_width",
    "tick_gap_px",
    "label_gap_px",
    "grid_width",
    "plot_margin_top",
    "plot_margin_bottom",
    "plot_margin_left",
    "plot_margin_right",
)
S027_TRANSFORM_CAPABILITIES = (
    "gsp.transform.affine2d@0.1",
    "gsp.transform.inline-affine2d@0.1",
    "gsp.transform.point@0.1",
    "gsp.transform.marker@0.1",
    "gsp.transform.segment@0.1",
    "gsp.transform.path@0.1",
)

_REQUIRED_DVZ_CAPTURE_FUNCTIONS = (
    "dvz_app",
    "dvz_view_offscreen",
    "dvz_view_capture_png",
)

_DVZ_CAPTURE_RENDER_FUNCTIONS = (
    "dvz_view_render_once",
    "dvz_app_render_once",
    "dvz_app_run",
)

_REQUIRED_DVZ_VIEW3D_CAMERA_FUNCTIONS = (
    "DvzCameraDesc",
    "DvzCameraView",
    "DvzCameraProjection",
    "dvz_camera_desc",
    "dvz_camera_set_orthographic_bounds",
    "dvz_panel_view3d_desc",
    "dvz_panel_set_view3d_desc",
    "dvz_panel_camera",
)

_REQUIRED_DVZ_VIEW3D_RETAINED_DATA_FUNCTIONS = (
    "DvzPanelView3DDesc",
    "DvzPanelView3DState",
    "dvz_panel_view3d_desc",
    "dvz_panel_set_view3d_desc",
    "dvz_panel_view3d_state",
    "dvz_panel_camera",
    "dvz_camera_set_view",
    "dvz_camera_get_view",
    "dvz_camera_get_projection",
    "dvz_camera_get_orthographic_bounds",
)

_REQUIRED_DVZ_LIVE_INPUT_FUNCTIONS = (
    "dvz_view_input",
    "dvz_input_subscribe_event",
    "dvz_input_unsubscribe",
    "DvzPointerEvent",
    "DvzInputEvent",
    "DvzInputEventContent",
)

_REQUIRED_DVZ_TEXTURE2D_MESH_FUNCTIONS = (
    "dvz_mesh",
    "dvz_visual_set_data",
    "dvz_visual_set_index_data",
    "dvz_sampled_field_desc",
    "dvz_field_data_view",
    "dvz_sampled_field",
    "dvz_sampled_field_set_data",
    "dvz_visual_set_field",
    "dvz_field_sampling_desc",
    "dvz_visual_set_field_sampling",
    "dvz_material_desc",
    "dvz_visual_set_material",
)

_REQUIRED_DVZ_PANEL_FRAME_SNAPSHOT_FUNCTIONS = (
    "DvzPanelFrameInfo",
    "DvzGuideLayout",
    "DvzRenderedContribution",
    "dvz_panel_resolve_frame",
    "dvz_panel_frame_info",
    "dvz_panel_frame_guide_count",
    "dvz_panel_frame_guide_layout",
    "dvz_panel_frame_contribution_count",
    "dvz_panel_frame_contribution",
)

_REQUIRED_DVZ_PANEL_FRAME_GUIDE_QUERY_FUNCTIONS = (
    "DvzGuideHit",
    "dvz_panel_frame_guide_hit",
)

_REQUIRED_DVZ_AXIS_FUNCTIONS = (
    "dvz_panel_set_domain",
    "dvz_panel_set_view2d",
    "dvz_panel_axis",
    "dvz_axis_set_label",
    "dvz_axis_set_tick_policy",
)

_REQUIRED_DVZ_AXIS_ALTERNATIVE_FUNCTIONS = {
    "dvz_panel_view2d_factory": ("dvz_panel_view2d_desc", "dvz_panel_view2d"),
}

_OPTIONAL_DVZ_AXIS_FUNCTIONS = (
    "dvz_axis_set_visible",
    "dvz_axis_set_grid",
    "dvz_axis_set_ticks",
    "dvz_axis_set_style",
    "dvz_axis_set_plot_margins",
    "dvz_panel_visible_domain",
    "dvz_panel_transform_point",
    "dvz_panel_position_to_data",
    "dvz_panel_data_to_position",
)

_DVZ_CAPABILITY_FIELDS = (
    "struct_size",
    "flags",
    "max_buffer_size",
    "max_texture_dimension_2d",
    "max_bind_groups",
    "max_vertex_buffers",
    "max_color_attachments",
    "max_color_sample_count",
    "max_depth_sample_count",
    "shader_format_wgsl",
    "shader_format_glsl",
    "render_target_format_rgba16float",
    "render_target_format_r16float",
    "supports_render_target_sampling",
    "supports_color_blending",
    "supports_readback",
    "min_texture_copy_bytes_per_row_alignment",
    "max_readback_size",
    "texture_format_r32uint",
    "texture_format_rg32uint",
    "render_target_format_r32uint",
    "render_target_format_rg32uint",
    "query_profile_u32_r32",
    "query_profile_u64_rg32",
    "query_profile_u64_2xr32",
)


def datoviz_v04_capability_snapshot(
    dvz: ModuleType | Any | None = None,
) -> CapabilitySnapshot:
    """Return the bounded GSP capability snapshot for the Datoviz v0.4 adapter."""
    raw_snapshot = None
    source = "static-gsp-slice"
    diagnostics: tuple[str, ...] = ()

    if dvz is None:
        bootstrap_datoviz_v04_source()
        try:
            import datoviz as imported_dvz
        except ModuleNotFoundError:
            diagnostics = (
                "Datoviz is not importable; using conservative static GSP slice capabilities",
            )
        else:
            dvz = imported_dvz
    if dvz is not None and hasattr(dvz, "dvz_capability_snapshot"):
        raw_snapshot = dvz.dvz_capability_snapshot()
        source = "dvz_capability_snapshot"
    elif dvz is not None:
        diagnostics = (
            "Datoviz Python binding is missing dvz_capability_snapshot; using conservative static GSP slice capabilities",
        )

    return gsp_capability_snapshot_from_datoviz(
        raw_snapshot, dvz=dvz, source=source, diagnostics=diagnostics
    )


def gsp_capability_snapshot_from_datoviz(
    raw_snapshot: Any | None,
    *,
    dvz: ModuleType | Any | None = None,
    source: str = "dvz_capability_snapshot",
    diagnostics: tuple[str, ...] = (),
) -> CapabilitySnapshot:
    """Translate a Datoviz v0.4 capability snapshot into the GSP capability surface.

    The translation deliberately advertises only features implemented by the current GSP Datoviz
    adapter. Raw Datoviz capability fields are retained in metadata for later parity missions.
    """
    raw_fields = (
        _raw_capability_fields(raw_snapshot) if raw_snapshot is not None else {}
    )
    texture_formats = ["rgba8"]
    if raw_fields.get("texture_format_r32uint") is True:
        texture_formats.append("r32uint")
    if raw_fields.get("texture_format_rg32uint") is True:
        texture_formats.append("rg32uint")

    capture_diagnostics = (
        datoviz_v04_capture_diagnostics(dvz)
        if dvz is not None
        else ("Datoviz is not importable",)
    )
    grid_clip_diagnostics = datoviz_v04_grid_clip_to_plot_rect_diagnostics(dvz)
    grid_clip_supported = not grid_clip_diagnostics
    grid_clip_status = "native-verified" if grid_clip_supported else "unsupported"
    grid_clip_audit_diagnostics = (
        ("grid_clip_native_verified",) if grid_clip_supported else grid_clip_diagnostics
    )
    frame_snapshot_diagnostics = datoviz_v04_panel_frame_snapshot_diagnostics(dvz)
    frame_snapshot_supported = not frame_snapshot_diagnostics
    frame_snapshot_status: Literal["none", "partial"] = (
        "partial" if frame_snapshot_supported else "none"
    )
    guide_query_diagnostics = datoviz_v04_panel_frame_guide_query_diagnostics(dvz)
    guide_query_supported = frame_snapshot_supported and not guide_query_diagnostics
    frame_snapshot_audit_diagnostics = (
        (
            "layout_snapshot_partial",
            "guide_layout_snapshot_first_slice",
            (
                "guide_query_native_verified"
                if guide_query_supported
                else "guide_query_missing"
            ),
            (
                "all_rendered_guides_native_verified"
                if guide_query_supported
                else "all_rendered_guides_unsupported"
            ),
            *guide_query_diagnostics,
        )
        if frame_snapshot_supported
        else ("resolved_layout_snapshot_unsupported", *frame_snapshot_diagnostics)
    )
    guide_layout_diagnostics = (
        "panel_text_guide_as_screen_text",
        "axis_style_mapping_partial",
        *grid_clip_audit_diagnostics,
        *frame_snapshot_audit_diagnostics,
        "guide_query_missing",
        "all_rendered_guides_unsupported",
    )

    metadata: dict[str, object] = {
        "profile_id": "gsp.datoviz-v0.4@0.2",
        "datoviz_api": "v0.4 dvz_* facade",
        "datoviz_capability_source": source,
        "image_path": (
            "RGBA8 NDC image path uses dvz_image_set_sampling() for nearest/linear "
            "sampling when the Datoviz facade exposes the v0.4 image sampling API"
        ),
        "query_support": "deferred until DvzQueryResult is decodable from Python",
        "capture_support": "PNG capture is advertised only when offscreen view capture bindings are available",
        "axis_provider": "datoviz.v04.panel_axis.wip when v0.4-dev Python symbols are exposed",
        "s028_guide_view2d": (
            "Datoviz native panel axes are an adapted provider in this GSP slice: "
            "panel View2D descriptor symbols are capability-gated, backend auto ticks "
            "may render, explicit GSP tick values/labels are applied when the "
            "dvz_axis_set_ticks convenience wrapper is exposed, guide query is "
            "deferred, and all-rendered guide contributions remain unsupported "
            "until Datoviz exposes guide picking/query semantics"
        ),
        "s028_guide_view2d_diagnostics": (
            "datoviz_axis_provider_adapted",
            "explicit_gsp_ticks_binding_dependent",
            "axis_guide_query_unsupported",
            "all_rendered_guides_unsupported",
            "strict_guide_title_query_unverified",
        ),
        "s034_layout_status": (
            "Datoviz guide/layout behavior is semantic/adapted in this slice. "
            "The adapter can produce a partial ResolvedLayoutSnapshot only when "
            "the M184 panel frame snapshot APIs are available; guide query geometry "
            "is still not a strict GSP query path and must not claim layout_strict."
        ),
        "s034_guide_layout_audit": {
            "semantic_guides": True,
            "resolved_layout_produce": frame_snapshot_status,
            "resolved_layout_consume": "none",
            "layout_strict": False,
            "panel_text_title": "adapted: panel_text_guide_as_screen_text",
            "axis_style_mapping": "partial"
            if dvz is not None and hasattr(dvz, "dvz_axis_set_style")
            else "unsupported",
            "axis_style_fields": DATOVIZ_S034_AXIS_STYLE_FIELDS,
            "grid_clip_to_plot_rect": grid_clip_status,
            "layout_snapshot_partial": frame_snapshot_supported,
            "layout_snapshot_guides": frame_snapshot_supported,
            "layout_snapshot_contributions": frame_snapshot_supported,
            "guide_query": guide_query_supported,
            "all_rendered_guides": guide_query_supported,
            "diagnostics": (
                "panel_text_guide_as_screen_text",
                "axis_style_mapping_partial",
                *grid_clip_audit_diagnostics,
                *frame_snapshot_audit_diagnostics,
                "guide_query_missing",
                "all_rendered_guides_unsupported",
                "font_metrics_parity_false",
            ),
        },
        "s026_scalar_color": (
            "finite eager scalar ImageVisual, PointVisual, and MarkerVisual fill "
            "data are CPU pre-mapped to canonical GSP RGBA8; point/image scalar "
            "source values are retained for semantic query payloads"
        ),
        "s026_scalar_color_capabilities": (
            "gsp.scalar-color@0.1",
            "gsp.colormap.named.gray@0.1",
            "gsp.colormap.named.viridis@0.1",
            "gsp.colormap.named.magma@0.1",
            "gsp.colormap.named.plasma@0.1",
            "gsp.colormap.named.inferno@0.1",
            "gsp.colormap.named.cividis@0.1",
            "gsp.scalar-image.color-scale@0.1",
            "gsp.point.scalar-color@0.1",
            "gsp.marker.scalar-fill@0.1",
            "gsp.colorbar-guide.render@0.1",
            "gsp.scalar-query.source-value@0.1",
            "gsp.scalar-query.normalized-value@0.1",
            "gsp.scalar-query.displayed-rgba@0.1",
        ),
        "s026_scalar_color_diagnostics": (
            "cpu_premap_scalar_to_rgba",
            "colorbar_explicit_ticks_unverified",
            "colorbar_query_unsupported",
            "mesh_face_scalar_unsupported",
        ),
        "s025_mesh": (
            "bounded 2D MeshVisual rows render through dvz_mesh with direct "
            "position/color/index upload; 2D DATA positions use retained panel "
            "domain/View2D placement, per-face RGBA is adapted by duplicating "
            "vertices, and scalar face colors plus mesh query payloads remain unsupported"
        ),
        "s027_transform": (
            "finite eager Point/Marker/Segment/Path/Text/Mesh positions are CPU "
            "pre-transformed before upload for inline and named AFFINE_2D bindings; "
            "2D DATA positions use retained panel domain/View2D placement with "
            "CPU remap reserved for explicit adapted fallback; transform query "
            "inverse, image affine, 3D camera/projection/controller semantics, and "
            "virtual-source materialization are unsupported"
        ),
        "s027_transform_diagnostics": (
            "cpu_adapter_affine2d_eager_ndc",
            "GSP_TRANSFORM_MISSING_REF",
            "GSP_QUERY_INVERSE_UNSUPPORTED",
            "GSP_TRANSFORM_IMAGE_AFFINE_DEFERRED",
            "GSP_TRANSFORM_VIRTUAL_SOURCE_DEFERRED",
            "GSP_CAMERA3D_DEFERRED",
        ),
        "s035_navigation": (
            "programmatic View2D navigation updates use retained Datoviz panel "
            "domain/View2D state via dvz_panel_set_domain and dvz_panel_set_view2d; "
            "unchanged visual buffers must not be re-uploaded for the retained fast path"
        ),
        "s035_navigation_diagnostics": (
            "retained_view2d_update_only",
            "live_native_input_adapter_deferred",
            "view_snapshot_query_binding_deferred",
        ),
    }
    if raw_fields:
        metadata["datoviz_raw_capabilities"] = raw_fields
        metadata["datoviz_shader_formats"] = tuple(
            name
            for name, supported in (
                ("wgsl", raw_fields.get("shader_format_wgsl")),
                ("glsl", raw_fields.get("shader_format_glsl")),
            )
            if supported is True
        )
        metadata["datoviz_query_profiles"] = tuple(
            name
            for name, supported in (
                ("u32_r32", raw_fields.get("query_profile_u32_r32")),
                ("u64_rg32", raw_fields.get("query_profile_u64_rg32")),
                ("u64_2xr32", raw_fields.get("query_profile_u64_2xr32")),
            )
            if supported is True
        )
    if diagnostics:
        metadata["datoviz_capability_diagnostics"] = diagnostics
    output_formats: tuple[str, ...] = ()
    if capture_diagnostics:
        metadata["datoviz_capture_diagnostics"] = capture_diagnostics
    else:
        output_formats = ("png",)
        metadata["capture_support"] = (
            "offscreen PNG screenshot/export; not scientific readback"
        )
    query_diagnostics = (
        datoviz_v04_query_binding_diagnostics(dvz)
        if dvz is not None
        else ("Datoviz is not importable",)
    )
    query_modes: tuple[str, ...] = ()
    query_capabilities: tuple[QueryScopeCapability, ...] = ()
    if query_diagnostics:
        metadata["datoviz_query_binding_diagnostics"] = query_diagnostics
    else:
        query_modes = ("panel-query", "point-item")
        query_capabilities = (_datoviz_data_query_capability(),)
        metadata["query_support"] = (
            "data-scope query queue, poll, and decode binding available; live payload "
            "parity currently supports point identity but not image texel/color/value"
        )

    view3d_diagnostics = _datoviz_v04_view3d_binding_diagnostics(dvz)
    retained_view3d_diagnostics = datoviz_v04_view3d_retained_data_diagnostics(dvz)
    live_input_diagnostics = datoviz_v04_live_input_diagnostics(dvz)
    texture2d_mesh_diagnostics = tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_TEXTURE2D_MESH_FUNCTIONS
        if dvz is None or not hasattr(dvz, name)
    )
    navigation_capabilities = ["interaction.view2d.navigation.v1"]
    view3d_capabilities: tuple[str, ...] = ()
    if view3d_diagnostics:
        metadata["datoviz_view3d_binding_diagnostics"] = view3d_diagnostics
    else:
        view3d_capabilities = (
            VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
            VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
            MESH3D_DATA_VIEW3D_CAPABILITY,
            MESH3D_NDC_CAPABILITY,
            QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
            MESH_MATERIAL_FLAT_LAMBERT_CAPABILITY,
            MESH_NORMALS_FACE3D_CAPABILITY,
            MESH_NORMAL_GENERATION_FACE_FLAT_CAPABILITY,
            VIEW3D_LIGHT_AMBIENT_CAPABILITY,
            VIEW3D_LIGHT_DIRECTIONAL_CAPABILITY,
        )
        if not texture2d_mesh_diagnostics:
            view3d_capabilities = (
                *view3d_capabilities,
                MESH_MATERIAL_TEXTURE2D_UNLIT_CAPABILITY,
                MESH_TEXTURE_FILTER_LINEAR_CAPABILITY,
            )
            metadata["s050_texture2d_unlit"] = (
                "public RGBA8 sampled-field mesh binding with vertex UVs, nearest-or-linear "
                "clamp/no-mipmap slot sampling, linear color role, and unlit material"
            )
        else:
            metadata["datoviz_texture2d_mesh_diagnostics"] = texture2d_mesh_diagnostics
        if not retained_view3d_diagnostics:
            view3d_capabilities = (
                *view3d_capabilities,
                VIEW3D_RETAINED_DATA_SPACE_VISUALS_CAPABILITY,
                MESH3D_OPAQUE_DEPTH_CAPABILITY,
            )
            metadata["view3d_retained_data_space_visuals"] = (
                "native DATA-space mesh attachments with retained camera/projection updates"
            )
            metadata["s050_opaque_depth"] = (
                "meshvisual.positions3d.opaque_depth.v1 is strict only on the retained "
                "DATA-space View3D path for fully opaque MeshVisuals; S050 face-order "
                "invariance artifacts prove nearer-fragment-wins behavior"
            )
        else:
            metadata["datoviz_view3d_retained_data_diagnostics"] = (
                retained_view3d_diagnostics
            )
        view3d_navigation_experimental_enabled = (
            os.environ.get(DATOVIZ_EXPERIMENTAL_VIEW3D_NAV_ENV) == "1"
        )
        if (
            not retained_view3d_diagnostics
            and not live_input_diagnostics
            and view3d_navigation_experimental_enabled
        ):
            view3d_capabilities = (
                *view3d_capabilities,
                VIEW3D_NAVIGATION_ORBIT_PAN_ZOOM_CAPABILITY,
            )
            navigation_capabilities.append(VIEW3D_NAVIGATION_ORBIT_PAN_ZOOM_CAPABILITY)
            metadata["view3d_navigation_support"] = (
                "canonical S037 action replay into retained Datoviz View3D state"
            )
        elif live_input_diagnostics:
            metadata["datoviz_live_input_diagnostics"] = live_input_diagnostics
        else:
            metadata["datoviz_view3d_navigation_diagnostics"] = (
                "Datoviz View3D live navigation is experimental and failed manual "
                "review; set GSP_DATOVIZ_ENABLE_EXPERIMENTAL_VIEW3D_NAV=1 to opt in"
            )
        query_modes = (*query_modes, "view3d-ray")
        metadata["view3d_support"] = (
            "static orthographic View3D mesh rendering and canonical ray-context payloads"
        )
        metadata["s044_mesh_triangle_pick"] = (
            "query.view3d.mesh_triangle_pick.v1 is not advertised until Datoviz can "
            "prove public visual_id and canonical primitive_index mapping plus "
            "layout/view/projection/pick-scene freshness"
        )
        metadata["s044_mesh_triangle_pick_diagnostics"] = (
            "pick.unsupported.no_public_primitive_map",
            "pick.unsupported.native_state_only",
        )
        if QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY in view3d_capabilities:
            raise AssertionError("Datoviz must not advertise S044 mesh picking yet")
        metadata["s040_flat_lambert"] = (
            "flat_lambert_cpu_resolved_strict: Datoviz S039 flat Lambert "
            "is resolved by protocol CPU face colors; native Datoviz lighting is not used"
        )

    return CapabilitySnapshot(
        server_name="datoviz-v0.4-protocol-slice",
        protocol_versions=("0.2",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32", "uint8", "rgba8"),
        texture_formats=tuple(texture_formats),
        visual_families=(
            "point",
            "marker",
            "segment",
            "path",
            "image",
            "text",
            "mesh",
        ),
        transform_placements=(
            TransformPlacement.CPU_ADAPTER.value,
            TransformPlacement.UNSUPPORTED.value,
        ),
        transform_capabilities=S027_TRANSFORM_CAPABILITIES,
        navigation_placements=(NavigationPlacement.RETAINED_GPU_STATE.value,),
        navigation_capabilities=tuple(navigation_capabilities),
        query_modes=query_modes,
        query_capabilities=query_capabilities,
        view3d_capabilities=view3d_capabilities,
        output_formats=output_formats,
        supported_data_source_localities=(),
        supported_credential_policies=("none",),
        cache_modes=("none",),
        deterministic=False,
        max_buffer_bytes=_optional_nonnegative_int(raw_fields.get("max_buffer_size")),
        axis_providers=(datoviz_v04_axis_provider_capability(dvz),),
        layout_capability=LayoutCapability(
            semantic_guides=True,
            resolved_layout_produce=frame_snapshot_status,
            resolved_layout_consume="none",
            layout_strict=False,
            diagnostics=(
                "panel_text_guide_as_screen_text",
                "axis_style_mapping_partial",
                *frame_snapshot_audit_diagnostics,
                "layout_strict_false",
            ),
        ),
        guide_layout_capability=GuideLayoutCapability(
            axis_native=True,
            axis_explicit_ticks=hasattr(dvz, "dvz_axis_set_ticks")
            if dvz is not None
            else False,
            axis_deterministic_gsp_ticks=False,
            axis_labels=True,
            axis_grid=True,
            axis_grid_clip_to_plot_rect=grid_clip_supported,
            axis_query=guide_query_supported,
            panel_text_title="adapted",
            panel_text_participates_in_layout=False,
            panel_text_query=False,
            colorbar="adapted",
            colorbar_query=False,
            legend="unsupported",
            diagnostics=guide_layout_diagnostics,
        ),
        font_layout_capability=FontLayoutCapability(
            logical_font_size_px=True,
            font_family_request=False,
            font_fallback_report=False,
            text_measurement="none",
            font_metrics_profile="backend_defined",
            rasterization_parity=False,
            diagnostics=("font_metrics_parity_false",),
        ),
        render_target_capability=RenderTargetCapability(
            logical_pixels=True,
            device_scale=frame_snapshot_supported,
            dpi_metadata=False,
            physical_framebuffer_scale=False,
            diagnostics=(
                ()
                if frame_snapshot_supported
                else ("device_scale_reporting_unverified",)
            ),
        ),
        query_layout_capability=QueryLayoutCapability(
            screen_logical_px=True,
            data_readout_uses_view_snapshot=True,
            guide_query=guide_query_supported,
            all_rendered_guides=guide_query_supported,
            reports_layout_snapshot_id=frame_snapshot_supported,
            diagnostics=(
                (
                    "guide_query_native_verified"
                    if guide_query_supported
                    else "guide_query_missing"
                ),
                (
                    "layout_snapshot_partial"
                    if frame_snapshot_supported
                    else "layout_snapshot_not_used"
                ),
            ),
        ),
        metadata=metadata,
    )


def _datoviz_data_query_capability() -> QueryScopeCapability:
    return QueryScopeCapability(
        scope=QueryScope.DATA,
        coordinate_spaces=(QueryCoordinateSpace.PANEL,),
        hit_policies=(QueryHitPolicy.FRONTMOST,),
        ordering=QueryOrderingGuarantee.NONE,
        targets=(
            QueryTargetCapability(
                target_kind=QueryTargetKind.VISUAL_FAMILY,
                target="point",
                payloads=(QueryPayload.IDENTITY,),
                diagnostics=(
                    "live Datoviz point queries return visual family and item id, but not displayed color or value",
                ),
            ),
        ),
        diagnostics=(
            "Datoviz v0.4 data query supports frontmost panel-coordinate identity requests only in this slice",
            "image texel/color/value payload parity remains unadvertised",
        ),
    )


def _datoviz_v04_view3d_binding_diagnostics(
    dvz: ModuleType | Any | None,
) -> tuple[str, ...]:
    if dvz is None:
        return ("Datoviz is not importable",)
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_VIEW3D_CAMERA_FUNCTIONS
        if (
            not callable(getattr(dvz, name, None))
            if name.startswith("dvz_")
            else not hasattr(dvz, name)
        )
    )


def datoviz_v04_view3d_retained_data_diagnostics(
    dvz: ModuleType | Any | None,
) -> tuple[str, ...]:
    """Return why retained DATA-space View3D visual attachment is unavailable."""
    if dvz is None:
        return ("Datoviz is not importable",)
    return (
        *_datoviz_v04_view3d_binding_diagnostics(dvz),
        *(
            f"missing {name}"
            for name in _REQUIRED_DVZ_VIEW3D_RETAINED_DATA_FUNCTIONS
            if not callable(getattr(dvz, name, None))
        ),
    )


def datoviz_v04_live_input_diagnostics(
    dvz: ModuleType | Any | None,
) -> tuple[str, ...]:
    """Return why live Datoviz input cannot drive retained navigation."""
    if dvz is None:
        return ("Datoviz is not importable",)
    return tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_LIVE_INPUT_FUNCTIONS
        if not hasattr(dvz, name)
    )


def datoviz_v04_panel_frame_snapshot_diagnostics(
    dvz: ModuleType | Any | None,
) -> tuple[str, ...]:
    """Return why Datoviz panel frame snapshot readback is unavailable."""
    if dvz is None:
        return ("Datoviz is not importable",)
    missing = tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_PANEL_FRAME_SNAPSHOT_FUNCTIONS
        if not hasattr(dvz, name)
    )
    return missing + _incomplete_ctypes_records(
        dvz,
        ("DvzPanelFrameInfo", "DvzGuideLayout", "DvzRenderedContribution"),
    )


def datoviz_v04_panel_frame_guide_query_diagnostics(
    dvz: ModuleType | Any | None,
) -> tuple[str, ...]:
    """Return why Datoviz panel frame guide hit/readback is unavailable."""
    if dvz is None:
        return ("Datoviz is not importable",)
    missing = tuple(
        f"missing {name}"
        for name in _REQUIRED_DVZ_PANEL_FRAME_GUIDE_QUERY_FUNCTIONS
        if not callable(getattr(dvz, name, None))
    )
    return missing + _incomplete_ctypes_records(dvz, ("DvzGuideHit",))


def _incomplete_ctypes_records(
    dvz: ModuleType | Any, names: tuple[str, ...]
) -> tuple[str, ...]:
    """Report generated ctypes records that are only empty forward declarations."""
    diagnostics: list[str] = []
    for name in names:
        record_type = getattr(dvz, name, None)
        if not isinstance(record_type, type):
            continue
        try:
            is_ctypes_record = issubclass(record_type, ctypes.Structure)
        except TypeError:
            continue
        if is_ctypes_record and ctypes.sizeof(record_type) == 0:
            diagnostics.append(f"incomplete ctypes layout for {name}")
    return tuple(diagnostics)


def datoviz_v04_capture_ready(dvz: ModuleType | Any) -> bool:
    """Return whether a facade exposes the bounded offscreen PNG capture path."""
    return not datoviz_v04_capture_diagnostics(dvz)


def datoviz_v04_capture_diagnostics(dvz: ModuleType | Any) -> tuple[str, ...]:
    """Return missing requirements for v0.4 offscreen PNG capture."""
    diagnostics = [
        f"missing {name}"
        for name in _REQUIRED_DVZ_CAPTURE_FUNCTIONS
        if not hasattr(dvz, name)
    ]
    if not any(hasattr(dvz, name) for name in _DVZ_CAPTURE_RENDER_FUNCTIONS):
        diagnostics.append(
            "missing one of dvz_view_render_once, dvz_app_render_once, dvz_app_run"
        )
    return tuple(diagnostics)


def datoviz_v04_grid_clip_to_plot_rect_ready_for_source(
    source: Path | str | None,
) -> bool:
    """Return whether a Datoviz source checkout contains the native grid clip fix."""
    if source is None:
        return False
    source_path = Path(source)
    return _datoviz_commit_contains(
        source_path, DATOVIZ_GRID_CLIP_TO_PLOT_RECT_COMMIT
    ) or _datoviz_source_has_grid_clip_fix(source_path)


def datoviz_v04_grid_clip_to_plot_rect_diagnostics(
    dvz: ModuleType | Any | None,
) -> tuple[str, ...]:
    """Return diagnostics for Datoviz native axis grid clipping to the plot rect."""
    if dvz is None:
        return ("grid_clip_not_enforced", "grid_clip_native_api_unverified")
    source = _datoviz_module_source_root(dvz)
    if source is not None and datoviz_v04_grid_clip_to_plot_rect_ready_for_source(
        source
    ):
        return ()
    return ("grid_clip_not_enforced", "grid_clip_native_api_unverified")


def datoviz_v04_axis_provider_capability(
    dvz: ModuleType | Any | None = None,
) -> AxisProviderCapability:
    """Return the Datoviz v0.4-dev native axis provider capability.

    The local v0.4-dev headers contain the native axis API. Runtime support is
    advertised only when the Python facade/raw binding exposes the verified symbols.
    """
    if dvz is None:
        bootstrap_datoviz_v04_source()
        try:
            import datoviz as imported_dvz
        except ModuleNotFoundError:
            return _unsupported("Datoviz is not importable")
        else:
            dvz = imported_dvz

    missing = [name for name in _REQUIRED_DVZ_AXIS_FUNCTIONS if not hasattr(dvz, name)]
    for name, alternatives in _REQUIRED_DVZ_AXIS_ALTERNATIVE_FUNCTIONS.items():
        if not any(hasattr(dvz, alternative) for alternative in alternatives):
            missing.append(f"{name} ({'/'.join(alternatives)})")
    missing_tuple = tuple(missing)
    if missing_tuple:
        return _unsupported(
            f"Datoviz Python binding is missing v0.4-dev axis symbols: {missing_tuple}"
        )

    supports_explicit_ticks = hasattr(dvz, "dvz_axis_set_ticks")
    explicit_tick_diagnostic = (
        "axis-provider-explicit-ticks: explicit GSP tick values and labels are wired through dvz_axis_set_ticks"
        if supports_explicit_ticks
        else "axis-provider-explicit-ticks-unsupported: missing dvz_axis_set_ticks"
    )
    grid_clip_diagnostic = (
        "axis-provider-grid-clip-to-plot-rect: native Datoviz axis grids use the plot viewport and plot clip rect without double-trimming geometry"
        if not datoviz_v04_grid_clip_to_plot_rect_diagnostics(dvz)
        else "axis-provider-grid-clip-to-plot-rect-unverified: native grid endpoint clipping is not verified for this Datoviz build"
    )
    guide_query_supported = not datoviz_v04_panel_frame_snapshot_diagnostics(
        dvz
    ) and not datoviz_v04_panel_frame_guide_query_diagnostics(dvz)
    guide_query_diagnostic = (
        "axis-guide-query-native-verified: Datoviz panel frame guide hit/readback uses the same snapshot id as guide layout records"
        if guide_query_supported
        else "axis-guide-query-unsupported: guide picking is deferred for Datoviz v0.4 RC"
    )
    all_rendered_diagnostic = (
        "all-rendered-guides-native-verified: Datoviz panel frame contribution enumeration reports guide contributions with snapshot ids"
        if guide_query_supported
        else "all-rendered-guides-unsupported: all-rendered guide contributions require guide query support"
    )

    return AxisProviderCapability(
        provider_id=DATOVIZ_V04_AXIS_PROVIDER,
        backend_id="datoviz",
        provider_status="adapted",
        supports_explicit_ticks=supports_explicit_ticks,
        supports_auto_ticks_gsp_policy=False,
        supports_backend_auto_ticks=True,
        supports_tick_labels=True,
        supports_axis_labels=True,
        supports_title=False,
        supports_grid=hasattr(dvz, "dvz_axis_set_grid"),
        supports_style_basic=hasattr(dvz, "dvz_axis_set_style"),
        supports_visible_domain_readback=hasattr(dvz, "dvz_panel_visible_domain"),
        supports_guide_query=guide_query_supported,
        supports_text_query=False,
        diagnostics=(
            "axis-provider-selected: datoviz.v04.panel_axis.wip",
            (
                "axis-provider-adapted: ordered DATA domains are carried by "
                "dvz_panel_set_domain with DvzPanelView2D fit policy, or by "
                "descriptor data_x/data_y when exposed; backend-native ticks remain "
                "adapted and strict guide promotion still excludes title/query semantics"
            ),
            explicit_tick_diagnostic,
            grid_clip_diagnostic,
            guide_query_diagnostic,
            all_rendered_diagnostic,
            "strict-guide-title-query-unverified: Datoviz guide rows remain adapted until title layout and guide query semantics are strict",
        ),
    )


def datoviz_v04_axis_symbols(dvz: ModuleType | Any) -> dict[str, bool]:
    """Return required/optional Datoviz axis symbol availability for diagnostics/tests."""
    names = _REQUIRED_DVZ_AXIS_FUNCTIONS + _OPTIONAL_DVZ_AXIS_FUNCTIONS
    symbols = {name: hasattr(dvz, name) for name in names}
    for name, alternatives in _REQUIRED_DVZ_AXIS_ALTERNATIVE_FUNCTIONS.items():
        symbols[name] = any(hasattr(dvz, alternative) for alternative in alternatives)
        for alternative in alternatives:
            symbols[alternative] = hasattr(dvz, alternative)
    return symbols


def _raw_capability_fields(raw_snapshot: Any) -> dict[str, object]:
    fields: dict[str, object] = {}
    for name in _DVZ_CAPABILITY_FIELDS:
        if hasattr(raw_snapshot, name):
            fields[name] = getattr(raw_snapshot, name)
    return fields


def _optional_nonnegative_int(value: object | None) -> int | None:
    if value is None:
        return None
    integer = int(cast(Any, value))
    return integer if integer >= 0 else None


def _datoviz_module_source_root(dvz: ModuleType | Any) -> Path | None:
    module_file = getattr(dvz, "__file__", None)
    if not isinstance(module_file, str):
        return None
    path = Path(module_file).resolve()
    if path.name == "__init__.py" and path.parent.name == "datoviz":
        return path.parent.parent
    for parent in path.parents:
        if (parent / "datoviz" / "__init__.py").is_file():
            return parent
    return None


def _datoviz_commit_contains(source: Path, commit: str) -> bool:
    if not (source / ".git").exists():
        return False
    try:
        result = subprocess.run(
            ("git", "merge-base", "--is-ancestor", commit, "HEAD"),
            cwd=source,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, ValueError):
        return False
    return result.returncode == 0


def _datoviz_source_has_grid_clip_fix(source: Path) -> bool:
    axis_visual = source / "src" / "scene" / "annotation" / "axis_visual.c"
    axis_tests = source / "src" / "scene" / "tests" / "axis.c"
    if not axis_visual.is_file():
        return False
    try:
        axis_visual_source = axis_visual.read_text(encoding="utf-8")
        axis_test_source = (
            axis_tests.read_text(encoding="utf-8") if axis_tests.is_file() else ""
        )
    except OSError:
        return False
    return (
        "_axis_inverse_panzoom_coord(extent, 0, 1, -1.0f)" in axis_visual_source
        and "_axis_inverse_panzoom_coord(extent, 0, 1, +1.0f)" in axis_visual_source
        and "_axis_inverse_panzoom_coord(extent, 2, 3, -1.0f)" in axis_visual_source
        and "_axis_inverse_panzoom_coord(extent, 2, 3, +1.0f)" in axis_visual_source
        and "test_axis_grid_style_margins_do_not_double_clip" in axis_test_source
    )


def _unsupported(diagnostic: str) -> AxisProviderCapability:
    return AxisProviderCapability(
        provider_id=DATOVIZ_V04_AXIS_PROVIDER,
        backend_id="datoviz",
        provider_status="unsupported",
        diagnostics=(diagnostic,),
    )
