"""Tests for S020 no-network security validation scaffolding."""

import pytest

from gsp.protocol import (
    AdaptationOutcome,
    CapabilitySnapshot,
    CredentialPolicy,
    DataLocality,
    DataSourceDescriptor,
    DataSourceKind,
    ExtensionKind,
    ExtensionManifest,
    REDACTED_CREDENTIAL_REF,
    REDACTED_PATH,
    REDACTED_SECRET,
    REDACTED_URL,
    SecurityDiagnosticCode,
    TransportKind,
    redact_security_value,
    s020_security_capability_metadata,
    validate_extension_manifest,
    validate_no_network_source_descriptor,
    validate_static_manifest_security,
)


def _descriptor(**overrides: object) -> DataSourceDescriptor:
    values: dict[str, object] = {
        "id": "source:secure",
        "kind": DataSourceKind.TILED_IMAGE,
        "shape": (16, 16, 4),
        "locality": DataLocality.SYNTHETIC,
    }
    values.update(overrides)
    return DataSourceDescriptor(**values)  # type: ignore[arg-type]


def test_no_network_descriptor_accepts_synthetic_and_in_memory_sources():
    synthetic = validate_no_network_source_descriptor(_descriptor(locality=DataLocality.SYNTHETIC))
    in_memory = validate_no_network_source_descriptor(_descriptor(locality=DataLocality.IN_MEMORY))

    assert synthetic.accepted
    assert in_memory.accepted


def test_no_network_descriptor_accepts_preconfigured_handle_without_fetch_details():
    source_ref = {"resolver_id": "gsp.test.synthetic-resolver", "source_id": "public-demo-pyramid"}
    descriptor = _descriptor(
        locality=DataLocality.PRECONFIGURED_SOURCE,
        credential_policy=CredentialPolicy.PRECONFIGURED,
        source_ref=source_ref,
    )

    result = validate_no_network_source_descriptor(descriptor, allowed_source_refs=(source_ref,))

    assert result.accepted


def test_no_network_descriptor_rejects_missing_or_unknown_preconfigured_handle():
    missing = validate_no_network_source_descriptor(_descriptor(locality=DataLocality.PRECONFIGURED_SOURCE))
    unknown = validate_no_network_source_descriptor(
        _descriptor(
            locality=DataLocality.PRECONFIGURED_SOURCE,
            source_ref={"resolver_id": "gsp.test.synthetic-resolver", "source_id": "unknown"},
        ),
        allowed_source_refs=({"resolver_id": "gsp.test.synthetic-resolver", "source_id": "public-demo-pyramid"},),
    )

    assert not missing.accepted
    assert not unknown.accepted
    assert SecurityDiagnosticCode.SOURCE_HANDLE_UNKNOWN in missing.codes
    assert SecurityDiagnosticCode.SOURCE_HANDLE_UNKNOWN in unknown.codes


@pytest.mark.parametrize(
    ("locality", "code"),
    (
        (DataLocality.DIRECT_REMOTE_FETCH, SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED),
        (DataLocality.SERVER_RESOLVED_REMOTE, SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED),
        (DataLocality.LOCAL_FILE_SANDBOXED, SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED),
        (DataLocality.SERVER_FETCH, SecurityDiagnosticCode.SOURCE_LOCALITY_UNSUPPORTED),
    ),
)
def test_no_network_descriptor_rejects_unsafe_localities(locality: DataLocality, code: SecurityDiagnosticCode):
    result = validate_no_network_source_descriptor(_descriptor(locality=locality))

    assert not result.accepted
    assert code in result.codes


