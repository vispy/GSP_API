"""S036 static View3D protocol models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import math
from typing import Any, TypeVar

from .ids import validate_id
from .transforms import ViewKind

CAMERA3D_EPSILON = 1.0e-12

VIEW3D_STATIC_ORTHOGRAPHIC_CAPABILITY = "view3d.static.orthographic.v1"
VIEW3D_STATIC_PERSPECTIVE_CAPABILITY = "view3d.static.perspective.v1"
MESH3D_DATA_VIEW3D_CAPABILITY = "meshvisual.positions3d.data.view3d.v1"
MESH3D_NDC_CAPABILITY = "meshvisual.positions3d.ndc.v1"
MESH3D_OPAQUE_DEPTH_CAPABILITY = "meshvisual.positions3d.opaque_depth.v1"
QUERY_VIEW3D_RAY_READBACK_CAPABILITY = "query.view3d.ray_readback.v1"
QUERY_VIEW3D_MESH_TRIANGLE_PICK_CAPABILITY = "query.view3d.mesh_triangle_pick.v1"
VIEW3D_RETAINED_DATA_SPACE_VISUALS_CAPABILITY = (
    "view3d.retained_data_space_visuals.v1"
)
VIEW3D_NAVIGATION_ORBIT_PAN_ZOOM_CAPABILITY = "view3d.navigation.orbit_pan_zoom.v1"
VIEW3D_LIGHT_AMBIENT_CAPABILITY = "view3d.light.ambient.v1"
VIEW3D_LIGHT_DIRECTIONAL_CAPABILITY = "view3d.light.directional.v1"

Float2 = tuple[float, float]
Float3 = tuple[float, float, float]
_PayloadT = TypeVar("_PayloadT")


class Projection3DKind(str, Enum):
    """Accepted public View3D projection kinds."""

    ORTHOGRAPHIC = "orthographic"
    PERSPECTIVE = "perspective"


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
    VIEW3D_NAVIGATION_UNSUPPORTED = "view3d_navigation_unsupported"
    VIEW3D_NAVIGATION_ACTION_UNSUPPORTED = "view3d_navigation_action_unsupported"
    VIEW3D_NAVIGATION_SNAPSHOT_MISMATCH = "view3d_navigation_snapshot_mismatch"
    VIEW3D_NAVIGATION_INVALID_DELTA = "view3d_navigation_invalid_delta"
    VIEW3D_NAVIGATION_INVALID_ZOOM = "view3d_navigation_invalid_zoom"
    VIEW3D_NAVIGATION_INVALID_RESULT = "view3d_navigation_invalid_result"
    AMBIENT_LIGHT_INVALID = "ambient_light_invalid"
    DIRECTIONAL_LIGHT_DIRECTION_INVALID = "directional_light_direction_invalid"
    DIRECTIONAL_LIGHT_INTENSITY_INVALID = "directional_light_intensity_invalid"


class View3DNavigationActionKind(str, Enum):
    """Accepted S037 backend-neutral View3D navigation actions."""

    ORBIT = "orbit"
    PAN = "pan"
    ZOOM = "zoom"
    SET_CAMERA = "set_camera"
    SET_PROJECTION = "set_projection"
    RESET = "reset"


@dataclass(frozen=True, slots=True)
class Camera3DBasis:
    """Derived orthonormal camera basis for diagnostics and later projection fixtures."""

    forward: Float3
    right: Float3
    true_up: Float3


@dataclass(frozen=True, slots=True)
class View3DProjectionSnapshot:
    """Resolved S036 camera/projection snapshot identity."""

    view_id: str
    panel_id: str
    view_revision: int
    layout_snapshot_id: str
    view_projection_snapshot_id: str
    eye: Float3
    target: Float3
    right: Float3
    true_up: Float3
    forward: Float3
    projection_kind: Projection3DKind
    near_far: Float2
    depth_mode: DepthMode3D
    xlim: Float2 | None = None
    ylim: Float2 | None = None
    fov_y_degrees: float | None = None
    aspect_ratio: float | None = None

    def __post_init__(self) -> None:
        validate_id(self.view_id)
        validate_id(self.panel_id)
        validate_id(self.layout_snapshot_id)
        validate_id(self.view_projection_snapshot_id)
        if self.view_revision < 0:
            raise ValueError("view_revision must be non-negative")
        if not isinstance(self.projection_kind, Projection3DKind):
            raise TypeError("projection_kind must be a Projection3DKind")


@dataclass(frozen=True, slots=True)
class Orbit3DPayload:
    """Rotate camera eye around the target while preserving radius."""

    delta_yaw_radians: float
    delta_pitch_radians: float
    pivot: str = "target"
    radius_policy: str = "preserve"

    def __post_init__(self) -> None:
        _validate_finite(
            "delta_yaw_radians",
            self.delta_yaw_radians,
            View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_DELTA,
        )
        _validate_finite(
            "delta_pitch_radians",
            self.delta_pitch_radians,
            View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_DELTA,
        )
        if self.pivot != "target":
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value}: "
                "only target pivot is accepted in S037"
            )
        if self.radius_policy != "preserve":
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value}: "
                "only preserve radius policy is accepted in S037"
            )


@dataclass(frozen=True, slots=True)
class Pan3DPayload:
    """Translate camera eye and target in the view right/up plane."""

    delta_view_right: float
    delta_view_up: float
    units: str = "data"

    def __post_init__(self) -> None:
        _validate_finite(
            "delta_view_right",
            self.delta_view_right,
            View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_DELTA,
        )
        _validate_finite(
            "delta_view_up",
            self.delta_view_up,
            View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_DELTA,
        )
        if self.units != "data":
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value}: "
                "only data pan units are accepted in S037"
            )


@dataclass(frozen=True, slots=True)
class Zoom3DPayload:
    """Scale orthographic bounds or dolly a perspective camera."""

    scale: float
    anchor_panel_ndc_xy: Float2 | None = None

    def __post_init__(self) -> None:
        _validate_finite(
            "scale",
            self.scale,
            View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_ZOOM,
        )
        if self.scale <= 0.0:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_ZOOM.value}: "
                "scale must be positive"
            )
        if self.anchor_panel_ndc_xy is not None:
            _validate_float2(
                "anchor_panel_ndc_xy",
                self.anchor_panel_ndc_xy,
                View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_ZOOM,
            )


@dataclass(frozen=True, slots=True)
class SetCamera3DPayload:
    """Replace canonical View3D camera state."""

    camera: Camera3D

    def __post_init__(self) -> None:
        if not isinstance(self.camera, Camera3D):
            raise TypeError("camera must be a Camera3D")


@dataclass(frozen=True, slots=True)
class SetProjection3DPayload:
    """Replace canonical View3D projection state."""

    projection: "Projection3D"

    def __post_init__(self) -> None:
        _validate_projection3d_instance(self.projection)


@dataclass(frozen=True, slots=True)
class ResetView3DPayload:
    """Restore explicit home camera/projection state."""

    camera: Camera3D
    projection: "Projection3D"

    def __post_init__(self) -> None:
        if not isinstance(self.camera, Camera3D):
            raise TypeError("camera must be a Camera3D")
        _validate_projection3d_instance(self.projection)


View3DNavigationPayload = (
    Orbit3DPayload
    | Pan3DPayload
    | Zoom3DPayload
    | SetCamera3DPayload
    | SetProjection3DPayload
    | ResetView3DPayload
)


@dataclass(frozen=True, slots=True)
class View3DNavigationAction:
    """Backend-neutral S037 navigation action over canonical View3D state."""

    kind: View3DNavigationActionKind
    view_id: str
    base_view_revision: int
    base_view_projection_snapshot_id: str
    payload: View3DNavigationPayload
    base_layout_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, View3DNavigationActionKind):
            raise TypeError("kind must be a View3DNavigationActionKind")
        validate_id(self.view_id)
        if not isinstance(self.base_view_revision, int) or self.base_view_revision < 0:
            raise ValueError("base_view_revision must be a non-negative integer")
        validate_id(self.base_view_projection_snapshot_id)
        if self.base_layout_snapshot_id is not None:
            validate_id(self.base_layout_snapshot_id)
        _validate_navigation_payload_kind(self.kind, self.payload)


@dataclass(frozen=True, slots=True)
class View3DNavigationResult:
    """Result of applying one S037 View3D navigation action."""

    accepted: bool
    view_id: str
    old_revision: int
    action_kind: View3DNavigationActionKind
    diagnostics: tuple[str, ...] = ()
    new_revision: int | None = None
    camera: Camera3D | None = None
    projection: "Projection3D | None" = None
    view: View3D | None = None
    layout_snapshot_id: str | None = None
    view_projection_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be a bool")
        validate_id(self.view_id)
        if not isinstance(self.old_revision, int) or self.old_revision < 0:
            raise ValueError("old_revision must be a non-negative integer")
        if not isinstance(self.action_kind, View3DNavigationActionKind):
            raise TypeError("action_kind must be a View3DNavigationActionKind")
        if self.new_revision is not None and self.new_revision < 0:
            raise ValueError("new_revision must be non-negative")
        if self.camera is not None and not isinstance(self.camera, Camera3D):
            raise TypeError("camera must be a Camera3D")
        if self.projection is not None:
            _validate_projection3d_instance(self.projection)
        if self.view is not None and not isinstance(self.view, View3D):
            raise TypeError("view must be a View3D")
        if self.layout_snapshot_id is not None:
            validate_id(self.layout_snapshot_id)
        if self.view_projection_snapshot_id is not None:
            validate_id(self.view_projection_snapshot_id)
        for diagnostic in self.diagnostics:
            if not diagnostic:
                raise ValueError("View3D navigation diagnostics must not be empty")
        if self.accepted:
            if (
                self.new_revision is None
                or self.camera is None
                or self.projection is None
                or self.view is None
                or self.view_projection_snapshot_id is None
            ):
                raise ValueError("accepted View3D navigation results require updated state")
        elif not self.diagnostics:
            raise ValueError("rejected View3D navigation results require diagnostics")


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
class PerspectiveProjection3D:
    """Perspective projection with a vertical field-of-view angle."""

    fov_y_degrees: float = 45.0
    near_far: Float2 = (0.1, 1000.0)
    aspect_ratio: float | None = None
    kind: Projection3DKind = Projection3DKind.PERSPECTIVE

    def __post_init__(self) -> None:
        if self.kind is not Projection3DKind.PERSPECTIVE:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_PROJECTION_UNSUPPORTED.value}: "
                "PerspectiveProjection3D requires kind='perspective'"
            )
        _validate_finite(
            "fov_y_degrees",
            self.fov_y_degrees,
            View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION,
        )
        if self.fov_y_degrees <= 0.0 or self.fov_y_degrees >= 180.0:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
                "fov_y_degrees must be within (0, 180)"
            )
        validate_projection3d_range("near_far", self.near_far, allow_reversed=False)
        near, far = self.near_far
        if near <= 0.0 or far <= near:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
                "perspective near_far must satisfy near > 0 and far > near"
            )
        if self.aspect_ratio is not None:
            _validate_finite(
                "aspect_ratio",
                self.aspect_ratio,
                View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION,
            )
            if self.aspect_ratio <= 0.0:
                raise ValueError(
                    f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
                    "aspect_ratio must be positive"
                )


Projection3D = OrthographicProjection3D | PerspectiveProjection3D


@dataclass(frozen=True, slots=True)
class DirectionalLight3D:
    """S039 scalar white DATA-space directional light."""

    direction_to_light: Float3
    intensity: float = 1.0

    def __post_init__(self) -> None:
        _validate_float3_with_diagnostic(
            "direction_to_light",
            self.direction_to_light,
            View3DDiagnosticCode.DIRECTIONAL_LIGHT_DIRECTION_INVALID,
        )
        _normalize3_with_diagnostic(
            self.direction_to_light,
            "direction_to_light must be nonzero",
            View3DDiagnosticCode.DIRECTIONAL_LIGHT_DIRECTION_INVALID,
        )
        _validate_unit_interval(
            "intensity",
            self.intensity,
            View3DDiagnosticCode.DIRECTIONAL_LIGHT_INTENSITY_INVALID,
        )


@dataclass(frozen=True, slots=True)
class View3D:
    """Static S036 3D view attached to one panel."""

    id: str
    panel_id: str
    camera: Camera3D
    projection: Projection3D
    depth_mode: DepthMode3D = DepthMode3D.OPAQUE_LESS
    ambient_light_intensity: float = 0.0
    directional_light: DirectionalLight3D | None = None
    kind: ViewKind = ViewKind.VIEW3D_CAMERA
    revision: int = 0

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        if not isinstance(self.camera, Camera3D):
            raise TypeError("camera must be a Camera3D")
        _validate_projection3d_instance(self.projection)
        if self.depth_mode is not DepthMode3D.OPAQUE_LESS:
            raise ValueError("only OPAQUE_LESS depth is accepted in S036")
        _validate_unit_interval(
            "ambient_light_intensity",
            self.ambient_light_intensity,
            View3DDiagnosticCode.AMBIENT_LIGHT_INVALID,
        )
        if self.directional_light is not None and not isinstance(
            self.directional_light, DirectionalLight3D
        ):
            raise TypeError("directional_light must be a DirectionalLight3D")
        if self.kind is not ViewKind.VIEW3D_CAMERA:
            raise ValueError("only VIEW3D_CAMERA views are accepted in S036")
        if not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("revision must be a non-negative integer")


def project_view3d_data_point(
    view: View3D, point: Float3, *, aspect_ratio: float | None = None
) -> Float3:
    """Project one DATA-space point into GSP panel NDC3."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    _validate_float3("point", point)
    basis = view.camera.basis()
    relative = _sub3(point, view.camera.eye)
    camera_x = _dot3(relative, basis.right)
    camera_y = _dot3(relative, basis.true_up)
    camera_z = _dot3(relative, basis.forward)
    near, far = view.projection.near_far
    if isinstance(view.projection, PerspectiveProjection3D):
        resolved_aspect = _resolve_perspective_aspect_ratio(
            view.projection, aspect_ratio
        )
        if camera_z <= 0.0:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
                "point is behind the perspective camera"
            )
        half_height = camera_z * _perspective_tan_half_fov(view.projection)
        half_width = half_height * resolved_aspect
        return (
            camera_x / half_width,
            camera_y / half_height,
            -1.0 + 2.0 * (camera_z - near) / (far - near),
        )
    x0, x1 = view.projection.xlim
    y0, y1 = view.projection.ylim
    return (
        -1.0 + 2.0 * (camera_x - x0) / (x1 - x0),
        -1.0 + 2.0 * (camera_y - y0) / (y1 - y0),
        -1.0 + 2.0 * (camera_z - near) / (far - near),
    )


