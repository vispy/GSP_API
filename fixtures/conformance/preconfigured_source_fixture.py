"""S021 no-network preconfigured-source resolver fixture validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any, TypeAlias, cast

from gsp.protocol import (
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    NoNetworkPreconfiguredSourceResolver,
    TileIndex,
    TileRequest,
    demo_no_network_preconfigured_source_resolver,
    s020_security_capability_metadata,
)


JsonFixture: TypeAlias = dict[str, Any]

S021_PRECONFIGURED_SOURCE_FIXTURE_NAME = "s021_preconfigured_source.json"


@dataclass(frozen=True, slots=True)
class PreconfiguredSourceCaseResult:
    """One validated S021 preconfigured-source fixture case."""

    case_id: str
    kind: str
    passed: bool
    diagnostic: str | None = None


def load_s021_preconfigured_source_fixture() -> JsonFixture:
    """Load the committed S021 preconfigured-source fixture."""
    text = resources.files(__package__).joinpath(S021_PRECONFIGURED_SOURCE_FIXTURE_NAME).read_text(encoding="utf-8")
    return cast(JsonFixture, json.loads(text))


def validate_s021_preconfigured_source_fixture(fixture: JsonFixture | None = None) -> tuple[PreconfiguredSourceCaseResult, ...]:
    """Validate the S021 resolver fixture without network I/O or dynamic loading."""
    loaded = load_s021_preconfigured_source_fixture() if fixture is None else fixture
    if loaded.get("schema_kind") != "gsp.conformance.preconfigured-source":
        raise ValueError("preconfigured-source fixture schema_kind must be gsp.conformance.preconfigured-source")
    if loaded.get("schema_version") != "0.1.0":
        raise ValueError("preconfigured-source fixture schema_version must be 0.1.0")
    protocol = _required_child_mapping(loaded, "protocol")
    if protocol.get("network_io_allowed") is not False:
        raise ValueError("S021 preconfigured-source fixture must disable network I/O")
    if protocol.get("dynamic_loading_allowed") is not False:
        raise ValueError("S021 preconfigured-source fixture must disable dynamic loading")

    resolver = demo_no_network_preconfigured_source_resolver()
    _validate_resolver_capability(_required_child_mapping(loaded, "resolver"))
    cases = loaded.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("preconfigured-source fixture cases must be a non-empty list")
    return tuple(_validate_case(_required_mapping(case, "case"), resolver) for case in cases)


def _validate_resolver_capability(resolver_record: dict[str, Any]) -> None:
    resolver = demo_no_network_preconfigured_source_resolver()
    metadata = s020_security_capability_metadata(preconfigured_resolvers=(resolver.capability_record(),))
    data_sources = _required_mapping(metadata.get("data_sources"), "data_sources")
    resolvers = data_sources.get("preconfigured_resolvers")
    if not isinstance(resolvers, list) or len(resolvers) != 1:
        raise ValueError("S021 capability metadata must advertise one preconfigured resolver")
    if resolvers[0] != resolver_record.get("expected_capability"):
        raise ValueError("S021 resolver capability metadata does not match fixture")


def _validate_case(
    case: dict[str, Any],
    resolver: NoNetworkPreconfiguredSourceResolver,
) -> PreconfiguredSourceCaseResult:
    case_id = _required_string(case, "case_id")
    kind = _required_string(case, "kind")
    if kind == "resolve-tile":
        return _validate_resolve_tile_case(case_id, case, resolver)
    if kind == "reject-descriptor":
        return _validate_reject_descriptor_case(case_id, case, resolver)
    raise ValueError(f"unsupported preconfigured-source fixture case kind {kind!r}")


def _validate_resolve_tile_case(
    case_id: str,
    case: dict[str, Any],
    resolver: NoNetworkPreconfiguredSourceResolver,
) -> PreconfiguredSourceCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    resolved = resolver.resolve(descriptor)
    if not resolved.accepted or resolved.source is None or resolved.provider is None:
        raise ValueError(f"preconfigured-source fixture case {case_id!r} did not resolve")
    tile_request = _required_child_mapping(case, "tile_request")
    tile = resolved.provider.get_tile(
        TileRequest(
            source_id=resolved.source.id,
            tile=TileIndex(
                level=_required_int(tile_request, "level"),
                x=_required_int(tile_request, "x"),
                y=_required_int(tile_request, "y"),
            ),
        )
    )
    if tile.data is None:
        raise ValueError(f"preconfigured-source fixture case {case_id!r} produced no tile data")
    expected = _required_child_mapping(case, "expected_tile")
    if list(tile.data.shape) != _required_int_list(expected, "shape"):
        raise ValueError(f"preconfigured-source fixture case {case_id!r} tile shape mismatch")
    if list(tile.data[0, 0]) != _required_int_list(expected, "first_rgba"):
        raise ValueError(f"preconfigured-source fixture case {case_id!r} first pixel mismatch")
    if list(tile.data[-1, -1]) != _required_int_list(expected, "last_rgba"):
        raise ValueError(f"preconfigured-source fixture case {case_id!r} last pixel mismatch")
    return PreconfiguredSourceCaseResult(case_id=case_id, kind="resolve-tile", passed=True)


def _validate_reject_descriptor_case(
    case_id: str,
    case: dict[str, Any],
    resolver: NoNetworkPreconfiguredSourceResolver,
) -> PreconfiguredSourceCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    resolved = resolver.resolve(descriptor)
    expected = _required_string(case, "expected_diagnostic")
    if resolved.accepted:
        raise ValueError(f"preconfigured-source fixture case {case_id!r} unexpectedly resolved")
    if resolved.diagnostic != expected:
        raise ValueError(f"preconfigured-source fixture case {case_id!r} diagnostic mismatch")
    return PreconfiguredSourceCaseResult(case_id=case_id, kind="reject-descriptor", passed=True, diagnostic=resolved.diagnostic)


def _source_descriptor(value: dict[str, Any]) -> DataSourceDescriptor:
    return DataSourceDescriptor(
        id=_required_string(value, "id"),
        kind=DataSourceKind(_required_string(value, "kind")),
        shape=tuple(_required_int_list(value, "shape")),
        locality=DataLocality(str(value.get("locality", DataLocality.IN_MEMORY.value))),
        source_ref=_optional_string_mapping(value.get("source_ref")),
        fetch_descriptor=_optional_any_mapping(value.get("fetch_descriptor")),
        metadata=_optional_any_mapping(value.get("metadata")),
    )


def _optional_string_mapping(value: object) -> dict[str, str] | None:
    if value is None:
        return None
    mapping = _required_mapping(value, "mapping")
    if not all(isinstance(key, str) and isinstance(item, str) for key, item in mapping.items()):
        raise ValueError("mapping must map strings to strings")
    return cast(dict[str, str], mapping)


def _optional_any_mapping(value: object) -> dict[str, Any] | None:
    if value is None:
        return None
    return _required_mapping(value, "mapping")


def _required_child_mapping(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    return _required_mapping(value.get(field_name), field_name)


def _required_mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return cast(dict[str, Any], value)


def _required_string(value: dict[str, Any], field_name: str) -> str:
    field = value.get(field_name)
    if not isinstance(field, str) or not field:
        raise ValueError(f"{field_name} must be a non-empty string")
    return field


def _required_int(value: dict[str, Any], field_name: str) -> int:
    field = value.get(field_name)
    if not isinstance(field, int):
        raise ValueError(f"{field_name} must be an integer")
    return field


def _required_int_list(value: dict[str, Any], field_name: str) -> list[int]:
    field = value.get(field_name)
    if not isinstance(field, list) or not field or not all(isinstance(item, int) for item in field):
        raise ValueError(f"{field_name} must be a non-empty integer list")
    return cast(list[int], field)
