"""Tests for the accepted S027 transform/view protocol model."""

import numpy as np
import pytest

from gsp.protocol import (
    AdaptationOutcome,
    AffineTransform2DResource,
    AspectPolicy,
    CapabilitySnapshot,
    CoordinateSpace,
    InlineAffineTransform2D,
    InverseStatus,
    PointVisual,
    QueryHit,
    QueryContributionKind,
    QueryResult,
    QueryStatus,
    TRANSFORM_QUERY_PAYLOAD_KIND,
    TransformDiagnosticCode,
    TransformKind,
    TransformPlacement,
    TransformQueryPayload,
    TransformRef,
    TransportKind,
    View2D,
    VisualTransformBinding,
)


IDENTITY = np.eye(3, dtype=np.float64)


def test_affine_transform_resource_accepts_identity_translate_scale_rotate_and_shear():
    matrices = (
        IDENTITY,
        np.array([[1.0, 0.0, 2.0], [0.0, 1.0, -3.0], [0.0, 0.0, 1.0]]),
        np.array([[2.0, 0.0, 0.0], [0.0, 0.5, 0.0], [0.0, 0.0, 1.0]]),
        np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
        np.array([[1.0, 0.25, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
    )

    for index, matrix in enumerate(matrices):
        transform = AffineTransform2DResource(
            id=f"transform:affine_{index}", matrix=matrix
        )
        assert transform.kind == TransformKind.AFFINE_2D
        assert np.allclose(transform.inverse_matrix @ matrix, IDENTITY)


@pytest.mark.parametrize(
    ("matrix", "diagnostic"),
    (
        (
            np.ones((2, 3), dtype=np.float64),
            TransformDiagnosticCode.TRANSFORM_BAD_SHAPE,
        ),
        (
            np.array(
                [[1.0, 0.0, 0.0], [0.0, np.inf, 0.0], [0.0, 0.0, 1.0]]
            ),
            TransformDiagnosticCode.TRANSFORM_NONFINITE,
        ),
        (
            np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.1, 1.0]]),
            TransformDiagnosticCode.TRANSFORM_NON_AFFINE,
        ),
        (
            np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]),
            TransformDiagnosticCode.TRANSFORM_SINGULAR,
        ),
    ),
)
def test_affine_transform_validation_rejects_invalid_matrices(matrix, diagnostic):
    with pytest.raises(ValueError, match=diagnostic.value):
        AffineTransform2DResource(id="transform:bad", matrix=matrix)


def test_affine_transform_rejects_deferred_3d_kind():
    with pytest.raises(ValueError, match="GSP_TRANSFORM_UNSUPPORTED_KIND"):
        AffineTransform2DResource(
            id="transform:bad", matrix=IDENTITY, kind=TransformKind.AFFINE_3D
        )


def test_inline_and_ref_visual_transform_bindings_are_validated():
    inline = VisualTransformBinding.inline_affine(IDENTITY)
    ref = VisualTransformBinding.from_ref("transform:model")

    assert isinstance(inline.inline, InlineAffineTransform2D)
    assert ref.ref == TransformRef("transform:model")

    with pytest.raises(ValueError, match="exactly one"):
        VisualTransformBinding()

    with pytest.raises(ValueError, match="exactly one"):
        VisualTransformBinding(ref=ref.ref, inline=inline.inline)


def test_point_visual_accepts_transform_binding_without_applying_it():
    binding = VisualTransformBinding.inline_affine(
        np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 3.0], [0.0, 0.0, 1.0]])
    )
    visual = PointVisual(
        id="visual:points",
        positions=np.array([[0.0, 0.0]], dtype=np.float32),
        colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
        sizes=4.0,
        coordinate_space=CoordinateSpace.DATA,
        transform=binding,
    )

    assert visual.transform is binding

    with pytest.raises(TypeError, match="VisualTransformBinding"):
        PointVisual(
            id="visual:bad",
            positions=np.array([[0.0, 0.0]], dtype=np.float32),
            colors=np.array([[255, 255, 255, 255]], dtype=np.uint8),
            sizes=4.0,
            transform=object(),  # type: ignore[arg-type]
        )


def test_view2d_accepts_reversed_limits_and_rejects_degenerate_or_equal_aspect():
    view = View2D(
        id="view:main",
        panel_id="panel:main",
        x_range=(10.0, -10.0),
        y_range=(-1.0, 1.0),
    )

    assert view.xlim == (10.0, -10.0)
    assert view.ylim == (-1.0, 1.0)
    assert view.clip is True

    with pytest.raises(ValueError, match="GSP_VIEW2D_DEGENERATE"):
        View2D(id="view:bad", panel_id="panel:main", x_range=(1.0, 1.0))

    with pytest.raises(ValueError, match="GSP_VIEW2D_NONFINITE"):
        View2D(id="view:bad", panel_id="panel:main", y_range=(0.0, np.nan))

    with pytest.raises(ValueError, match="GSP_VIEW2D_ASPECT_UNSUPPORTED"):
        View2D(
            id="view:bad",
            panel_id="panel:main",
            aspect_policy=AspectPolicy.EQUAL,
        )


def test_transform_query_payload_validates_coordinate_chain_and_status():
    payload = TransformQueryPayload(
        visual_id="visual:points",
        panel_xy=(10.0, 20.0),
        panel_ndc=(-0.5, 0.25),
        declared_coordinate_space=CoordinateSpace.DATA.value,
        declared_space_coord=(1.0, 2.0),
        source_coord=(-1.0, -2.0),
        data_coord=(1.0, 2.0),
        transform_ids=("transform:model",),
        view_id="view:main",
        inverse_status=InverseStatus.EXACT,
    )
    result = QueryResult(
        request_id="query:transform",
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=(10.0, 20.0),
        hits=(
            QueryHit(
                contribution_kind=QueryContributionKind.DATA,
                visual_id="visual:points",
                visual_family="point",
                extension_payload_kind=TRANSFORM_QUERY_PAYLOAD_KIND,
                extension_payload=payload,
            ),
        ),
    )

    assert result.extension_payload_kind == TRANSFORM_QUERY_PAYLOAD_KIND
    assert result.extension_payload == payload

    with pytest.raises(ValueError, match="inverse_status"):
        TransformQueryPayload(
            visual_id="visual:points",
            panel_xy=(0.0, 0.0),
            panel_ndc=(0.0, 0.0),
            declared_coordinate_space=CoordinateSpace.NDC.value,
            declared_space_coord=(0.0, 0.0),
            source_coord=(0.0, 0.0),
            data_coord=None,
            inverse_status="not-a-status",
        )


def test_transform_capabilities_adapt_semantic_support_and_placement():
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        transform_placements=(TransformPlacement.CPU_ADAPTER.value,),
        transform_capabilities=("gsp.transform.affine2d@0.1",),
    )

    assert caps.supports_transform_placement(TransformPlacement.CPU_ADAPTER)
    assert caps.supports_transform_capability("gsp.transform.affine2d@0.1")
    assert (
        caps.adapt_transform_capability("gsp.transform.affine2d@0.1").outcome
        == AdaptationOutcome.ACCEPT
    )

    rejected = caps.adapt_transform_capability("gsp.transform.camera3d@0.1")
    assert rejected.outcome == AdaptationOutcome.REJECT
    assert rejected.diagnostic is not None
