"""Tests for the accepted S035 View2D navigation protocol model."""

import math

import pytest

import gsp.protocol.navigation as navigation_module
from gsp.protocol import (
    AdaptationOutcome,
    CapabilitySnapshot,
    LogicalPixelRect,
    NavigationActionKind,
    NavigationDiagnosticCode,
    NavigationPlacement,
    NavigationPointerEvent,
    NavigationPointerEventKind,
    NavigationResult,
    PanByAction,
    ResetViewAction,
    SetViewAction,
    TransportKind,
    View2D,
    View2DNavigationInputAdapter,
    View2DNavigationController,
    ZoomAboutAction,
    navigation_pointer_event_from_ndc,
    pan_view2d,
    zoom_view2d_about,
)


def test_view2d_navigation_controller_targets_one_panel_view_pair():
    home = View2D(id="view:main", panel_id="panel:main", x_range=(-2.0, 2.0))
    controller = View2DNavigationController(
        id="nav:main",
        panel_id="panel:main",
        view_id="view:main",
        current_view2d_revision="view-rev:1",
        home_view=home,
    )

    assert controller.enabled is True
    assert controller.home_view is home

    with pytest.raises(ValueError, match="home_view id"):
        View2DNavigationController(
            id="nav:bad",
            panel_id="panel:main",
            view_id="view:main",
            current_view2d_revision="view-rev:1",
            home_view=View2D(id="view:other", panel_id="panel:main"),
        )

    with pytest.raises(TypeError, match="enabled"):
        View2DNavigationController(
            id="nav:bad",
            panel_id="panel:main",
            view_id="view:main",
            current_view2d_revision="view-rev:1",
            enabled="yes",  # type: ignore[arg-type]
        )


def test_pan_and_zoom_actions_validate_finite_values_and_positive_zoom():
    pan = PanByAction(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        dx_px=12.5,
        dy_px=-4.0,
        layout_snapshot_id="layout:main",
    )
    zoom = ZoomAboutAction(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        anchor_px=(320.0, 240.0),
        factor_x=1.2,
        factor_y=0.8,
    )

    assert pan.kind is NavigationActionKind.PAN_BY
    assert zoom.kind is NavigationActionKind.ZOOM_ABOUT

    with pytest.raises(ValueError, match=NavigationDiagnosticCode.NAVIGATION_NONFINITE.value):
        PanByAction(
            controller_id="nav:main",
            view2d_revision="view-rev:1",
            dx_px=float("nan"),
            dy_px=0.0,
        )

    with pytest.raises(
        ValueError, match=NavigationDiagnosticCode.NAVIGATION_INVALID_ZOOM_FACTOR.value
    ):
        ZoomAboutAction(
            controller_id="nav:main",
            view2d_revision="view-rev:1",
            anchor_px=(0.0, 0.0),
            factor_x=0.0,
            factor_y=1.0,
        )


def test_set_and_reset_view_actions_validate_view_and_revision_identity():
    view = View2D(id="view:main", panel_id="panel:main")

    set_view = SetViewAction(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        view=view,
    )
    reset = ResetViewAction(controller_id="nav:main", view2d_revision="view-rev:1")

    assert set_view.kind is NavigationActionKind.SET_VIEW
    assert reset.kind is NavigationActionKind.RESET_VIEW

    with pytest.raises(TypeError, match="view must be a View2D"):
        SetViewAction(
            controller_id="nav:main",
            view2d_revision="view-rev:1",
            view=object(),  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="invalid protocol id"):
        ResetViewAction(controller_id="nav:main", view2d_revision="bad id")