def unproject_view3d_panel_ndc_point(
    view: View3D, point: Float3, *, aspect_ratio: float | None = None
) -> Float3:
    """Unproject one panel NDC3 point into DATA space."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    _validate_float3("point", point)
    basis = view.camera.basis()
    near, far = view.projection.near_far
    camera_z = near + (point[2] + 1.0) * 0.5 * (far - near)
    if isinstance(view.projection, PerspectiveProjection3D):
        resolved_aspect = _resolve_perspective_aspect_ratio(
            view.projection, aspect_ratio
        )
        half_height = camera_z * _perspective_tan_half_fov(view.projection)
        half_width = half_height * resolved_aspect
        camera_x = point[0] * half_width
        camera_y = point[1] * half_height
    else:
        x0, x1 = view.projection.xlim
        y0, y1 = view.projection.ylim
        camera_x = x0 + (point[0] + 1.0) * 0.5 * (x1 - x0)
        camera_y = y0 + (point[1] + 1.0) * 0.5 * (y1 - y0)
    return _add3(
        view.camera.eye,
        _add3(
            _scale3(basis.right, camera_x),
            _add3(_scale3(basis.true_up, camera_y), _scale3(basis.forward, camera_z)),
        ),
    )


def resolve_view3d_projection_snapshot(
    view: View3D, *, layout_snapshot_id: str
) -> View3DProjectionSnapshot:
    """Return a deterministic S036 projection snapshot for one view/layout pair."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    validate_id(layout_snapshot_id)
    basis = view.camera.basis()
    snapshot_id = _projection_snapshot_id(view, layout_snapshot_id, basis)
    return View3DProjectionSnapshot(
        view_id=view.id,
        panel_id=view.panel_id,
        view_revision=view.revision,
        layout_snapshot_id=layout_snapshot_id,
        view_projection_snapshot_id=snapshot_id,
        eye=view.camera.eye,
        target=view.camera.target,
        right=basis.right,
        true_up=basis.true_up,
        forward=basis.forward,
        projection_kind=view.projection.kind,
        near_far=view.projection.near_far,
        depth_mode=view.depth_mode,
        xlim=view.projection.xlim
        if isinstance(view.projection, OrthographicProjection3D)
        else None,
        ylim=view.projection.ylim
        if isinstance(view.projection, OrthographicProjection3D)
        else None,
        fov_y_degrees=view.projection.fov_y_degrees
        if isinstance(view.projection, PerspectiveProjection3D)
        else None,
        aspect_ratio=view.projection.aspect_ratio
        if isinstance(view.projection, PerspectiveProjection3D)
        else None,
    )


