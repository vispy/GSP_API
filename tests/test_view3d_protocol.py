"""Tests for the accepted S036/S047 View3D protocol baseline."""

import pytest

from gsp.protocol import (
    AdaptationOutcome,
    Camera3D,
    CapabilitySnapshot,
    DepthMode3D,
    DirectionalLight3D,
    FaceCulling,
    MESH3D_DATA_VIEW3D_CAPABILITY,
    Orbit3DPayload,
    OrthographicProjection3D,
    Pan3DPayload,
    PerspectiveProjection3D,
    ProjectedFaceClassification,
    Projection3DKind,
    QUERY_VIEW3D_MESH_TRIANGLE_PICK_FACING_CAPABILITY,
    QUERY_VIEW3D_MESH_TRIANGLE_PICK_GEOMETRY_CAPABILITY,
    QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY,
    QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
    QueryDiagnostic,
    QueryDiagnosticSeverity,
    QueryStatus,
    ResetView3DPayload,
    SetCamera3DPayload,
    SetProjection3DPayload,
    TransportKind,
    VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
    VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
    VIEW3D_NAVIGATION_ORBIT_PAN_ZOOM_CAPABILITY,
    View3D,
    View3DDiagnosticCode,
    View3DMeshPickDiagnosticCode,
    View3DMeshTrianglePickGeometryPayload,
    View3DMeshTrianglePickPayload,
    View3DMeshTrianglePickRequest,
    View3DNavigationAction,
    View3DNavigationActionKind,
    ViewKind,
    Zoom3DPayload,
    apply_view3d_navigation_action,
    classify_projected_triangle,
    face_culling_excludes,
    mesh_pick_barycentric_2d,
    mesh_pick_data_xyz,
    mesh_pick_panel_ndc_z,
    mesh_pick_projected_front_facing,
    orbit_view3d,
    pan_view3d,
    project_view3d_data_point,
    projected_triangle_area2,
    projected_triangle_has_strict_contribution,
    resolve_view3d_projection_snapshot,
    unproject_view3d_panel_ndc_point,
    zoom_view3d,
)


def test_camera3d_accepts_canonical_basis():
    camera = Camera3D(
        eye=(0.0, 0.0, 1.0),
        target=(0.0, 0.0, 0.0),
        up=(0.0, 1.0, 0.0),
    )

    basis = camera.basis()

    assert basis.forward == pytest.approx((0.0, 0.0, -1.0))
    assert basis.right == pytest.approx((1.0, -0.0, 0.0))
    assert basis.true_up == pytest.approx((0.0, 1.0, 0.0))


@pytest.mark.parametrize(
    "camera",
    (
        Camera3D,
    ),
)
def test_camera3d_rejects_degenerate_inputs(camera):
    diagnostic = View3DDiagnosticCode.VIEW3D_INVALID_CAMERA_DEGENERATE.value

    with pytest.raises(ValueError, match=diagnostic):
        camera(eye=(0.0, 0.0, 0.0), target=(0.0, 0.0, 0.0), up=(0.0, 1.0, 0.0))

    with pytest.raises(ValueError, match=diagnostic):
        camera(eye=(0.0, 0.0, 1.0), target=(0.0, 0.0, 0.0), up=(0.0, 0.0, 0.0))

    with pytest.raises(ValueError, match=diagnostic):
        camera(eye=(0.0, 0.0, 1.0), target=(0.0, 0.0, 0.0), up=(0.0, 0.0, 2.0))

    with pytest.raises(ValueError, match=diagnostic):
        camera(eye=(0.0, 0.0, 1.0), target=(0.0, 0.0, 0.0), up=(float("nan"), 1.0, 0.0))


def test_orthographic_projection_accepts_reversed_xy_and_rejects_bad_ranges():
    projection = OrthographicProjection3D(
        xlim=(1.0, -1.0),
        ylim=(2.0, -2.0),
        near_far=(0.1, 10.0),
    )

    assert projection.kind is Projection3DKind.ORTHOGRAPHIC
    assert projection.xlim == (1.0, -1.0)
    assert projection.ylim == (2.0, -2.0)

    diagnostic = View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value
    with pytest.raises(ValueError, match=diagnostic):
        OrthographicProjection3D(xlim=(1.0, 1.0))
    with pytest.raises(ValueError, match=diagnostic):
        OrthographicProjection3D(ylim=(0.0, float("inf")))
    with pytest.raises(ValueError, match=diagnostic):
        OrthographicProjection3D(near_far=(-0.1, 1.0))
    with pytest.raises(ValueError, match=diagnostic):
        OrthographicProjection3D(near_far=(1.0, 1.0))
    with pytest.raises(ValueError, match=diagnostic):
        OrthographicProjection3D(near_far=(2.0, 1.0))