def test_navigation_result_requires_new_view_when_accepted_and_diagnostics_when_rejected():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(0.0, 10.0))
    accepted = NavigationResult(
        accepted=True,
        controller_id="nav:main",
        old_view2d_revision="view-rev:1",
        new_view2d_revision="view-rev:2",
        view=view,
        view_snapshot_id="view-snapshot:2",
        layout_snapshot_id="layout:main",
    )

    assert accepted.view is view
    assert accepted.new_view2d_revision == "view-rev:2"

    with pytest.raises(ValueError, match="accepted navigation results"):
        NavigationResult(
            accepted=True,
            controller_id="nav:main",
            old_view2d_revision="view-rev:1",
        )

    rejected = NavigationResult(
        accepted=False,
        controller_id="nav:main",
        old_view2d_revision="view-rev:1",
        diagnostics=(NavigationDiagnosticCode.NAVIGATION_STALE_VIEW.value,),
    )
    assert rejected.view is None

    with pytest.raises(ValueError, match="rejected navigation results"):
        NavigationResult(
            accepted=False,
            controller_id="nav:main",
            old_view2d_revision="view-rev:1",
        )


def test_navigation_capabilities_adapt_semantic_support_and_placement():
    caps = CapabilitySnapshot(
        server_name="navigation-test",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        navigation_placements=(NavigationPlacement.RETAINED_GPU_STATE.value,),
        navigation_capabilities=("interaction.view2d.navigation.v1",),
    )

    assert caps.supports_navigation_placement(NavigationPlacement.RETAINED_GPU_STATE)
    assert caps.supports_navigation_capability("interaction.view2d.navigation.v1")
    assert (
        caps.adapt_navigation_capability("interaction.view2d.navigation.v1").outcome
        == AdaptationOutcome.ACCEPT
    )

    rejected = caps.adapt_navigation_capability("interaction.view3d.navigation.v1")
    assert rejected.outcome == AdaptationOutcome.REJECT
    assert rejected.diagnostic is not None


def test_pan_view2d_moves_limits_by_signed_data_span():
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(0.0, 100.0),
        y_range=(50.0, -50.0),
    )
    panel_rect = LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0)

    panned = pan_view2d(view, panel_rect, dx_px=40.0, dy_px=20.0)

    assert panned.x_range == pytest.approx((-10.0, 90.0))
    assert panned.y_range == pytest.approx((60.0, -40.0))
    assert panned.id == view.id
    assert panned.panel_id == view.panel_id


def test_zoom_view2d_about_anchor_preserves_anchor_data_coordinate():
    view = View2D(id="view:main", panel_id="panel:main", x_range=(0.0, 100.0), y_range=(0.0, 80.0))
    panel_rect = LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0)

    zoomed = zoom_view2d_about(
        view,
        panel_rect,
        anchor_px=(110.0, 120.0),
        factor_x=2.0,
        factor_y=4.0,
    )

    assert zoomed.x_range == pytest.approx((12.5, 62.5))
    assert zoomed.y_range == pytest.approx((30.0, 50.0))


def test_zoom_view2d_about_preserves_reversed_limits():
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(100.0, 0.0),
        y_range=(80.0, 0.0),
    )
    panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=400.0, height=200.0)

    zoomed = zoom_view2d_about(
        view,
        panel_rect,
        anchor_px=(100.0, 100.0),
        factor_x=2.0,
        factor_y=2.0,
    )

    assert zoomed.x_range == pytest.approx((87.5, 37.5))
    assert zoomed.y_range == pytest.approx((60.0, 20.0))


def test_navigation_math_rejects_invalid_panel_rect():
    view = View2D(id="view:main", panel_id="panel:main")
    panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=0.0, height=100.0)

    with pytest.raises(
        ValueError, match=NavigationDiagnosticCode.NAVIGATION_INVALID_PANEL_RECT.value
    ):
        pan_view2d(view, panel_rect, dx_px=1.0, dy_px=0.0)


