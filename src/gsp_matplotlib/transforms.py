"""Reference transform helpers for S027 Matplotlib paths."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import numpy.typing as npt

from gsp.protocol import AffineTransform2DResource, CoordinateSpace, View2D
from gsp.protocol.transforms import VisualTransformBinding


def transformed_positions(
    positions: npt.NDArray[np.float32] | npt.NDArray[np.float64],
    binding: VisualTransformBinding | None,
    resources: Mapping[str, AffineTransform2DResource] | None,
) -> npt.NDArray[np.float64]:
    """Apply the optional visual-local transform to x/y positions."""
    xy = np.asarray(positions[:, :2], dtype=np.float64)
    if binding is None:
        return xy
    matrix = _binding_matrix(binding, resources)
    homogeneous = np.column_stack([xy, np.ones((xy.shape[0],), dtype=np.float64)])
    return np.asarray((homogeneous @ matrix.T)[:, :2], dtype=np.float64)


def inverse_transform_coordinate(
    coordinate: tuple[float, float],
    binding: VisualTransformBinding | None,
    resources: Mapping[str, AffineTransform2DResource] | None,
) -> tuple[float, float]:
    """Map a declared-space coordinate back to source/local x/y."""
    if binding is None:
        return coordinate
    matrix = np.linalg.inv(_binding_matrix(binding, resources))
    vector = np.array([coordinate[0], coordinate[1], 1.0], dtype=np.float64)
    result = matrix @ vector
    return (float(result[0]), float(result[1]))


def data_to_panel_ndc(
    coordinate: tuple[float, float], view: View2D | None
) -> tuple[float, float]:
    """Map DATA coordinates through a linear View2D into panel NDC."""
    if view is None:
        return coordinate
    x0, x1 = view.xlim
    y0, y1 = view.ylim
    x, y = coordinate
    return (
        float(-1.0 + 2.0 * (x - x0) / (x1 - x0)),
        float(-1.0 + 2.0 * (y - y0) / (y1 - y0)),
    )


def declared_to_panel_ndc(
    coordinate: tuple[float, float],
    coordinate_space: CoordinateSpace,
    view: View2D | None,
) -> tuple[float, float]:
    """Map a declared-space coordinate to panel NDC."""
    if coordinate_space is CoordinateSpace.DATA:
        return data_to_panel_ndc(coordinate, view)
    return coordinate


def panel_ndc_to_axes_fraction(
    coordinates: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Map panel NDC coordinates to Matplotlib axes-fraction coordinates."""
    return (coordinates + 1.0) * 0.5


def coordinate_to_axes_fraction(coordinate: tuple[float, float]) -> tuple[float, float]:
    """Map one panel NDC coordinate to axes-fraction coordinates."""
    return ((coordinate[0] + 1.0) * 0.5, (coordinate[1] + 1.0) * 0.5)


def binding_transform_ids(binding: VisualTransformBinding | None) -> tuple[str, ...]:
    """Return named transform ids represented by a visual binding."""
    if binding is None or binding.ref is None:
        return ()
    return (binding.ref.id,)


def binding_inline_digest(binding: VisualTransformBinding | None) -> str | None:
    """Return a stable inline transform digest string for query payloads."""
    if binding is None or binding.inline is None:
        return None
    values = np.asarray(binding.inline.matrix, dtype=np.float64).reshape(-1)
    return ",".join(f"{value:.17g}" for value in values)


def _binding_matrix(
    binding: VisualTransformBinding,
    resources: Mapping[str, AffineTransform2DResource] | None,
) -> npt.NDArray[np.float64]:
    if binding.inline is not None:
        return np.asarray(binding.inline.matrix, dtype=np.float64)
    if binding.ref is None:
        raise ValueError("visual transform binding has no inline transform or ref")
    if resources is None or binding.ref.id not in resources:
        raise ValueError(f"missing transform resource: {binding.ref.id}")
    return np.asarray(resources[binding.ref.id].matrix, dtype=np.float64)