def test_orthographic_projection_rejects_non_orthographic_kind():
    with pytest.raises(
        ValueError,
        match=View3DDiagnosticCode.VIEW3D_PROJECTION_UNSUPPORTED.value,
    ):
        OrthographicProjection3D(kind="perspective")  # type: ignore[arg-type]


def test_perspective_projection_accepts_fov_and_rejects_bad_ranges():
    projection = PerspectiveProjection3D(
        fov_y_degrees=60.0,
        near_far=(0.1, 100.0),
        aspect_ratio=16.0 / 9.0,
    )

    assert projection.kind is Projection3DKind.PERSPECTIVE
    assert projection.fov_y_degrees == 60.0
    assert projection.aspect_ratio == pytest.approx(16.0 / 9.0)

    diagnostic = View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value
    with pytest.raises(ValueError, match=diagnostic):
        PerspectiveProjection3D(fov_y_degrees=0.0)
    with pytest.raises(ValueError, match=diagnostic):
        PerspectiveProjection3D(fov_y_degrees=180.0)
    with pytest.raises(ValueError, match=diagnostic):
        PerspectiveProjection3D(near_far=(0.0, 10.0))
    with pytest.raises(ValueError, match=diagnostic):
        PerspectiveProjection3D(near_far=(10.0, 1.0))
    with pytest.raises(ValueError, match=diagnostic):
        PerspectiveProjection3D(aspect_ratio=0.0)


def test_perspective_projection_rejects_non_perspective_kind():
    with pytest.raises(
        ValueError,
        match=View3DDiagnosticCode.VIEW3D_PROJECTION_UNSUPPORTED.value,
    ):
        PerspectiveProjection3D(kind="orthographic")  # type: ignore[arg-type]


def test_view3d_targets_one_panel_and_validates_runtime_fields():
    camera = Camera3D(
        eye=(0.0, 0.0, 5.0),
        target=(0.0, 0.0, 0.0),
        up=(0.0, 1.0, 0.0),
    )
    projection = OrthographicProjection3D(near_far=(1.0, 10.0))
    view = View3D(
        id="view:main3d",
        panel_id="panel:main",
        camera=camera,
        projection=projection,
        revision=2,
        ambient_light_intensity=0.25,
        directional_light=DirectionalLight3D(
            direction_to_light=(0.0, 0.0, 1.0),
            intensity=0.75,
        ),
    )

    assert view.kind is ViewKind.VIEW3D_CAMERA
    assert view.depth_mode is DepthMode3D.OPAQUE_LESS
    assert view.revision == 2
    assert view.ambient_light_intensity == 0.25
    assert view.directional_light is not None
    assert view.directional_light.intensity == 0.75

    with pytest.raises(TypeError, match="camera"):
        View3D(
            id="view:bad",
            panel_id="panel:main",
            camera=object(),  # type: ignore[arg-type]
            projection=projection,
        )

    with pytest.raises(TypeError, match="projection"):
        View3D(
            id="view:bad",
            panel_id="panel:main",
            camera=camera,
            projection=object(),  # type: ignore[arg-type]
        )

    with pytest.raises(ValueError, match="revision"):
        View3D(
            id="view:bad",
            panel_id="panel:main",
            camera=camera,
            projection=projection,
            revision=-1,
        )

    perspective = View3D(
        id="view:perspective",
        panel_id="panel:main",
        camera=camera,
        projection=PerspectiveProjection3D(),
    )
    assert perspective.projection.kind is Projection3DKind.PERSPECTIVE


def test_directional_light3d_validates_s039_fields():
    light = DirectionalLight3D(direction_to_light=(0.0, 0.0, 2.0), intensity=0.5)

    assert light.direction_to_light == (0.0, 0.0, 2.0)
    assert light.intensity == 0.5

    with pytest.raises(ValueError, match="directional_light_direction_invalid"):
        DirectionalLight3D(direction_to_light=(0.0, 0.0, 0.0))
    with pytest.raises(ValueError, match="directional_light_direction_invalid"):
        DirectionalLight3D(direction_to_light=(float("nan"), 0.0, 1.0))
    with pytest.raises(ValueError, match="directional_light_intensity_invalid"):
        DirectionalLight3D(direction_to_light=(0.0, 0.0, 1.0), intensity=1.5)


