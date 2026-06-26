"""Reference scalar color mapping utilities for the Matplotlib backend."""

from __future__ import annotations

import matplotlib
import numpy as np

from gsp.protocol import ColorScale
from gsp.protocol.color_mapping import (
    ScalarColorResult,
    canonical_lut,
    map_scalar_value,
    map_scalar_values,
    resolve_color_scale,
)


def listed_colormap_for_scale(scale: ColorScale) -> matplotlib.colors.ListedColormap:
    """Build a Matplotlib colormap from the canonical GSP LUT."""
    lut = canonical_lut(scale.colormap.id).astype(np.float64) / 255.0
    return matplotlib.colors.ListedColormap(lut, name=f"gsp-{scale.colormap.id.value}")


__all__ = [
    "ScalarColorResult",
    "canonical_lut",
    "listed_colormap_for_scale",
    "map_scalar_value",
    "map_scalar_values",
    "resolve_color_scale",
]
