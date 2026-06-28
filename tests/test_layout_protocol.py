"""Tests for the S029/S034 resolved layout protocol model."""

import pytest

from gsp.protocol import (
    AdaptationOutcome,
    CapabilitySnapshot,
    ConformanceTier,
    FontLayoutCapability,
    GuideLayoutCapability,
    LayoutCapability,
    LayoutDiagnostic,
    LayoutDiagnosticStatus,
    LayoutResolveRequest,
    LayoutResolveResult,
    LayoutResolveStatus,
    LogicalPixelRect,
    QueryLayoutCapability,
    QueryRequest,
    QueryResult,
    QueryStatus,
    RenderTarget,
    RenderTargetCapability,
    ResolvedGuideBox,
    ResolvedLayoutSnapshot,
    TransportKind,
    logical_px_to_points,
)
from gsp_matplotlib.capabilities import capability_snapshot as matplotlib_capability_snapshot
from gsp_datoviz.capabilities import gsp_capability_snapshot_from_datoviz


def test_render_target_uses_logical_pixels_and_device_scale():
    target = RenderTarget(
        logical_width_px=900,
        logical_height_px=650,
        device_scale=2.0,
        dpi=100,
    )

    assert target.framebuffer_width_px == 1800
    assert target.framebuffer_height_px == 1300
    assert logical_px_to_points(20.0, 100.0) == 14.4

    with pytest.raises(ValueError, match="device_scale"):
        RenderTarget(logical_width_px=900, logical_height_px=650, device_scale=0.0)


def test_resolved_layout_snapshot_records_plot_guides_and_grid_clip():
    target = RenderTarget(logical_width_px=900, logical_height_px=650)
    panel_rect = LogicalPixelRect(0, 0, 900, 650)
    plot_rect = LogicalPixelRect(80, 70, 760, 500)
    title_box = ResolvedGuideBox(
        guide_id="guide:title",
        kind="title",
        rect_px=LogicalPixelRect(80, 16, 760, 32),
        role="title",
    )
    snapshot = ResolvedLayoutSnapshot(
        snapshot_id="layout:main",
        render_target=target,
        panel_rect_px=panel_rect,
        plot_rect_px=plot_rect,
        view_id="view:main",
        title_boxes=(title_box,),
        grid_clip_rect_px=plot_rect,
    )

    assert snapshot.title_boxes == (title_box,)
    assert snapshot.grid_clip_rect_px == plot_rect
    assert snapshot.data_to_screen_transform == (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)

    with pytest.raises(ValueError, match="data_to_screen_transform"):
        ResolvedLayoutSnapshot(
            snapshot_id="layout:bad",
            render_target=target,
            panel_rect_px=panel_rect,
            plot_rect_px=plot_rect,
            data_to_screen_transform=(1.0, 2.0),
        )


def test_layout_resolve_result_requires_snapshot_or_diagnostic():
    request = LayoutResolveRequest(
        request_id="layout-request:main",
        scene_id="scene:main",
        render_target=RenderTarget(logical_width_px=640, logical_height_px=480),
    )
    snapshot = ResolvedLayoutSnapshot(
        snapshot_id="layout:main",
        render_target=request.render_target,
        panel_rect_px=LogicalPixelRect(0, 0, 640, 480),
        plot_rect_px=LogicalPixelRect(60, 40, 520, 380),
    )

    result = LayoutResolveResult(
        request_id=request.request_id,
        status=LayoutResolveStatus.RESOLVED,
        snapshot=snapshot,
    )

    assert result.snapshot is snapshot

    with pytest.raises(ValueError, match="require diagnostics"):
        LayoutResolveResult(request_id=request.request_id, status=LayoutResolveStatus.UNSUPPORTED)

    unsupported = LayoutResolveResult(
        request_id=request.request_id,
        status=LayoutResolveStatus.UNSUPPORTED,
        diagnostics=(
            LayoutDiagnostic(
                code="resolved_layout_unsupported",
                status=LayoutDiagnosticStatus.UNSUPPORTED,
            ),
        ),
    )
    assert unsupported.snapshot is None


def test_query_request_and_result_can_identify_layout_snapshot():
    request = QueryRequest(
        id="query:guide-title",
        panel_id="panel:main",
        coordinate=(10, 20),
        layout_snapshot_id="layout:main",
    )
    result = QueryResult(
        request_id=request.id,
        status=QueryStatus.MISS,
        hit=False,
        panel_coordinate=(10, 20),
        layout_snapshot_id=request.layout_snapshot_id,
    )

    assert result.layout_snapshot_id == "layout:main"

    with pytest.raises(ValueError, match="layout_snapshot_id"):
        QueryRequest(
            id="query:bad",
            panel_id="panel:main",
            coordinate=(0, 0),
            layout_snapshot_id="bad id",
        )


def test_layout_capabilities_adapt_tiers_and_validate_strict_claims():
    caps = CapabilitySnapshot(
        server_name="layout-test",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        layout_capability=LayoutCapability(
            semantic_guides=True,
            resolved_layout_produce="full",
            layout_strict=True,
        ),
        guide_layout_capability=GuideLayoutCapability(
            axis_native=True,
            axis_explicit_ticks=True,
            axis_deterministic_gsp_ticks=True,
            axis_grid_clip_to_plot_rect=True,
            panel_text_title="resolved",
            panel_text_participates_in_layout=True,
        ),
        font_layout_capability=FontLayoutCapability(logical_font_size_px=True, text_measurement="reference"),
        render_target_capability=RenderTargetCapability(logical_pixels=True, device_scale=True, dpi_metadata=True),
        query_layout_capability=QueryLayoutCapability(guide_query=True, reports_layout_snapshot_id=True),
    )

    assert caps.supports_layout_tier(ConformanceTier.SEMANTIC_STRICT)
    assert caps.supports_layout_tier(ConformanceTier.LAYOUT_STRICT)
    assert caps.adapt_layout_tier("layout_strict").outcome == AdaptationOutcome.ACCEPT

    rejected = caps.adapt_layout_tier(ConformanceTier.PIXEL_PARITY)
    assert rejected.outcome == AdaptationOutcome.REJECT

    with pytest.raises(ValueError, match="layout_strict requires"):
        LayoutCapability(layout_strict=True)


def test_backend_capability_postures_are_explicit_for_layout_work():
    mpl = matplotlib_capability_snapshot()
    dvz = gsp_capability_snapshot_from_datoviz(None, dvz=None)

    assert mpl.layout_capability.semantic_guides
    assert mpl.layout_capability.resolved_layout_produce == "partial"
    assert not mpl.layout_capability.layout_strict
    assert mpl.guide_layout_capability.panel_text_participates_in_layout

    assert dvz.layout_capability.semantic_guides
    assert dvz.layout_capability.resolved_layout_produce == "none"
    assert not dvz.layout_capability.layout_strict
    assert dvz.guide_layout_capability.panel_text_title == "adapted"
    assert "grid_clip_not_enforced" in dvz.guide_layout_capability.diagnostics