def test_view3d_rejects_invalid_s039_lighting_fields():
    camera = Camera3D(
        eye=(0.0, 0.0, 5.0),
        target=(0.0, 0.0, 0.0),
        up=(0.0, 1.0, 0.0),
    )
    projection = OrthographicProjection3D(near_far=(1.0, 10.0))

    with pytest.raises(ValueError, match="ambient_light_invalid"):
        View3D(
            id="view:bad",
            panel_id="panel:main",
            camera=camera,
            projection=projection,
            ambient_light_intensity=-0.1,
        )
    with pytest.raises(TypeError, match="directional_light"):
        View3D(
            id="view:bad",
            panel_id="panel:main",
            camera=camera,
            projection=projection,
            directional_light=object(),  # type: ignore[arg-type]
        )


def test_view3d_capabilities_adapt_semantic_support():
    caps = CapabilitySnapshot(
        server_name="view3d-test",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        view3d_capabilities=(
            VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
            MESH3D_DATA_VIEW3D_CAPABILITY,
            QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
            QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY,
            VIEW3D_NAVIGATION_ORBIT_PAN_ZOOM_CAPABILITY,
            VIEW3D_STATIC_PERSPECTIVE_CAPABILITY,
        ),
    )

    assert caps.supports_view3d_capability(VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY)
    assert (
        caps.adapt_view3d_capability(VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY).outcome
        == AdaptationOutcome.ACCEPT
    )

    rejected = caps.adapt_view3d_capability("view3d.perspective.v1")
    assert rejected.outcome == AdaptationOutcome.REJECT
    assert rejected.diagnostic is not None
    assert caps.supports_view3d_capability(VIEW3D_STATIC_PERSPECTIVE_CAPABILITY)


def test_view3d_mesh_triangle_pick_request_and_payload_validate_s044_fields():
    request = View3DMeshTrianglePickRequest(
        view_id="view:main",
        panel_id="panel:main",
        panel_xy=(12.0, 24.0),
        expected_layout_snapshot_id="layout:main",
        expected_view_revision=3,
        expected_view_projection_snapshot_id="view3d-projection:abc",
        expected_pick_scene_snapshot_id="pick-scene:abc",
    )
    diagnostic = QueryDiagnostic(
        code=View3DMeshPickDiagnosticCode.ADAPTED_CPU_REFERENCE,
        severity=QueryDiagnosticSeverity.INFO,
    )

    payload = View3DMeshTrianglePickPayload(
        status=QueryStatus.HIT,
        hit=True,
        view_id=request.view_id,
        panel_id="panel:main",
        panel_xy=request.panel_xy,
        panel_ndc_xy=(0.0, 0.0),
        layout_snapshot_id="layout:main",
        view_revision=3,
        view_projection_snapshot_id="view3d-projection:abc",
        pick_scene_snapshot_id="pick-scene:abc",
        depth_mode="opaque_less",
        visual_id="visual:mesh",
        visual_type="MeshVisual",
        primitive_kind="triangle",
        primitive_index=2,
        diagnostics=(diagnostic,),
    )

    assert request.kind == QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY
    assert payload.kind == QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY
    assert payload.primitive_index == 2

    with pytest.raises(ValueError, match="visual_id is required"):
        View3DMeshTrianglePickPayload(
            status=QueryStatus.HIT,
            hit=True,
            view_id="view:main",
            panel_id="panel:main",
            panel_xy=(0.0, 0.0),
            panel_ndc_xy=(0.0, 0.0),
            layout_snapshot_id="layout:main",
            view_revision=0,
            view_projection_snapshot_id="view3d-projection:abc",
            pick_scene_snapshot_id="pick-scene:abc",
            depth_mode="opaque_less",
        )


