"""Projected-NDC mesh face-culling helpers."""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
import math

from .visuals import FaceCulling

Float3Like = Sequence[float]

MESH_FACE_CULLING_DATA3D_PROJECTED_NDC_CAPABILITY = (
    "meshvisual.face_culling.data3d.projected_ndc.v1"
)
MESH_FACE_CULLING_NDC3_PANEL_WINDING_CAPABILITY = (
    "meshvisual.face_culling.ndc3.panel_winding.v1"
)
QUERY_VIEW3D_MESH_TRIANGLE_PICK_FACE_CULLING_CAPABILITY = (
    "query.view3d.mesh_triangle_pick.face_culling.v1"
)


class ProjectedFaceClassification(str, Enum):
    """Projected panel-NDC winding classification for one triangle."""

    FRONT = "front"
    BACK = "back"
    DEGENERATE = "degenerate"


def projected_triangle_area2(
    q0: Float3Like, q1: Float3Like, q2: Float3Like
) -> float:
    """Return the signed 2D area in panel NDC x/y.

    Positive area is front-facing under the S050 projected-NDC contract.
    """
    _validate_projected_vertex("q0", q0)
    _validate_projected_vertex("q1", q1)
    _validate_projected_vertex("q2", q2)
    return (float(q1[0]) - float(q0[0])) * (float(q2[1]) - float(q0[1])) - (
        float(q1[1]) - float(q0[1])
    ) * (float(q2[0]) - float(q0[0]))


def classify_projected_triangle(
    area2: float, *, epsilon: float = 0.0
) -> ProjectedFaceClassification:
    """Classify a projected triangle from its signed panel-NDC area."""
    _validate_epsilon(epsilon)
    if not math.isfinite(area2):
        raise ValueError("area2 must be finite")
    if area2 > epsilon:
        return ProjectedFaceClassification.FRONT
    if area2 < -epsilon:
        return ProjectedFaceClassification.BACK
    return ProjectedFaceClassification.DEGENERATE


def face_culling_excludes(
    classification: ProjectedFaceClassification, face_culling: FaceCulling
) -> bool:
    """Return whether culling suppresses a non-degenerate projected triangle."""
    if not isinstance(classification, ProjectedFaceClassification):
        raise TypeError("classification must be a ProjectedFaceClassification")
    if not isinstance(face_culling, FaceCulling):
        raise TypeError("face_culling must be a FaceCulling")
    if classification is ProjectedFaceClassification.DEGENERATE:
        return False
    if face_culling is FaceCulling.BACK:
        return classification is ProjectedFaceClassification.BACK
    if face_culling is FaceCulling.FRONT:
        return classification is ProjectedFaceClassification.FRONT
    return False


def projected_triangle_has_strict_contribution(
    area2: float, face_culling: FaceCulling, *, epsilon: float = 0.0
) -> bool:
    """Return whether a projected triangle can contribute strict raster fragments."""
    classification = classify_projected_triangle(area2, epsilon=epsilon)
    if classification is ProjectedFaceClassification.DEGENERATE:
        return False
    return not face_culling_excludes(classification, face_culling)


def _validate_projected_vertex(name: str, value: Float3Like) -> None:
    if len(value) < 2:
        raise ValueError(f"{name} must contain at least x and y")
    if not math.isfinite(float(value[0])) or not math.isfinite(float(value[1])):
        raise ValueError(f"{name} x/y values must be finite")


def _validate_epsilon(epsilon: float) -> None:
    if not math.isfinite(epsilon) or epsilon < 0.0:
        raise ValueError("epsilon must be finite and non-negative")
