"""GSP v0.1 conformance fixture package."""

from .baseline import (
    ConformanceScene,
    GuideConformanceScene,
    TiledSourceConformanceScene,
    capability_snapshot_fixture,
    guide_scene,
    image_visual_fixture,
    point_over_image_scene,
    point_visual_fixture,
    tiled_image_source_fixture,
    tiled_source_scene,
)
from .debug_report import conformance_debug_report
from .matrix import BackendConformanceExpectation, backend_conformance_matrix
from .replay import InProcessReplayResult, replay_conformance_fixtures

__all__ = [
    "BackendConformanceExpectation",
    "ConformanceScene",
    "GuideConformanceScene",
    "InProcessReplayResult",
    "TiledSourceConformanceScene",
    "backend_conformance_matrix",
    "capability_snapshot_fixture",
    "conformance_debug_report",
    "guide_scene",
    "image_visual_fixture",
    "point_over_image_scene",
    "point_visual_fixture",
    "replay_conformance_fixtures",
    "tiled_image_source_fixture",
    "tiled_source_scene",
]
