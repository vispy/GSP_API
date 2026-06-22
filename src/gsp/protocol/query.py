"""First-slice panel query models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ids import validate_id
from .guides import AxisDimension


class QueryCoordinateSpace(str, Enum):
    """Coordinate space used by a query request."""

    PANEL = "panel"
    DATA = "data"


class QueryScope(str, Enum):
    """Contribution scope considered by a panel query."""

    DATA = "data"
    GUIDES = "guides"
    ALL_RENDERED = "all-rendered"


class QueryHitPolicy(str, Enum):
    """How to choose a hit when multiple visuals contain the coordinate."""

    FRONTMOST = "frontmost"
    ALL = "all"


class QueryPayload(str, Enum):
    """Payload families requested by a panel query."""

    IDENTITY = "identity"
    COORDINATE = "coordinate"
    COLOR = "color"
    VALUE = "value"


class QueryStatus(str, Enum):
    """First-slice query result status."""

    HIT = "hit"
    MISS = "miss"
    OUTSIDE_PANEL = "outside-panel"
    UNSUPPORTED = "unsupported"
    STALE = "stale"
    DROPPED = "dropped"
    FAILED = "failed"


class VisualFamily(str, Enum):
    """Visual families reported by first-slice query results."""

    POINT = "point"
    IMAGE = "image"


class QueryContributionKind(str, Enum):
    """Top-level kind of contribution represented by a query hit."""

    DATA = "data"
    GUIDE = "guide"


GUIDE_QUERY_PAYLOAD_KIND = "gsp.guide-query@0.1"


@dataclass(frozen=True, slots=True)
class GuideQueryPayload:
    """Guide-specific payload for bounded reference guide queries."""

    guide_id: str
    role: str
    axis_dimension: AxisDimension | None = None
    tick_value: float | None = None
    text_value: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.guide_id)
        if not self.role:
            raise ValueError("guide query role must not be empty")


@dataclass(frozen=True, slots=True)
class QueryRequest:
    """One panel-local query request."""

    id: str
    panel_id: str
    coordinate: tuple[float, float]
    coordinate_space: QueryCoordinateSpace = QueryCoordinateSpace.DATA
    scope: QueryScope = QueryScope.DATA
    hit_policy: QueryHitPolicy = QueryHitPolicy.FRONTMOST
    requested_payload: tuple[QueryPayload, ...] = (
        QueryPayload.IDENTITY,
        QueryPayload.COORDINATE,
        QueryPayload.COLOR,
        QueryPayload.VALUE,
    )
    requested_extension_payload_kinds: tuple[str, ...] = ()
    freshness_policy: str = "latest"

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        if not self.requested_payload:
            raise ValueError("requested_payload must not be empty")
        for kind in self.requested_extension_payload_kinds:
            if not kind:
                raise ValueError("requested extension payload kinds must not be empty")


@dataclass(frozen=True, slots=True)
class QueryHit:
    """One contribution hit under a panel query coordinate."""

    contribution_kind: QueryContributionKind
    visual_id: str | None = None
    visual_family: VisualFamily | str | None = None
    item_id: int | None = None
    texel: tuple[int, int] | None = None
    visual_coordinate: tuple[float, float] | None = None
    data_coordinate: tuple[float, float] | None = None
    displayed_rgba: tuple[float, float, float, float] | None = None
    value: object | None = None
    extension_payload_kind: str | None = None
    extension_payload: object | None = None

    def __post_init__(self) -> None:
        if self.visual_id is not None:
            validate_id(self.visual_id)
        if self.item_id is not None and self.item_id < 0:
            raise ValueError("item_id must be non-negative")
        if self.texel is not None and (self.texel[0] < 0 or self.texel[1] < 0):
            raise ValueError("texel coordinates must be non-negative")
        if (self.extension_payload is None) != (self.extension_payload_kind is None):
            raise ValueError("extension payload kind and value must be provided together")


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Structured answer to a panel query."""

    request_id: str
    status: QueryStatus
    hit: bool
    panel_coordinate: tuple[float, float]
    hits: tuple[QueryHit, ...] = ()
    visual_id: str | None = None
    visual_family: VisualFamily | str | None = None
    item_id: int | None = None
    texel: tuple[int, int] | None = None
    visual_coordinate: tuple[float, float] | None = None
    data_coordinate: tuple[float, float] | None = None
    displayed_rgba: tuple[float, float, float, float] | None = None
    value: object | None = None
    extension_payload_kind: str | None = None
    extension_payload: object | None = None
    diagnostic: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.request_id)
        if self.status == QueryStatus.HIT and not self.hit:
            raise ValueError("hit results must set hit=True")
        if self.status != QueryStatus.HIT and self.hit:
            raise ValueError("non-hit results must set hit=False")
        self._normalize_hit_payloads()
        if self.status in (QueryStatus.UNSUPPORTED, QueryStatus.STALE, QueryStatus.DROPPED, QueryStatus.FAILED):
            if not self.diagnostic:
                raise ValueError(f"{self.status.value} query results require a diagnostic")
        if self.status != QueryStatus.HIT and (
            self.hits
            or self.visual_id is not None
            or self.visual_family is not None
            or self.item_id is not None
            or self.texel is not None
            or self.visual_coordinate is not None
            or self.data_coordinate is not None
            or self.displayed_rgba is not None
            or self.value is not None
            or self.extension_payload_kind is not None
            or self.extension_payload is not None
        ):
            raise ValueError("non-hit query results must not include hit payload fields")
        if (self.extension_payload is None) != (self.extension_payload_kind is None):
            raise ValueError("extension payload kind and value must be provided together")

    def _normalize_hit_payloads(self) -> None:
        if self.status != QueryStatus.HIT:
            return
        if not self.hits:
            object.__setattr__(self, "hits", (_query_hit_from_result_fields(self),))
            return

        first = self.hits[0]
        _set_if_none(self, "visual_id", first.visual_id)
        _set_if_none(self, "visual_family", first.visual_family)
        _set_if_none(self, "item_id", first.item_id)
        _set_if_none(self, "texel", first.texel)
        _set_if_none(self, "visual_coordinate", first.visual_coordinate)
        _set_if_none(self, "data_coordinate", first.data_coordinate)
        _set_if_none(self, "displayed_rgba", first.displayed_rgba)
        _set_if_none(self, "value", first.value)
        _set_if_none(self, "extension_payload_kind", first.extension_payload_kind)
        _set_if_none(self, "extension_payload", first.extension_payload)


def _query_hit_from_result_fields(result: QueryResult) -> QueryHit:
    contribution_kind = (
        QueryContributionKind.GUIDE if result.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND else QueryContributionKind.DATA
    )
    return QueryHit(
        contribution_kind=contribution_kind,
        visual_id=result.visual_id,
        visual_family=result.visual_family,
        item_id=result.item_id,
        texel=result.texel,
        visual_coordinate=result.visual_coordinate,
        data_coordinate=result.data_coordinate,
        displayed_rgba=result.displayed_rgba,
        value=result.value,
        extension_payload_kind=result.extension_payload_kind,
        extension_payload=result.extension_payload,
    )


def _set_if_none(result: QueryResult, field_name: str, value: object | None) -> None:
    if getattr(result, field_name) is None and value is not None:
        object.__setattr__(result, field_name, value)
