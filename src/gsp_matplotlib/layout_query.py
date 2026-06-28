"""Layout-snapshot guide query helpers for Matplotlib reference output."""

from __future__ import annotations

from gsp.protocol import (
    GUIDE_QUERY_PAYLOAD_KIND,
    GuideQueryPayload,
    QueryCoordinateSpace,
    QueryHitPolicy,
    QueryRequest,
    QueryResult,
    QueryStatus,
    ResolvedGuideBox,
    ResolvedLayoutSnapshot,
)


def query_resolved_layout_guides(
    request: QueryRequest,
    snapshot: ResolvedLayoutSnapshot,
) -> QueryResult:
    """Query guide boxes from a resolved Matplotlib layout snapshot."""
    if request.coordinate_space != QueryCoordinateSpace.PANEL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.UNSUPPORTED,
            hit=False,
            panel_coordinate=request.coordinate,
            diagnostic="resolved layout guide query requires panel logical-pixel coordinates",
            layout_snapshot_id=snapshot.snapshot_id,
        )
    hits = tuple(
        _hit_for_box(request, snapshot.snapshot_id, box, index)
        for index, box in enumerate(_queryable_boxes(snapshot))
        if _contains(box, request.coordinate)
    )
    if not hits:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.MISS,
            hit=False,
            panel_coordinate=request.coordinate,
            layout_snapshot_id=snapshot.snapshot_id,
        )
    if request.hit_policy == QueryHitPolicy.ALL:
        return QueryResult(
            request_id=request.id,
            status=QueryStatus.HIT,
            hit=True,
            panel_coordinate=request.coordinate,
            hits=tuple(hit.hits[0] for hit in hits),
            layout_snapshot_id=snapshot.snapshot_id,
        )
    return hits[0]


def _queryable_boxes(
    snapshot: ResolvedLayoutSnapshot,
) -> tuple[ResolvedGuideBox, ...]:
    return (
        snapshot.title_boxes
        + snapshot.axis_label_boxes
        + snapshot.tick_label_boxes
        + snapshot.legend_boxes
        + snapshot.colorbar_boxes
    )


def _hit_for_box(
    request: QueryRequest,
    snapshot_id: str,
    box: ResolvedGuideBox,
    item_id: int,
) -> QueryResult:
    role = box.role or box.kind
    payload = GuideQueryPayload(guide_id=box.guide_id, role=role)
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=box.guide_id,
        item_id=item_id,
        value=role,
        extension_payload_kind=GUIDE_QUERY_PAYLOAD_KIND,
        extension_payload=payload,
        layout_snapshot_id=snapshot_id,
    )


def _contains(box: ResolvedGuideBox, coordinate: tuple[float, float]) -> bool:
    x, y = coordinate
    rect = box.rect_px
    return rect.x <= x <= rect.x + rect.width and rect.y <= y <= rect.y + rect.height
