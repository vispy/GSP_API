"""View3D mesh-triangle pick geometry helpers."""

from __future__ import annotations

from collections.abc import Sequence
import math

from .mesh_culling import (
    ProjectedFaceClassification,
    classify_projected_triangle,
    projected_triangle_area2,
)

Float2Like = Sequence[float]
Float3Like = Sequence[float]

QUERY_VIEW3D_MESH_TRIANGLE_PICK_GEOMETRY_CAPABILITY = (
    "query.view3d.mesh_triangle_pick.geometry.v1"
)
QUERY_VIEW3D_MESH_TRIANGLE_PICK_FACING_CAPABILITY = (
    "query.view3d.mesh_triangle_pick.facing.v1"
)


def mesh_pick_barycentric_2d(
    point_xy: Float2Like,
    q0: Float3Like,
    q1: Float3Like,
    q2: Float3Like,
    *,
    epsilon: float = 1.0e-12,
) -> tuple[float, float, float] | None:
    """Return barycentric coordinates in projected panel NDC x/y.

    Coordinates are ordered in the public source face order ``(q0, q1, q2)``.
    ``None`` means the point is outside the projected triangle or the triangle is
    projected-degenerate for geometry-payload purposes.
    """
    _validate_float2("point_xy", point_xy)
    _validate_float3_xy("q0", q0)
    _validate_float3_xy("q1", q1)
    _validate_float3_xy("q2", q2)
    _validate_epsilon(epsilon)

    v0 = (float(q2[0]) - float(q0[0]), float(q2[1]) - float(q0[1]))
    v1 = (float(q1[0]) - float(q0[0]), float(q1[1]) - float(q0[1]))
    v2 = (float(point_xy[0]) - float(q0[0]), float(point_xy[1]) - float(q0[1]))
    dot00 = v0[0] * v0[0] + v0[1] * v0[1]
    dot01 = v0[0] * v1[0] + v0[1] * v1[1]
    dot02 = v0[0] * v2[0] + v0[1] * v2[1]
    dot11 = v1[0] * v1[0] + v1[1] * v1[1]
    dot12 = v1[0] * v2[0] + v1[1] * v2[1]
    denominator = dot00 * dot11 - dot01 * dot01
    if abs(denominator) <= epsilon:
        return None
    inv_denominator = 1.0 / denominator
    u = (dot11 * dot02 - dot01 * dot12) * inv_denominator
    v = (dot00 * dot12 - dot01 * dot02) * inv_denominator
    w = 1.0 - u - v
    if u < -epsilon or v < -epsilon or w < -epsilon:
        return None
    return (w, v, u)


def mesh_pick_panel_ndc_z(
    barycentric: Float3Like,
    q0: Float3Like,
    q1: Float3Like,
    q2: Float3Like,
) -> float:
    """Interpolate panel-NDC z for a picked triangle hit."""
    lambdas = _validate_barycentric(barycentric)
    _validate_float3("q0", q0)
    _validate_float3("q1", q1)
    _validate_float3("q2", q2)
    return (
        lambdas[0] * float(q0[2])
        + lambdas[1] * float(q1[2])
        + lambdas[2] * float(q2[2])
    )


def mesh_pick_data_xyz(
    barycentric: Float3Like,
    p0: Float3Like,
    p1: Float3Like,
    p2: Float3Like,
) -> tuple[float, float, float]:
    """Interpolate DATA-space xyz for a picked triangle hit."""
    lambdas = _validate_barycentric(barycentric)
    _validate_float3("p0", p0)
    _validate_float3("p1", p1)
    _validate_float3("p2", p2)
    return (
        lambdas[0] * float(p0[0])
        + lambdas[1] * float(p1[0])
        + lambdas[2] * float(p2[0]),
        lambdas[0] * float(p0[1])
        + lambdas[1] * float(p1[1])
        + lambdas[2] * float(p2[1]),
        lambdas[0] * float(p0[2])
        + lambdas[1] * float(p1[2])
        + lambdas[2] * float(p2[2]),
    )


def mesh_pick_projected_front_facing(
    q0: Float3Like, q1: Float3Like, q2: Float3Like
) -> bool:
    """Return projected panel-NDC facing for a non-degenerate triangle."""
    area2 = projected_triangle_area2(q0, q1, q2)
    classification = classify_projected_triangle(area2)
    if classification is ProjectedFaceClassification.DEGENERATE:
        raise ValueError("projected-degenerate triangles do not have facing")
    return classification is ProjectedFaceClassification.FRONT


def _validate_float2(name: str, value: Float2Like) -> None:
    if len(value) != 2:
        raise ValueError(f"{name} must contain two values")
    if not math.isfinite(float(value[0])) or not math.isfinite(float(value[1])):
        raise ValueError(f"{name} values must be finite")


def _validate_float3(name: str, value: Float3Like) -> None:
    if len(value) != 3:
        raise ValueError(f"{name} must contain three values")
    if not all(math.isfinite(float(component)) for component in value):
        raise ValueError(f"{name} values must be finite")


def _validate_float3_xy(name: str, value: Float3Like) -> None:
    if len(value) != 3:
        raise ValueError(f"{name} must contain three values")
    if not math.isfinite(float(value[0])) or not math.isfinite(float(value[1])):
        raise ValueError(f"{name} x/y values must be finite")


def _validate_barycentric(value: Float3Like) -> tuple[float, float, float]:
    _validate_float3("barycentric", value)
    return (float(value[0]), float(value[1]), float(value[2]))


def _validate_epsilon(epsilon: float) -> None:
    if not math.isfinite(epsilon) or epsilon < 0.0:
        raise ValueError("epsilon must be finite and non-negative")
