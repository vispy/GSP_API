"""S020 no-network security negative fixture validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Any, Mapping, TypeAlias, cast

from gsp.protocol import (
    CredentialPolicy,
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    ExtensionKind,
    ExtensionManifest,
    SecurityDiagnosticCode,
    redact_security_value,
    s020_security_capability_metadata,
    validate_no_network_source_descriptor,
    validate_static_manifest_security,
)


JsonFixture: TypeAlias = dict[str, Any]

S020_SECURITY_NEGATIVE_FIXTURE_NAME = "s020_security_negative.json"


@dataclass(frozen=True, slots=True)
class SecurityNegativeCaseResult:
    """One validated S020 negative fixture case."""

    case_id: str
    kind: str
    passed: bool
    observed_codes: tuple[str, ...] = ()


def load_s020_security_negative_fixture() -> JsonFixture:
    """Load the committed S020 no-network security negative fixture."""
    text = resources.files(__package__).joinpath(S020_SECURITY_NEGATIVE_FIXTURE_NAME).read_text(encoding="utf-8")
    return cast(JsonFixture, json.loads(text))


def validate_s020_security_negative_fixture(fixture: JsonFixture | None = None) -> tuple[SecurityNegativeCaseResult, ...]:
    """Validate all S020 security-negative fixture records without network I/O."""
    loaded = load_s020_security_negative_fixture() if fixture is None else fixture
    if loaded.get("schema_kind") != "gsp.conformance.security-negative":
        raise ValueError("security fixture schema_kind must be gsp.conformance.security-negative")
    if loaded.get("schema_version") != "0.1.0":
        raise ValueError("security fixture schema_version must be 0.1.0")
    protocol = _required_child_mapping(loaded, "protocol")
    if protocol.get("network_io_allowed") is not False:
        raise ValueError("S020 security fixture must disable network I/O")
    if protocol.get("dynamic_loading_allowed") is not False:
        raise ValueError("S020 security fixture must disable dynamic loading")

    allowed_source_refs = _allowed_source_refs(loaded)
    cases = loaded.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("security fixture cases must be a non-empty list")
    return tuple(_validate_case(_required_mapping(case, "case"), allowed_source_refs) for case in cases)


def _validate_case(case: dict[str, Any], allowed_source_refs: tuple[Mapping[str, str], ...]) -> SecurityNegativeCaseResult:
    case_id = _required_string(case, "case_id")
    kind = _required_string(case, "kind")
    if kind == "source-descriptor":
        return _validate_source_case(case_id, case, allowed_source_refs)
    if kind == "extension-manifest":
        return _validate_manifest_case(case_id, case)
    if kind == "redaction":
        return _validate_redaction_case(case_id, case)
    if kind == "capability-metadata":
        return _validate_capability_case(case_id, case)
    raise ValueError(f"unsupported security fixture case kind {kind!r}")


def _validate_source_case(
    case_id: str,
    case: dict[str, Any],
    allowed_source_refs: tuple[Mapping[str, str], ...],
) -> SecurityNegativeCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    result = validate_no_network_source_descriptor(descriptor, allowed_source_refs=allowed_source_refs)
    expected_codes = _expected_codes(case)
    observed_codes = tuple(code.value for code in result.codes)
    if not set(expected_codes).issubset(observed_codes):
        raise ValueError(f"security fixture case {case_id!r} did not produce expected diagnostic codes")
    return SecurityNegativeCaseResult(case_id=case_id, kind="source-descriptor", passed=True, observed_codes=observed_codes)


def _validate_manifest_case(case_id: str, case: dict[str, Any]) -> SecurityNegativeCaseResult:
    manifest = _extension_manifest(_required_child_mapping(case, "manifest"))
    result = validate_static_manifest_security(manifest)
    expected_codes = _expected_codes(case)
    observed_codes = tuple(code.value for code in result.codes)
    if not set(expected_codes).issubset(observed_codes):
        raise ValueError(f"security fixture case {case_id!r} did not produce expected diagnostic codes")
    return SecurityNegativeCaseResult(case_id=case_id, kind="extension-manifest", passed=True, observed_codes=observed_codes)


def _validate_redaction_case(case_id: str, case: dict[str, Any]) -> SecurityNegativeCaseResult:
    redacted = redact_security_value(case.get("value"))
    expected = case.get("expected_redacted")
    if redacted != expected:
        raise ValueError(f"security fixture case {case_id!r} redaction output does not match")
    return SecurityNegativeCaseResult(case_id=case_id, kind="redaction", passed=True)


def _validate_capability_case(case_id: str, case: dict[str, Any]) -> SecurityNegativeCaseResult:
    metadata = s020_security_capability_metadata()
    expected = _required_child_mapping(case, "expected")
    for dotted_key, expected_value in expected.items():
        observed = _get_dotted(metadata, dotted_key)
        if observed != expected_value:
            raise ValueError(f"security fixture case {case_id!r} expected {dotted_key}={expected_value!r}")
    return SecurityNegativeCaseResult(case_id=case_id, kind="capability-metadata", passed=True)


def _source_descriptor(value: dict[str, Any]) -> DataSourceDescriptor:
    return DataSourceDescriptor(
        id=_required_string(value, "id"),
        kind=DataSourceKind(_required_string(value, "kind")),
        shape=tuple(_required_int_list(value, "shape")),
        locality=DataLocality(str(value.get("locality", DataLocality.IN_MEMORY.value))),
        credential_policy=CredentialPolicy(str(value.get("credential_policy", CredentialPolicy.NONE.value))),
        source_ref=_optional_string_mapping(value.get("source_ref")),
        fetch_descriptor=_optional_any_mapping(value.get("fetch_descriptor")),
        credential_ref=_optional_string(value.get("credential_ref")),
        cache_policy=_optional_any_mapping(value.get("cache_policy")),
        metadata=_optional_any_mapping(value.get("metadata")),
    )


def _extension_manifest(value: dict[str, Any]) -> ExtensionManifest:
    return ExtensionManifest(
        id=_required_string(value, "id"),
        version=_required_string(value, "version"),
        kind=ExtensionKind(_required_string(value, "kind")),
        title=_required_string(value, "title"),
        schema=_optional_any_mapping(value.get("schema")) or {},
        implementations=cast(Mapping[str, str], _optional_any_mapping(value.get("implementations")) or {}),
        query_contract=_optional_any_mapping(value.get("query_contract")),
    )


def _expected_codes(case: dict[str, Any]) -> tuple[str, ...]:
    codes = case.get("expected_codes")
    if not isinstance(codes, list) or not codes:
        raise ValueError("security fixture case expected_codes must be a non-empty list")
    for code in codes:
        if not isinstance(code, str):
            raise ValueError("security fixture expected_codes entries must be strings")
        SecurityDiagnosticCode(code)
    return tuple(cast(list[str], codes))


def _allowed_source_refs(fixture: dict[str, Any]) -> tuple[Mapping[str, str], ...]:
    refs = fixture.get("allowed_source_refs", [])
    if not isinstance(refs, list):
        raise ValueError("security fixture allowed_source_refs must be a list")
    return tuple(_string_mapping(ref, "allowed_source_ref") for ref in refs)


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected optional string")
    return value


def _optional_string_mapping(value: object) -> dict[str, str] | None:
    if value is None:
        return None
    return dict(_string_mapping(value, "mapping"))


def _optional_any_mapping(value: object) -> dict[str, Any] | None:
    if value is None:
        return None
    return _required_mapping(value, "mapping")


def _string_mapping(value: object, field_name: str) -> Mapping[str, str]:
    mapping = _required_mapping(value, field_name)
    if not all(isinstance(key, str) and isinstance(item, str) for key, item in mapping.items()):
        raise ValueError(f"{field_name} must map strings to strings")
    return cast(Mapping[str, str], mapping)


def _get_dotted(value: Mapping[str, Any], dotted_key: str) -> object:
    current: object = value
    for part in dotted_key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise ValueError(f"missing capability metadata field {dotted_key!r}")
        current = current[part]
    return current


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


def _required_int_list(value: dict[str, Any], field_name: str) -> list[int]:
    field = value.get(field_name)
    if not isinstance(field, list) or not field or not all(isinstance(item, int) for item in field):
        raise ValueError(f"{field_name} must be a non-empty integer list")
    return cast(list[int], field)
