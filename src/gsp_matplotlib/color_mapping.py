"""Reference scalar color mapping utilities for the Matplotlib backend."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from collections.abc import Mapping

import matplotlib
import numpy as np
import numpy.typing as npt

from gsp.protocol import ColorMapId, ColorScale, ScalarRangeClass


@dataclass(frozen=True, slots=True)
class ScalarColorResult:
    """One canonical scalar-to-RGBA mapping result."""

    source_value: float
    normalized_value_raw: float
    normalized_value_clipped: float
    range_class: ScalarRangeClass
    lut_index: int
    displayed_rgba: tuple[float, float, float, float]


def resolve_color_scale(
    color_scales: Mapping[str, ColorScale] | None, color_scale_id: str
) -> ColorScale:
    """Return a color scale by id, with a protocol-oriented error."""
    if color_scales is None or color_scale_id not in color_scales:
        raise ValueError(f"missing color scale: {color_scale_id}")
    return color_scales[color_scale_id]


@lru_cache(maxsize=None)
def canonical_lut(colormap_id: ColorMapId) -> npt.NDArray[np.uint8]:
    """Return the canonical 256-entry RGBA uint8 LUT for an S026 colormap."""
    if colormap_id is ColorMapId.GRAY:
        values = np.arange(256, dtype=np.uint8)
        alpha = np.full((256,), 255, dtype=np.uint8)
        return np.stack([values, values, values, alpha], axis=1)

    cmap = matplotlib.colormaps[colormap_id.value]
    rgba = cmap(np.linspace(0.0, 1.0, 256, dtype=np.float64))
    return np.rint(rgba * 255.0).astype(np.uint8)


def listed_colormap_for_scale(scale: ColorScale) -> matplotlib.colors.ListedColormap:
    """Build a Matplotlib colormap from the canonical GSP LUT."""
    lut = canonical_lut(scale.colormap.id).astype(np.float64) / 255.0
    return matplotlib.colors.ListedColormap(lut, name=f"gsp-{scale.colormap.id.value}")


def map_scalar_value(
    value: float, scale: ColorScale, *, alpha: float = 1.0
) -> ScalarColorResult:
    """Map one scalar value using S026 linear normalization and LUT sampling."""
    source = float(value)
    normalize = scale.normalize
    raw = (source - normalize.vmin) / (normalize.vmax - normalize.vmin)
    clipped = float(np.clip(raw, 0.0, 1.0))
    if raw < 0.0:
        range_class = ScalarRangeClass.UNDER
    elif raw > 1.0:
        range_class = ScalarRangeClass.OVER
    else:
        range_class = ScalarRangeClass.IN_RANGE
    lut_index = int(min(255, np.floor(clipped * 256.0)))
    rgba = canonical_lut(scale.colormap.id)[lut_index].astype(np.float64) / 255.0
    rgba[3] *= float(alpha)
    return ScalarColorResult(
        source_value=source,
        normalized_value_raw=float(raw),
        normalized_value_clipped=clipped,
        range_class=range_class,
        lut_index=lut_index,
        displayed_rgba=(float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3])),
    )


def map_scalar_values(
    values: npt.ArrayLike, scale: ColorScale, *, alpha: float = 1.0
) -> npt.NDArray[np.float64]:
    """Map scalar array values to canonical RGBA float colors."""
    array = np.asarray(values, dtype=np.float64)
    normalize = scale.normalize
    raw = (array - normalize.vmin) / (normalize.vmax - normalize.vmin)
    clipped = np.clip(raw, 0.0, 1.0)
    indices = np.minimum(255, np.floor(clipped * 256.0)).astype(np.int16)
    rgba = canonical_lut(scale.colormap.id)[indices].astype(np.float64) / 255.0
    rgba[..., 3] *= float(alpha)
    return rgba
