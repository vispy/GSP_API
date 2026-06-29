"""Datoviz v0.4-dev protocol capability declarations."""

from __future__ import annotations

from types import ModuleType
from typing import Any, cast

from gsp.protocol import (
    AxisProviderCapability,
    CapabilitySnapshot,
    FontLayoutCapability,
    GuideLayoutCapability,
    LayoutCapability,
    NavigationPlacement,
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
)
from gsp_datoviz.query import datoviz_v04_query_binding_diagnostics
from gsp_datoviz.v04_import import bootstrap_datoviz_v04_source


DATOVIZ_V04_AXIS_PROVIDER = "datoviz.v04.panel_axis.wip"
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

_REQUIRED_DVZ_AXIS_FUNCTIONS = (
    "dvz_panel_set_domain",
    "dvz_panel_view2d",
    "dvz_panel_set_view2d",
    "dvz_panel_axis",
    "dvz_axis_set_label",
    "dvz_axis_set_tick_policy",
)

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


def datoviz_v04_capability_snapshot(dvz: ModuleType | Any | None = None) -> CapabilitySnapshot:
    """Return the bounded GSP capability snapshot for the Datoviz v0.4 adapter."""
    raw_snapshot = None
    source = "static-gsp-slice"
    diagnostics: tuple[str, ...] = ()

    if dvz is None:
        bootstrap_datoviz_v04_source()
        try:
            import datoviz as imported_dvz
        except ModuleNotFoundError:
            diagnostics = ("Datoviz is not importable; using conservative static GSP slice capabilities",)
        else:
            dvz = imported_dvz
    if dvz is not None and hasattr(dvz, "dvz_capability_snapshot"):
        raw_snapshot = dvz.dvz_capability_snapshot()
        source = "dvz_capability_snapshot"
    elif dvz is not None:
        diagnostics = ("Datoviz Python binding is missing dvz_capability_snapshot; using conservative static GSP slice capabilities",)

    return gsp_capability_snapshot_from_datoviz(raw_snapshot, dvz=dvz, source=source, diagnostics=diagnostics)


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
    raw_fields = _raw_capability_fields(raw_snapshot) if raw_snapshot is not None else {}
    texture_formats = ["rgba8"]
    if raw_fields.get("texture_format_r32uint") is True:
        texture_formats.append("r32uint")
    if raw_fields.get("texture_format_rg32uint") is True:
        texture_formats.append("rg32uint")

    capture_diagnostics = datoviz_v04_capture_diagnostics(dvz) if dvz is not None else ("Datoviz is not importable",)

    metadata: dict[str, object] = {
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
            "The adapter does not produce or consume ResolvedLayoutSnapshot, "
            "does not provide guide query geometry, and must not claim layout_strict."
        ),
        "s034_guide_layout_audit": {
            "semantic_guides": True,
            "resolved_layout_produce": "none",
            "resolved_layout_consume": "none",
            "layout_strict": False,
            "panel_text_title": "adapted: panel_text_guide_as_screen_text",
            "axis_style_mapping": "partial" if dvz is not None and hasattr(dvz, "dvz_axis_set_style") else "unsupported",
            "axis_style_fields": DATOVIZ_S034_AXIS_STYLE_FIELDS,
            "grid_clip_to_plot_rect": "unsupported",
            "guide_query": False,
            "all_rendered_guides": False,
            "diagnostics": (
                "panel_text_guide_as_screen_text",
                "resolved_layout_snapshot_unsupported",
                "axis_style_mapping_partial",
                "grid_clip_not_enforced",
                "grid_clip_native_api_unverified",
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
            "position/color/index upload; DATA positions are CPU-mapped through "
            "View2D when present, per-face RGBA is adapted by duplicating vertices, "
            "and scalar face colors plus mesh query payloads remain unsupported"
        ),
        "s027_transform": (
            "finite eager Point/Marker/Segment/Path/Text/Mesh positions are CPU "
            "pre-transformed before upload for inline and named AFFINE_2D bindings; "
            "DATA positions are CPU-mapped through View2D when present; transform "
            "query inverse, image affine, 3D camera/projection/controller semantics, "
            "and virtual-source materialization are unsupported"
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
        metadata["capture_support"] = "offscreen PNG screenshot/export; not scientific readback"
    query_diagnostics = datoviz_v04_query_binding_diagnostics(dvz) if dvz is not None else ("Datoviz is not importable",)
    query_modes: tuple[str, ...] = ()
    query_capabilities: tuple[QueryScopeCapability, ...] = ()
    if query_diagnostics:
        metadata["datoviz_query_binding_diagnostics"] = query_diagnostics
    else:
        query_modes = ("panel-query", "point-item", "image-texel")
        query_capabilities = (_datoviz_data_query_capability(),)
        metadata["query_support"] = "data-scope point/image query queue, poll, and decode binding available"

    return CapabilitySnapshot(
        server_name="datoviz-v0.4-protocol-slice",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32", "uint8", "rgba8"),
        texture_formats=tuple(texture_formats),
        visual_families=("point", "image"),
        transform_placements=(
            TransformPlacement.CPU_ADAPTER.value,
            TransformPlacement.UNSUPPORTED.value,
        ),
        transform_capabilities=S027_TRANSFORM_CAPABILITIES,
        navigation_placements=(NavigationPlacement.RETAINED_GPU_STATE.value,),
        navigation_capabilities=("interaction.view2d.navigation.v1",),
        query_modes=query_modes,
        query_capabilities=query_capabilities,
        output_formats=output_formats,
        supported_data_source_localities=(),
        supported_credential_policies=("none",),
        cache_modes=("none",),
        deterministic=False,
        max_buffer_bytes=_optional_nonnegative_int(raw_fields.get("max_buffer_size")),
        axis_providers=(datoviz_v04_axis_provider_capability(dvz),),
        layout_capability=LayoutCapability(
            semantic_guides=True,
            resolved_layout_produce="none",
            resolved_layout_consume="none",
            layout_strict=False,
            diagnostics=(
                "panel_text_guide_as_screen_text",
                "resolved_layout_snapshot_unsupported",
                "axis_style_mapping_partial",
                "layout_strict_false",
            ),
        ),
        guide_layout_capability=GuideLayoutCapability(
            axis_native=True,
            axis_explicit_ticks=hasattr(dvz, "dvz_axis_set_ticks") if dvz is not None else False,
            axis_deterministic_gsp_ticks=False,
            axis_labels=True,
            axis_grid=True,
            axis_grid_clip_to_plot_rect=False,
            axis_query=False,
            panel_text_title="adapted",
            panel_text_participates_in_layout=False,
            panel_text_query=False,
            colorbar="adapted",
            colorbar_query=False,
            legend="unsupported",
            diagnostics=(
                "panel_text_guide_as_screen_text",
                "axis_style_mapping_partial",
                "grid_clip_not_enforced",
                "guide_query_missing",
                "all_rendered_guides_unsupported",
            ),
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
            device_scale=False,
            dpi_metadata=False,
            physical_framebuffer_scale=False,
            diagnostics=("device_scale_reporting_unverified",),
        ),
        query_layout_capability=QueryLayoutCapability(
            screen_logical_px=True,
            data_readout_uses_view_snapshot=True,
            guide_query=False,
            all_rendered_guides=False,
            reports_layout_snapshot_id=False,
            diagnostics=(
                "guide_query_missing",
                "layout_snapshot_not_used",
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
                payloads=(QueryPayload.IDENTITY, QueryPayload.COORDINATE, QueryPayload.COLOR, QueryPayload.VALUE),
                diagnostics=("point source-value payload may be absent if Datoviz returns no value fields",),
            ),
            QueryTargetCapability(
                target_kind=QueryTargetKind.VISUAL_FAMILY,
                target="image",
                payloads=(QueryPayload.IDENTITY, QueryPayload.COORDINATE, QueryPayload.COLOR, QueryPayload.VALUE),
            ),
        ),
        diagnostics=("Datoviz v0.4 data query supports frontmost panel-coordinate requests only in this slice",),
    )


def datoviz_v04_capture_ready(dvz: ModuleType | Any) -> bool:
    """Return whether a facade exposes the bounded offscreen PNG capture path."""
    return not datoviz_v04_capture_diagnostics(dvz)


def datoviz_v04_capture_diagnostics(dvz: ModuleType | Any) -> tuple[str, ...]:
    """Return missing requirements for v0.4 offscreen PNG capture."""
    diagnostics = [f"missing {name}" for name in _REQUIRED_DVZ_CAPTURE_FUNCTIONS if not hasattr(dvz, name)]
    if not any(hasattr(dvz, name) for name in _DVZ_CAPTURE_RENDER_FUNCTIONS):
        diagnostics.append("missing one of dvz_view_render_once, dvz_app_render_once, dvz_app_run")
    return tuple(diagnostics)


def datoviz_v04_axis_provider_capability(dvz: ModuleType | Any | None = None) -> AxisProviderCapability:
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

    missing = tuple(name for name in _REQUIRED_DVZ_AXIS_FUNCTIONS if not hasattr(dvz, name))
    if missing:
        return _unsupported(f"Datoviz Python binding is missing v0.4-dev axis symbols: {missing}")

    supports_explicit_ticks = hasattr(dvz, "dvz_axis_set_ticks")
    explicit_tick_diagnostic = (
        "axis-provider-explicit-ticks: explicit GSP tick values and labels are wired through dvz_axis_set_ticks"
        if supports_explicit_ticks
        else "axis-provider-explicit-ticks-unsupported: missing dvz_axis_set_ticks"
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
        supports_guide_query=False,
        supports_text_query=False,
        diagnostics=(
            "axis-provider-selected: datoviz.v04.panel_axis.wip",
            "axis-provider-adapted: panel DATA domains use dvz_panel_set_domain; backend-native ticks remain adapted and strict guide promotion still excludes title/query semantics",
            explicit_tick_diagnostic,
            "axis-guide-query-unsupported: guide picking is deferred for Datoviz v0.4 RC",
            "all-rendered-guides-unsupported: all-rendered guide contributions require guide query support",
            "strict-guide-title-query-unverified: Datoviz guide rows remain adapted until title layout and guide query semantics are strict",
        ),
    )


def datoviz_v04_axis_symbols(dvz: ModuleType | Any) -> dict[str, bool]:
    """Return required/optional Datoviz axis symbol availability for diagnostics/tests."""
    names = _REQUIRED_DVZ_AXIS_FUNCTIONS + _OPTIONAL_DVZ_AXIS_FUNCTIONS
    return {name: hasattr(dvz, name) for name in names}


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


def _unsupported(diagnostic: str) -> AxisProviderCapability:
    return AxisProviderCapability(
        provider_id=DATOVIZ_V04_AXIS_PROVIDER,
        backend_id="datoviz",
        provider_status="unsupported",
        diagnostics=(diagnostic,),
    )