def test_navigation_input_adapter_emits_incremental_pan_actions():
    adapter = View2DNavigationInputAdapter(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        panel_rect=LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0),
        layout_snapshot_id="layout:main",
    )

    assert (
        adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.BUTTON_PRESS,
                x_px=110.0,
                y_px=120.0,
                left_button=True,
            )
        )
        is None
    )
    first_pan = adapter.handle_pointer_event(
        NavigationPointerEvent(
            kind=NavigationPointerEventKind.MOUSE_MOVE,
            x_px=130.0,
            y_px=115.0,
        )
    )
    second_pan = adapter.handle_pointer_event(
        NavigationPointerEvent(
            kind=NavigationPointerEventKind.MOUSE_MOVE,
            x_px=125.0,
            y_px=135.0,
        )
    )

    assert isinstance(first_pan, PanByAction)
    assert first_pan.dx_px == pytest.approx(20.0)
    assert first_pan.dy_px == pytest.approx(-5.0)
    assert first_pan.view2d_revision == "view-rev:1"
    assert first_pan.layout_snapshot_id == "layout:main"
    assert isinstance(second_pan, PanByAction)
    assert second_pan.dx_px == pytest.approx(-5.0)
    assert second_pan.dy_px == pytest.approx(20.0)

    assert (
        adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.BUTTON_RELEASE,
                x_px=125.0,
                y_px=135.0,
            )
        )
        is None
    )
    assert (
        adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.MOUSE_MOVE,
                x_px=150.0,
                y_px=150.0,
            )
        )
        is None
    )


def test_navigation_input_adapter_emits_wheel_zoom_and_tracks_accepted_revision():
    panel_rect = LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0)
    adapter = View2DNavigationInputAdapter(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        panel_rect=panel_rect,
    )

    zoom = adapter.handle_pointer_event(
        NavigationPointerEvent(
            kind=NavigationPointerEventKind.WHEEL,
            x_px=210.0,
            y_px=120.0,
            scroll_steps=2.0,
        )
    )

    assert isinstance(zoom, ZoomAboutAction)
    assert zoom.anchor_px == pytest.approx((210.0, 120.0))
    expected_factor_x, expected_factor_y = (
        navigation_module._DatovizPanzoomProfile.for_platform().wheel_zoom_factor(
            panel_rect, 2.0
        )
    )
    assert zoom.factor_x == pytest.approx(expected_factor_x)
    assert zoom.factor_y == pytest.approx(expected_factor_y)
    assert zoom.view2d_revision == "view-rev:1"

    result = NavigationResult(
        accepted=True,
        controller_id="nav:main",
        old_view2d_revision="view-rev:1",
        new_view2d_revision="view-rev:2",
        view=View2D(id="view:main", panel_id="panel:main"),
    )
    adapter.accept_navigation_result(result)

    next_zoom = adapter.handle_pointer_event(
        NavigationPointerEvent(
            kind=NavigationPointerEventKind.WHEEL,
            x_px=210.0,
            y_px=120.0,
            scroll_steps=-1.0,
        )
    )
    assert isinstance(next_zoom, ZoomAboutAction)
    assert next_zoom.view2d_revision == "view-rev:2"
    expected_next_factor_x, expected_next_factor_y = (
        navigation_module._DatovizPanzoomProfile.for_platform().wheel_zoom_factor(
            panel_rect, -1.0
        )
    )
    assert next_zoom.factor_x == pytest.approx(expected_next_factor_x)
    assert next_zoom.factor_y == pytest.approx(expected_next_factor_y)


def test_navigation_input_adapter_emits_right_drag_axis_zoom_actions():
    panel_rect = LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0)
    adapter = View2DNavigationInputAdapter(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        panel_rect=panel_rect,
        layout_snapshot_id="layout:main",
    )

    assert (
        adapter.handle_pointer_event(
            NavigationPointerEvent(
                kind=NavigationPointerEventKind.BUTTON_PRESS,
                x_px=210.0,
                y_px=120.0,
                right_button=True,
            )
        )
        is None
    )
    zoom = adapter.handle_pointer_event(
        NavigationPointerEvent(
            kind=NavigationPointerEventKind.MOUSE_MOVE,
            x_px=230.0,
            y_px=110.0,
        )
    )

    assert isinstance(zoom, ZoomAboutAction)
    assert zoom.anchor_px == pytest.approx((210.0, 120.0))
    expected_factor_x, expected_factor_y = (
        navigation_module._DatovizPanzoomProfile.for_platform().drag_zoom_factor(
            panel_rect, 20.0, -10.0
        )
    )
    assert zoom.factor_x == pytest.approx(expected_factor_x)
    assert zoom.factor_y == pytest.approx(expected_factor_y)
    assert zoom.layout_snapshot_id == "layout:main"


