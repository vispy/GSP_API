"""Matplotlib protocol capability declarations."""

from __future__ import annotations

from gsp.protocol import AxisProviderCapability, CapabilitySnapshot, TILED_IMAGE_EXTENSION_CAPABILITY, TransportKind


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
        supports_guide_query=False,
        supports_text_query=False,
    )


def capability_snapshot() -> CapabilitySnapshot:
    """Return the Matplotlib reference capability surface."""
    return CapabilitySnapshot(
        server_name="matplotlib-reference",
        protocol_versions=("0.1", "0.2"),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32", "float64", "uint8", "rgba8"),
        texture_formats=("rgba8",),
        visual_families=("point", "image"),
        query_modes=("panel-query", "point-item", "image-texel"),
        output_formats=("png", "svg", "pdf"),
        extensions=(TILED_IMAGE_EXTENSION_CAPABILITY,),
        supports_extension_manifests=True,
        supports_virtual_data_sources=True,
        supports_tiled_image_sources=True,
        supports_synthetic_data_sources=True,
        max_tiles_per_request=256,
        max_mosaic_pixels=4096,
        deterministic=True,
        axis_providers=(matplotlib_axis_provider_capability(),),
    )
