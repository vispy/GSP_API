"""Tests for semantic axis provider capability selection."""

import pytest

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    AxisGuideStyle,
    AxisProviderRequest,
    AxisSide,
    CapabilitySnapshot,
    TILED_IMAGE_EXTENSION_CAPABILITY,
    VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
    PanelTextGuide,
    PanelTextGuideStyle,
    PanelTextRole,
    TickSpec,
    TickSpecKind,
    TransportKind,
)
from gsp.protocol.capabilities import AxisProviderCapability
from gsp_matplotlib.capabilities import MATPLOTLIB_NATIVE_AXIS_PROVIDER, capability_snapshot


def test_matplotlib_advertises_strict_native_axis_provider():
    caps = capability_snapshot()
    provider = caps.axis_provider(MATPLOTLIB_NATIVE_AXIS_PROVIDER)

    assert provider is not None
    assert provider.provider_status == "strict"
    assert provider.supports_explicit_ticks
    assert provider.supports_axis_labels
    assert provider.supports_guide_query
    assert caps.supports_extension(TILED_IMAGE_EXTENSION_CAPABILITY)
    assert caps.guide_layout_capability.axis_query
    assert caps.query_layout_capability.guide_query
    assert caps.query_layout_capability.all_rendered_guides
    assert caps.query_layout_capability.reports_layout_snapshot_id
    assert caps.render_target_capability.device_scale
    assert not caps.render_target_capability.physical_framebuffer_scale
    assert caps.supports_extension_manifests
    assert caps.supports_virtual_data_sources
    assert caps.supports_tiled_image_sources
    assert caps.supports_synthetic_data_sources
    assert caps.supports_view3d_capability(VIEW3D_STATIC_PERSPECTIVE_CAPABILITY)


def test_axis_provider_selection_policies():
    generated = AxisProviderCapability(
        provider_id="gsp.reference.generated_primitives.v0",
        backend_id="reference",
        provider_status="strict",
    )
    native = AxisProviderCapability(
        provider_id="matplotlib.native.axes.v0",
        backend_id="matplotlib",
        provider_status="adapted",
    )
    caps = CapabilitySnapshot(
        server_name="test",
        protocol_versions=("0.2",),
        transports=(TransportKind.INPROC,),
        axis_providers=(generated, native),
    )

    assert caps.select_axis_provider(AxisProviderRequest(policy="require_strict_gsp")) == generated
    assert caps.select_axis_provider(AxisProviderRequest(policy="prefer_native")) == native
    assert caps.select_axis_provider(AxisProviderRequest(policy="generated_primitives_only")) == generated
    assert caps.select_axis_provider(AxisProviderRequest(policy="disabled")) is None


def test_semantic_axis_guide_intent_is_not_a_data_visual():
    ticks = TickSpec(
        kind=TickSpecKind.EXPLICIT,
        explicit_values=(0.0, 0.5, 1.0),
        explicit_labels=("zero", "half", "one"),
        target_count=None,
    )
    guide = AxisGuide(
        id="guide:x",
        view_id="view:main",
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        label_text="time",
        tick_spec=ticks,
    )
    title = PanelTextGuide(id="guide:title", panel_id="panel:main", role=PanelTextRole.TITLE, text="Demo")

    assert guide.tick_spec.explicit_values == (0.0, 0.5, 1.0)
    assert guide.label_text == "time"
    assert title.text == "Demo"


def test_guide_style_fields_are_logical_pixel_hints():
    style = AxisGuideStyle(
        axis_label_font_size_px=16.0,
        tick_label_font_size_px=12.0,
        tick_length_px=6.0,
        tick_width_px=1.5,
        tick_label_padding_px=4.0,
        axis_label_padding_px=8.0,
        grid_width_px=1.0,
        guide_margin_px=10.0,
    )
    title_style = PanelTextGuideStyle(title_font_size_px=20.0, guide_margin_px=12.0)

    guide = AxisGuide(
        id="guide:styled-x",
        view_id="view:main",
        dimension=AxisDimension.X,
        side=AxisSide.BOTTOM,
        style=style,
    )
    title = PanelTextGuide(
        id="guide:styled-title",
        panel_id="panel:main",
        role=PanelTextRole.TITLE,
        text="Styled",
        style=title_style,
    )

    assert guide.style.tick_width_px == 1.5
    assert title.style.title_font_size_px == 20.0

    with pytest.raises(ValueError, match="tick_width_px"):
        AxisGuideStyle(tick_width_px=-1.0)

    with pytest.raises(ValueError, match="title_font_size_px"):
        PanelTextGuideStyle(title_font_size_px=float("nan"))


def test_first_axis_guide_slice_rejects_unsupported_sides_and_bad_ticks():
    with pytest.raises(ValueError, match="bottom"):
        AxisGuide(id="guide:x", view_id="view:main", dimension=AxisDimension.X, side=AxisSide.LEFT)

    with pytest.raises(ValueError, match="labels"):
        TickSpec(kind=TickSpecKind.EXPLICIT, explicit_values=(0.0, 1.0), explicit_labels=("zero",))
