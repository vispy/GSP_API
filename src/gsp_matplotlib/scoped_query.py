"""Reference scoped query routing for Matplotlib-backed protocol scenes."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from gsp.protocol import (
    GUIDE_QUERY_PAYLOAD_KIND,
    QueryContributionKind,
    QueryHit,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryScope,
    QueryStatus,
    ResolvedLayoutSnapshot,
    View2D,
)
from gsp_matplotlib.guide_query import QueryGuideEntry, query_axis_guides
from gsp_matplotlib.layout_query import query_resolved_layout_guides
from gsp_matplotlib.protocol_query import QueryVisualEntry, query_visuals, unsupported_query_result


@dataclass(frozen=True, slots=True)
class _OrderedHit:
    """Query hit with bounded reference render order."""

    hit: QueryHit
    z_order: int


@dataclass(frozen=True, slots=True)
class QueryExtensionEntry:
    """Data-scoped extension query provider plus bounded render order."""

    query: Callable[[QueryRequest], QueryResult]
    extension_payload_kinds: tuple[str, ...]
    z_order: int = 0

    def __post_init__(self) -> None:
        for kind in self.extension_payload_kinds:
            if not kind:
                raise ValueError("extension payload kinds must not be empty")


def query_scoped_scene(
    request: QueryRequest,
    *,
    visual_entries: Iterable[QueryVisualEntry] = (),
    extension_entries: Iterable[QueryExtensionEntry] = (),
    view: View2D | None = None,
    guide_entries: tuple[QueryGuideEntry, ...] = (),
    layout_snapshot: ResolvedLayoutSnapshot | None = None,
    panel_bounds: tuple[float, float, float, float] | None = None,
) -> QueryResult:
    """Route a reference query by GSP query scope.

    This is the bounded Matplotlib/reference path for S015. It treats `z_order` on
    data and guide entries as the comparable render-order key for conformance fixtures.
    """
    visual_entries = tuple(visual_entries)
    extension_entries = tuple(extension_entries)
    if request.scope == QueryScope.DATA:
        return _query_data_scope(request, visual_entries, extension_entries, panel_bounds)
    if request.scope == QueryScope.GUIDES:
        if layout_snapshot is not None:
            if request.requested_extension_payload_kinds and not _guide_entries_support(request):
                return unsupported_query_result(request, "guide query cannot satisfy requested extension payloads")
            return query_resolved_layout_guides(request, layout_snapshot)
        if view is None:
            return unsupported_query_result(request, "guide query requires a View2D")
        if request.requested_extension_payload_kinds and not _guide_entries_support(request):
            return unsupported_query_result(request, "guide query cannot satisfy requested extension payloads")
        return query_axis_guides(request, view, guide_entries)
    if request.scope == QueryScope.ALL_RENDERED:
        if guide_entries and view is None and layout_snapshot is None:
            return unsupported_query_result(request, "all-rendered query with guides requires a View2D")
        return _query_all_rendered(
            request,
            visual_entries,
            extension_entries,
            view,
            guide_entries,
            layout_snapshot,
            panel_bounds,
        )
    return unsupported_query_result(request, f"query scope {request.scope.value!r} is not supported")


def _query_all_rendered(
    request: QueryRequest,
    visual_entries: tuple[QueryVisualEntry, ...],
    extension_entries: tuple[QueryExtensionEntry, ...],
    view: View2D | None,
    guide_entries: tuple[QueryGuideEntry, ...],
    layout_snapshot: ResolvedLayoutSnapshot | None,
    panel_bounds: tuple[float, float, float, float] | None,
) -> QueryResult:
    if request.requested_extension_payload_kinds:
        data_supported = _extension_entries_support(request, extension_entries)
        guide_supported = (layout_snapshot is not None or bool(guide_entries)) and _guide_entries_support(request)
        if not data_supported and not guide_supported:
            return unsupported_query_result(request, "all-rendered query cannot satisfy requested extension payloads")
        data_result = (
            _query_all_data_hits(request, visual_entries, extension_entries, panel_bounds)
            if data_supported
            else _miss_result(request)
        )
        guide_result = (
            _query_all_guide_hits(request, view, guide_entries, layout_snapshot)
            if guide_supported
            else _miss_result(request)
        )
        if data_result.status == QueryStatus.OUTSIDE_PANEL:
            return data_result
        return _merge_ordered_results(request, data_result, guide_result, visual_entries, extension_entries, guide_entries)

    data_result = _query_all_data_hits(request, visual_entries, extension_entries, panel_bounds)
    if data_result.status == QueryStatus.OUTSIDE_PANEL:
        return data_result
    guide_result = _query_all_guide_hits(request, view, guide_entries, layout_snapshot)

    return _merge_ordered_results(request, data_result, guide_result, visual_entries, extension_entries, guide_entries)


def _merge_ordered_results(
    request: QueryRequest,
    data_result: QueryResult,
    guide_result: QueryResult,
    visual_entries: tuple[QueryVisualEntry, ...],
    extension_entries: tuple[QueryExtensionEntry, ...],
    guide_entries: tuple[QueryGuideEntry, ...],
) -> QueryResult:
    for result in (data_result, guide_result):
        if result.status == QueryStatus.UNSUPPORTED:
            return result
        if result.status == QueryStatus.FAILED:
            return result

    ordered_hits = (
        _ordered_data_hits(data_result, visual_entries)
        + _ordered_extension_hits(data_result, extension_entries)
        + _ordered_guide_hits(guide_result, guide_entries)
    )
    ordered_hits.sort(key=lambda item: item.z_order, reverse=True)

    if not ordered_hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=request.layout_snapshot_id,
        )

    hits = tuple(item.hit for item in ordered_hits)
    if request.hit_policy == QueryHitPolicy.ALL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            hits=hits,
            layout_snapshot_id=request.layout_snapshot_id,
        )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        hits=(hits[0],),
        layout_snapshot_id=request.layout_snapshot_id,
    )


def _query_all_data_hits(
    request: QueryRequest,
    visual_entries: tuple[QueryVisualEntry, ...],
    extension_entries: tuple[QueryExtensionEntry, ...],
    panel_bounds: tuple[float, float, float, float] | None,
) -> QueryResult:
    return _query_data_scope(
        _with_hit_policy(request, QueryHitPolicy.ALL),
        visual_entries,
        extension_entries,
        panel_bounds=panel_bounds,
    )


def _query_data_scope(
    request: QueryRequest,
    visual_entries: tuple[QueryVisualEntry, ...],
    extension_entries: tuple[QueryExtensionEntry, ...],
    panel_bounds: tuple[float, float, float, float] | None,
) -> QueryResult:
    if panel_bounds is not None and not _contains(panel_bounds, request.coordinate):
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.OUTSIDE_PANEL,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=request.layout_snapshot_id,
        )
    if request.requested_extension_payload_kinds and not _extension_entries_support(request, extension_entries):
        return unsupported_query_result(request, "data query cannot satisfy requested extension payloads")

    ordered_hits: list[_OrderedHit] = []
    if not request.requested_extension_payload_kinds:
        data_result = query_visuals(
            _with_hit_policy(request, QueryHitPolicy.ALL),
            visual_entries,
            panel_bounds=None,
        )
        if data_result.status in (QueryStatus.UNSUPPORTED, QueryStatus.FAILED):
            return data_result
        ordered_hits.extend(_ordered_data_hits(data_result, visual_entries))

    extension_result = _query_extension_hits(_with_hit_policy(request, QueryHitPolicy.ALL), extension_entries)
    if extension_result.status in (QueryStatus.UNSUPPORTED, QueryStatus.FAILED):
        return extension_result
    ordered_hits.extend(_ordered_extension_hits(extension_result, extension_entries))
    ordered_hits.sort(key=lambda item: item.z_order, reverse=True)

    if not ordered_hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=request.layout_snapshot_id,
        )

    hits = tuple(item.hit for item in ordered_hits)
    if request.hit_policy == QueryHitPolicy.ALL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            hits=hits,
            layout_snapshot_id=request.layout_snapshot_id,
        )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        hits=(hits[0],),
        layout_snapshot_id=request.layout_snapshot_id,
    )


def _query_extension_hits(request: QueryRequest, entries: tuple[QueryExtensionEntry, ...]) -> QueryResult:
    hits: list[QueryHit] = []
    for entry in entries:
        if request.requested_extension_payload_kinds and not _extension_entry_supports(request, entry):
            continue
        result = entry.query(request)
        if result.status in (QueryStatus.UNSUPPORTED, QueryStatus.FAILED):
            return result
        if result.status == QueryStatus.HIT:
            hits.extend(
                QueryHit(
                    contribution_kind=QueryContributionKind.DATA,
                    visual_id=hit.visual_id,
                    visual_family=hit.visual_family,
                    item_id=hit.item_id,
                    texel=hit.texel,
                    visual_coordinate=hit.visual_coordinate,
                    data_coordinate=hit.data_coordinate,
                    displayed_rgba=hit.displayed_rgba,
                    value=hit.value,
                    extension_payload_kind=hit.extension_payload_kind,
                    extension_payload=hit.extension_payload,
                )
                for hit in result.hits
            )
    if not hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=request.layout_snapshot_id,
        )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        hits=tuple(hits),
        layout_snapshot_id=request.layout_snapshot_id,
    )


def _query_all_guide_hits(
    request: QueryRequest,
    view: View2D | None,
    guide_entries: tuple[QueryGuideEntry, ...],
    layout_snapshot: ResolvedLayoutSnapshot | None = None,
) -> QueryResult:
    if layout_snapshot is not None:
        return query_resolved_layout_guides(
            _with_hit_policy(request, QueryHitPolicy.ALL), layout_snapshot
        )
    if not guide_entries:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=request.layout_snapshot_id,
        )
    if view is None:
        return unsupported_query_result(request, "all-rendered guide query requires a View2D")
    return query_axis_guides(_with_hit_policy(request, QueryHitPolicy.ALL), view, guide_entries)


def _ordered_data_hits(result: QueryResult, entries: tuple[QueryVisualEntry, ...]) -> list[_OrderedHit]:
    z_by_visual = {entry.visual.id: entry.z_order for entry in entries}
    return [
        _OrderedHit(hit, z_by_visual.get(hit.visual_id or "", 0))
        for hit in result.hits
        if hit.extension_payload_kind is None
    ]


def _ordered_guide_hits(result: QueryResult, entries: tuple[QueryGuideEntry, ...]) -> list[_OrderedHit]:
    z_by_guide = {entry.guide.id: entry.z_order for entry in entries}
    return [_OrderedHit(hit, z_by_guide.get(hit.visual_id or "", 0)) for hit in result.hits]


def _ordered_extension_hits(result: QueryResult, entries: tuple[QueryExtensionEntry, ...]) -> list[_OrderedHit]:
    z_by_kind = {kind: entry.z_order for entry in entries for kind in entry.extension_payload_kinds}
    return [
        _OrderedHit(hit, z_by_kind.get(hit.extension_payload_kind or "", 0))
        for hit in result.hits
        if hit.extension_payload_kind is not None
    ]


def _extension_entries_support(request: QueryRequest, entries: tuple[QueryExtensionEntry, ...]) -> bool:
    available = {kind for entry in entries for kind in entry.extension_payload_kinds}
    return set(request.requested_extension_payload_kinds).issubset(available)


def _extension_entry_supports(request: QueryRequest, entry: QueryExtensionEntry) -> bool:
    return set(request.requested_extension_payload_kinds).issubset(set(entry.extension_payload_kinds))


def _guide_entries_support(request: QueryRequest) -> bool:
    return set(request.requested_extension_payload_kinds).issubset({GUIDE_QUERY_PAYLOAD_KIND})


def _miss_result(request: QueryRequest) -> QueryResult:
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.MISS,
        hit=False,
        panel_coordinate=request.coordinate,
        layout_snapshot_id=request.layout_snapshot_id,
    )


def _contains(bounds: tuple[float, float, float, float], coordinate: tuple[float, float]) -> bool:
    left, right, bottom, top = bounds
    x, y = coordinate
    x_min, x_max = sorted((left, right))
    y_min, y_max = sorted((bottom, top))
    return x_min <= x <= x_max and y_min <= y <= y_max


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
        layout_snapshot_id=request.layout_snapshot_id,
    )