def test_view3d_mesh_pick_geometry_helpers_interpolate_public_triangle_fields():
    q0 = (-1.0, -1.0, -0.5)
    q1 = (1.0, -1.0, 0.5)
    q2 = (-1.0, 1.0, 0.0)
    point_xy = (-0.5, -0.5)
    barycentric = mesh_pick_barycentric_2d(point_xy, q0, q1, q2)

    assert barycentric == pytest.approx((0.5, 0.25, 0.25))
    assert mesh_pick_panel_ndc_z(barycentric, q0, q1, q2) == pytest.approx(-0.125)
    assert mesh_pick_data_xyz(
        barycentric,
        (-1.0, -1.0, 0.0),
        (1.0, -1.0, 2.0),
        (-1.0, 1.0, 4.0),
    ) == pytest.approx((-0.5, -0.5, 1.5))
    assert mesh_pick_projected_front_facing(q0, q1, q2) is True
    assert mesh_pick_projected_front_facing(q0, q2, q1) is False
    assert mesh_pick_barycentric_2d((1.0, 1.0), q0, q1, q2) is None

    with pytest.raises(ValueError, match="projected-degenerate"):
        mesh_pick_projected_front_facing(q0, q0, q2)


def test_view3d_mesh_triangle_pick_geometry_payload_validates_s050_fields():
    diagnostic = QueryDiagnostic(
        code=View3DMeshPickDiagnosticCode.ADAPTED_PUBLIC_GEOMETRY_RECONSTRUCTION,
        severity=QueryDiagnosticSeverity.INFO,
    )
    payload = View3DMeshTrianglePickGeometryPayload(
        status=QueryStatus.HIT,
        hit=True,
        view_id="view:main",
        panel_id="panel:main",
        panel_xy=(12.0, 24.0),
        panel_ndc_xy=(0.0, 0.0),
        layout_snapshot_id="layout:main",
        view_revision=3,
        view_projection_snapshot_id="view3d-projection:abc",
        pick_scene_snapshot_id="pick-scene:abc",
        depth_mode="opaque_less",
        visual_id="visual:mesh",
        visual_type="MeshVisual",
        primitive_kind="triangle",
        primitive_index=2,
        hit_barycentric=(0.5, 0.25, 0.25),
        hit_panel_ndc_z=-0.125,
        hit_data_xyz=(-0.5, -0.5, 1.5),
        front_facing=True,
        diagnostics=(diagnostic,),
    )

    assert payload.kind == QUERY_VIEW3D_MESH_TRIANGLE_PICK_GEOMETRY_CAPABILITY
    assert QUERY_VIEW3D_MESH_TRIANGLE_PICK_FACING_CAPABILITY.endswith(".facing.v1")
    assert payload.hit_barycentric == pytest.approx((0.5, 0.25, 0.25))
    assert payload.front_facing is True

    with pytest.raises(ValueError, match="hit_barycentric is required"):
        View3DMeshTrianglePickGeometryPayload(
            status=QueryStatus.HIT,
            hit=True,
            view_id="view:main",
            panel_id="panel:main",
            panel_xy=(0.0, 0.0),
            panel_ndc_xy=(0.0, 0.0),
            layout_snapshot_id="layout:main",
            view_revision=0,
            view_projection_snapshot_id="view3d-projection:abc",
            pick_scene_snapshot_id="pick-scene:abc",
            depth_mode="opaque_less",
            visual_id="visual:mesh",
            visual_type="MeshVisual",
            primitive_kind="triangle",
            primitive_index=0,
            hit_panel_ndc_z=0.0,
            hit_data_xyz=(0.0, 0.0, 0.0),
        )

    with pytest.raises(ValueError, match="non-hit geometry payloads"):
        View3DMeshTrianglePickGeometryPayload(
            status=QueryStatus.MISS,
            hit=False,
            view_id="view:main",
            panel_id="panel:main",
            panel_xy=(0.0, 0.0),
            panel_ndc_xy=(0.0, 0.0),
            layout_snapshot_id="layout:main",
            view_revision=0,
            view_projection_snapshot_id="view3d-projection:abc",
            pick_scene_snapshot_id="pick-scene:abc",
            depth_mode="opaque_less",
            hit_barycentric=(1.0, 0.0, 0.0),
        )