def test_navigation_input_adapter_emits_double_click_reset_action():
    adapter = View2DNavigationInputAdapter(
        controller_id="nav:main",
        view2d_revision="view-rev:1",
        panel_rect=LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0),
        layout_snapshot_id="layout:main",
    )

    action = adapter.handle_pointer_event(
        NavigationPointerEvent(
            kind=NavigationPointerEventKind.DOUBLE_CLICK,
            x_px=210.0,
            y_px=120.0,
        )
    )

    assert isinstance(action, ResetViewAction)
    assert action.controller_id == "nav:main"
    assert action.view2d_revision == "view-rev:1"
    assert action.layout_snapshot_id == "layout:main"


def test_datoviz_panzoom_profile_matches_platform_constants_and_formulas():
    apple = navigation_module._DatovizPanzoomProfile.for_platform("darwin")
    other = navigation_module._DatovizPanzoomProfile.for_platform("linux")
    panel_rect = LogicalPixelRect(x=0.0, y=0.0, width=800.0, height=400.0)

    assert apple.drag_coef == pytest.approx(0.003)
    assert apple.wheel_coef == pytest.approx(12.0)
    assert other.drag_coef == pytest.approx(0.002)
    assert other.wheel_coef == pytest.approx(120.0)

    drag_x, drag_y = apple.drag_zoom_factor(panel_rect, 40.0, -20.0)
    assert drag_x == pytest.approx(math.exp(0.003 * 600.0 * (2.0 * 40.0 / 800.0)))
    assert drag_y == pytest.approx(math.exp(0.003 * 600.0 * (2.0 * -20.0 / 400.0)))

    wheel_x, wheel_y = apple.wheel_zoom_factor(panel_rect, 2.0)
    shift_x = 12.0 * (2.0 / 4.0)
    shift_y = -(400.0 / 800.0) * shift_x
    assert wheel_x == pytest.approx(math.exp(0.003 * 600.0 * (2.0 * shift_x / 800.0)))
    assert wheel_y == pytest.approx(math.exp(0.003 * 600.0 * (-2.0 * shift_y / 400.0)))

    assert apple.clamp_zoom(0.0) == pytest.approx(1.0)
    assert apple.clamp_zoom(1e-6) == pytest.approx(1e-3)
    assert apple.clamp_zoom(1e6) == pytest.approx(1e4)


def test_navigation_pointer_event_from_ndc_resolves_logical_pixels():
    panel_rect = LogicalPixelRect(x=10.0, y=20.0, width=400.0, height=200.0)

    event = navigation_pointer_event_from_ndc(
        kind=NavigationPointerEventKind.WHEEL,
        x_ndc=-0.5,
        y_ndc=0.25,
        panel_rect=panel_rect,
        scroll_steps=1.0,
    )

    assert event.x_px == pytest.approx(110.0)
    assert event.y_px == pytest.approx(145.0)
    assert event.scroll_steps == pytest.approx(1.0)

    press = navigation_pointer_event_from_ndc(
        kind=NavigationPointerEventKind.BUTTON_PRESS,
        x_ndc=0.0,
        y_ndc=0.0,
        panel_rect=panel_rect,
        right_button=True,
    )
    assert press.right_button is True


def test_navigation_input_adapter_rejects_invalid_pointer_adapter_state():
    with pytest.raises(TypeError, match="zoom_base"):
        View2DNavigationInputAdapter(
            controller_id="nav:main",
            view2d_revision="view-rev:1",
            panel_rect=LogicalPixelRect(x=0.0, y=0.0, width=100.0, height=100.0),
            zoom_base=1.0,  # type: ignore[call-arg]
        )

    with pytest.raises(TypeError, match="NavigationPointerEventKind"):
        NavigationPointerEvent(
            kind="wheel",  # type: ignore[arg-type]
            x_px=0.0,
            y_px=0.0,
        )