def orbit_view3d(view: View3D, payload: Orbit3DPayload) -> View3D:
    """Return the View3D produced by an S037 orbit payload."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    if not isinstance(payload, Orbit3DPayload):
        raise TypeError("payload must be an Orbit3DPayload")
    basis = view.camera.basis()
    eye_from_target = _sub3(view.camera.eye, view.camera.target)
    yawed_eye = _rotate3(
        eye_from_target, basis.true_up, payload.delta_yaw_radians
    )
    yawed_right = _rotate3(basis.right, basis.true_up, payload.delta_yaw_radians)
    pitched_eye = _rotate3(
        yawed_eye, yawed_right, payload.delta_pitch_radians
    )
    return _replace_view3d(
        view,
        camera=Camera3D(
            eye=_add3(view.camera.target, pitched_eye),
            target=view.camera.target,
            up=view.camera.up,
        ),
    )


def pan_view3d(view: View3D, payload: Pan3DPayload) -> View3D:
    """Return the View3D produced by an S037 pan payload."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    if not isinstance(payload, Pan3DPayload):
        raise TypeError("payload must be a Pan3DPayload")
    basis = view.camera.basis()
    offset = _add3(
        _scale3(basis.right, payload.delta_view_right),
        _scale3(basis.true_up, payload.delta_view_up),
    )
    return _replace_view3d(
        view,
        camera=Camera3D(
            eye=_add3(view.camera.eye, offset),
            target=_add3(view.camera.target, offset),
            up=view.camera.up,
        ),
    )


