"""Bounded reference query support for semantic guide contributions."""

from __future__ import annotations

from dataclasses import dataclass
import math

from gsp.protocol import (
    AxisDimension,
    AxisGuide,
    GUIDE_QUERY_PAYLOAD_KIND,
    GuideQueryPayload,
    QueryRequest,
    QueryResult,
    QueryStatus,
    QueryHitPolicy,
    View2D,
    resolve_ticks,
)
from gsp_matplotlib.protocol_query import unsupported_query_result


@dataclass(frozen=True, slots=True)
class QueryGuideEntry:
    """Semantic guide plus z-order for reference guide query evaluation."""

    guide: AxisGuide
    z_order: int = 0


def query_axis_guides(
    request: QueryRequest,
    view: View2D,
    entries: tuple[QueryGuideEntry, ...],
    *,
    tolerance: float = 1e-9,
) -> QueryResult:
    """Answer a bounded guide query against semantic axis-guide tick contributions."""
    hits: list[QueryResult] = []
    for entry in sorted(entries, key=lambda item: item.z_order, reverse=True):
        guide = entry.guide
        if not guide.visible:
            continue
        hit = _query_axis_guide(request, view, guide, tolerance)
        if hit is not None:
            hits.append(hit)
    if hits:
        if request.hit_policy == QueryHitPolicy.ALL:
            return QueryResult(
                request_id=request.id,
                status=QueryStatus.HIT,
                hit=True,
                panel_coordinate=request.coordinate,
                hits=tuple(hit.hits[0] for hit in hits),
                layout_snapshot_id=request.layout_snapshot_id,
            )
        return hits[0]
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.MISS,
        hit=False,
        panel_coordinate=request.coordinate,
        layout_snapshot_id=request.layout_snapshot_id,
    )


def unsupported_guide_query_result(request: QueryRequest, provider_id: str) -> QueryResult:
    """Return unsupported for providers that render guides but cannot query them."""
    return unsupported_query_result(request, f"axis provider {provider_id!r} does not support guide queries")


def _query_axis_guide(request: QueryRequest, view: View2D, guide: AxisGuide, tolerance: float) -> QueryResult | None:
    x, y = request.coordinate
    if guide.dimension == AxisDimension.X:
        axis_value = view.y_range[0]
        if not _close(y, axis_value, tolerance):
            return None
        ticks = resolve_ticks(guide.tick_spec, view.x_range)
        for index, (value, label) in enumerate(zip(ticks.values, ticks.labels)):
            if _close(x, value, tolerance):
                return _hit(request, guide, "tick", value, label, item_id=index)
        if _within(x, view.x_range, tolerance):
            return _hit(request, guide, "spine", None, guide.label_text)

    if guide.dimension == AxisDimension.Y:
        axis_value = view.x_range[0]
        if not _close(x, axis_value, tolerance):
            return None
        ticks = resolve_ticks(guide.tick_spec, view.y_range)
        for index, (value, label) in enumerate(zip(ticks.values, ticks.labels)):
            if _close(y, value, tolerance):
                return _hit(request, guide, "tick", value, label, item_id=index)
        if _within(y, view.y_range, tolerance):
            return _hit(request, guide, "spine", None, guide.label_text)
    return None


def _hit(
    request: QueryRequest,
    guide: AxisGuide,
    role: str,
    tick_value: float | None,
    text_value: str | None,
    *,
    item_id: int | None = None,
) -> QueryResult:
    payload = GuideQueryPayload(
        guide_id=guide.id,
        role=role,
        axis_dimension=guide.dimension,
        tick_value=tick_value,
        text_value=text_value,
    )
    return QueryResult(
        request_id=request.id,
        status=QueryStatus.HIT,
        hit=True,
        panel_coordinate=request.coordinate,
        visual_id=guide.id,
        item_id=item_id,
        data_coordinate=request.coordinate,
        value=text_value if text_value is not None else tick_value,
        extension_payload_kind=GUIDE_QUERY_PAYLOAD_KIND,
        extension_payload=payload,
        layout_snapshot_id=request.layout_snapshot_id,
    )


def _close(left: float, right: float, tolerance: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=tolerance)


def _within(value: float, bounds: tuple[float, float], tolerance: float) -> bool:
    low, high = sorted(bounds)
    return low - tolerance <= value <= high + tolerance
