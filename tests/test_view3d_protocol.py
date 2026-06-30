"""Tests for the accepted S036 static View3D protocol baseline."""

import pytest

from gsp.protocol import (
    AdaptationOutcome,
    Camera3D,
    CapabilitySnapshot,
    DepthMode3D,
    MESH3D_DATA_VIEW3D_CAPABILITY,
    OrthographicProjection3D,
    Projection3DKind,
    QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
    TransportKind,
    VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
    View3D,
    View3DDiagnosticCode,
    ViewKind,
    project_view3d_data_point,
    resolve_view3d_projection_snapshot,
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
    )

    assert view.kind is ViewKind.VIEW3D_CAMERA
    assert view.depth_mode is DepthMode3D.OPAQUE_LESS
    assert view.revision == 2

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


def test_view3d_capabilities_adapt_semantic_support():
    caps = CapabilitySnapshot(
        server_name="view3d-test",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        view3d_capabilities=(
            VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY,
            MESH3D_DATA_VIEW3D_CAPABILITY,
            QUERY_VIEW3D_RAY_READBACK_CAPABILITY,
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
