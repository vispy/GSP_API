"""S027 transform and view protocol support."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
import numpy.typing as npt

from .ids import validate_id


class TransformKind(str, Enum):
    """Accepted and reserved transform kinds."""

    AFFINE_2D = "affine-2d"
    AFFINE_3D = "affine-3d"


class ViewKind(str, Enum):
    """Accepted and reserved view kinds."""

    VIEW2D_LINEAR = "view2d-linear"
    VIEW3D_CAMERA = "view3d-camera"


class TransformPlacement(str, Enum):
    """Where a backend applies transform semantics."""

    GPU_BACKEND = "gpu-backend"
    CPU_ADAPTER = "cpu-adapter"
    SERVER_SIDE = "server-side"
    CLIENT_SIDE = "client-side"
    MIXED = "mixed"
    UNSUPPORTED = "unsupported"


class InverseStatus(str, Enum):
    """Status for transformed query inverse/readout fields."""

    EXACT = "exact"
    APPROXIMATE = "approximate"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"
    NOT_APPLICABLE = "not-applicable"
    AMBIGUOUS = "ambiguous"


class TransformDiagnosticCode(str, Enum):
    """Structured S027 transform/view diagnostic vocabulary."""

    TRANSFORM_BAD_SHAPE = "GSP_TRANSFORM_BAD_SHAPE"
    TRANSFORM_NONFINITE = "GSP_TRANSFORM_NONFINITE"
    TRANSFORM_NON_AFFINE = "GSP_TRANSFORM_NON_AFFINE"
    TRANSFORM_SINGULAR = "GSP_TRANSFORM_SINGULAR"
    TRANSFORM_UNSUPPORTED_KIND = "GSP_TRANSFORM_UNSUPPORTED_KIND"
    TRANSFORM_UNSUPPORTED_DIMENSION = "GSP_TRANSFORM_UNSUPPORTED_DIMENSION"
    TRANSFORM_MISSING_REF = "GSP_TRANSFORM_MISSING_REF"
    VIEW2D_NONFINITE = "GSP_VIEW2D_NONFINITE"
    VIEW2D_DEGENERATE = "GSP_VIEW2D_DEGENERATE"
    VIEW2D_UNSUPPORTED_SCALE = "GSP_VIEW2D_UNSUPPORTED_SCALE"
    VIEW2D_ASPECT_UNSUPPORTED = "GSP_VIEW2D_ASPECT_UNSUPPORTED"
    CAMERA3D_DEFERRED = "GSP_CAMERA3D_DEFERRED"


Matrix3x3 = npt.NDArray[np.float32] | npt.NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class AffineTransform2DResource:
    """Named finite invertible 2D affine transform resource."""

    id: str
    matrix: Matrix3x3
    kind: TransformKind = TransformKind.AFFINE_2D
    label: str | None = None
    metadata: dict[str, object] | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_affine_2d_matrix(self.matrix)
        if self.kind is not TransformKind.AFFINE_2D:
            raise ValueError(
                f"{TransformDiagnosticCode.TRANSFORM_UNSUPPORTED_KIND.value}: "
                "only AFFINE_2D transforms are accepted in S027"
            )

    @property
    def inverse_matrix(self) -> npt.NDArray[np.float64]:
        """Return the float64 inverse transform matrix."""
        return np.linalg.inv(np.asarray(self.matrix, dtype=np.float64))


@dataclass(frozen=True, slots=True)
class InlineAffineTransform2D:
    """Inline finite invertible 2D affine transform."""

    matrix: Matrix3x3
    kind: TransformKind = TransformKind.AFFINE_2D

    def __post_init__(self) -> None:
        validate_affine_2d_matrix(self.matrix)
        if self.kind is not TransformKind.AFFINE_2D:
            raise ValueError(
                f"{TransformDiagnosticCode.TRANSFORM_UNSUPPORTED_KIND.value}: "
                "only AFFINE_2D transforms are accepted in S027"
            )

    @property
    def inverse_matrix(self) -> npt.NDArray[np.float64]:
        """Return the float64 inverse transform matrix."""
        return np.linalg.inv(np.asarray(self.matrix, dtype=np.float64))


@dataclass(frozen=True, slots=True)
class TransformRef:
    """Reference to a named transform resource."""

    id: str
    required: bool = True

    def __post_init__(self) -> None:
        validate_id(self.id)
        if not isinstance(self.required, bool):
            raise TypeError("required must be a bool")


@dataclass(frozen=True, slots=True)
class VisualTransformBinding:
    """Optional visual-local transform binding for positional geometry."""

    ref: TransformRef | None = None
    inline: InlineAffineTransform2D | None = None

    def __post_init__(self) -> None:
        if (self.ref is None) == (self.inline is None):
            raise ValueError("exactly one of ref or inline transform must be provided")

    @classmethod
    def from_ref(cls, transform_id: str, *, required: bool = True) -> "VisualTransformBinding":
        """Construct a binding to a named transform resource."""
        return cls(ref=TransformRef(transform_id, required=required))

    @classmethod
    def inline_affine(cls, matrix: Matrix3x3) -> "VisualTransformBinding":
        """Construct a binding with an inline affine transform."""
        return cls(inline=InlineAffineTransform2D(matrix))


def validate_affine_2d_matrix(matrix: Matrix3x3) -> None:
    """Validate S027 finite invertible affine 2D matrix semantics."""
    if not isinstance(matrix, np.ndarray):
        raise TypeError("matrix must be a numpy array")
    if matrix.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
        raise TypeError("matrix must be float32 or float64")
    if matrix.shape != (3, 3):
        raise ValueError(
            f"{TransformDiagnosticCode.TRANSFORM_BAD_SHAPE.value}: matrix must have shape (3, 3)"
        )
    if not np.all(np.isfinite(matrix)):
        raise ValueError(
            f"{TransformDiagnosticCode.TRANSFORM_NONFINITE.value}: matrix values must be finite"
        )
    if not np.array_equal(matrix[2, :], np.array([0.0, 0.0, 1.0], dtype=matrix.dtype)):
        raise ValueError(
            f"{TransformDiagnosticCode.TRANSFORM_NON_AFFINE.value}: final row must be [0, 0, 1]"
        )
    determinant = float(np.linalg.det(np.asarray(matrix[:2, :2], dtype=np.float64)))
    if determinant == 0.0:
        raise ValueError(
            f"{TransformDiagnosticCode.TRANSFORM_SINGULAR.value}: upper-left 2x2 matrix must be invertible"
        )


def validate_view2d_limits(name: str, limits: tuple[float, float]) -> None:
    """Validate S027 linear View2D axis limits."""
    if len(limits) != 2:
        raise ValueError(f"{name} must contain two values")
    low, high = limits
    if not np.isfinite(low) or not np.isfinite(high):
        raise ValueError(
            f"{TransformDiagnosticCode.VIEW2D_NONFINITE.value}: {name} values must be finite"
        )
    if low == high:
        raise ValueError(
            f"{TransformDiagnosticCode.VIEW2D_DEGENERATE.value}: {name} endpoints must differ"
        )
