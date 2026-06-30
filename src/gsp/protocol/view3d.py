"""S036 static View3D protocol models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from .ids import validate_id
from .transforms import ViewKind

CAMERA3D_EPSILON = 1.0e-12

VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY = "view3d.static.orthographic.v1"
MESH3D_DATA_VIEW3D_CAPABILITY = "meshvisual.positions3d.data.view3d.v1"
MESH3D_NDC_CAPABILITY = "meshvisual.positions3d.ndc.v1"
MESH3D_OPAQUE_DEPTH_CAPABILITY = "meshvisual.positions3d.opaque_depth.v1"
QUERY_VIEW3D_RAY_READBACK_CAPABILITY = "query.view3d.ray_readback.v1"

Float2 = tuple[float, float]
Float3 = tuple[float, float, float]


class Projection3DKind(str, Enum):
    """Accepted S036 projection kinds."""

    ORTHOGRAPHIC = "orthographic"


class DepthMode3D(str, Enum):
    """Accepted S036 3D depth mode."""

    OPAQUE_LESS = "opaque_less"


class View3DDiagnosticCode(str, Enum):
    """Structured S036 View3D diagnostic vocabulary."""

    VIEW3D_NOT_SUPPORTED = "view3d_not_supported"
    VIEW3D_PROJECTION_UNSUPPORTED = "view3d_projection_unsupported"
    VIEW3D_INVALID_CAMERA_DEGENERATE = "view3d_invalid_camera_degenerate"
    VIEW3D_INVALID_PROJECTION = "view3d_invalid_projection"
    MESH3D_REQUIRES_VIEW3D = "mesh3d_requires_view3d"
    MESH3D_COORDINATE_SPACE_UNSUPPORTED = "mesh3d_coordinate_space_unsupported"
    MESH3D_TRANSFORM_UNSUPPORTED = "mesh3d_transform_unsupported"
    MESH3D_DEPTH_UNSUPPORTED = "mesh3d_depth_unsupported"
    MESH3D_DEPTH_ADAPTED = "mesh3d_depth_adapted"
    MESH3D_ALPHA_NOT_STRICT = "mesh3d_alpha_not_strict"
    MESH3D_CLIPPING_ADAPTED = "mesh3d_clipping_adapted"
    QUERY_3D_VISUAL_HIT_DEFERRED = "query_3d_visual_hit_deferred"
    QUERY_3D_SNAPSHOT_MISMATCH = "query_3d_snapshot_mismatch"


@dataclass(frozen=True, slots=True)
class Camera3DBasis:
    """Derived orthonormal camera basis for diagnostics and later projection fixtures."""

    forward: Float3
    right: Float3
    true_up: Float3


@dataclass(frozen=True, slots=True)
class Camera3D:
    """Camera-parameter-first S036 3D camera."""

    eye: Float3
    target: Float3
    up: Float3

    def __post_init__(self) -> None:
        _validate_float3("eye", self.eye)
        _validate_float3("target", self.target)
        _validate_float3("up", self.up)
        self.basis()

    def basis(self) -> Camera3DBasis:
        """Return the derived S036 camera basis or raise if the camera is degenerate."""
        forward_raw = _sub3(self.target, self.eye)
        forward = _normalize3(forward_raw, "eye and target must differ")
        up_normalized = _normalize3(self.up, "up vector must be nonzero")
        right_raw = _cross3(forward, up_normalized)
        right = _normalize3(
            right_raw,
            "up vector must not be parallel to target - eye",
        )
        true_up = _cross3(right, forward)
        return Camera3DBasis(forward=forward, right=right, true_up=true_up)


@dataclass(frozen=True, slots=True)
class OrthographicProjection3D:
    """S036 orthographic projection bounds in the camera plane."""

    xlim: Float2 = (-1.0, 1.0)
    ylim: Float2 = (-1.0, 1.0)
    near_far: Float2 = (0.0, 1.0)
    kind: Projection3DKind = Projection3DKind.ORTHOGRAPHIC

    def __post_init__(self) -> None:
        if self.kind is not Projection3DKind.ORTHOGRAPHIC:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_PROJECTION_UNSUPPORTED.value}: "
                "only orthographic projection is accepted in S036"
            )
        validate_projection3d_range("xlim", self.xlim, allow_reversed=True)
        validate_projection3d_range("ylim", self.ylim, allow_reversed=True)
        validate_projection3d_range("near_far", self.near_far, allow_reversed=False)
        near, far = self.near_far
        if near < 0.0 or far <= near:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
                "near_far must satisfy near >= 0 and far > near"
            )


@dataclass(frozen=True, slots=True)
class View3D:
    """Static S036 3D view attached to one panel."""

    id: str
    panel_id: str
    camera: Camera3D
    projection: OrthographicProjection3D
    depth_mode: DepthMode3D = DepthMode3D.OPAQUE_LESS
    kind: ViewKind = ViewKind.VIEW3D_CAMERA
    revision: int = 0

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        if not isinstance(self.camera, Camera3D):
            raise TypeError("camera must be a Camera3D")
        if not isinstance(self.projection, OrthographicProjection3D):
            raise TypeError("projection must be an OrthographicProjection3D")
        if self.depth_mode is not DepthMode3D.OPAQUE_LESS:
            raise ValueError("only OPAQUE_LESS depth is accepted in S036")
        if self.kind is not ViewKind.VIEW3D_CAMERA:
            raise ValueError("only VIEW3D_CAMERA views are accepted in S036")
        if not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("revision must be a non-negative integer")


def validate_projection3d_range(
    name: str, limits: Float2, *, allow_reversed: bool
) -> None:
    """Validate a finite non-degenerate S036 projection range."""
    if len(limits) != 2:
        raise ValueError(f"{name} must contain two values")
    low, high = limits
    if not math.isfinite(low) or not math.isfinite(high):
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
            f"{name} values must be finite"
        )
    if low == high:
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
            f"{name} endpoints must differ"
        )
    if not allow_reversed and high < low:
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
            f"{name} endpoints must not be reversed"
        )


def _validate_float3(name: str, value: Float3) -> None:
    if len(value) != 3:
        raise ValueError(f"{name} must contain three values")
    if not all(math.isfinite(component) for component in value):
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_INVALID_CAMERA_DEGENERATE.value}: "
            f"{name} values must be finite"
        )


def _sub3(left: Float3, right: Float3) -> Float3:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _cross3(left: Float3, right: Float3) -> Float3:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _norm3(value: Float3) -> float:
    return math.sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2])


def _normalize3(value: Float3, message: str) -> Float3:
    norm = _norm3(value)
    if norm <= CAMERA3D_EPSILON:
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_INVALID_CAMERA_DEGENERATE.value}: "
            f"{message}"
        )
    return (value[0] / norm, value[1] / norm, value[2] / norm)