def test_view3d_navigation_action_validates_payload_kind():
    view = _canonical_view3d(revision=2)
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )

    action = View3DNavigationAction(
        kind=View3DNavigationActionKind.PAN,
        view_id=view.id,
        base_view_revision=view.revision,
        base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        payload=Pan3DPayload(delta_view_right=1.0, delta_view_up=-0.5),
        base_layout_snapshot_id=snapshot.layout_snapshot_id,
    )

    assert action.kind is View3DNavigationActionKind.PAN
    assert action.base_view_revision == 2

    with pytest.raises(TypeError, match="pan"):
        View3DNavigationAction(
            kind=View3DNavigationActionKind.PAN,
            view_id=view.id,
            base_view_revision=view.revision,
            base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
            payload=Zoom3DPayload(scale=2.0),
        )

    with pytest.raises(
        ValueError,
        match=View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_ZOOM.value,
    ):
        Zoom3DPayload(scale=0.0)


def test_view3d_navigation_reducers_pan_zoom_and_orbit():
    view = _canonical_view3d()

    panned = pan_view3d(view, Pan3DPayload(delta_view_right=1.5, delta_view_up=-0.5))
    assert panned.revision == view.revision + 1
    assert panned.camera.eye == pytest.approx((1.5, -0.5, 5.0))
    assert panned.camera.target == pytest.approx((1.5, -0.5, 0.0))

    zoomed = zoom_view3d(view, Zoom3DPayload(scale=2.0))
    assert zoomed.revision == view.revision + 1
    assert zoomed.projection.xlim == pytest.approx((-1.0, 1.0))
    assert zoomed.projection.ylim == pytest.approx((-1.0, 1.0))

    anchored = zoom_view3d(
        view, Zoom3DPayload(scale=2.0, anchor_panel_ndc_xy=(-1.0, -1.0))
    )
    assert anchored.projection.xlim == pytest.approx((-2.0, 0.0))
    assert anchored.projection.ylim == pytest.approx((-2.0, 0.0))

    orbited = orbit_view3d(
        view,
        Orbit3DPayload(
            delta_yaw_radians=3.141592653589793 / 2.0,
            delta_pitch_radians=0.0,
        ),
    )
    assert orbited.revision == view.revision + 1
    assert orbited.camera.eye == pytest.approx((5.0, 0.0, 0.0))
    assert orbited.camera.target == pytest.approx(view.camera.target)


def test_view3d_navigation_reducer_zooms_perspective_by_dolly():
    view = _canonical_view3d(
        projection=PerspectiveProjection3D(
            fov_y_degrees=45.0,
            near_far=(0.1, 100.0),
            aspect_ratio=1.0,
        )
    )

    zoomed = zoom_view3d(view, Zoom3DPayload(scale=2.0))

    assert zoomed.revision == view.revision + 1
    assert zoomed.camera.eye == pytest.approx((0.0, 0.0, 2.5))
    assert zoomed.camera.target == pytest.approx(view.camera.target)
    assert zoomed.camera.up == pytest.approx(view.camera.up)
    assert zoomed.projection == view.projection

    zoomed_out = zoom_view3d(view, Zoom3DPayload(scale=0.5))
    assert zoomed_out.camera.eye == pytest.approx((0.0, 0.0, 10.0))

    with pytest.raises(
        ValueError,
        match=View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value,
    ):
        zoom_view3d(view, Zoom3DPayload(scale=2.0, anchor_panel_ndc_xy=(0.25, -0.25)))


def test_apply_view3d_navigation_action_accepts_and_refreshes_snapshot():
    view = _canonical_view3d(revision=3)
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    action = View3DNavigationAction(
        kind=View3DNavigationActionKind.ZOOM,
        view_id=view.id,
        base_view_revision=view.revision,
        base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        payload=Zoom3DPayload(scale=2.0),
        base_layout_snapshot_id=snapshot.layout_snapshot_id,
    )

    result = apply_view3d_navigation_action(
        view, action, layout_snapshot_id="layout:main"
    )

    assert result.accepted
    assert result.old_revision == 3
    assert result.new_revision == 4
    assert result.view is not None
    assert result.view.revision == 4
    assert result.projection is not None
    assert result.projection.xlim == pytest.approx((-1.0, 1.0))
    assert result.view_projection_snapshot_id != snapshot.view_projection_snapshot_id


