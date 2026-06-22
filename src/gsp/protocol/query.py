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
    hit_policy: QueryHitPolicy = QueryHitPolicy.FRONTMOST
    requested_payload: tuple[QueryPayload, ...] = (
        QueryPayload.IDENTITY,
        QueryPayload.COORDINATE,
        QueryPayload.COLOR,
        QueryPayload.VALUE,
    )
    freshness_policy: str = "latest"

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        if not self.requested_payload:
            raise ValueError("requested_payload must not be empty")


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Structured answer to a panel query."""

    request_id: str
    status: QueryStatus
    hit: bool
    panel_coordinate: tuple[float, float]
    visual_id: str | None = None
    visual_family: VisualFamily | None = None
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
        if self.status in (QueryStatus.UNSUPPORTED, QueryStatus.STALE, QueryStatus.DROPPED, QueryStatus.FAILED):
            if not self.diagnostic:
                raise ValueError(f"{self.status.value} query results require a diagnostic")
        if self.status != QueryStatus.HIT and (
            self.visual_id is not None
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
