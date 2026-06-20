"""GSP v0.1 conformance fixture package."""

from .baseline import (
    ConformanceScene,
    capability_snapshot_fixture,
    image_visual_fixture,
    point_over_image_scene,
    point_visual_fixture,
)

__all__ = [
    "ConformanceScene",
    "capability_snapshot_fixture",
    "image_visual_fixture",
    "point_over_image_scene",
    "point_visual_fixture",
]
