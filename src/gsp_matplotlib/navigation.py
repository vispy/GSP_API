"""Matplotlib reference application of S035 View2D navigation actions."""

from __future__ import annotations

from gsp.protocol import (
    LogicalPixelRect,
    NavigationDiagnosticCode,
    NavigationResult,
    PanByAction,
    ResetViewAction,
    SetViewAction,
    View2D,
    View2DNavigationController,
    ZoomAboutAction,
    pan_view2d,
    zoom_view2d_about,
)


NavigationAction = PanByAction | ZoomAboutAction | SetViewAction | ResetViewAction


def apply_view2d_navigation_action(
    controller: View2DNavigationController,
    current_view: View2D,
    panel_rect: LogicalPixelRect,
    action: NavigationAction,
    *,
    next_view2d_revision: str,
    view_snapshot_id: str | None = None,
    expected_layout_snapshot_id: str | None = None,
) -> NavigationResult:
    """Apply one deterministic S035 navigation action to a View2D.

    This is the Matplotlib reference path for programmatic navigation. It does not
    listen to GUI events; GUI backends may adapt mouse/wheel events into these
    protocol actions in later missions.
    """
    if action.controller_id != controller.id:
        return _reject(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_UNSUPPORTED,
            "navigation action targets a different controller",
        )
    if not controller.enabled:
        return _reject(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_DISABLED,
            "navigation controller is disabled",
        )
    if action.view2d_revision != controller.current_view2d_revision:
        return _reject(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_STALE_VIEW,
            "navigation action references a stale View2D revision",
        )
    if current_view.id != controller.view_id or current_view.panel_id != controller.panel_id:
        return _reject(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_UNSUPPORTED,
            "current View2D does not match the controller target",
        )
    if (
        expected_layout_snapshot_id is not None
        and action.layout_snapshot_id is not None
        and action.layout_snapshot_id != expected_layout_snapshot_id
    ):
        return _reject(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_STALE_LAYOUT,
            "navigation action references a stale layout snapshot",
        )

    if isinstance(action, PanByAction):
        next_view = pan_view2d(current_view, panel_rect, action.dx_px, action.dy_px)
    elif isinstance(action, ZoomAboutAction):
        next_view = zoom_view2d_about(
            current_view,
            panel_rect,
            action.anchor_px,
            action.factor_x,
            action.factor_y,
        )
    elif isinstance(action, SetViewAction):
        if action.view.id != controller.view_id or action.view.panel_id != controller.panel_id:
            return _reject(
                controller,
                action,
                NavigationDiagnosticCode.NAVIGATION_UNSUPPORTED,
                "set_view target does not match the controller target",
            )
        next_view = action.view
    elif isinstance(action, ResetViewAction):
        if controller.home_view is None:
            return _reject(
                controller,
                action,
                NavigationDiagnosticCode.NAVIGATION_RESET_UNAVAILABLE,
                "reset_view requires a controller home_view",
            )
        next_view = controller.home_view
    else:
        return _reject(
            controller,
            action,
            NavigationDiagnosticCode.NAVIGATION_UNSUPPORTED,
            "unsupported navigation action",
        )

    return NavigationResult(
        accepted=True,
        controller_id=controller.id,
        old_view2d_revision=controller.current_view2d_revision,
        new_view2d_revision=next_view2d_revision,
        view=next_view,
        view_snapshot_id=view_snapshot_id,
        layout_snapshot_id=action.layout_snapshot_id or expected_layout_snapshot_id,
    )


def _reject(
    controller: View2DNavigationController,
    action: NavigationAction,
    code: NavigationDiagnosticCode,
    message: str,
) -> NavigationResult:
    return NavigationResult(
        accepted=False,
        controller_id=controller.id,
        old_view2d_revision=action.view2d_revision,
        diagnostics=(f"{code.value}: {message}",),
        layout_snapshot_id=action.layout_snapshot_id,
    )