def zoom_view3d(view: View3D, payload: Zoom3DPayload) -> View3D:
    """Return the View3D produced by an S037 zoom payload."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    if not isinstance(payload, Zoom3DPayload):
        raise TypeError("payload must be a Zoom3DPayload")
    if isinstance(view.projection, PerspectiveProjection3D):
        if payload.anchor_panel_ndc_xy is not None:
            raise ValueError(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value}: "
                "anchored perspective zoom semantics are deferred"
            )
        basis = view.camera.basis()
        eye_to_target = _sub3(view.camera.target, view.camera.eye)
        distance = _dot3(eye_to_target, basis.forward)
        new_distance = max(distance / payload.scale, CAMERA3D_EPSILON * 10.0)
        return _replace_view3d(
            view,
            camera=Camera3D(
                eye=_sub3(view.camera.target, _scale3(basis.forward, new_distance)),
                target=view.camera.target,
                up=view.camera.up,
            ),
        )
    if payload.anchor_panel_ndc_xy is None:
        x_anchor_t = 0.5
        y_anchor_t = 0.5
    else:
        x_anchor_t = (payload.anchor_panel_ndc_xy[0] + 1.0) * 0.5
        y_anchor_t = (payload.anchor_panel_ndc_xy[1] + 1.0) * 0.5

    x0, x1 = view.projection.xlim
    y0, y1 = view.projection.ylim
    x_anchor = x0 + x_anchor_t * (x1 - x0)
    y_anchor = y0 + y_anchor_t * (y1 - y0)
    new_x_span = (x1 - x0) / payload.scale
    new_y_span = (y1 - y0) / payload.scale
    projection = OrthographicProjection3D(
        xlim=(
            x_anchor - x_anchor_t * new_x_span,
            x_anchor + (1.0 - x_anchor_t) * new_x_span,
        ),
        ylim=(
            y_anchor - y_anchor_t * new_y_span,
            y_anchor + (1.0 - y_anchor_t) * new_y_span,
        ),
        near_far=view.projection.near_far,
        kind=view.projection.kind,
    )
    return _replace_view3d(view, projection=projection)


def apply_view3d_navigation_action(
    view: View3D,
    action: View3DNavigationAction,
    *,
    layout_snapshot_id: str,
) -> View3DNavigationResult:
    """Apply one S037 navigation action with strict revision/snapshot freshness."""
    if not isinstance(view, View3D):
        raise TypeError("view must be a View3D")
    if not isinstance(action, View3DNavigationAction):
        raise TypeError("action must be a View3DNavigationAction")
    validate_id(layout_snapshot_id)
    current_snapshot = resolve_view3d_projection_snapshot(
        view, layout_snapshot_id=layout_snapshot_id
    )
    mismatch_diagnostic = View3DDiagnosticCode.VIEW3D_NAVIGATION_SNAPSHOT_MISMATCH.value
    if action.view_id != view.id:
        return _reject_view3d_navigation(
            view,
            action,
            layout_snapshot_id=layout_snapshot_id,
            diagnostics=(f"{mismatch_diagnostic}: action view_id does not match",),
        )
    if action.base_view_revision != view.revision:
        return _reject_view3d_navigation(
            view,
            action,
            layout_snapshot_id=layout_snapshot_id,
            diagnostics=(f"{mismatch_diagnostic}: stale view revision",),
        )
    if (
        action.base_view_projection_snapshot_id
        != current_snapshot.view_projection_snapshot_id
    ):
        return _reject_view3d_navigation(
            view,
            action,
            layout_snapshot_id=layout_snapshot_id,
            diagnostics=(f"{mismatch_diagnostic}: stale projection snapshot",),
        )
    if (
        action.base_layout_snapshot_id is not None
        and action.base_layout_snapshot_id != layout_snapshot_id
    ):
        return _reject_view3d_navigation(
            view,
            action,
            layout_snapshot_id=layout_snapshot_id,
            diagnostics=(f"{mismatch_diagnostic}: stale layout snapshot",),
        )

    try:
        updated = _apply_fresh_view3d_navigation_action(view, action)
    except (TypeError, ValueError) as error:
        return _reject_view3d_navigation(
            view,
            action,
            layout_snapshot_id=layout_snapshot_id,
            diagnostics=(
                f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_INVALID_RESULT.value}: "
                f"{error}",
            ),
        )

    updated_snapshot = resolve_view3d_projection_snapshot(
        updated, layout_snapshot_id=layout_snapshot_id
    )
    return View3DNavigationResult(
        accepted=True,
        view_id=view.id,
        old_revision=view.revision,
        new_revision=updated.revision,
        camera=updated.camera,
        projection=updated.projection,
        view=updated,
        layout_snapshot_id=layout_snapshot_id,
        view_projection_snapshot_id=updated_snapshot.view_projection_snapshot_id,
        action_kind=action.kind,
    )


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


def _apply_fresh_view3d_navigation_action(
    view: View3D, action: View3DNavigationAction
) -> View3D:
    if action.kind is View3DNavigationActionKind.ORBIT:
        return orbit_view3d(view, _expect_payload(action.payload, Orbit3DPayload))
    if action.kind is View3DNavigationActionKind.PAN:
        return pan_view3d(view, _expect_payload(action.payload, Pan3DPayload))
    if action.kind is View3DNavigationActionKind.ZOOM:
        return zoom_view3d(view, _expect_payload(action.payload, Zoom3DPayload))
    if action.kind is View3DNavigationActionKind.SET_CAMERA:
        camera_payload = _expect_payload(action.payload, SetCamera3DPayload)
        return _replace_view3d(view, camera=camera_payload.camera)
    if action.kind is View3DNavigationActionKind.SET_PROJECTION:
        projection_payload = _expect_payload(action.payload, SetProjection3DPayload)
        return _replace_view3d(view, projection=projection_payload.projection)
    if action.kind is View3DNavigationActionKind.RESET:
        reset_payload = _expect_payload(action.payload, ResetView3DPayload)
        return _replace_view3d(
            view, camera=reset_payload.camera, projection=reset_payload.projection
        )
    raise ValueError(
        f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value}: "
        f"unsupported action kind {action.kind!r}"
    )


def _reject_view3d_navigation(
    view: View3D,
    action: View3DNavigationAction,
    *,
    layout_snapshot_id: str,
    diagnostics: tuple[str, ...],
) -> View3DNavigationResult:
    return View3DNavigationResult(
        accepted=False,
        view_id=action.view_id,
        old_revision=view.revision,
        action_kind=action.kind,
        diagnostics=diagnostics,
        layout_snapshot_id=layout_snapshot_id,
    )


def _replace_view3d(
    view: View3D,
    *,
    camera: Camera3D | None = None,
    projection: Projection3D | None = None,
) -> View3D:
    return View3D(
        id=view.id,
        panel_id=view.panel_id,
        camera=view.camera if camera is None else camera,
        projection=view.projection if projection is None else projection,
        depth_mode=view.depth_mode,
        ambient_light_intensity=view.ambient_light_intensity,
        directional_light=view.directional_light,
        kind=view.kind,
        revision=view.revision + 1,
    )


def _validate_navigation_payload_kind(
    kind: View3DNavigationActionKind, payload: View3DNavigationPayload
) -> None:
    expected: type[Any]
    if kind is View3DNavigationActionKind.ORBIT:
        expected = Orbit3DPayload
    elif kind is View3DNavigationActionKind.PAN:
        expected = Pan3DPayload
    elif kind is View3DNavigationActionKind.ZOOM:
        expected = Zoom3DPayload
    elif kind is View3DNavigationActionKind.SET_CAMERA:
        expected = SetCamera3DPayload
    elif kind is View3DNavigationActionKind.SET_PROJECTION:
        expected = SetProjection3DPayload
    elif kind is View3DNavigationActionKind.RESET:
        expected = ResetView3DPayload
    else:
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_NAVIGATION_ACTION_UNSUPPORTED.value}: "
            f"unsupported action kind {kind!r}"
        )
    if not isinstance(payload, expected):
        raise TypeError(f"{kind.value} action payload must be {expected.__name__}")


def _expect_payload(payload: View3DNavigationPayload, expected: type[_PayloadT]) -> _PayloadT:
    if not isinstance(payload, expected):
        raise TypeError(f"payload must be {expected.__name__}")
    return payload


def _validate_float2(
    name: str, value: Float2, diagnostic: View3DDiagnosticCode
) -> None:
    if len(value) != 2:
        raise ValueError(f"{name} must contain two values")
    _validate_finite(f"{name}[0]", value[0], diagnostic)
    _validate_finite(f"{name}[1]", value[1], diagnostic)


def _validate_float3(name: str, value: Float3) -> None:
    _validate_float3_with_diagnostic(
        name,
        value,
        View3DDiagnosticCode.VIEW3D_INVALID_CAMERA_DEGENERATE,
    )


def _validate_float3_with_diagnostic(
    name: str, value: Float3, diagnostic: View3DDiagnosticCode
) -> None:
    if len(value) != 3:
        raise ValueError(f"{name} must contain three values")
    if not all(math.isfinite(component) for component in value):
        raise ValueError(f"{diagnostic.value}: {name} values must be finite")


def _validate_projection3d_instance(projection: Projection3D) -> None:
    if not isinstance(projection, (OrthographicProjection3D, PerspectiveProjection3D)):
        raise TypeError(
            "projection must be an OrthographicProjection3D or PerspectiveProjection3D"
        )


def _validate_finite(
    name: str, value: float, diagnostic: View3DDiagnosticCode
) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{diagnostic.value}: {name} must be finite")


def _validate_unit_interval(
    name: str, value: float, diagnostic: View3DDiagnosticCode
) -> None:
    _validate_finite(name, value, diagnostic)
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{diagnostic.value}: {name} must be within [0, 1]")


def _resolve_perspective_aspect_ratio(
    projection: PerspectiveProjection3D, aspect_ratio: float | None
) -> float:
    resolved = aspect_ratio if aspect_ratio is not None else projection.aspect_ratio
    if resolved is None:
        return 1.0
    _validate_finite(
        "aspect_ratio",
        resolved,
        View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION,
    )
    if resolved <= 0.0:
        raise ValueError(
            f"{View3DDiagnosticCode.VIEW3D_INVALID_PROJECTION.value}: "
            "aspect_ratio must be positive"
        )
    return resolved


def _perspective_tan_half_fov(projection: PerspectiveProjection3D) -> float:
    return math.tan(math.radians(projection.fov_y_degrees) * 0.5)


def _sub3(left: Float3, right: Float3) -> Float3:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _add3(left: Float3, right: Float3) -> Float3:
    return (left[0] + right[0], left[1] + right[1], left[2] + right[2])


def _scale3(value: Float3, scale: float) -> Float3:
    return (value[0] * scale, value[1] * scale, value[2] * scale)


def _cross3(left: Float3, right: Float3) -> Float3:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _dot3(left: Float3, right: Float3) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def _norm3(value: Float3) -> float:
    return math.sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2])


def _normalize3(value: Float3, message: str) -> Float3:
    return _normalize3_with_diagnostic(
        value,
        message,
        View3DDiagnosticCode.VIEW3D_INVALID_CAMERA_DEGENERATE,
    )


def _normalize3_with_diagnostic(
    value: Float3, message: str, diagnostic: View3DDiagnosticCode
) -> Float3:
    norm = _norm3(value)
    if norm <= CAMERA3D_EPSILON:
        raise ValueError(f"{diagnostic.value}: {message}")
    return (value[0] / norm, value[1] / norm, value[2] / norm)


def _rotate3(value: Float3, axis: Float3, angle_radians: float) -> Float3:
    axis_normalized = _normalize3(axis, "rotation axis must be nonzero")
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)
    cross = _cross3(axis_normalized, value)
    dot = _dot3(axis_normalized, value)
    return _add3(
        _add3(_scale3(value, cos_angle), _scale3(cross, sin_angle)),
        _scale3(axis_normalized, dot * (1.0 - cos_angle)),
    )


def _projection_snapshot_id(
    view: View3D, layout_snapshot_id: str, basis: Camera3DBasis
) -> str:
    parts = (
        view.id,
        view.panel_id,
        str(view.revision),
        layout_snapshot_id,
        _format_float3(view.camera.eye),
        _format_float3(view.camera.target),
        _format_float3(view.camera.up),
        _format_float3(basis.right),
        _format_float3(basis.true_up),
        _format_float3(basis.forward),
        view.projection.kind.value,
        _format_projection_parameters(view.projection),
        _format_float2(view.projection.near_far),
        view.depth_mode.value,
    )
    digest = hashlib.sha256("|".join(parts).encode("ascii")).hexdigest()[:16]
    return f"view3d-projection:{digest}"


def _format_float2(value: Float2) -> str:
    return ",".join(f"{component:.17g}" for component in value)


def _format_float3(value: Float3) -> str:
    return ",".join(f"{component:.17g}" for component in value)


def _format_projection_parameters(projection: Projection3D) -> str:
    if isinstance(projection, OrthographicProjection3D):
        return "|".join(
            (
                _format_float2(projection.xlim),
                _format_float2(projection.ylim),
            )
        )
    return "|".join(
        (
            f"{projection.fov_y_degrees:.17g}",
            "" if projection.aspect_ratio is None else f"{projection.aspect_ratio:.17g}",
        )
    )
