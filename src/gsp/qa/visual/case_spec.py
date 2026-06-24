"""Case models for the S023 visual QA harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeAlias

import numpy as np

from gsp.protocol import (
    ColorScale,
    ColorbarGuide,
    ImageVisual,
    MeshVisual,
    MarkerVisual,
    PathVisual,
    PointVisual,
    SegmentVisual,
    TextVisual,
)


ProtocolVisual: TypeAlias = (
    PointVisual
    | MarkerVisual
    | SegmentVisual
    | PathVisual
    | ImageVisual
    | TextVisual
    | MeshVisual
)


@dataclass(frozen=True, slots=True)
class VisualQAScene:
    """A protocol scene plus array sidecars for one visual QA case."""

    case_id: str
    visuals: tuple[ProtocolVisual, ...]
    arrays: dict[str, np.ndarray]
    color_scales: tuple[ColorScale, ...] = ()
    colorbar_guides: tuple[ColorbarGuide, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class VisualQACase:
    """Metadata and builder for one visual QA case."""

    case_id: str
    title: str
    family: str
    required_features: tuple[str, ...]
    builder: Callable[[], VisualQAScene]

    def build(self) -> VisualQAScene:
        """Build the protocol scene for this case."""
        return self.builder()
