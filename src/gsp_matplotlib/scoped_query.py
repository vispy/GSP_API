"""Reference scoped query routing for Matplotlib-backed protocol scenes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from gsp.protocol import QueryHit, QueryHitPolicy, QueryRequest, QueryResult, QueryScope, QueryStatus, View2D
from gsp_matplotlib.guide_query import QueryGuideEntry, query_axis_guides
from gsp_matplotlib.protocol_query import QueryVisualEntry, query_visuals, unsupported_query_result


@dataclass(frozen=True, slots=True)
class _OrderedHit:
    """Query hit with bounded reference render order."""

    hit: QueryHit
    z_order: int


def query_scoped_scene(
    request: QueryRequest,
    *,
    visual_entries: Iterable[QueryVisualEntry] = (),
    view: View2D | None = None,
    guide_entries: tuple[QueryGuideEntry, ...] = (),
    panel_bounds: tuple[float, float, float, float] | None = None,
) -> QueryResult:
    """Route a reference query by GSP query scope.

    This is the bounded Matplotlib/reference path for S015. It treats `z_order` on
    data and guide entries as the comparable render-order key for conformance fixtures.
    """
    if request.scope == QueryScope.DATA:
        return query_visuals(request, visual_entries, panel_bounds=panel_bounds)
    if request.scope == QueryScope.GUIDES:
        if view is None:
            return unsupported_query_result(request, "guide query requires a View2D")
        return query_axis_guides(request, view, guide_entries)
    if request.scope == QueryScope.ALL_RENDERED:
        if guide_entries and view is None:
            return unsupported_query_result(request, "all-rendered query with guides requires a View2D")
        return _query_all_rendered(request, tuple(visual_entries), view, guide_entries, panel_bounds)
    return unsupported_query_result(request, f"query scope {request.scope.value!r} is not supported")


def _query_all_rendered(
    request: QueryRequest,
    visual_entries: tuple[QueryVisualEntry, ...],
    view: View2D | None,
    guide_entries: tuple[QueryGuideEntry, ...],
    panel_bounds: tuple[float, float, float, float] | None,
) -> QueryResult:
    data_result = _query_all_data_hits(request, visual_entries, panel_bounds)
    if data_result.status == QueryStatus.OUTSIDE_PANEL:
        return data_result
    guide_result = _query_all_guide_hits(request, view, guide_entries)

    for result in (data_result, guide_result):
        if result.status == QueryStatus.UNSUPPORTED:
            return result
        if result.status == QueryStatus.FAILED:
            return result

    ordered_hits = _ordered_data_hits(data_result, visual_entries) + _ordered_guide_hits(guide_result, guide_entries)
    ordered_hits.sort(key=lambda item: item.z_order, reverse=True)

    if not ordered_hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
        )

    hits = tuple(item.hit for item in ordered_hits)
    if request.hit_policy == QueryHitPolicy.ALL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            hits=hits,
        )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        hits=(hits[0],),
    )


def _query_all_data_hits(
    request: QueryRequest,
    visual_entries: tuple[QueryVisualEntry, ...],
    panel_bounds: tuple[float, float, float, float] | None,
) -> QueryResult:
    return query_visuals(
        _with_hit_policy(request, QueryHitPolicy.ALL),
        visual_entries,
        panel_bounds=panel_bounds,
    )


def _query_all_guide_hits(
    request: QueryRequest,
    view: View2D | None,
    guide_entries: tuple[QueryGuideEntry, ...],
) -> QueryResult:
    if not guide_entries:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
        )
    if view is None:
        return unsupported_query_result(request, "all-rendered guide query requires a View2D")
    return query_axis_guides(_with_hit_policy(request, QueryHitPolicy.ALL), view, guide_entries)


def _ordered_data_hits(result: QueryResult, entries: tuple[QueryVisualEntry, ...]) -> list[_OrderedHit]:
    z_by_visual = {entry.visual.id: entry.z_order for entry in entries}
    return [_OrderedHit(hit, z_by_visual.get(hit.visual_id or "", 0)) for hit in result.hits]


def _ordered_guide_hits(result: QueryResult, entries: tuple[QueryGuideEntry, ...]) -> list[_OrderedHit]:
    z_by_guide = {entry.guide.id: entry.z_order for entry in entries}
    return [_OrderedHit(hit, z_by_guide.get(hit.visual_id or "", 0)) for hit in result.hits]


def _with_hit_policy(request: QueryRequest, hit_policy: QueryHitPolicy) -> QueryRequest:
    return QueryRequest(
        id=request.id,
        panel_id=request.panel_id,
        coordinate=request.coordinate,
        coordinate_space=request.coordinate_space,
        scope=request.scope,
        hit_policy=hit_policy,
        requested_payload=request.requested_payload,
        requested_extension_payload_kinds=request.requested_extension_payload_kinds,
        freshness_policy=request.freshness_policy,
    )