def test_apply_view3d_navigation_action_rejects_stale_state():
    view = _canonical_view3d(revision=3)
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    stale_action = View3DNavigationAction(
        kind=View3DNavigationActionKind.PAN,
        view_id=view.id,
        base_view_revision=2,
        base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        payload=Pan3DPayload(delta_view_right=1.0, delta_view_up=0.0),
        base_layout_snapshot_id=snapshot.layout_snapshot_id,
    )

    result = apply_view3d_navigation_action(
        view, stale_action, layout_snapshot_id="layout:main"
    )

    assert not result.accepted
    assert result.view is None
    assert result.new_revision is None
    assert View3DDiagnosticCode.VIEW3D_NAVIGATION_SNAPSHOT_MISMATCH.value in result.diagnostics[0]


def test_apply_view3d_navigation_action_supports_setters_and_reset():
    view = _canonical_view3d(revision=1)
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    camera = Camera3D(
        eye=(1.0, 2.0, 6.0),
        target=(1.0, 2.0, 0.0),
        up=(0.0, 1.0, 0.0),
    )
    set_camera = View3DNavigationAction(
        kind=View3DNavigationActionKind.SET_CAMERA,
        view_id=view.id,
        base_view_revision=view.revision,
        base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        payload=SetCamera3DPayload(camera=camera),
    )

    result = apply_view3d_navigation_action(
        view, set_camera, layout_snapshot_id="layout:main"
    )
    assert result.accepted
    assert result.camera == camera

    updated = result.view
    assert updated is not None
    updated_snapshot = resolve_view3d_projection_snapshot(
        updated, layout_snapshot_id="layout:main"
    )
    projection = OrthographicProjection3D(xlim=(-4.0, 4.0), near_far=(1.0, 12.0))
    reset_action = View3DNavigationAction(
        kind=View3DNavigationActionKind.RESET,
        view_id=updated.id,
        base_view_revision=updated.revision,
        base_view_projection_snapshot_id=updated_snapshot.view_projection_snapshot_id,
        payload=ResetView3DPayload(camera=view.camera, projection=projection),
    )

    reset = apply_view3d_navigation_action(
        updated, reset_action, layout_snapshot_id="layout:main"
    )
    assert reset.accepted
    assert reset.camera == view.camera
    assert reset.projection == projection

    projection_snapshot = resolve_view3d_projection_snapshot(
        reset.view, layout_snapshot_id="layout:main"
    )
    set_projection = View3DNavigationAction(
        kind=View3DNavigationActionKind.SET_PROJECTION,
        view_id=reset.view.id,
        base_view_revision=reset.view.revision,
        base_view_projection_snapshot_id=projection_snapshot.view_projection_snapshot_id,
        payload=SetProjection3DPayload(projection=view.projection),
    )
    set_projection_result = apply_view3d_navigation_action(
        reset.view, set_projection, layout_snapshot_id="layout:main"
    )
    assert set_projection_result.accepted
    assert set_projection_result.projection == view.projection


def test_apply_view3d_navigation_accepts_perspective_zoom_dolly():
    view = _canonical_view3d(
        projection=PerspectiveProjection3D(
            fov_y_degrees=45.0,
            near_far=(0.1, 100.0),
            aspect_ratio=1.0,
        ),
        revision=3,
    )
    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    action = View3DNavigationAction(
        kind=View3DNavigationActionKind.ZOOM,
        view_id=view.id,
        base_view_revision=view.revision,
        base_view_projection_snapshot_id=snapshot.view_projection_snapshot_id,
        payload=Zoom3DPayload(scale=2.0),
        base_layout_snapshot_id=snapshot.layout_snapshot_id,
    )

    result = apply_view3d_navigation_action(
        view, action, layout_snapshot_id="layout:main"
    )

    assert result.accepted
    assert result.view is not None
    assert result.view.revision == view.revision + 1
    assert result.camera is not None
    assert result.camera.eye == pytest.approx((0.0, 0.0, 2.5))
    assert result.camera.target == pytest.approx(view.camera.target)
    assert result.projection == view.projection
    assert result.view_projection_snapshot_id != snapshot.view_projection_snapshot_id


def _canonical_view3d(
    *,
    revision: int = 0,
    projection: OrthographicProjection3D | PerspectiveProjection3D | None = None,
) -> View3D:
    return View3D(
        id="view:nav3d",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=projection
        or OrthographicProjection3D(
            xlim=(-2.0, 2.0),
            ylim=(-2.0, 2.0),
            near_far=(1.0, 10.0),
        ),
        revision=revision,
    )


