"""Case models for the S023 visual QA harness."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeAlias

import numpy as np

from gsp.protocol import ImageVisual, MarkerVisual, PointVisual


ProtocolVisual: TypeAlias = PointVisual | MarkerVisual | ImageVisual


@dataclass(frozen=True, slots=True)
class VisualQAScene:
    """A protocol scene plus array sidecars for one visual QA case."""

    case_id: str
    visuals: tuple[ProtocolVisual, ...]
    arrays: dict[str, np.ndarray]
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