def test_no_network_descriptor_rejects_fetch_descriptor_and_private_urls():
    result = validate_no_network_source_descriptor(
        _descriptor(
            fetch_descriptor={"url": "http://169.254.169.254/latest/meta-data", "headers": {"Authorization": "token"}},
            metadata={"redirect_policy": "follow"},
        )
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.FETCH_DESCRIPTOR_REJECTED in result.codes
    assert SecurityDiagnosticCode.REMOTE_FETCH_DISABLED in result.codes
    assert SecurityDiagnosticCode.URL_RESOLVES_PRIVATE in result.codes
    assert SecurityDiagnosticCode.INLINE_SECRET_REJECTED in result.codes


def test_no_network_descriptor_rejects_paths_inline_secrets_and_credential_refs():
    result = validate_no_network_source_descriptor(
        _descriptor(
            credential_policy=CredentialPolicy.INLINE,
            credential_ref="aws-prod-admin",
            metadata={"local_path": "/etc/passwd", "api_key": "secret"},
        )
    )

    assert not result.accepted
    assert SecurityDiagnosticCode.CREDENTIAL_POLICY_UNSUPPORTED in result.codes
    assert SecurityDiagnosticCode.CREDENTIAL_REF_REJECTED in result.codes
    assert SecurityDiagnosticCode.LOCAL_PATH_FORBIDDEN in result.codes
    assert SecurityDiagnosticCode.INLINE_SECRET_REJECTED in result.codes


def test_static_manifest_security_rejects_executable_fields():
    manifest = ExtensionManifest(
        id="gsp.bad",
        version="0.1",
        kind=ExtensionKind.DATA_SOURCE,
        title="Bad manifest",
        schema={"source_kind": "tiled-image", "python_import": "evil.plugin"},
    )

    result = validate_static_manifest_security(manifest)

    assert not result.accepted
    assert SecurityDiagnosticCode.MANIFEST_EXECUTION_FORBIDDEN in result.codes
    with pytest.raises(ValueError, match="GSP_MANIFEST_EXECUTION_FORBIDDEN"):
        validate_extension_manifest(manifest)


def test_security_redaction_is_deterministic_and_recursive():
    redacted = redact_security_value(
        {
            "credential_ref": "aws-prod-admin",
            "url": "https://example.invalid/private?token=secret",
            "local_path": "/home/user/private.zarr",
            "nested": {"Authorization": "Bearer abc", "safe": "public"},
        }
    )

    assert redacted == {
        "credential_ref": REDACTED_CREDENTIAL_REF,
        "url": REDACTED_URL,
        "local_path": REDACTED_PATH,
        "nested": {"Authorization": REDACTED_SECRET, "safe": "public"},
    }


def test_capability_snapshot_defaults_keep_dangerous_features_absent():
    caps = CapabilitySnapshot(
        server_name="secure",
        protocol_versions=("0.2",),
        transports=(TransportKind.INPROC,),
        supported_data_source_localities=("synthetic", "in-memory", "preconfigured-source"),
        supported_credential_policies=("none", "preconfigured"),
        cache_modes=("none", "session-memory"),
    )

    assert caps.adapt_visual("point").outcome == AdaptationOutcome.REJECT
    assert caps.supports_remote_fetch_descriptors is False
    assert caps.supports_server_side_fetch is False
    assert caps.supports_dynamic_extension_loading is False
    assert caps.supports_package_entry_points is False
    assert caps.supports_executable_extension_hooks is False
    assert caps.supports_custom_decoders is False
    assert caps.supports_runtime_shaders is False
    assert caps.diagnostic_redaction is True


def test_capability_snapshot_rejects_dynamic_extension_loading_for_s020():
    with pytest.raises(ValueError, match="dynamic extension loading"):
        CapabilitySnapshot(
            server_name="unsafe",
            protocol_versions=("0.2",),
            transports=(TransportKind.INPROC,),
            supports_dynamic_extension_loading=True,
        )


def test_s020_security_capability_metadata_shape():
    metadata = s020_security_capability_metadata()

    assert metadata["data_sources"]["remote_fetch_descriptors"] == {"accepted": False}
    assert metadata["extensions"]["dynamic_discovery"] is False
    assert metadata["security"]["redaction_profile"] == "gsp.s020.no-network"
