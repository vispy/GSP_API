"""Datoviz v0.4-dev protocol capability declarations."""

from __future__ import annotations

from types import ModuleType
from typing import Any, cast

from gsp.protocol import (
    AxisProviderCapability,
    CapabilitySnapshot,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryOrderingGuarantee,
    QueryPayload,
    QueryScope,
    QueryScopeCapability,
    QueryTargetCapability,
    QueryTargetKind,
    TransportKind,
)
from gsp_datoviz.query import datoviz_v04_query_binding_diagnostics


DATOVIZ_V04_AXIS_PROVIDER = "datoviz.v04.panel_axis.wip"

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
    "dvz_axis_set_style",
    "dvz_axis_set_plot_margins",
    "dvz_panel_visible_domain",
    "dvz_panel_data_to_visual_positions",
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
            "RGBA8 image path is guarded: current Datoviz v0.4 facade lacks a public "
            "nearest-sampler setter, so the adapter refuses nearest images instead of "
            "silently rendering with linear sampling"
        ),
        "query_support": "deferred until DvzQueryResult is decodable from Python",
        "capture_support": "PNG capture is advertised only when offscreen view capture bindings are available",
        "axis_provider": "datoviz.v04.panel_axis.wip when v0.4-dev Python symbols are exposed",
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
        query_modes=query_modes,
        query_capabilities=query_capabilities,
        output_formats=output_formats,
        supported_data_source_localities=(),
        supported_credential_policies=("none",),
        cache_modes=("none",),
        deterministic=False,
        max_buffer_bytes=_optional_nonnegative_int(raw_fields.get("max_buffer_size")),
        axis_providers=(datoviz_v04_axis_provider_capability(dvz),),
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
        try:
            import datoviz as imported_dvz
        except ModuleNotFoundError:
            return _unsupported("Datoviz is not importable")
        else:
            dvz = imported_dvz

    missing = tuple(name for name in _REQUIRED_DVZ_AXIS_FUNCTIONS if not hasattr(dvz, name))
    if missing:
        return _unsupported(f"Datoviz Python binding is missing v0.4-dev axis symbols: {missing}")

    return AxisProviderCapability(
        provider_id=DATOVIZ_V04_AXIS_PROVIDER,
        backend_id="datoviz",
        provider_status="adapted",
        supports_explicit_ticks=False,
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
            "axis-provider-adapted: backend-native ticks used; explicit GSP ticks unsupported by verified binding",
            "axis-guide-query-unsupported: provider renders guides but cannot query tick labels",
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