def test_view3d_projects_canonical_cube_vertices_to_ndc3():
    view = View3D(
        id="view:cube",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-2.0, 2.0),
            ylim=(-2.0, 2.0),
            near_far=(1.0, 10.0),
        ),
    )

    assert project_view3d_data_point(view, (-2.0, -2.0, 4.0)) == pytest.approx(
        (-1.0, -1.0, -1.0)
    )
    assert project_view3d_data_point(view, (2.0, 2.0, -5.0)) == pytest.approx(
        (1.0, 1.0, 1.0)
    )
    assert project_view3d_data_point(view, (0.0, 0.0, -0.5)) == pytest.approx(
        (0.0, 0.0, 0.0)
    )


def test_projected_ndc_face_culling_helpers_classify_panel_winding():
    front_area = projected_triangle_area2(
        (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.0, 0.5, 0.0)
    )
    back_area = projected_triangle_area2(
        (-0.5, -0.5, 0.0), (0.0, 0.5, 0.0), (0.5, -0.5, 0.0)
    )

    assert front_area == pytest.approx(1.0)
    assert back_area == pytest.approx(-1.0)
    assert classify_projected_triangle(front_area) is ProjectedFaceClassification.FRONT
    assert classify_projected_triangle(back_area) is ProjectedFaceClassification.BACK
    assert classify_projected_triangle(0.0) is ProjectedFaceClassification.DEGENERATE
    assert not face_culling_excludes(
        ProjectedFaceClassification.FRONT, FaceCulling.BACK
    )
    assert face_culling_excludes(ProjectedFaceClassification.BACK, FaceCulling.BACK)
    assert projected_triangle_has_strict_contribution(front_area, FaceCulling.BACK)
    assert not projected_triangle_has_strict_contribution(front_area, FaceCulling.FRONT)
    assert not projected_triangle_has_strict_contribution(0.0, FaceCulling.NONE)


def test_projected_ndc_face_culling_uses_projected_view3d_bounds():
    normal_view = View3D(
        id="view:main",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 1.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-1.0, 1.0),
            ylim=(-1.0, 1.0),
            near_far=(0.0, 2.0),
        ),
    )
    reversed_x_view = View3D(
        id="view:main",
        panel_id="panel:main",
        camera=normal_view.camera,
        projection=OrthographicProjection3D(
            xlim=(1.0, -1.0),
            ylim=(-1.0, 1.0),
            near_far=(0.0, 2.0),
        ),
    )
    data_triangle = (
        (-0.5, -0.5, 0.0),
        (0.5, -0.5, 0.0),
        (0.0, 0.5, 0.0),
    )

    normal_projected = tuple(
        project_view3d_data_point(normal_view, point) for point in data_triangle
    )
    reversed_projected = tuple(
        project_view3d_data_point(reversed_x_view, point) for point in data_triangle
    )

    assert (
        classify_projected_triangle(projected_triangle_area2(*normal_projected))
        is ProjectedFaceClassification.FRONT
    )
    assert (
        classify_projected_triangle(projected_triangle_area2(*reversed_projected))
        is ProjectedFaceClassification.BACK
    )


def test_view3d_unprojects_panel_ndc3_to_data_space():
    view = View3D(
        id="view:unproject",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-2.0, 2.0),
            ylim=(-2.0, 2.0),
            near_far=(1.0, 10.0),
        ),
    )

    assert unproject_view3d_panel_ndc_point(view, (-1.0, -1.0, -1.0)) == pytest.approx(
        (-2.0, -2.0, 4.0)
    )
    assert unproject_view3d_panel_ndc_point(view, (1.0, 1.0, 1.0)) == pytest.approx(
        (2.0, 2.0, -5.0)
    )


def test_view3d_projects_perspective_points_to_ndc3():
    view = View3D(
        id="view:perspective-project",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 0.0),
            target=(0.0, 0.0, -1.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=90.0,
            near_far=(1.0, 10.0),
            aspect_ratio=1.0,
        ),
    )

    assert project_view3d_data_point(view, (0.0, 0.0, -1.0)) == pytest.approx(
        (0.0, 0.0, -1.0)
    )
    assert project_view3d_data_point(view, (1.0, 1.0, -1.0)) == pytest.approx(
        (1.0, 1.0, -1.0)
    )
    assert project_view3d_data_point(view, (0.0, 0.0, -5.5)) == pytest.approx(
        (0.0, 0.0, 0.0)
    )


