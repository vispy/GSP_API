"""In-process replay harness for conformance fixtures."""

from __future__ import annotations

from dataclasses import dataclass

from gsp.protocol import QueryResult
from gsp_matplotlib.guide_query import query_axis_guides
from gsp_matplotlib.protocol_query import query_visuals
from gsp_matplotlib.tiled_image import query_tiled_image_source

from .baseline import capability_snapshot_fixture, guide_scene, point_over_image_scene, tiled_source_scene


@dataclass(frozen=True, slots=True)
class InProcessReplayResult:
    """Semantic replay result for the current Python/in-process conformance baseline."""

    server_name: str
    visual_families: tuple[str, ...]
    extensions: tuple[str, ...]
    point_query: QueryResult
    guide_query: QueryResult
    guide_miss: QueryResult
    tiled_query: QueryResult
    tiled_mosaic_source_rect: tuple[int, int, int, int]
    tiled_mosaic_shape: tuple[int, ...]


def replay_conformance_fixtures() -> InProcessReplayResult:
    """Replay the current conformance fixtures without JSON/base64 serialization."""
    capabilities = capability_snapshot_fixture()
    point_scene = point_over_image_scene()
    guide = guide_scene()
    tiled = tiled_source_scene()

    point_query = query_visuals(point_scene.query, point_scene.entries)
    guide_query = query_axis_guides(guide.tick_query, guide.view, guide.guide_entries)
    guide_miss = query_axis_guides(guide.miss_query, guide.view, guide.guide_entries)
    tiled_mosaic = tiled.provider.get_viewport_mosaic(tiled.mosaic_request)
    tiled_query = query_tiled_image_source(
        tiled.query,
        tiled.source,
        tiled.provider,
        source_rect=tiled.mosaic_request.source_rect,
        extent=tiled.extent,
        visual_id=tiled.visual_id,
    )

    return InProcessReplayResult(
        server_name=capabilities.server_name,
        visual_families=capabilities.visual_families,
        extensions=capabilities.extensions,
        point_query=point_query,
        guide_query=guide_query,
        guide_miss=guide_miss,
        tiled_query=tiled_query,
        tiled_mosaic_source_rect=tiled_mosaic.source_rect,
        tiled_mosaic_shape=tuple(tiled_mosaic.data.shape),
    )
