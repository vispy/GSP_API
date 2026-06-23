"""S020 no-network security validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, TypeAlias

from .data_sources import CredentialPolicy, DataLocality, DataSourceDescriptor, DataSourceKind, MaterializationPolicy
from .extensions import ExtensionManifest


JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class SecurityDiagnosticCode(str, Enum):
    """Stable S020 security diagnostic codes."""

    SOURCE_LOCALITY_UNSUPPORTED = "GSP_SOURCE_LOCALITY_UNSUPPORTED"
    SOURCE_HANDLE_UNKNOWN = "GSP_SOURCE_HANDLE_UNKNOWN"
    REMOTE_FETCH_DISABLED = "GSP_REMOTE_FETCH_DISABLED"
    SERVER_SIDE_FETCH_DISABLED = "GSP_SERVER_SIDE_FETCH_DISABLED"
    FETCH_DESCRIPTOR_REJECTED = "GSP_FETCH_DESCRIPTOR_REJECTED"
    URL_SCHEME_FORBIDDEN = "GSP_URL_SCHEME_FORBIDDEN"
    URL_USERINFO_FORBIDDEN = "GSP_URL_USERINFO_FORBIDDEN"
    URL_HOST_NOT_ALLOWED = "GSP_URL_HOST_NOT_ALLOWED"
    URL_RESOLVES_PRIVATE = "GSP_URL_RESOLVES_PRIVATE"
    URL_REDIRECT_REJECTED = "GSP_URL_REDIRECT_REJECTED"
    LOCAL_PATH_FORBIDDEN = "GSP_LOCAL_PATH_FORBIDDEN"
    LOCAL_PATH_TRAVERSAL = "GSP_LOCAL_PATH_TRAVERSAL"
    CREDENTIAL_POLICY_UNSUPPORTED = "GSP_CREDENTIAL_POLICY_UNSUPPORTED"
    CREDENTIAL_REF_REJECTED = "GSP_CREDENTIAL_REF_REJECTED"
    INLINE_SECRET_REJECTED = "GSP_INLINE_SECRET_REJECTED"
    MANIFEST_SCHEMA_INVALID = "GSP_MANIFEST_SCHEMA_INVALID"
    MANIFEST_EXECUTION_FORBIDDEN = "GSP_MANIFEST_EXECUTION_FORBIDDEN"
    EXTENSION_DYNAMIC_LOADING_DISABLED = "GSP_EXTENSION_DYNAMIC_LOADING_DISABLED"
    DECODER_PLUGIN_DISABLED = "GSP_DECODER_PLUGIN_DISABLED"
    SHADER_EXTENSION_DISABLED = "GSP_SHADER_EXTENSION_DISABLED"
    CHUNK_METADATA_INVALID = "GSP_CHUNK_METADATA_INVALID"
    CHUNK_LIMIT_EXCEEDED = "GSP_CHUNK_LIMIT_EXCEEDED"
    DECOMPRESSION_LIMIT_EXCEEDED = "GSP_DECOMPRESSION_LIMIT_EXCEEDED"
    CACHE_POLICY_UNSUPPORTED = "GSP_CACHE_POLICY_UNSUPPORTED"
    QUERY_SCOPE_VIOLATION = "GSP_QUERY_SCOPE_VIOLATION"
    QUERY_RESULT_LIMIT_EXCEEDED = "GSP_QUERY_RESULT_LIMIT_EXCEEDED"
    REPLAY_REDACTION_REQUIRED = "GSP_REPLAY_REDACTION_REQUIRED"
    SOURCE_CONTRACT_UNSUPPORTED = "GSP_SOURCE_CONTRACT_UNSUPPORTED"
    DECODER_UNSUPPORTED = "GSP_DECODER_UNSUPPORTED"
    CONTENT_TYPE_UNSUPPORTED = "GSP_CONTENT_TYPE_UNSUPPORTED"
    CONTENT_ENCODING_UNSUPPORTED = "GSP_CONTENT_ENCODING_UNSUPPORTED"
    HTTP_STATUS_REJECTED = "GSP_HTTP_STATUS_REJECTED"
    URL_FRAGMENT_FORBIDDEN = "GSP_URL_FRAGMENT_FORBIDDEN"
    URL_QUERY_FORBIDDEN = "GSP_URL_QUERY_FORBIDDEN"
    URL_DNS_REBINDING_REJECTED = "GSP_URL_DNS_REBINDING_REJECTED"
    HTTP_TLS_VALIDATION_FAILED = "GSP_HTTP_TLS_VALIDATION_FAILED"
    HTTP_TIMEOUT = "GSP_HTTP_TIMEOUT"


@dataclass(frozen=True, slots=True)
class SecurityDiagnostic:
    """One stable no-network security diagnostic."""

    code: SecurityDiagnosticCode
    message: str


@dataclass(frozen=True, slots=True)
class SecurityValidationResult:
    """Result for S020 validation helpers."""

    accepted: bool
    diagnostics: tuple[SecurityDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if not self.accepted and not self.diagnostics:
            raise ValueError("rejected security validation results require diagnostics")

    @property
    def codes(self) -> tuple[SecurityDiagnosticCode, ...]:
        """Return diagnostic codes for assertions and fixture expectations."""
        return tuple(diagnostic.code for diagnostic in self.diagnostics)


S020_EXECUTABLE_LOCALITIES: tuple[DataLocality, ...] = (
    DataLocality.SYNTHETIC,
    DataLocality.IN_MEMORY,
    DataLocality.PRECONFIGURED_SOURCE,
)
S020_CREDENTIAL_POLICIES: tuple[CredentialPolicy, ...] = (
    CredentialPolicy.NONE,
    CredentialPolicy.PRECONFIGURED,
)

REDACTED_CREDENTIAL_REF = "<redacted:credential-ref>"
REDACTED_SOURCE_REF = "<redacted:source-ref>"
REDACTED_URL = "<redacted:url>"
REDACTED_PATH = "<redacted:path>"
REDACTED_SECRET = "<redacted:secret>"

_URL_SCHEMES = (
    "http://",
    "https://",
    "s3://",
    "gs://",
    "gcs://",
    "file://",
    "ftp://",
    "gopher://",
    "data:",
    "dict://",
    "smb://",
    "ssh://",
)
_PRIVATE_URL_MARKERS = (
    "127.",
    "localhost",
    "169.254.169.254",
    "[::1]",
    "10.",
    "192.168.",
    "172.16.",
)
_SENSITIVE_KEY_PARTS = (
    "authorization",
    "cookie",
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "credential",
)
_URL_KEY_PARTS = ("url", "uri", "endpoint")
_PATH_KEY_PARTS = ("path", "filename", "local_file")
_EXECUTABLE_MANIFEST_KEYS = (
    "python_import",
    "import_path",
    "module",
    "class",
    "entry_point",
    "entry_points",
    "hook",
    "hooks",
    "callback",
    "callbacks",
    "decoder_callback",
    "shader_source",
    "shader_url",
    "runtime_shader",
    "command",
    "shell",
    "code_url",
    "pickle",
    "cloudpickle",
    "dill",
)
S022_HTTP_ARRAY_FORMAT = "npy"
S022_HTTP_ARRAY_DECODER_ID = "gsp.decoder.npy.v1"
S022_HTTP_ARRAY_MATERIALIZATION_TARGET = "array-resource"
S022_HTTP_ARRAY_COORDINATE_SYSTEM = "array-index"
S022_HTTP_ARRAY_CACHE_MODES = ("none", "session-memory")
S022_HTTP_ARRAY_ALLOWED_DTYPES = ("uint8", "uint16", "float32")
_S022_FORBIDDEN_METADATA_KEYS = (
    "fetch_descriptor",
    "url",
    "uri",
    "href",
    "endpoint",
    "host",
    "port",
    "path",
    "bucket",
    "object_key",
    "signed_url",
    "query",
    "headers",
    "cookies",
    "authorization",
    "credential_ref",
    "credentials",
    "secret",
    "token",
    "api_key",
    "decoder_config",
    "decoder_module",
    "decoder_import",
    "python_import",
    "entry_point",
    "package",
    "pip",
    "callback",
    "hook",
    "plugin",
    "shader",
    "shader_source",
    "runtime_shader",
    "cache_key",
    "resolved_url",
    "dns_result",
    "ip_address",
    "etag_from_resolver",
    "private_digest",
)
_S022_SECRET_METADATA_KEYS = (
    "headers",
    "cookies",
    "authorization",
    "credential_ref",
    "credentials",
    "secret",
    "token",
    "api_key",
)
_S022_URL_METADATA_KEYS = (
    "fetch_descriptor",
    "url",
    "uri",
    "href",
    "endpoint",
    "host",
    "port",
    "bucket",
    "object_key",
    "signed_url",
    "query",
    "resolved_url",
)
_S022_PATH_METADATA_KEYS = ("path",)
_S022_DECODER_PLUGIN_METADATA_KEYS = (
    "decoder_config",
    "decoder_module",
    "decoder_import",
    "python_import",
    "entry_point",
    "package",
    "pip",
    "callback",
    "hook",
    "plugin",
)


def validate_no_network_source_descriptor(
    descriptor: DataSourceDescriptor,
    *,
    allowed_source_refs: tuple[Mapping[str, str], ...] | None = None,
) -> SecurityValidationResult:
    """Validate a data-source descriptor against the S020 no-network posture."""
    diagnostics: list[SecurityDiagnostic] = []
    if descriptor.locality not in S020_EXECUTABLE_LOCALITIES:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED,
                f"source locality {descriptor.locality.value!r} is not executable in S020 no-network mode",
            )
        )
    if descriptor.locality == DataLocality.PRECONFIGURED_SOURCE and not descriptor.source_ref:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.SOURCE_HANDLE_UNKNOWN,
                "preconfigured-source descriptors require an opaque source_ref",
            )
        )
    if descriptor.locality == DataLocality.PRECONFIGURED_SOURCE and descriptor.source_ref and allowed_source_refs is not None:
        source_ref = dict(descriptor.source_ref)
        allowed = tuple(dict(ref) for ref in allowed_source_refs)
        if source_ref not in allowed:
            diagnostics.append(
                SecurityDiagnostic(
                    SecurityDiagnosticCode.SOURCE_HANDLE_UNKNOWN,
                    "preconfigured-source source_ref is not advertised by the no-network resolver",
                )
            )
    if descriptor.fetch_descriptor:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.FETCH_DESCRIPTOR_REJECTED,
                "fetch_descriptor is reserved and rejected in S020 no-network mode",
            )
        )
    if descriptor.credential_policy not in S020_CREDENTIAL_POLICIES:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CREDENTIAL_POLICY_UNSUPPORTED,
                f"credential policy {descriptor.credential_policy.value!r} is not supported in S020 no-network mode",
            )
        )
    if descriptor.credential_ref:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CREDENTIAL_REF_REJECTED,
                "credential_ref selection is reserved and rejected in S020 no-network mode",
            )
        )
    _scan_mapping(descriptor.source_ref or {}, diagnostics)
    _scan_mapping(descriptor.fetch_descriptor or {}, diagnostics)
    _scan_mapping(descriptor.cache_policy or {}, diagnostics)
    _scan_mapping(descriptor.metadata or {}, diagnostics)
    return SecurityValidationResult(accepted=not diagnostics, diagnostics=tuple(diagnostics))


def validate_s022_http_array_source_descriptor(
    descriptor: DataSourceDescriptor,
    *,
    allowed_source_refs: tuple[Mapping[str, str], ...] | None = None,
) -> SecurityValidationResult:
    """Validate the S022 no-network HTTP single-resource array descriptor shape.

    This validates only scene-visible descriptor metadata. It does not fetch, parse URLs, resolve
    hosts, inspect files, look up credentials, execute decoders, or load plugins.
    """
    diagnostics: list[SecurityDiagnostic] = list(
        validate_no_network_source_descriptor(descriptor, allowed_source_refs=allowed_source_refs).diagnostics
    )
    if descriptor.kind != DataSourceKind.ARRAY:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.SOURCE_CONTRACT_UNSUPPORTED,
                "S022 HTTP single-resource proof requires source_kind='array'",
            )
        )
    if descriptor.locality != DataLocality.PRECONFIGURED_SOURCE:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED,
                "S022 HTTP array descriptors require locality='preconfigured-source'",
            )
        )
    if descriptor.credential_policy != CredentialPolicy.NONE:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CREDENTIAL_POLICY_UNSUPPORTED,
                "S022 HTTP array descriptors require credential_policy='none'",
            )
        )
    if descriptor.dtype not in S022_HTTP_ARRAY_ALLOWED_DTYPES:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                f"S022 HTTP array dtype {descriptor.dtype!r} is not allowed",
            )
        )
    if len(descriptor.shape) not in (2, 3):
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                "S022 HTTP array shape must have rank 2 or 3",
            )
        )
    if len(descriptor.shape) == 2 and descriptor.channels != 1:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                "S022 rank-2 arrays require channels=1",
            )
        )
    if descriptor.coordinate_system != S022_HTTP_ARRAY_COORDINATE_SYSTEM:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                "S022 HTTP array descriptors require coordinate_system='array-index'",
            )
        )
    if descriptor.materialization_policy != MaterializationPolicy.FULL:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                "S022 HTTP array descriptors require materialization_policy='full'",
            )
        )
    metadata = descriptor.metadata or {}
    format_value = metadata.get("format")
    decoder_id = metadata.get("decoder_id")
    materialization_target = metadata.get("materialization_target")
    if format_value != S022_HTTP_ARRAY_FORMAT:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                "S022 HTTP array descriptors require metadata.format='npy'",
            )
        )
    if decoder_id != S022_HTTP_ARRAY_DECODER_ID:
        code = (
            SecurityDiagnosticCode.DECODER_PLUGIN_DISABLED
            if _looks_executable_decoder_id(decoder_id)
            else SecurityDiagnosticCode.DECODER_UNSUPPORTED
        )
        diagnostics.append(
            SecurityDiagnostic(
                code,
                "S022 HTTP array descriptors require metadata.decoder_id='gsp.decoder.npy.v1'",
            )
        )
    if materialization_target != S022_HTTP_ARRAY_MATERIALIZATION_TARGET:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CHUNK_METADATA_INVALID,
                "S022 HTTP array descriptors require metadata.materialization_target='array-resource'",
            )
        )
    _validate_s022_cache_policy(descriptor.cache_policy or {}, diagnostics)
    _scan_s022_forbidden_mapping(metadata, diagnostics, allowed_keys=("format", "decoder_id", "materialization_target"))
    return SecurityValidationResult(accepted=not diagnostics, diagnostics=tuple(diagnostics))


def validate_static_manifest_security(manifest: ExtensionManifest) -> SecurityValidationResult:
    """Validate that a manifest remains data-only and cannot activate code."""
    diagnostics: list[SecurityDiagnostic] = []
    for section_name, section in (
        ("schema", manifest.schema),
        ("implementations", manifest.implementations),
        ("query_contract", manifest.query_contract or {}),
    ):
        _scan_manifest_mapping(section_name, section, diagnostics)
    return SecurityValidationResult(accepted=not diagnostics, diagnostics=tuple(diagnostics))


def redact_security_value(value: object) -> JsonValue:
    """Return a JSON-safe value with S020-sensitive keys and strings redacted."""
    if value is None or isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, Mapping):
        redacted: dict[str, JsonValue] = {}
        for key, item in value.items():
            key_text = str(key)
            redacted[key_text] = _redacted_placeholder_for_key(key_text) or redact_security_value(item)
        return redacted
    if isinstance(value, tuple):
        return [redact_security_value(item) for item in value]
    if isinstance(value, list):
        return [redact_security_value(item) for item in value]
    return repr(value)


def s020_security_capability_metadata(
    preconfigured_resolvers: tuple[Mapping[str, object], ...] = (),
) -> dict[str, JsonValue]:
    """Return a conservative no-network capability metadata block."""
    return {
        "data_sources": {
            "supported_source_localities": [locality.value for locality in S020_EXECUTABLE_LOCALITIES],
            "supported_credential_policies": [policy.value for policy in S020_CREDENTIAL_POLICIES],
            "preconfigured_resolvers": [redact_security_value(resolver) for resolver in preconfigured_resolvers],
            "remote_fetch_descriptors": {"accepted": False},
            "supports_server_side_fetch": {"accepted": False},
            "cache_modes": ["none", "session-memory"],
        },
        "extensions": {
            "static_manifest_validation": True,
            "dynamic_discovery": False,
            "package_entry_points": False,
            "executable_hooks": False,
            "custom_decoders": False,
            "runtime_shaders": False,
        },
        "security": {
            "redaction_profile": "gsp.s020.no-network",
            "diagnostic_redaction": True,
            "fixture_remote_sources_allowed": False,
        },
    }


def _scan_mapping(value: Mapping[str, object], diagnostics: list[SecurityDiagnostic]) -> None:
    for raw_key, item in value.items():
        key = str(raw_key).lower()
        if any(part in key for part in _SENSITIVE_KEY_PARTS):
            diagnostics.append(
                SecurityDiagnostic(SecurityDiagnosticCode.INLINE_SECRET_REJECTED, f"field {raw_key!r} may contain secret material")
            )
        if any(part in key for part in _URL_KEY_PARTS):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.REMOTE_FETCH_DISABLED, f"field {raw_key!r} is URL-like"))
        if any(part in key for part in _PATH_KEY_PARTS):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.LOCAL_PATH_FORBIDDEN, f"field {raw_key!r} is path-like"))
        _scan_value(item, diagnostics)


def _validate_s022_cache_policy(value: Mapping[str, object], diagnostics: list[SecurityDiagnostic]) -> None:
    mode = value.get("mode", "none")
    if mode not in S022_HTTP_ARRAY_CACHE_MODES:
        diagnostics.append(
            SecurityDiagnostic(
                SecurityDiagnosticCode.CACHE_POLICY_UNSUPPORTED,
                f"S022 HTTP array cache mode {mode!r} is not supported",
            )
        )
    _scan_s022_forbidden_mapping(value, diagnostics, allowed_keys=("mode",))


def _scan_s022_forbidden_mapping(
    value: Mapping[str, object],
    diagnostics: list[SecurityDiagnostic],
    *,
    allowed_keys: tuple[str, ...],
) -> None:
    for raw_key, item in value.items():
        key = str(raw_key).lower()
        if key.startswith("x-"):
            _scan_value(item, diagnostics)
            continue
        forbidden = key in _S022_FORBIDDEN_METADATA_KEYS
        if key in _S022_SECRET_METADATA_KEYS or any(part in key for part in _SENSITIVE_KEY_PARTS):
            diagnostics.append(
                SecurityDiagnostic(SecurityDiagnosticCode.INLINE_SECRET_REJECTED, f"field {raw_key!r} is forbidden in S022 descriptors")
            )
        if key in _S022_URL_METADATA_KEYS or any(part in key for part in _URL_KEY_PARTS):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.REMOTE_FETCH_DISABLED, f"field {raw_key!r} is URL-like"))
        if key in _S022_PATH_METADATA_KEYS or any(part in key for part in _PATH_KEY_PARTS):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.LOCAL_PATH_FORBIDDEN, f"field {raw_key!r} is path-like"))
        if key in _S022_DECODER_PLUGIN_METADATA_KEYS:
            diagnostics.append(
                SecurityDiagnostic(SecurityDiagnosticCode.DECODER_PLUGIN_DISABLED, f"field {raw_key!r} implies decoder plugin behavior")
            )
        if key not in allowed_keys and not forbidden:
            diagnostics.append(
                SecurityDiagnostic(SecurityDiagnosticCode.MANIFEST_SCHEMA_INVALID, f"field {raw_key!r} is not allowed in S022 descriptors")
            )
        if (
            forbidden
            and key not in _S022_SECRET_METADATA_KEYS
            and key not in _S022_URL_METADATA_KEYS
            and key not in _S022_PATH_METADATA_KEYS
            and key not in _S022_DECODER_PLUGIN_METADATA_KEYS
        ):
            diagnostics.append(
                SecurityDiagnostic(SecurityDiagnosticCode.MANIFEST_SCHEMA_INVALID, f"field {raw_key!r} is forbidden in S022 descriptors")
            )
        _scan_value(item, diagnostics)


def _looks_executable_decoder_id(value: object) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(marker in lowered for marker in ("python", "import", "entry_point", "plugin", "callback", "hook", ":", "/"))


def _scan_value(value: object, diagnostics: list[SecurityDiagnostic]) -> None:
    if isinstance(value, str):
        lowered = value.lower()
        if any(lowered.startswith(scheme) for scheme in _URL_SCHEMES):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.REMOTE_FETCH_DISABLED, "URL-like values are rejected"))
        if any(marker in lowered for marker in _PRIVATE_URL_MARKERS):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.URL_RESOLVES_PRIVATE, "private or metadata-service targets are rejected"))
        if "@" in lowered and (lowered.startswith("http://") or lowered.startswith("https://")):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.URL_USERINFO_FORBIDDEN, "URL userinfo is rejected"))
        if ".." in lowered or lowered.startswith("/") or lowered.startswith("\\\\"):
            diagnostics.append(SecurityDiagnostic(SecurityDiagnosticCode.LOCAL_PATH_FORBIDDEN, "path-like values are rejected"))
    elif isinstance(value, Mapping):
        _scan_mapping({str(key): item for key, item in value.items()}, diagnostics)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _scan_value(item, diagnostics)


def _scan_manifest_mapping(
    section_name: str,
    value: Mapping[str, object],
    diagnostics: list[SecurityDiagnostic],
) -> None:
    for raw_key, item in value.items():
        key = str(raw_key).lower()
        if any(part in key for part in _EXECUTABLE_MANIFEST_KEYS):
            diagnostics.append(
                SecurityDiagnostic(
                    SecurityDiagnosticCode.MANIFEST_EXECUTION_FORBIDDEN,
                    f"manifest {section_name}.{raw_key} implies executable behavior",
                )
            )
        if isinstance(item, Mapping):
            _scan_manifest_mapping(f"{section_name}.{raw_key}", {str(key): child for key, child in item.items()}, diagnostics)
        elif isinstance(item, (list, tuple)):
            for index, child in enumerate(item):
                if isinstance(child, Mapping):
                    _scan_manifest_mapping(
                        f"{section_name}.{raw_key}[{index}]",
                        {str(key): nested for key, nested in child.items()},
                        diagnostics,
                    )


def _redacted_placeholder_for_key(key: str) -> str | None:
    lowered = key.lower()
    if lowered in ("credential_policy", "credential_policies", "supported_credential_policies"):
        return None
    if "credential_ref" in lowered:
        return REDACTED_CREDENTIAL_REF
    if "source_ref" in lowered:
        return REDACTED_SOURCE_REF
    if any(part in lowered for part in _SENSITIVE_KEY_PARTS):
        return REDACTED_SECRET
    if any(part in lowered for part in _URL_KEY_PARTS):
        return REDACTED_URL
    if any(part in lowered for part in _PATH_KEY_PARTS):
        return REDACTED_PATH
    return None


def _redact_string(value: str) -> str:
    lowered = value.lower()
    if any(lowered.startswith(scheme) for scheme in _URL_SCHEMES):
        return REDACTED_URL
    if lowered.startswith("/") or lowered.startswith("\\\\") or ".." in lowered:
        return REDACTED_PATH
    return value