def test_view3d_perspective_projection_uses_resolved_aspect_ratio():
    view = View3D(
        id="view:perspective-aspect",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 0.0),
            target=(0.0, 0.0, -1.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=90.0,
            near_far=(1.0, 10.0),
        ),
    )

    assert project_view3d_data_point(
        view, (2.0, 1.0, -1.0), aspect_ratio=2.0
    ) == pytest.approx((1.0, 1.0, -1.0))


def test_view3d_unprojects_perspective_panel_ndc3_to_data_space():
    view = View3D(
        id="view:perspective-unproject",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 0.0),
            target=(0.0, 0.0, -1.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=PerspectiveProjection3D(
            fov_y_degrees=90.0,
            near_far=(1.0, 10.0),
            aspect_ratio=1.0,
        ),
    )

    assert unproject_view3d_panel_ndc_point(view, (1.0, 1.0, -1.0)) == pytest.approx(
        (1.0, 1.0, -1.0)
    )
    assert unproject_view3d_panel_ndc_point(view, (0.0, 0.0, 0.0)) == pytest.approx(
        (0.0, 0.0, -5.5)
    )


def test_view3d_projection_preserves_reversed_xy_bounds():
    view = View3D(
        id="view:reversed",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(2.0, -2.0),
            ylim=(2.0, -2.0),
            near_far=(1.0, 10.0),
        ),
    )

    assert project_view3d_data_point(view, (-2.0, -2.0, 4.0)) == pytest.approx(
        (1.0, 1.0, -1.0)
    )


def test_view3d_projection_uses_explicit_off_axis_bounds():
    view = View3D(
        id="view:offaxis",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(0.0, 4.0),
            ylim=(-1.0, 3.0),
            near_far=(1.0, 10.0),
        ),
    )

    assert project_view3d_data_point(view, (0.0, 0.0, 4.0)) == pytest.approx(
        (-1.0, -0.5, -1.0)
    )


def test_view3d_projection_snapshot_identity_tracks_view_and_layout_state():
    view = View3D(
        id="view:snapshot",
        panel_id="panel:main",
        camera=Camera3D(
            eye=(0.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=OrthographicProjection3D(
            xlim=(-2.0, 2.0),
            ylim=(-2.0, 2.0),
            near_far=(1.0, 10.0),
        ),
        revision=3,
    )

    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    same = resolve_view3d_projection_snapshot(view, layout_snapshot_id="layout:main")
    different_layout = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:other"
    )
    updated_view = View3D(
        id=view.id,
        panel_id=view.panel_id,
        camera=Camera3D(
            eye=(1.0, 0.0, 5.0),
            target=(0.0, 0.0, 0.0),
            up=(0.0, 1.0, 0.0),
        ),
        projection=view.projection,
        revision=4,
    )
    updated = resolve_view3d_projection_snapshot(
        updated_view, layout_snapshot_id="layout:main"
    )

    assert snapshot.view_projection_snapshot_id.startswith("view3d-projection:")
    assert snapshot.view_projection_snapshot_id == same.view_projection_snapshot_id
    assert snapshot.view_projection_snapshot_id != different_layout.view_projection_snapshot_id
    assert snapshot.view_projection_snapshot_id != updated.view_projection_snapshot_id
    assert snapshot.view_revision == 3
    assert snapshot.forward == pytest.approx((0.0, 0.0, -1.0))


def test_view3d_perspective_projection_snapshot_tracks_projection_parameters():
    view = _canonical_view3d(
        projection=PerspectiveProjection3D(
            fov_y_degrees=45.0,
            near_far=(0.1, 100.0),
            aspect_ratio=1.5,
        )
    )
    changed = _canonical_view3d(
        projection=PerspectiveProjection3D(
            fov_y_degrees=60.0,
            near_far=(0.1, 100.0),
            aspect_ratio=1.5,
        )
    )

    snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id="layout:main"
    )
    changed_snapshot = resolve_view3d_projection_snapshot(
        changed, layout_snapshot_id="layout:main"
    )

    assert snapshot.projection_kind is Projection3DKind.PERSPECTIVE
    assert snapshot.xlim is None
    assert snapshot.ylim is None
    assert snapshot.fov_y_degrees == pytest.approx(45.0)
    assert snapshot.aspect_ratio == pytest.approx(1.5)
    assert snapshot.view_projection_snapshot_id != (
        changed_snapshot.view_projection_snapshot_id
    )
