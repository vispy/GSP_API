"""S022 no-network mock HTTP `.npy` array fixture validation."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import json
from importlib import resources
from typing import Any, Mapping, TypeAlias, cast

import numpy as np
import numpy.typing as npt

from gsp.protocol import (
    CredentialPolicy,
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    MaterializationPolicy,
    S022NpyDecoderPolicy,
    SecurityDiagnosticCode,
    redact_security_value,
    validate_s022_http_array_source_descriptor,
    validate_s022_npy_decoder_payload,
)


JsonFixture: TypeAlias = dict[str, Any]

S022_HTTP_MOCK_ARRAY_FIXTURE_NAME = "s022_http_mock_array.json"
_SOURCE_REF = {"resolver_id": "gsp.demo.http-resource-resolver", "source_id": "demo-http-npy-array"}
_FETCHER_ID = "gsp.fetcher.http.mock.v1"
_DECODER_ID = "gsp.decoder.npy.v1"
_CONTENT_TYPES = ("application/x-npy", "application/octet-stream")


@dataclass(frozen=True, slots=True)
class S022HttpMockArrayCaseResult:
    """One validated S022 mock HTTP array fixture case."""

    case_id: str
    kind: str
    passed: bool
    observed_codes: tuple[str, ...] = ()


def load_s022_http_mock_array_fixture() -> JsonFixture:
    """Load the committed S022 no-network mock HTTP array fixture."""
    text = resources.files(__package__).joinpath(S022_HTTP_MOCK_ARRAY_FIXTURE_NAME).read_text(encoding="utf-8")
    return cast(JsonFixture, json.loads(text))


def validate_s022_http_mock_array_fixture(fixture: JsonFixture | None = None) -> tuple[S022HttpMockArrayCaseResult, ...]:
    """Validate S022 mock HTTP `.npy` array fixtures without network I/O."""
    loaded = load_s022_http_mock_array_fixture() if fixture is None else fixture
    if loaded.get("schema_kind") != "gsp.conformance.s022-http-mock-array":
        raise ValueError("S022 fixture schema_kind must be gsp.conformance.s022-http-mock-array")
    if loaded.get("schema_version") != "0.1.0":
        raise ValueError("S022 fixture schema_version must be 0.1.0")
    protocol = _required_child_mapping(loaded, "protocol")
    if protocol.get("network_io_allowed") is not False:
        raise ValueError("S022 mock HTTP array fixture must disable network I/O")
    if protocol.get("dynamic_loading_allowed") is not False:
        raise ValueError("S022 mock HTTP array fixture must disable dynamic loading")

    _validate_access_record(_required_child_mapping(loaded, "mock_access"))
    cases = loaded.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("S022 mock HTTP array fixture cases must be a non-empty list")
    return tuple(_validate_case(_required_mapping(case, "case")) for case in cases)


def s022_http_mock_array_capability_metadata() -> dict[str, object]:
    """Return the public S022 mock HTTP array capability posture."""
    return {
        "data_sources": {
            "supported_source_localities": ["synthetic", "in-memory", "preconfigured-source"],
            "supported_source_contracts": [
                {
                    "source_kind": "array",
                    "contract_id": "gsp.source.array.v1",
                    "formats": ["npy"],
                    "decoder_ids": [_DECODER_ID],
                    "materialization_targets": ["array-resource"],
                    "query_contracts": ["gsp.query.array-value.v1"],
                    "max_rank": 3,
                    "max_elements": 1_048_576,
                    "max_decoded_bytes": 4_194_304,
                }
            ],
            "supported_credential_policies": ["none"],
            "remote_fetch_descriptors": {"accepted": False},
            "supports_server_side_fetch": {"accepted": False, "reason": "s022-mock-fetch-only"},
            "remote_access": {
                "scene_supplied_urls": False,
                "configured_access_only": True,
                "access_mechanisms": [
                    {
                        "id": "http",
                        "fetcher_ids": [_FETCHER_ID],
                        "network_io": False,
                        "schemes": ["https"],
                        "methods": ["GET"],
                        "url_in_protocol": False,
                        "host_policy": "admin-allowlist-private-address-reject",
                        "redirect_policy": {"mode": "reject", "max_redirects": 0},
                        "timeout_ms_max": 2000,
                        "retries_max": 0,
                        "response_bytes_max": 1_048_576,
                        "content_encoding": ["identity"],
                        "request_headers": "admin-fixed-safe-only",
                        "cookies": False,
                        "userinfo_allowed": False,
                        "fragments_allowed": False,
                        "query_strings_allowed": False,
                        "dns_rebinding_protection": True,
                    }
                ],
            },
            "decoders": [
                {
                    "decoder_id": _DECODER_ID,
                    "format": "npy",
                    "content_types": list(_CONTENT_TYPES),
                    "allow_pickle": False,
                    "allow_object_dtype": False,
                    "allow_structured_dtype": False,
                    "allow_string_dtype": False,
                    "allow_fortran_order": False,
                    "allowed_dtypes": ["uint8", "uint16", "float32"],
                    "allowed_npy_versions": ["1.0", "2.0"],
                    "max_header_bytes": 4096,
                    "max_rank": 3,
                    "max_elements": 1_048_576,
                    "max_decoded_bytes": 4_194_304,
                }
            ],
            "preconfigured_resolvers": [
                {
                    "resolver_id": _SOURCE_REF["resolver_id"],
                    "source_kinds": ["array"],
                    "source_ids": [_SOURCE_REF["source_id"]],
                    "access_mechanisms": ["http"],
                    "decoder_ids": [_DECODER_ID],
                    "credential_policies": ["none"],
                    "network_io": False,
                }
            ],
            "cache_modes": ["none", "session-memory"],
        },
        "security": {
            "redaction_profile": "gsp.s022.http-single-resource.mock",
            "diagnostic_redaction": True,
            "fixture_remote_sources_allowed": False,
            "raw_urls_in_protocol": False,
            "raw_credentials_in_protocol": False,
            "resolver_outputs_in_replay": False,
        },
    }


def _validate_case(case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    case_id = _required_string(case, "case_id")
    kind = _required_string(case, "kind")
    if kind == "mock-array-success":
        return _validate_success_case(case_id, case)
    if kind == "descriptor-negative":
        return _validate_descriptor_negative_case(case_id, case)
    if kind == "mock-response-negative":
        return _validate_mock_response_negative_case(case_id, case)
    if kind == "query-negative":
        return _validate_query_negative_case(case_id, case)
    if kind == "capability-metadata":
        return _validate_capability_case(case_id, case)
    if kind == "redaction":
        return _validate_redaction_case(case_id, case)
    if kind == "cache-isolation":
        return _validate_cache_isolation_case(case_id, case)
    raise ValueError(f"unsupported S022 fixture case kind {kind!r}")


def _validate_success_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    descriptor_result = validate_s022_http_array_source_descriptor(descriptor, allowed_source_refs=(_SOURCE_REF,))
    if not descriptor_result.accepted:
        raise ValueError(f"S022 fixture case {case_id!r} descriptor did not validate")
    response = _required_child_mapping(case, "mock_response")
    payload = _mock_response_payload(response)
    policy = _decoder_policy(descriptor, _required_child_mapping(case, "decoder_policy"))
    decoder_result = validate_s022_npy_decoder_payload(payload, policy)
    if not decoder_result.accepted:
        raise ValueError(f"S022 fixture case {case_id!r} decoder did not validate")
    array = _materialize_array(payload)
    expected = _required_child_mapping(case, "expected_array")
    if list(array.shape) != _required_int_list(expected, "shape"):
        raise ValueError(f"S022 fixture case {case_id!r} materialized shape mismatch")
    if str(array.dtype) != _required_string(expected, "dtype"):
        raise ValueError(f"S022 fixture case {case_id!r} materialized dtype mismatch")
    if array.tolist() != expected.get("values"):
        raise ValueError(f"S022 fixture case {case_id!r} materialized values mismatch")
    query = _required_child_mapping(case, "query")
    value = _array_value_at(array, tuple(_required_int_list(query, "index")))
    if value != query.get("expected_value"):
        raise ValueError(f"S022 fixture case {case_id!r} query value mismatch")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="mock-array-success", passed=True)


def _validate_descriptor_negative_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    result = validate_s022_http_array_source_descriptor(descriptor, allowed_source_refs=(_SOURCE_REF,))
    expected_codes = _expected_codes(case)
    observed_codes = tuple(code.value for code in result.codes)
    if result.accepted or not set(expected_codes).issubset(observed_codes):
        raise ValueError(f"S022 fixture case {case_id!r} did not produce expected descriptor diagnostics")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="descriptor-negative", passed=True, observed_codes=observed_codes)


def _validate_mock_response_negative_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    response = _required_child_mapping(case, "mock_response")
    policy = _decoder_policy(descriptor, _required_child_mapping(case, "decoder_policy"))
    observed_codes = _validate_mock_response(response, policy)
    expected_codes = _expected_codes(case)
    if not set(expected_codes).issubset(observed_codes):
        raise ValueError(f"S022 fixture case {case_id!r} did not produce expected response diagnostics")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="mock-response-negative", passed=True, observed_codes=observed_codes)


def _validate_query_negative_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    descriptor = _source_descriptor(_required_child_mapping(case, "descriptor"))
    array = _deterministic_array(tuple(descriptor.shape), descriptor.dtype)
    query = _required_child_mapping(case, "query")
    expected_codes = _expected_codes(case)
    observed_codes = _validate_array_query(array, tuple(_required_int_list(query, "index")), _required_int(query, "max_result_values"))
    if not set(expected_codes).issubset(observed_codes):
        raise ValueError(f"S022 fixture case {case_id!r} did not produce expected query diagnostics")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="query-negative", passed=True, observed_codes=observed_codes)


def _validate_capability_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    metadata = s022_http_mock_array_capability_metadata()
    expected = _required_child_mapping(case, "expected")
    for dotted_key, expected_value in expected.items():
        observed = _get_dotted(metadata, dotted_key)
        if observed != expected_value:
            raise ValueError(f"S022 fixture case {case_id!r} expected {dotted_key}={expected_value!r}")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="capability-metadata", passed=True)


def _validate_redaction_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    redacted = redact_security_value(case.get("value"))
    expected = case.get("expected_redacted")
    if redacted != expected:
        raise ValueError(f"S022 fixture case {case_id!r} redaction output does not match")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="redaction", passed=True)


def _validate_cache_isolation_case(case_id: str, case: dict[str, Any]) -> S022HttpMockArrayCaseResult:
    left = _required_child_mapping(case, "left")
    right = _required_child_mapping(case, "right")
    left_parts = _cache_identity_parts(left)
    right_parts = _cache_identity_parts(right)
    if left_parts == right_parts:
        raise ValueError(f"S022 fixture case {case_id!r} did not isolate cache identity parts")
    if "expected_public_cache_fields" in case and case["expected_public_cache_fields"] != []:
        raise ValueError(f"S022 fixture case {case_id!r} serialized cache fields must be empty")
    return S022HttpMockArrayCaseResult(case_id=case_id, kind="cache-isolation", passed=True)


def _validate_access_record(access: dict[str, Any]) -> None:
    if access.get("mechanism") != "http":
        raise ValueError("S022 mock access mechanism must be http")
    if access.get("fetcher_id") != _FETCHER_ID:
        raise ValueError("S022 mock access must use gsp.fetcher.http.mock.v1")
    if access.get("network_io") is not False:
        raise ValueError("S022 mock access must disable network I/O")
    if access.get("configured_access_only") is not True:
        raise ValueError("S022 mock access must be configured-only")
    if access.get("scene_supplied_urls") is not False:
        raise ValueError("S022 mock access must reject scene-supplied URLs")


def _validate_mock_response(response: dict[str, Any], policy: S022NpyDecoderPolicy) -> tuple[str, ...]:
    observed: list[str] = []
    content_type = _required_string(response, "content_type")
    if content_type not in _CONTENT_TYPES:
        observed.append(SecurityDiagnosticCode.CONTENT_TYPE_UNSUPPORTED.value)
    content_encoding = _required_string(response, "content_encoding")
    if content_encoding != "identity":
        observed.append(SecurityDiagnosticCode.CONTENT_ENCODING_UNSUPPORTED.value)
    payload = _mock_response_payload(response)
    if len(payload) > _required_int(response, "response_bytes_max"):
        observed.append(SecurityDiagnosticCode.CHUNK_LIMIT_EXCEEDED.value)
    decoder_result = validate_s022_npy_decoder_payload(payload, policy)
    observed.extend(code.value for code in decoder_result.codes)
    return tuple(observed)


def _mock_response_payload(response: dict[str, Any]) -> bytes:
    body_kind = _required_string(response, "body_kind")
    if body_kind == "deterministic-npy-array":
        shape = tuple(_required_int_list(response, "shape"))
        dtype = _required_string(response, "dtype")
        return _npy_bytes(_deterministic_array(shape, dtype))
    if body_kind == "invalid-npy-magic":
        return b"not-npy"
    if body_kind == "oversized-npy-array":
        shape = tuple(_required_int_list(response, "shape"))
        dtype = _required_string(response, "dtype")
        return _npy_bytes(np.zeros(shape, dtype=np.dtype(dtype)))
    raise ValueError(f"unsupported S022 mock response body_kind {body_kind!r}")


def _deterministic_array(shape: tuple[int, ...], dtype: str) -> npt.NDArray[np.generic]:
    total = int(np.prod(shape))
    values = np.arange(total, dtype=np.dtype(dtype)).reshape(shape)
    return cast(npt.NDArray[np.generic], values)


def _npy_bytes(array: npt.NDArray[np.generic]) -> bytes:
    buffer = BytesIO()
    np.save(buffer, array, allow_pickle=False)
    return buffer.getvalue()


def _materialize_array(payload: bytes) -> npt.NDArray[np.generic]:
    with BytesIO(payload) as buffer:
        loaded = np.load(buffer, allow_pickle=False)
    return cast(npt.NDArray[np.generic], loaded)


def _decoder_policy(descriptor: DataSourceDescriptor, value: dict[str, Any]) -> S022NpyDecoderPolicy:
    return S022NpyDecoderPolicy(
        expected_shape=tuple(descriptor.shape),
        expected_dtype=descriptor.dtype,
        max_header_bytes=_required_int(value, "max_header_bytes"),
        max_rank=_required_int(value, "max_rank"),
        max_elements=_required_int(value, "max_elements"),
        max_decoded_bytes=_required_int(value, "max_decoded_bytes"),
    )


def _array_value_at(array: npt.NDArray[np.generic], index: tuple[int, ...]) -> object:
    if len(index) != array.ndim:
        raise ValueError("query index rank must match array rank")
    if any(dim < 0 or dim >= array.shape[offset] for offset, dim in enumerate(index)):
        raise ValueError("query index is outside declared array bounds")
    return cast(object, array[index].item())


def _validate_array_query(array: npt.NDArray[np.generic], index: tuple[int, ...], max_result_values: int) -> tuple[str, ...]:
    observed: list[str] = []
    if len(index) != array.ndim or any(dim < 0 or dim >= array.shape[offset] for offset, dim in enumerate(index)):
        observed.append(SecurityDiagnosticCode.QUERY_SCOPE_VIOLATION.value)
    if max_result_values < 1:
        observed.append(SecurityDiagnosticCode.QUERY_RESULT_LIMIT_EXCEEDED.value)
    return tuple(observed)


def _cache_identity_parts(value: dict[str, Any]) -> tuple[object, ...]:
    return (
        _required_string(value, "tenant_id"),
        _required_string(value, "session_id"),
        _required_string(value, "resolver_id"),
        _required_string(value, "source_id"),
        _required_string(value, "authorization_generation"),
        tuple(_required_int_list(value, "shape")),
        _required_string(value, "dtype"),
        _required_string(value, "decoder_id"),
        _required_string(value, "decoder_policy_revision"),
        _required_string(value, "source_generation"),
    )


def _source_descriptor(value: dict[str, Any]) -> DataSourceDescriptor:
    return DataSourceDescriptor(
        id=_required_string(value, "id"),
        kind=DataSourceKind(_required_string(value, "kind")),
        shape=tuple(_required_int_list(value, "shape")),
        dtype=str(value.get("dtype", "uint8")),
        channels=_required_int(value, "channels"),
        coordinate_system=str(value.get("coordinate_system", "pixel")),
        locality=DataLocality(str(value.get("locality", DataLocality.IN_MEMORY.value))),
        credential_policy=CredentialPolicy(str(value.get("credential_policy", CredentialPolicy.NONE.value))),
        source_ref=_optional_string_mapping(value.get("source_ref")),
        fetch_descriptor=_optional_any_mapping(value.get("fetch_descriptor")),
        credential_ref=_optional_string(value.get("credential_ref")),
        cache_policy=_optional_any_mapping(value.get("cache_policy")),
        materialization_policy=MaterializationPolicy(str(value.get("materialization_policy", MaterializationPolicy.FULL.value))),
        metadata=_optional_any_mapping(value.get("metadata")),
    )


def _expected_codes(case: dict[str, Any]) -> tuple[str, ...]:
    codes = case.get("expected_codes")
    if not isinstance(codes, list) or not codes:
        raise ValueError("S022 fixture case expected_codes must be a non-empty list")
    for code in codes:
        if not isinstance(code, str):
            raise ValueError("S022 fixture expected_codes entries must be strings")
        SecurityDiagnosticCode(code)
    return tuple(cast(list[str], codes))


def _get_dotted(value: Mapping[str, Any], dotted_key: str) -> object:
    current: object = value
    for part in dotted_key.split("."):
        if isinstance(current, list):
            if not part.isdigit() or int(part) >= len(current):
                raise ValueError(f"missing S022 capability metadata field {dotted_key!r}")
            current = current[int(part)]
            continue
        if not isinstance(current, Mapping) or part not in current:
            raise ValueError(f"missing S022 capability metadata field {dotted_key!r}")
        current = current[part]
    return current


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected optional string")
    return value


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
