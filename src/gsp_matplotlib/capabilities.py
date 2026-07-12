"""Matplotlib protocol capability declarations."""

from __future__ import annotations

from gsp.protocol import (
    AxisProviderCapability,
    CapabilitySnapshot,
    FontLayoutCapability,
    GuideLayoutCapability,
    LayoutCapability,
    MESH3D_DATA_VIEW3D_CAPABILITY,
    MESH3D_NDC_CAPABILITY,
    NavigationPlacement,
    QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
    QueryLayoutCapability,
    RenderTargetCapability,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    TransportKind,
    VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
    VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
)


MATPLOTLIB_NATIVE_AXIS_PROVIDER = "matplotlib.native.axes.v0"


def matplotlib_axis_provider_capability() -> AxisProviderCapability:
    """Return the native Matplotlib axis provider capability for the current slice."""
    return AxisProviderCapability(
        provider_id=MATPLOTLIB_NATIVE_AXIS_PROVIDER,
        backend_id="matplotlib",
        provider_status="strict",
        supports_explicit_ticks=True,
        supports_auto_ticks_gsp_policy=True,
        supports_backend_auto_ticks=True,
        supports_tick_labels=True,
        supports_axis_labels=True,
        supports_title=True,
        supports_grid=True,
        supports_style_basic=True,
        supports_guide_query=True,
        supports_text_query=False,
    )


def capability_snapshot() -> CapabilitySnapshot:
    """Return the Matplotlib reference capability surface."""
    return CapabilitySnapshot(
        server_name="matplotlib-reference",
        protocol_versions=("0.2",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32", "float64", "uint8", "rgba8"),
        texture_formats=("rgba8",),
        visual_families=(
            "point",
            "marker",
            "segment",
            "path",
            "image",
            "text",
            "mesh",
        ),
        query_modes=("panel-query", "point-item", "image-texel"),
        navigation_placements=(NavigationPlacement.CLIENT_SIDE.value,),
        navigation_capabilities=("interaction.view2d.navigation.v1",),
        view3d_capabilities=(
            VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
            VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
            MESH3D_DATA_VIEW3D_CAPABILITY,
            MESH3D_NDC_CAPABILITY,
            QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
        ),
        output_formats=("png", "svg", "pdf"),
        extensions=(TILED_IMAGE_EXTENSION_CAPABILITY,),
        supports_extension_manifests=True,
        supports_virtual_data_sources=True,
        supports_tiled_image_sources=True,
        supports_synthetic_data_sources=True,
        supports_in_memory_data_sources=True,
        supported_data_source_localities=("synthetic", "in-memory"),
        supported_credential_policies=("none",),
        cache_modes=("none", "session-memory"),
        max_tiles_per_request=256,
        max_mosaic_pixels=4096,
        deterministic=True,
        metadata={"profile_id": "gsp.matplotlib@0.2"},
        axis_providers=(matplotlib_axis_provider_capability(),),
        layout_capability=LayoutCapability(
            semantic_guides=True,
            resolved_layout_produce="full",
            layout_strict=False,
            diagnostics=("layout_strict-awaits-readback-snapshot-contract",),
        ),
        guide_layout_capability=GuideLayoutCapability(
            axis_native=True,
            axis_explicit_ticks=True,
            axis_deterministic_gsp_ticks=True,
            axis_labels=True,
            axis_grid=True,
            axis_grid_clip_to_plot_rect=True,
            axis_query=True,
            panel_text_title="native",
            panel_text_participates_in_layout=True,
            panel_text_query=True,
            colorbar="native",
            colorbar_query=False,
            legend="unsupported",
            diagnostics=("layout-strict-promotion-pending",),
        ),
        font_layout_capability=FontLayoutCapability(
            logical_font_size_px=True,
            font_family_request=True,
            font_fallback_report=False,
            text_measurement="backend",
            font_metrics_profile="backend_defined",
        ),
        render_target_capability=RenderTargetCapability(
            logical_pixels=True,
            device_scale=True,
            dpi_metadata=True,
            physical_framebuffer_scale=False,
        ),
        query_layout_capability=QueryLayoutCapability(
            screen_logical_px=True,
            data_readout_uses_view_snapshot=True,
            guide_query=True,
            all_rendered_guides=True,
            reports_layout_snapshot_id=True,
            diagnostics=("layout-strict-promotion-pending",),
        ),
    )
