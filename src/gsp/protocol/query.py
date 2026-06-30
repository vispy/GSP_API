"""First-slice panel query models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from .color import ScalarColorSlot, ScalarRangeClass
from .ids import validate_id
from .guides import AxisDimension
from .transforms import InverseStatus


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
    TEXT = "text"
    MESH = "mesh"


class QueryContributionKind(str, Enum):
    """Top-level kind of contribution represented by a query hit."""

    DATA = "data"
    GUIDE = "guide"


GUIDE_QUERY_PAYLOAD_KIND = "gsp.guide-query@0.1"
TEXT_QUERY_PAYLOAD_KIND = "gsp.text-query@0.1"
MESH_QUERY_PAYLOAD_KIND = "gsp.mesh-query@0.1"
SCALAR_COLOR_QUERY_PAYLOAD_KIND = "gsp.scalar-color-query@0.1"
TRANSFORM_QUERY_PAYLOAD_KIND = "gsp.transform-query@0.1"
VIEW3D_QUERY_PAYLOAD_KIND = "gsp.view3d-query@0.1"


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
class MeshQueryPayload:
    """Mesh-specific payload for bounded face-level reference queries."""

    visual_id: str
    hit_kind: str
    face_index: int
    vertex_indices: tuple[int, int, int]
    panel_xy: tuple[float, float]
    coordinate_space: str
    displayed_rgba: tuple[float, float, float, float]

    def __post_init__(self) -> None:
        validate_id(self.visual_id)
        if self.hit_kind != "face":
            raise ValueError("mesh query hit_kind must be 'face'")
        if self.face_index < 0:
            raise ValueError("face_index must be non-negative")
        if len(self.vertex_indices) != 3 or any(
            index < 0 for index in self.vertex_indices
        ):
            raise ValueError("vertex_indices must contain three non-negative indices")


@dataclass(frozen=True, slots=True)
class ScalarColorQueryPayload:
    """Scalar color mapping payload for deterministic query/readback tests."""

    visual_id: str
    item_kind: str
    color_slot: ScalarColorSlot | str
    color_scale_id: str
    colormap_id: str
    source_value: float
    normalized_value_raw: float
    normalized_value_clipped: float
    range_class: ScalarRangeClass | str
    lut_index: int
    displayed_rgba: tuple[float, float, float, float]
    item_id: int | None = None
    texel: tuple[int, int] | None = None
    face_index: int | None = None

    def __post_init__(self) -> None:
        validate_id(self.visual_id)
        validate_id(self.color_scale_id)
        if not self.item_kind:
            raise ValueError("item_kind must not be empty")
        if isinstance(self.color_slot, str):
            ScalarColorSlot(self.color_slot)
        elif not isinstance(self.color_slot, ScalarColorSlot):
            raise TypeError("color_slot must be a ScalarColorSlot or string")
        if not self.colormap_id:
            raise ValueError("colormap_id must not be empty")
        if isinstance(self.range_class, str):
            ScalarRangeClass(self.range_class)
        elif not isinstance(self.range_class, ScalarRangeClass):
            raise TypeError("range_class must be a ScalarRangeClass or string")
        if not all(
            np.isfinite(value)
            for value in (
                self.source_value,
                self.normalized_value_raw,
                self.normalized_value_clipped,
            )
        ):
            raise ValueError("scalar query numeric fields must be finite")
        if self.normalized_value_clipped < 0.0 or self.normalized_value_clipped > 1.0:
            raise ValueError("normalized_value_clipped must be in [0, 1]")
        if self.lut_index < 0 or self.lut_index > 255:
            raise ValueError("lut_index must be in [0, 255]")
        if len(self.displayed_rgba) != 4 or any(
            not np.isfinite(channel) or channel < 0.0 or channel > 1.0
            for channel in self.displayed_rgba
        ):
            raise ValueError("displayed_rgba must contain four values in [0, 1]")
        if self.item_id is not None and self.item_id < 0:
            raise ValueError("item_id must be non-negative")
        if self.texel is not None and (self.texel[0] < 0 or self.texel[1] < 0):
            raise ValueError("texel coordinates must be non-negative")
        if self.face_index is not None and self.face_index < 0:
            raise ValueError("face_index must be non-negative")


@dataclass(frozen=True, slots=True)
class TransformQueryPayload:
    """Transformed query inverse/readout payload for S027."""

    visual_id: str
    panel_xy: tuple[float, float]
    panel_ndc: tuple[float, float]
    declared_coordinate_space: str
    declared_space_coord: tuple[float, float] | None
    source_coord: tuple[float, float] | None
    data_coord: tuple[float, float] | None
    inverse_status: InverseStatus | str
    transform_ids: tuple[str, ...] = ()
    inline_transform_digest: str | None = None
    view_id: str | None = None
    view_digest: str | None = None
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        validate_id(self.visual_id)
        _validate_finite_pair("panel_xy", self.panel_xy)
        _validate_finite_pair("panel_ndc", self.panel_ndc)
        if not self.declared_coordinate_space:
            raise ValueError("declared_coordinate_space must not be empty")
        _validate_optional_finite_pair("declared_space_coord", self.declared_space_coord)
        _validate_optional_finite_pair("source_coord", self.source_coord)
        _validate_optional_finite_pair("data_coord", self.data_coord)
        if isinstance(self.inverse_status, str):
            try:
                InverseStatus(self.inverse_status)
            except ValueError as exc:
                raise ValueError("inverse_status must be a valid InverseStatus") from exc
        elif not isinstance(self.inverse_status, InverseStatus):
            raise TypeError("inverse_status must be an InverseStatus or string")
        for transform_id in self.transform_ids:
            validate_id(transform_id)
        if self.inline_transform_digest is not None and not self.inline_transform_digest:
            raise ValueError("inline_transform_digest must not be empty")
        if self.view_id is not None:
            validate_id(self.view_id)
        if self.view_digest is not None and not self.view_digest:
            raise ValueError("view_digest must not be empty")
        for diagnostic in self.diagnostics:
            if not diagnostic:
                raise ValueError("diagnostics must not contain empty strings")


@dataclass(frozen=True, slots=True)
class View3DQueryPayload:
    """S036 projection-inverse ray context for one View3D panel query."""

    view_id: str
    view_revision: int
    layout_snapshot_id: str
    view_projection_snapshot_id: str
    panel_xy: tuple[float, float]
    panel_ndc: tuple[float, float]
    near_data_point: tuple[float, float, float]
    far_data_point: tuple[float, float, float]
    ray_direction: tuple[float, float, float]

    def __post_init__(self) -> None:
        validate_id(self.view_id)
        validate_id(self.layout_snapshot_id)
        validate_id(self.view_projection_snapshot_id)
        if self.view_revision < 0:
            raise ValueError("view_revision must be non-negative")
        _validate_finite_pair("panel_xy", self.panel_xy)
        _validate_finite_pair("panel_ndc", self.panel_ndc)
        _validate_finite_triple("near_data_point", self.near_data_point)
        _validate_finite_triple("far_data_point", self.far_data_point)
        _validate_finite_triple("ray_direction", self.ray_direction)
        norm = float(np.linalg.norm(np.asarray(self.ray_direction, dtype=np.float64)))
        if not np.isclose(norm, 1.0):
            raise ValueError("ray_direction must be normalized")


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
    layout_snapshot_id: str | None = None
    view_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.id)
        validate_id(self.panel_id)
        if self.layout_snapshot_id is not None:
            try:
                validate_id(self.layout_snapshot_id)
            except ValueError as exc:
                raise ValueError(f"layout_snapshot_id invalid: {exc}") from exc
        if self.view_snapshot_id is not None:
            try:
                validate_id(self.view_snapshot_id)
            except ValueError as exc:
                raise ValueError(f"view_snapshot_id invalid: {exc}") from exc
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
            raise ValueError(
                "extension payload kind and value must be provided together"
            )


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
    layout_snapshot_id: str | None = None
    view_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        validate_id(self.request_id)
        if self.layout_snapshot_id is not None:
            try:
                validate_id(self.layout_snapshot_id)
            except ValueError as exc:
                raise ValueError(f"layout_snapshot_id invalid: {exc}") from exc
        if self.view_snapshot_id is not None:
            try:
                validate_id(self.view_snapshot_id)
            except ValueError as exc:
                raise ValueError(f"view_snapshot_id invalid: {exc}") from exc
        if self.status == QueryStatus.HIT and not self.hit:
            raise ValueError("hit results must set hit=True")
        if self.status != QueryStatus.HIT and self.hit:
            raise ValueError("non-hit results must set hit=False")
        self._normalize_hit_payloads()
        if self.status in (
            QueryStatus.UNSUPPORTED,
            QueryStatus.STALE,
            QueryStatus.DROPPED,
            QueryStatus.FAILED,
        ):
            if not self.diagnostic:
                raise ValueError(
                    f"{self.status.value} query results require a diagnostic"
                )
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
            raise ValueError(
                "non-hit query results must not include hit payload fields"
            )
        if (self.extension_payload is None) != (self.extension_payload_kind is None):
            raise ValueError(
                "extension payload kind and value must be provided together"
            )

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
        QueryContributionKind.GUIDE
        if result.extension_payload_kind == GUIDE_QUERY_PAYLOAD_KIND
        else QueryContributionKind.DATA
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


def _validate_finite_pair(name: str, value: tuple[float, float]) -> None:
    if len(value) != 2 or not all(np.isfinite(component) for component in value):
        raise ValueError(f"{name} must contain two finite values")


def _validate_finite_triple(name: str, value: tuple[float, float, float]) -> None:
    if len(value) != 3 or not all(np.isfinite(component) for component in value):
        raise ValueError(f"{name} must contain three finite values")


def _validate_optional_finite_pair(
    name: str, value: tuple[float, float] | None
) -> None:
    if value is not None:
        _validate_finite_pair(name, value)
